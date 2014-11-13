from .store import Store


class EntityStore(Store):

    def __init__(self):
        # Use Redis db=5 for ACL's
        super(EntityStore, self).__init__(db=5)


entity_store = EntityStore()
