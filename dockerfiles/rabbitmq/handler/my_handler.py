from base_handler import BaseHandler
import supervisor


class MyHandler(BaseHandler):

    def setup(self):
        supervisor.start('rabbitmq')