from .store import Store


class StatsStore(Store):

    def __init__(self):
        # Use Redis db=7 for stats
        super(StatsStore, self).__init__(db=7)


stats_store = StatsStore()
