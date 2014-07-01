import cPickle

import redis

from .config import Config
from .adapter import Adapter


class Adapters(object):

    def __init__(self):
        self._db = redis.StrictRedis(host=Config.get('store', 'host'),
                                     port=Config.getint('store', 'port'),
                                     db=0)

    def add(self, adapter):
        obj = cPickle.dumps(adapter)
        self._db.set(adapter.iden, obj)

    def list_all(self):
        return list(self._list_all())

    def _list_all(self):
        for key in self._db.keys():
            obj = self._db.get(key)
            yield cPickle.loads(obj).to_json()


adapters = Adapters()
