from flask import g
from flask.ext import restful

from .api import APIException, ok, api_url_for
from .namespace_store import namespace_store
from .swagger import swagger
from .entity import get_permissions


@swagger.model
class NamespaceModel(object):

    resource_fields = {
        'name': restful.fields.String(attribute='Name of the namespace'),
        'url': restful.fields.String(
            attribute='Url associated to the namespace '
                      '(for documentation purposes)'),
        'self': restful.fields.String(
            attribute='Url to access this namespace'),
        'description': restful.fields.String(
            attribute='Description of the namespace'),
    }


@swagger.model
@swagger.nested(
    result=NamespaceModel.__name__
)
class NamespaceResponseModel(object):

    resource_fields = {
        'status': restful.fields.String(attribute='success or error'),
        'result': restful.fields.Nested(NamespaceModel.resource_fields)
    }


@swagger.model
class DeleteResponseModel(object):

    resource_fields = {
        'status': restful.fields.String(attribute='success')
    }


class Namespace(object):

    def __init__(self, name, url, description, users=None):
        self.name = name
        self.url = url
        self.description = description
        # {user: [methods allowed...]}
        self.users = users or {}

        self.validate_args()

    def validate_args(self):
        if not self.name:
            raise APIException(
                'Namespace cannot be an empty string')

    def to_json(self):
        obj = {
            'name': self.name,
            'url': self.url,
            'users': self.users,
            'description': self.description
            }
        try:
            obj['self'] = api_url_for('namespace', namespace=self.name)
        except RuntimeError:
            # no app context, ignore 'self' field
            pass
        return obj


class NamespaceResource(restful.Resource):

    @swagger.operation(
        notes='Return information about a namespace.',
        nickname='getNamespace',
        responseClass=NamespaceResponseModel.__name__,
        parameters=[
            {
                'name': 'namespace',
                'description': 'name of namespace',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'path'
            }
        ]
    )
    def get(self, namespace):
        """Get information about a namespace"""

        try:
            ns = namespace_store[namespace]
            return ok({'result': ns.to_json()})
        except KeyError:
            raise APIException(
                "namespace not found: {}'".format(namespace), 404)

    @swagger.operation(
        notes='Delete a namespace. Note that this operation always succeed '
              'regardless of the existence of the namespace.',
        nickname='deleteNamespace',
        responseClass=DeleteResponseModel.__name__,
        parameters=[
            {
                'name': 'namespace',
                'description': 'name of namespace',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'path'
            }
        ]
    )
    def delete(self, namespace):
        """Delete a namespace"""

        try:
            ns = namespace_store[namespace]
            if 'DELETE' in tuple(get_permissions(ns.users, g.user)):
                del namespace_store[namespace]
            else:
                raise APIException(
                    'user {} does not have permissions for DELETE'
                    .format(g.user))
        except KeyError:
            pass
        return ok({})