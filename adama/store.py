import collections
import cPickle

import redis

from .config import Config


class Store(collections.MutableMapping):

    def __init__(self):
        self._db = redis.StrictRedis(host=Config.get('store', 'host'),
                                     port=Config.getint('store', 'port'),
                                     db=0)

    def __getitem__(self, key):
        obj = self._db.get(key)
        if obj is None:
            raise KeyError('"{}" not found'.format(key))
        return cPickle.loads(obj)

    def __setitem__(self, key, value):
        obj = cPickle.dumps(value)
        self._db.set(key, obj)

    def __delitem__(self, key):
        self._db.delete(key)

    def __iter__(self):
        return self._db.scan_iter()

    def __len__(self):
        return self._db.dbsize()


store = Store()
