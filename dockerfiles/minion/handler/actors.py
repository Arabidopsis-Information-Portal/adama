import json

import mischief.actors.process_actor as pa


class MinionServer(pa.ProcessActor):

    def act(self):
        while True:
            self.receive(
                start=self.start
            )

    def start(self, msg):
        with open('/msg', 'w') as f:
            f.write(json.dumps(msg))


class Another(pa.ProcessActor):

    def act(self):
        while True:
            self.receive()

