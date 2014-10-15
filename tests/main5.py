import json

def search(arg):
    return ('text/csv',
            json.dumps({'hi': 'there',
                        'arg': arg}))
