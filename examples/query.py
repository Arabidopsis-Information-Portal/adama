"""A simple example of query."""

import json
from urlparse import urljoin
import sys

import requests

# Change this url to match where APIM is running
URL = 'http://localhost:8000'


def example(service):
    query = {'locus': 'At2g26230'}
    resp = requests.post(urljoin(URL, 'query'),
                         data=json.dumps({
                             'serviceName': service,
                             'query': query}))
    print json.dumps(resp.json(), indent=4)


if __name__ == '__main__':
    try:
        example(sys.argv[1])
    except IndexError:
        print('Usage: query.py <service-name>')