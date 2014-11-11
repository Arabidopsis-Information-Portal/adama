from .entity_store import entity_store


class Entity(object):

    def __init__(self, name, parent=None):
        # type(parent) is str or None
        self.name = name
        self.parent = parent

    def __contains__(self, item):
        # type(item) is str
        if self.name == item:
            return True
        try:
            item_obj = entity_store[item]
            return item_obj.parent in self
        except KeyError:
            return False
        except AttributeError:
            return False

