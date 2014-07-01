import cPickle

import redis

from .config import Config
from .adapter import Adapter


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
        return list(self.get_adapters())

    def get_adapters(self):
        for key in self._db.keys():
            obj = cPickle.loads(self._db.get(key))
            yield {
                'identifier': obj.iden,
                'version': obj.version,
                'metadata': obj.metadata,
                'language': obj.language,
                'workers': obj.workers
            }

adapters = Adapters()