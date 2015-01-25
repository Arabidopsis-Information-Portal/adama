import collections
import pickle

import redis

from .serf import node


class Store(collections.MutableMapping):

    def __init__(self, db=0):
        host, port = node(role='redis', port=6379)
        self._db = redis.StrictRedis(host=host, port=port, db=db)

    def __getitem__(self, key):
        obj = self._db.get(key)
        if obj is None:
            raise KeyError('"{}" not found'.format(key))
        return pickle.loads(obj)

    def __setitem__(self, key, value):
        obj = pickle.dumps(value)
        self._db.set(key, obj)

    def __delitem__(self, key):
        self._db.delete(key)

    def __iter__(self):
        return self._db.scan_iter()

    def __len__(self):
        return self._db.dbsize()


store = Store()
