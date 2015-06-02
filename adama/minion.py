import json
import time

from tasks import QueueConnection


class Minion(QueueConnection):

    def callback(self, message, responder):
        print 'Got', message
        time.sleep(10)
        responder(json.dumps({'ok': True}))

    def run(self):
        self.consume_forever(self.callback)


