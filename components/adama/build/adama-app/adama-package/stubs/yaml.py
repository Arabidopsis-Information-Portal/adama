from typing import Any, Dict, Union, typevar, Undefined

JSON = typevar('JSON', values=(Union[Dict, int, float, str],))


def load(x: Any) -> JSON: pass
error = Undefined(Any)
