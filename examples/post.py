"""A simple example of posting to register a module."""

import json
import os
from urlparse import urljoin

from apim.tools import location_of
import requests

# Change this url to match where APIM is running
URL = 'http://localhost:8000'

HERE = location_of(__file__)


def example():
    code = open(os.path.join(
        HERE, '../apim/containers/adapters/thalemine/main.py')).read()
    resp = requests.post(urljoin(URL, 'register'),
                         data={'name': 'foo',
                               'url': 'http://bar.spam',
                               'requirements': 'requests'},
                         files={'code': code})
    registration = resp.json()
    if registration['status'] == 'success':
        print('Registration successful.')
        print('Service name is: {0}'
              .format(registration['result']['identifier']))
    else:
        print('Error in registration: code {0}'.format(resp.status_code))
        print('Full JSON response:')
        print('')
        print(json.dumps(resp.json(), indent=4))


if __name__ == '__main__':
    example()
