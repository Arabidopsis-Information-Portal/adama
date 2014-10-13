import urlparse

from flask import url_for
from flask.ext import restful

from .swagger import swagger
from .api import APIException, ok
from .requestparser import RequestParser
from .namespace import Namespace, NamespaceModel, NamespaceResponseModel
from .namespace_store import namespace_store


@swagger.model
@swagger.nested(
    result=NamespaceModel.__name__
)
class NamespacesResponseModel(object):
     """List of namespaces"""

     resource_fields = {
         'status': restful.fields.String(attribute='success or error'),
         'result': restful.fields.List(
             restful.fields.Nested(NamespaceModel.resource_fields))
     }


@swagger.model
class CreatedNamespaceModel(object):

    resource_fields = {
        'status': restful.fields.String(attribute='success or error'),
        'result': restful.fields.String(
            attribute='Url of the new created namespace')
    }

class NamespacesResource(restful.Resource):

    @swagger.operation(
        notes='Create a new namespace.',
        nickname='createNamespace',
        responseClass=CreatedNamespaceModel.__name__,
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
        """Create a new namespace"""

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

    @swagger.operation(
        notes="Return a list of all registered namespaces.",
        responseClass=NamespacesResponseModel.__name__,
        nickname='getNamespaces',
        responseMessages=[
            {
                'code': 200,
                'message': 'list of namespaces'
            },
            {
                'code': 500,
                'message': 'internal error'
            },
        ]
    )
    def get(self):
        """Get list of namespaces"""

        result = [ns.to_json() for (name, ns) in namespace_store.items()]
        return ok({'result': result})
