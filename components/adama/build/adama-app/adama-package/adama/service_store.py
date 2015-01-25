from .store import Store


class ServicesStore(Store):

    def __init__(self):
        # Use Redis db=2 for services
        super(ServicesStore, self).__init__(db=2)


service_store = ServicesStore()
