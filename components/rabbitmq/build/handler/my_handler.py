from base_handler import BaseHandler
import supervisor


class MyHandler(BaseHandler):

    def setup(self):
        super(MyHandler, self).setup()
        supervisor.start_docker(
            'rabbitmq.conf',
            '--rm {} dockerfile/rabbitmq'.format(self.volumes))
