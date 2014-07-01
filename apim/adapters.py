import cPickle

import redis

from .config import Config


class Adapters(dict):

    def __init__(self):
        super(Adapters, self).__init__()
        self._db = redis.StrictRedis(host=Config.get('store', 'host'),
                                     port=Config.getint('store', 'port'),
                                     db=0)

    def add(self, adapter):
        obj = cPickle.dumps(adapter)
        self._db.set(adapter.iden, obj)

    def list_all(self):
        return self._db.keys()


adapters = Adapters()