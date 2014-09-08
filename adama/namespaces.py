from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger

from .api import APIException
from .namespace import Namespace
from .store import Store


class NamespaceStore(Store):
    pass


class Namespaces(restful.Resource):

    def post(self):
        args = self.validate_post()
        return self.register_namespace(args)

    def register_namespace(self, args):
        name = args['name']
        url=args.get('url', None)
        description=args.get('description', None)

        if name in namespace_store:
            raise APIException("namespace '{}' already exists"
                               .format(name), 400)

        ns = Namespace(name=name, url=url, description=description)
        namespace_store[name] = ns
        return {
            'status': 'success',
            'result': name
        }

    def validate_post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='name of namespace is required')
        parser.add_argument('url', type=str)
        parser.add_argument('description', type=str)
        args = parser.parse_args()
        return args


namespace_store = NamespaceStore()