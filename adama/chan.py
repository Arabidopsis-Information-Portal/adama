import json
import time
import uuid

import rabbitpy


class TimeoutException(Exception):
    pass


class Message(object):

    def __init__(self, headers, body):
        self._headers = headers
        self._body = body

    @property
    def body(self):
        """
        :rtype: T
        """
        return self._body

    @property
    def headers(self):
        """
        :rtype: Dict[str, Any]
        """
        return self._headers


class AbstractConnection(object):

    def connect(self):
        """Connect to the message broker.

        This method should be idempotent.
        """
        pass

    def close(self):
        pass

    def setup(self, name):
        """Setup a queue ``name`` in the broker.

        :type name: str
        """
        pass

    def get(self):
        """
        :rtype: Optional[Message[T]]
        """
        pass

    def put(self, msg):
        """
        :type msg: Message[T]
        """
        pass


class RabbitConnection(AbstractConnection):

    def __init__(self, uri):
        self._uri = uri or 'ampq://127.0.0.1:5672'
        self._conn = None

    def connect(self):
        if self._conn is not None and self._conn._io.is_alive():
            return

        self._conn = rabbitpy.Connection(self._uri)
        self._ch = self._conn.channel()

    def setup(self, name):
        self._name = name
        self._queue = rabbitpy.Queue(self._ch, name)
        self._queue.durable = True
        self._queue.declare()

    def get(self):
        msg = self._queue.get()
        if msg is None:
            return None
        msg.ack()
        return Message(msg.properties['headers'] or {}, msg.body)

    def put(self, msg):
        _msg = rabbitpy.Message(self._ch, msg.body, {'headers': msg.headers})
        _msg.publish('', self._name)


class Channel(object):

    POLL_FREQUENCY = 0.1  # seconds

    def __init__(self, name=None, connection=None):
        if isinstance(name, Channel):
            # if name is another Channel, reuse its connection
            self._conn = name._conn
        else:
            self._conn = connection

        self._name = name or uuid.uuid4().hex
        self._conn.connect()
        self._conn.setup(self._name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del exc_type, exc_val, exc_tb
        self._conn.close()

    def get(self, timeout=float('inf')):
        self._conn.connect()
        start = time.time()
        while True:
            msg = self._conn.get()
            if msg is not None:
                return self._process(msg)
            if time.time() - start > timeout:
                raise TimeoutException()
            time.sleep(self.POLL_FREQUENCY)

    def _process(self, msg):
        ch = msg.headers.get('_channel')
        if ch is None:
            return json.loads(msg.body)
        else:
            uri = msg.headers.get('_uri')
            conn = RabbitConnection(uri)
            return Channel(name=ch, connection=conn)

    def put(self, value):
        self._conn.connect()
        if isinstance(value, Channel):
            headers = {
                '_channel': value._name,
                '_uri': value._conn._uri
            }
            self._conn.put(Message(headers, ''))
        else:
            self._conn.put(Message({}, json.dumps(value)))


class RabbitChannel(Channel):

    def __init__(self, name=None, uri=None):
        conn = RabbitConnection(uri)
        super(RabbitChannel, self).__init__(name, conn)


def test(a, b, c):
    """

    :type a: ChanIn[int]
    :type b: ChanIn[str]
    :type c: ChanOut[Dict]
    :rtype: ChanOut[int]
    """
    x = a.get()
    assert isinstance(x, int)

    y = b.get()
    assert isinstance(y, basestring)

    c.put({'a': x, 'b': y})

    d = Channel(a)
    d.put(5)
    return d

