import json
import time
import uuid

import rabbitpy


class TimeoutException(Exception):
    pass


class Channel(object):

    POLL_FREQUENCY = 0.1  # seconds

    def __init__(self, uri=None, name=None):
        if isinstance(uri, Channel):
            self._uri = uri._uri
        else:
            self._uri = uri or 'ampq://127.0.0.1:5672'
        self._name = name or uuid.uuid4().hex
        self._conn = None
        self._connect()

    def _connect(self):
        if self._conn is not None and self._conn._io.isAlive():
            return

        self._conn = rabbitpy.Connection(self._uri)
        self._ch = self._conn.channel()
        self._queue = rabbitpy.Queue(self._ch, self._name)
        self._queue.durable = True
        self._queue.declare()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def get(self, timeout=float('inf')):
        self._connect()
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
            return Channel(uri=uri, name=ch)

    def put(self, value):
        self._connect()
        if isinstance(value, Channel):
            headers = {
                '_channel': value._name,
                '_uri': value._uri
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
    assert isinstance(y, basestring)

    c.put({'a': x, 'b': y})

    d = Channel(a)
    d.put(5)
    return d

