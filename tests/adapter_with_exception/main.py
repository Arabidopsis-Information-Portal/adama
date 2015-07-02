import json


def search(args, adama=None):
    if args.get('empty', None):
        return
    if args.get('first', None):
        raise Exception('foo')
    print(json.dumps({'x': 5}))
    print('---')
    raise Exception('bar')

