from .config import Config
from channelpy import Channel, RabbitConnection


class AChannel(Channel):

    def __init__(self, name=None):
        uri = 'amqp://{}:{}'.format(
            Config.get('queue', 'host'),
            Config.getint('queue', 'port'))
        super(AChannel, self).__init__(
            name=name,
            connection_type=RabbitConnection,
            uri=uri)


