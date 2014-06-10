import json

import requests


def process(args):

    print(json.dumps({'hey': 'there',
                      'key': args}, indent=4))
    print '---'
    print(json.dumps(kwargs))
    print '---'
    print('END')
