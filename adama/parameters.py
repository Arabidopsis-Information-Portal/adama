import copy
import urlparse
import os

from .api import APIException
from .config import Config
from .tools import adapter_iden


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


DEFS = {
    'Generic': {
        'properties': {
            'status': {
                'type': 'string',
                'enum': ['success', 'error'],
                'description': 'Status of response'
            },
            'message': {
                'type': 'string',
                'description': 'Human readable message'
            },
            'result': {
                'type': 'object',
                'description': 'Result'
            }
        }
    }
}


def fix_metadata(metadata):
    """

    :type metadata: dict[str, object|dict]
    :rtype: dict[str, object|dict]
    """

    md = copy.deepcopy(metadata)
    endpoints = md['endpoints']
    for endpoint in endpoints:
        descr = endpoints[endpoint]
        keys = set(descr.keys())
        if keys.issubset(['parameters', 'responses', 'response',
                          'summary', 'description']):
            # simple declaration of a GET
            endpoints[endpoint] = {'get': descr}
        elif keys.issubset(['post', 'get', 'put']):
            # full declaration of verbs
            endpoints[endpoint] = descr
        else:
            raise APIException(
                'unrecognized keys: {}'.format(list(keys)))
    return md


def metadata_to_swagger(metadata):
    """

    :type metadata: dict[str, object|dict]
    :rtype: dict[str, object]
    """
    adapter_name = adapter_iden(metadata['name'], metadata['version'])
    swagger = {
        'swagger': '2.0',
        'info': {
            'title': 'Adapter: {} v{}'.format(metadata['name'],
                                              metadata['version']),
            'description': metadata.get('description', ''),
            'version': metadata.get('version', '0.1')
        },
        'host': urlparse.urlsplit(Config.get('server', 'api_url')).netloc,
        'schemes': ['https'],
        'basePath': os.path.join(
            Config.get('server', 'api_prefix'),
            metadata['namespace'],
            adapter_name),
        'paths': dict(endpoints_to_paths(metadata)),
        'definitions': dict(get_definitions(metadata))
    }
    return swagger


def endpoints_to_paths(metadata):
    """

    :type metadata: dict[str, dict]
    :rtype: collections.Iterable[(str, dict)]
    """
    md = copy.deepcopy(metadata)
    for endpoint, descr in md['endpoints'].items():
        out = dict(
            fix_id(
                fix_summary(
                    fix_parameters(
                        fix_responses(item, endpoint)),
                    endpoint),
                endpoint)
            for item in descr.items())
        yield endpoint, out


def fix_id(item, endpoint):
    """

    :type item: (str, dict)
    :type endpoint: str
    :rtype: (str, dict)
    """
    verb, descr = item
    new_descr = copy.deepcopy(descr)
    op_id = '{}_{}'.format(
        endpoint[1:],
        verb)
    new_descr.setdefault('operationId', op_id)
    return verb, new_descr


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


def fix_responses(item, endpoint):
    """

    :type item: (str, dict)
    :type endpoint: str
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
            'schema': {
                '$ref': '#/definitions{}'.format(
                    endpoint.title()
                    if 'response' in new_descr
                    else '/Generic')
            }
        }
        new_descr['responses'] = responses
        try:
            del new_descr['response']
        except KeyError:
            pass
    return verb, new_descr


def get_definitions(metadata):
    """

    :type metadata: dict[str, dict]
    :rtype: collections.Iterable[(str, object)]
    """
    yield 'Generic', copy.deepcopy(DEFS['Generic'])
    endpoints = metadata.get('endpoints', {})
    for endpoint_name, endpoint in endpoints.items():
        for descr in endpoint.values():
            if 'response' in descr:
                defs = copy.deepcopy(DEFS['Generic'])
                defs['properties']['result'] = descr['response']
                yield endpoint_name[1:].title(), defs
