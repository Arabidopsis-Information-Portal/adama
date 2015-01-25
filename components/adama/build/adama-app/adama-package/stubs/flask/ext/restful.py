from typing import Undefined, Any, overload

class Api(object):
    def __init__(self, *args: Any, **kwargs: Any) -> None: pass
    def handler_error(self, exc: Exception) -> Any: pass
    def with_traceback(self, data: dict, exc: Exception, code: int = 500): pass
    def make_response(self, data: dict, code: int) -> Any: pass

class Resource(object):

    def get(self, *args: Any, **kwargs: Any) -> Any: pass


fields = Undefined(Any)
