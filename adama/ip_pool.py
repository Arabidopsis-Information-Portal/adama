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
