import os

from serf_master import SerfHandler
from utils import with_payload, truncated_stdout


class BaseHandler(SerfHandler):

    @truncated_stdout
    @with_payload
    def where(self, role=None):
        my_role = os.environ.get('ROLE', 'no_role')
        if my_role == role:
            print(self.my_info())

    def my_info(self):
        return {
            'ip': os.environ.get('ADVERTISE', None)
        }