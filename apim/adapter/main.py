import json

def process(*args, **kwargs):
    print(json.dumps({'hey': 'there',
                      'key': args}, indent=4))
    print '---'
    print(json.dumps(kwargs))
    print '---'
    print('END')
