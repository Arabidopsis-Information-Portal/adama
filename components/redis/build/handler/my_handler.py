from base_handler import BaseHandler
import supervisor


class MyHandler(BaseHandler):

    def setup(self):
        super(MyHandler, self).setup()
        supervisor.start_docker(
            'redis.conf',
            '--rm {} redis redis-server --appendonly yes'.format(self.volumes))
