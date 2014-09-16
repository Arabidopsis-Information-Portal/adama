from .store import Store


class NamespaceStore(Store):

    def __init__(self):
        # Use Redis db=1 for namespaces
        super(NamespaceStore, self).__init__(db=1)


namespace_store = NamespaceStore()
