# {% raw %}
# Adapter: {{ cookiecutter.adapter_name }}
# Author: {{ cookiecutter.full_name }} <{{ cookiecutter.email }}>
#

import json


def search(args):
    """Search a data source.

    ``args`` is a dictionary with the query and pagination
    requested.

    For example, the request::

        /my_namespace/{{ cookiecutter.adapter_name }}/search?key=5

    will result in::

        args = {'key': 5,
                'count': False,
                'page': 1,
                'page_size': None}

    """

    print json.dumps({'this_adapter': "{{ cookiecutter.adapter_name }}"})
    print '---'
    print json.dumps({'args': args})


def list(args):
    """List a data source.

    This method implements a listing, if possible, of the data
    source.

    ``args`` contains only the information for the pagination.

    """

    for i in range(5):
        print json.dumps({'item': i})
        print '---'
# {% endraw %}
