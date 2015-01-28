from flask import g
from flask.ext import restful

from typing import Dict, List, Any

from .swagger import swagger
from .api import APIException, ok, api_url_for
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

        args = validate_post()
        return ok({'result': register_namespace(args)})

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

        return ok({'result': namespaces()})


def namespaces() -> List[Dict[str, Any]]:
    return [ns.to_json() for (name, ns) in namespace_store.items()]


def validate_post() -> Dict[str, Any]:
    parser = RequestParser()
    parser.add_argument('name', type=str, required=True,
                        help='name of namespace is required')
    parser.add_argument('url', type=str)
    parser.add_argument('description', type=str)
    args = parser.parse_args()
    return args


def register_namespace(args: Dict[str, Any]) -> str:
    name = args['name']
    url = args.get('url', None)
    description = args.get('description', None)

    if name in namespace_store:
        raise APIException("namespace '{}' already exists"
                           .format(name), 400)

    ns = Namespace(name=name, url=url,
                   description=description,
                   users={g.user: ['POST', 'PUT', 'DELETE']})
    namespace_store[name] = ns
    return api_url_for('namespace', namespace=name)

