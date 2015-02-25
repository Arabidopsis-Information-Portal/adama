import copy

from .api import APIException
from .config import Config


DOCS = {
    '/search': {
        'get': {
            'summary': 'Search',
            'description': 'do a search'
        }
    },
    '/list': {
        'get': {
            'summary': 'List',
            'description': 'list all'
        }
    },
    '/access': {
        'get': {
            'summary': 'Access get',
            'description': 'do a get to a passthrough'
        },
        'post': {
            'summary': 'Access post',
            'description': 'do a post to a passthrough'
        }
    }
}


def metadata_to_swagger(metadata):
    """

    :type metadata: dict[str, object|dict]
    :rtype: dict[str, object]
    """
    swagger = {
        'swagger': '2.0',
        'info': {
            'title': 'Adapter: {}'.format(metadata['name']),
            'description': metadata.get('description', ''),
            'version': metadata.get('version', '0.1')
        },
        'host': Config.get('server', 'api_url'),
        'schemes': ['https'],
        'basePath': Config.get('server', 'api_prefix'),
        'paths': dict(endpoints_to_paths(metadata)),
        'definitions': get_definitions()
    }
    return swagger


def endpoints_to_paths(metadata):
    """

    :type metadata: dict[str, dict]
    :rtype: collections.Iterable[(str, dict)]
    """
    md = copy.deepcopy(metadata)
    for endpoint, descr in md['endpoints'].items():
        keys = set(descr.keys())
        if keys.issubset(['parameters', 'responses', 'response']):
            # simple declaration of a GET
            new_descr = {'get': descr}
        elif keys.issubset(['post', 'get', 'put']):
            # full declaration of verbs
            new_descr = descr
        else:
            raise APIException(
                'unrecognized keys: {}'.format(list(keys)))
        out = dict(fix_summary(fix_parameters(fix_responses(item)), endpoint)
                   for item in new_descr.items())
        yield endpoint, out


def fix_parameters(item):
    """

    :type item: (str, dict)
    :rtype: (str, dict)
    """
    verb, descr = item
    new_descr = copy.deepcopy(descr)
    parameters = new_descr.setdefault('parameters', [])
    for parameter in parameters:
        parameter.setdefault('in', 'query')
    return verb, new_descr


def fix_summary(item, endpoint):
    """

    :type item: (str, dict)
    :type endpoint: str
    :rtype: (str, dict)
    """
    verb, descr = item
    new_descr = copy.deepcopy(descr)
    for field, value in DOCS[endpoint][verb].items():
        new_descr.setdefault(field, value)
    return verb, new_descr


def fix_responses(item):
    """

    :type item: (str, dict)
    :rtype: (str, dict)
    """
    verb, descr = item
    new_descr = copy.deepcopy(descr)
    if 'response' in new_descr or 'responses' not in new_descr:
        # declaration of a simple 200 response.
        # add it to 'responses'
        responses = new_descr.setdefault('responses', {})
        responses['200'] = {
            'description': 'successful response',
            'schema': new_descr.get('response',
                                    {
                                        '$ref': '#/definitions/Generic'
                                    })
        }
        new_descr['responses'] = responses
        try:
            del new_descr['response']
        except KeyError:
            pass
    return verb, new_descr


def get_definitions():
    """

    :rtype: dict[str, object]
    """
    return {}