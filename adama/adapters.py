import cPickle

import redis

from .config import Config


class Adapters(object):

    def __init__(self):
        self._db = redis.StrictRedis(host=Config.get('store', 'host'),
                                     port=Config.getint('store', 'port'),
                                     db=0)

    def add(self, adapter):
        self._set(adapter.iden, adapter)

    def stop(self, iden):
        adapter = self._get(iden)
        adapter.stop_workers()

    def delete(self, iden):
        try:
            self.stop(iden)
            self._del(iden)
        except KeyError:
            # ignore if adapter does not exist
            pass

    def set_attr(self, adapter, attr, value):
        iden = adapter.iden
        adapter = self._get(iden)
        setattr(adapter, attr, value)
        self._set(iden, adapter)

    def list_all(self):
        return list(self._list_all())

    def _list_all(self):
        for key in self._db.keys():
            obj = self._db.get(key)
            yield cPickle.loads(obj).to_json()

    def _get(self, key):
        obj = self._db.get(key)
        if obj is None:
            raise KeyError('"{}" not found'.format(key))
        return cPickle.loads(obj)

    def _set(self, key, value):
        obj = cPickle.dumps(value)
        self._db.set(key, obj)

    def _del(self, key):
        self._db.delete(key)

    def __getitem__(self, key):
        return self._get(key)


adapters = Adapters()
