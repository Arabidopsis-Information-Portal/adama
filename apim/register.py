from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger

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
        parser.add_argument('name', type=str, required=True, dest='name',
                            help='name of the adapter is required')
        args = parser.parse_args()
        raise APIException('aborted', 400)

        metadata = request.form
        try:
            code = request.files['code']
        except KeyError:
            raise APIException('no file provided', 400)
