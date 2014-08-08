"""A simple example of posting to register a module."""

import json
import os
import pprint
import sys
from urlparse import urljoin

from adama.tools import location_of
import requests

# Change this url to match where ADAMA is running
URL = 'http://localhost:8000'

HERE = location_of(__file__)


def example(full=False):
    code = open(os.path.join(
        HERE, '../adama/containers/adapters/thalemine/main.py')).read()
    resp = requests.post(urljoin(URL, 'register'),
                         data={'name': 'foo',
                               'url': 'http://bar.spam',
                               'requirements': 'requests'},
                         files={'code': ('main.py', code)})
    registration = resp.json()
    if registration['status'] == 'success':
        print('Registration successful.')
        print('Service name is: {0}'
              .format(registration['result']['identifier']))
        if full:
            pprint.pprint(registration)
    else:
        print('Error in registration: code {0}'.format(resp.status_code))
        print('Full JSON response:')
        print('')
        print(json.dumps(resp.json(), indent=4))


if __name__ == '__main__':
    full = len(sys.argv) > 1
    example(full)
