from functools import partial
import os

from store import Store


configured_store = partial(
    Store,
    host=os.environ.get('REDIS_PORT_6379_TCP_ADDR', '172.17.42.1'),
    port=int(os.environ.get('REDIS_PORT_6379_TCP_PORT', 6379)))


namespace_store = configured_store(db=1)
service_store = configured_store(db=2)
token_store = configured_store(db=3)
ip_pool = configured_store(db=4)
entity_store = configured_store(db=5)
prov_store = configured_store(db=6)
stats_store = configured_store(db=7)
debug_store = configured_store(db=8)
registration_store = configured_store(db=9)




