import collections
import json

import redis


def _do_get(getter, key):
    obj = getter(key)
    if obj is None:
        raise KeyError('"{}" not found'.format(key))
    return json.loads(obj.decode('utf-8'))


def _do_set(setter, key, value):
    obj = json.dumps(value)
    setter(key, obj.encode('utf-8'))


class StoreMutexException(Exception):
    pass


class AbstractStore(collections.MutableMapping):
    """A persitent dictionary."""

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __iter__(self):
        """Iterator for the keys."""
        pass

    def __len__(self):
        """Size of db."""
        pass

    def update(self, key, field, value):
        "Atomic ``self[key][field] = value``."""
        pass

    def getset(self, key, value):
        "Atomically: ``self[key] = value`` and return previous ``self[key]``."
        pass
    
    def mutex_acquire(self, key):
        """Try to use key as a mutex.

        Raise StoreMutexException if not available.
        """

        busy = self.getset(key, True)
        if busy:
            raise StoreMutexException('{} is busy'.format(key))

    def mutex_release(self, key):
        self[key] = False

        
class Store(AbstractStore):

    def __init__(self, host, port, db=0):
        self._db = redis.StrictRedis(host=host, port=port, db=db)

    def __getitem__(self, key):
        return _do_get(self._db.get, key)

    def __setitem__(self, key, value):
        _do_set(self._db.set, key, value)

    def __delitem__(self, key):
        self._db.delete(key)

    def __iter__(self):
        return self._db.scan_iter()

    def __len__(self):
        return self._db.dbsize()

    def update(self, key, field, value):
        "Atomic ``self[key][field] = value``."""

        def _update(pipe):
            cur = _do_get(pipe.get, key)
            cur[field] = value
            pipe.multi()
            _do_set(pipe.set, key, cur)

        self._db.transaction(_update, key)

    def getset(self, key, value):
        "Atomically: ``self[key] = value`` and return previous ``self[key]``."

        value = self._db.getset(key, json.dumps(value).encode('utf-8'))
        if value is not None:
            return json.loads(value.decode('utf-8'))
    
