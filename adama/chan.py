import json
import time
import uuid

import rabbitpy


class TimeoutException(Exception):
    pass


class Connection(object):

    def __init__(self, uri, name):
        self._uri = uri
        self._name = name or uuid.uuid4().hex
        self._connect()

    def _connect(self):
        self._conn = rabbitpy.Connection(self._uri)
        self._ch = self._conn.channel()
        self._queue = rabbitpy.Queue(self._ch, self._name)
        self._queue.durable = True
        self._queue.declare()

    def _type(self, ch_type):
        return {
            'in': ChanIn,
            'out': ChanOut
        }[ch_type]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()


class ChanIn(Connection):

    POLL_FREQUENCY = 0.1  # seconds

    def __init__(self, uri=None, name=None):
        super(ChanIn, self).__init__(uri, name)

    def get(self, timeout=float('inf')):
        start = time.time()
        while True:
            msg = self._queue.get()
            if msg is not None:
                return self._process(msg)
            if time.time() - start > timeout:
                raise TimeoutException()
            time.sleep(self.POLL_FREQUENCY)

    def _process(self, msg):
        msg.ack()
        headers = msg.properties.get('headers') or {}
        ch = headers.get('_channel')
        if ch is None:
            return json.loads(msg.body)
        else:
            uri = headers.get('_uri')
            chan_type = headers.get('_chan_type', 'in')
            return self._type(chan_type)(uri=uri, name=ch)


class ChanOut(Connection):

    def __init__(self, uri=None, name=None):
        super(ChanOut, self).__init__(uri, name)

    def put(self, value):
        if isinstance(value, (ChanIn, ChanOut)):
            headers = {
                '_channel': value._name,
                '_uri': value._uri,
                '_chan_type': 'in' if isinstance(value, ChanIn) else 'out'
            }
            msg = rabbitpy.Message(self._ch, '', {'headers': headers})
        else:
            msg = rabbitpy.Message(self._ch, json.dumps(value), {})
        msg.publish('', self._name)


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
    assert isinstance(y, str)

    c.put({'a': x, 'b': y})

    d = ChanOut()
    d.put(5)
    return d

