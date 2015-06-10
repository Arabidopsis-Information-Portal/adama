import json
from collections import Sequence


def search(args):
    # grab parameters from JSON object
    x = args['x']
    y = args.get('y', None)
    z = args['z']
    w = args['w']

    # check that they have the proper types
    assert isinstance(x, basestring)
    if y is not None:
        assert isinstance(y, int)
    assert isinstance(z, Sequence)
    assert w in ('Spam', 'Eggs')

    # output the values
    print json.dumps('x = {}'.format(x))
    print '---'
    print json.dumps('y = {}'.format(y))
    print '---'
    print json.dumps('z = {}'.format(z))
    print '---'
    print json.dumps('w = {}'.format(w))

