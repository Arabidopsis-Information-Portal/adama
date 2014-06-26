from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger
from werkzeug.exceptions import ClientDisconnected
from werkzeug.datastructures import FileStorage

from .adapter.register import register, run_workers, check_health
from .config import Config
from .api import APIException


@swagger.model
class AdapterIdentifierModel(object):
    resource_fields = {
        'identifier': restful.fields.String,
        'workers': restful.fields.List(restful.fields.String)
    }


@swagger.model
@swagger.nested(
    result=AdapterIdentifierModel.__name__
)
class AdapterModel(object):
    resource_fields = {
        'status': restful.fields.String(attribute='success or failure'),
        'result': restful.fields.Nested(AdapterIdentifierModel.resource_fields)
    }


class Register(restful.Resource):

    @swagger.operation(
        notes='Register an adapter for a data source',
        nickname='register',
        responseClass=AdapterModel.__name__,
        parameters=[
            {
                'name': 'name',
                'description': 'name of the service provided by this adapter',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'version',
                'description': ('version of the service provided by this '
                                'adapter'),
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'url',
                'description': 'URL of the original data source',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'description',
                'description': ('Description of the service provided by '
                                'this adapter'),
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'requirements',
                'description': 'comma separated list of third party modules',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'code',
                'description': "user's code for the adapter",
                'required': True,
                'allowMultiple': False,
                'dataType': 'File',
                'paramType': 'form'
            }
        ]
    )
    def post(self):
        metadata, code = self.validate()
        iden = register(metadata, code)
        num_instances = Config.getint(
            'workers',
            '{}_instances'.format(metadata['language']))
        workers = run_workers(iden, n=num_instances)
        check_health(workers)
        return {'status': 'success',
                'result': {
                    'identifier': iden,
                    'workers': workers,
                }}

    def validate(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='name of the adapter is required')
        parser.add_argument('version', type=str)
        parser.add_argument('description', type=str)
        parser.add_argument('url', type=str, required=True,
                            help='url of the data service is required')
        parser.add_argument('requirements', type=str, dest='requirements')
        parser.add_argument('code', type=FileStorage, required=True,
                            location='files',
                            help='a file, tarball, or zip, must be uploaded')
        try:
            args = parser.parse_args()
        except ClientDisconnected as exc:
            raise APIException(exc.data['message'], 400)
