from base_handler import BaseHandler
import supervisor


class MyHandler(BaseHandler):

    def setup(self):
        super(MyHandler, self).setup()
        supervisor.start_docker(
            'registry',
            '--rm {} -e STORAGE_PATH=/data registry'.format(self.all_volumes))

