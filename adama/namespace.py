from flask.ext import restful

from .api import APIException, ok
from .namespace_store import namespace_store


class Namespace(object):

    def __init__(self, name, url, description):
        self.name = name
        self.url = url
        self.description = description

    def to_json(self):
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description
        }


class NamespaceResource(restful.Resource):

    def get(self, namespace):
        try:
            ns = namespace_store[namespace]
            return ok({'result': ns.to_json()})
        except KeyError:
            raise APIException(
                "namespace '{}' not found'".format(namespace))

    def delete(self, namespace):
        try:
            del namespace_store[namespace]
        except KeyError:
            pass
        return ok({})