from typing import Undefined

registry = Undefined(dict)
registry = {
    'apis': [],
    'models': {}
}

registered = False
api_spec_endpoint = ''