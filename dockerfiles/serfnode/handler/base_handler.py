import os
import socket

from serf_master import SerfHandler
from utils import with_payload, truncated_stdout


class BaseHandler(SerfHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.setup()

    def setup(self):
        pass

    @truncated_stdout
    @with_payload
    def where(self, role=None):
        my_role = os.environ.get('ROLE', 'no_role')
        if my_role == role:
            print(self.my_info())

    def my_info(self):
        ip = (os.environ.get('ADVERTISE') or
              socket.gethostbyname(socket.gethostname()))
        return {'ip': ip}
