import json
import time
import uuid

import rabbitpy


class TimeoutException(Exception):
    pass


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

    def delete(self):
        """Delete the queue in the broker. """
        pass

    def get(self):
        """
        :rtype: Optional[T]
        """
        pass

    def put(self, msg):
        """
        :type msg: T
        """
        pass


class RabbitConnection(AbstractConnection):

    _conn = None

    def __init__(self, uri):
        self._uri = uri or 'ampq://127.0.0.1:5672'
        self._ch = None

    def connect(self):
        if self._conn is None or not self._conn._io.is_alive():
            RabbitConnection._conn = rabbitpy.Connection(self._uri)

        if self._ch is None or self._ch.closed:
            self._ch = self._conn.channel()

    def setup(self, name):
        self._name = name
        self._queue = rabbitpy.Queue(self._ch, name)
        self._queue.durable = True
        self._queue.declare()

    def close(self):
        self._ch.close()

    def delete(self):
        self._queue.delete()

    def get(self):
        msg = self._queue.get()
        if msg is None:
            return None
        msg.ack()
        return msg.body

    def put(self, msg):
        _msg = rabbitpy.Message(self._ch, msg, {})
        _msg.publish('', self._name)


class ChannelEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Channel):
            return {
                '__channel__': True,
                'name': obj._name,
                'uri': obj.uri
            }
        return super(ChannelEncoder, self).default(obj)


def as_channel(dct):
    if '__channel__' in dct:
        return Channel(dct['name'], dct['uri'])
    return dct


class Channel(object):

    POLL_FREQUENCY = 0.1  # seconds

    def __init__(self, name=None, uri=None):
        """
        :type name: str
        :type uri: str
        """
        self.uri = uri
        self._name = name or uuid.uuid4().hex
        self._conn = RabbitConnection(uri)
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
        return json.loads(msg, object_hook=as_channel)

    def put(self, value):
        self._conn.connect()
        self._conn.put(json.dumps(value, cls=ChannelEncoder))

    def close(self):
        self._conn.delete()


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

    d = Channel(uri=a.uri)
    d.put(5)
    return d
