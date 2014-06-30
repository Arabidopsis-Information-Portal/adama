import shelve


class Adapters(dict):

    def __init__(self):
        super(Adapters, self).__init__()
        self._db = {}

    def __getitem__(self, key):
        return self._db[key]

    def __setitem__(self, key, value):
        self._db[key] = value

    def list(self):
        return self._db.keys()


adapters = Adapters()