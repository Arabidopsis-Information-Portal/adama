from functools import partial

from .store import Store
from .config import Config


config_store = partial(
    Store, Config.get('store', 'host'), Config.getint('store', 'port'))

namespace_store = config_store(db=1)
service_store = config_store(db=2)
token_store = config_store(db=3)
ip_pool = config_store(db=4)
entity_store = config_store(db=5)
prov_store = config_store(db=6)

# Reserve gateway ip: 172.17.42.1
ip_pool[(42, 1)] = True
