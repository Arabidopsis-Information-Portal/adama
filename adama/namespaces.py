import urlparse

from flask import url_for
from flask.ext import restful
from adama.swagger import swagger

from .api import APIException, ok
from .requestparser import RequestParser
from .namespace import Namespace
from .namespace_store import namespace_store


@swagger.model
class NamespaceModel(object):
    pass

@swagger.model
@swagger.nested(
    result=NamespaceModel.__name__
)
class NamespacesResponse(object):
    "A response"

    resource_fields = {
        'status': restful.fields.String(attribute='success or error'),
        'result': restful.fields.List(
            restful.fields.Nested(NamespaceModel.resource_fileds))
    }


class NamespacesResource(restful.Resource):

    @swagger.operation(
        notes='Register a new namespace',
        nickname='registerNamespace',
        responseClass=NamespacesResponse.__name__,
        parameters=[
            {
                'name': 'name',
                'description': 'name of the namespace',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'url',
                'description': 'url associated to this namespace',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'description',
                'description': 'description of this namespace',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            }
        ]
    )
    def post(self):
        args = self.validate_post()
        return self.register_namespace(args)

    def register_namespace(self, args):
        name = args['name']
        url = args.get('url', None)
        description = args.get('description', None)

        if name in namespace_store:
            raise APIException("namespace '{}' already exists"
                               .format(name), 400)

        ns = Namespace(name=name, url=url, description=description)
        namespace_store[name] = ns
        return ok({
            'result': url_for(
                'namespace',
                namespace=name,
                _external=True)
        })

    def validate_post(self):
        parser = RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='name of namespace is required')
        parser.add_argument('url', type=str)
        parser.add_argument('description', type=str)
        args = parser.parse_args()
        return args

    def get(self):
        result = [ns.to_json() for (name, ns) in namespace_store.items()]
        return ok({'result': result})
