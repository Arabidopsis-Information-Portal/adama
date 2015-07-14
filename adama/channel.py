from .config import Config
from .chan import Channel, TimeoutException


class AChannel(Channel):

    def __init__(self, name=None):
        uri = 'amqp://{}:{}'.format(
            Config.get('queue', 'host'),
            Config.getint('queue', 'port'))
        super(AChannel, self).__init__(name=name, uri=uri)


