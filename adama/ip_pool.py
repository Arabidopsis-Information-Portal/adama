import threading
from collections import deque
import json
import multiprocessing

from .tasks import QueueConnection
from .config import Config


class IPPoolDeque(object):

    def __init__(self):
        self.ips = deque((i, j)
                         for i in range(1, 255)
                         for j in range(1, 255))
        self.ips.remove((42, 1))

    def get(self):
        return self.ips.popleft()

    def put(self, obj):
        if obj in self.ips:
            return
        self.ips.append(obj)


class IPPoolServer(object):

    def __init__(self):
        self.ips = IPPoolDeque()
        self.start()

    def act(self, message, responder):
        msg = json.loads(message)
        if msg['tag'] == 'get':
            try:
                responder(json.dumps({'ip': self.ips.get()}))
            except IndexError:
                # no more ip's available
                responder(json.dumps({'ip': None}))
        if msg['tag'] == 'put':
            self.ips.put(msg['ip'])

    def _run(self):
        conn = QueueConnection(Config.get('queue', 'host'),
                               Config.getint('queue', 'port'),
                               'ip_pool')
        conn.consume_forever(self.act, exclusive=True)

    def start(self):
        self.proc = multiprocessing.Process(
            target=self._run, name='ip_pool_server')
        self.proc.start()


class IPPoolClient(object):

    def connect(self):
        return QueueConnection(Config.get('queue', 'host'),
                               Config.getint('queue', 'port'),
                               'ip_pool')

    def get(self):
        conn = self.connect()
        conn.send(json.dumps({'tag': 'get'}))
        g = conn.receive()
        try:
            return json.loads(next(g))
        finally:
            g.close()
            conn.connection.close()

    def put(self, obj):
        conn = self.connect()
        conn.send(json.dumps({'tag': 'put', 'ip': obj}))


def get(s, m):
    cl = IPPoolClient()
    for i in range(m):
        s.add(tuple(cl.get()['ip']))

def test(n=50, m=10):
    sets = [set() for i in range(n)]
    threads = []
    for a_set in sets:
        t = threading.Thread(target=get, args=(a_set, m))
        t.start()
        threads.append(t)
    [t.join() for t in threads]
    return sets

def check(sets):
    return not any(u.intersection(v) for u in sets for v in sets if u != v)

