import json

from mischief.actors.process_actor import ProcessActor


class MinionServer(ProcessActor):

    def act(self):
        while True:
            self.receive(
                start=self.start
            )

    def start(self, msg):
        with open('/msg', 'w') as f:
            f.write(json.dumps(msg))
