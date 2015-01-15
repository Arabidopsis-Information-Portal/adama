from base_handler import BaseHandler
import supervisor


class MyHandler(BaseHandler):

    def setup(self):
        super(MyHandler, self).setup()
        supervisor.start_docker(
            'app.conf',
            '--rm {} ubuntu sleep infinity'.format(self.volumes))
