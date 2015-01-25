
# Adapter: {{ cookiecutter.adapter_name }}
# Author: {{ cookiecutter.full_name }} <{{ cookiecutter.email }}>
#

import json


def map_filter(arg):
    """Transform or filter an object.

    ``arg`` is a dictionary.  Return another dictionary or ``None`` to
    discard this object.

    """
    arg['processed_by'] = 'Adama'
    return arg
