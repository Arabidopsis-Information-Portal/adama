import json
import multiprocessing

from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger
import requests
from werkzeug.exceptions import ClientDisconnected
from werkzeug.datastructures import FileStorage

from .adapter import Adapter
from .adapters import Adapters
from .config import Config
from .api import APIException
from . import app

@swagger.model
class AdapterIdentifierModel(object):
    resource_fields = {
        'identifier': restful.fields.String,
        'name': restful.fields.String,
        'version': restful.fields.String,
        'url': restful.fields.String,
        'language': restful.fields.String,
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

@swagger.model
@swagger.nested(
    result=AdapterIdentifierModel.__name__
)
class AdaptersResponse(object):
    resource_fields = {
        'status': restful.fields.String(attribute='success or failure'),
        'result': restful.fields.List(
            restful.fields.Nested(AdapterIdentifierModel.resource_fields))
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
                'name': 'notify',
                'description': 'URL to notify when adapter is ready',
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
        app.logger.debug('/register received POST')
        args = self.validate()
        self.async_register(args)
        return {
            'status': 'success',
            'message': ("registration started; will POST to '{}' when ready"
                        .format(args.notify))
        }

    def async_register(self, args):
        try:
            print("to spawn")
            code = args.code.read()
            proc = multiprocessing.Process(
                target=self._register_adapter, args=(args, code))
            proc.start()
            print("after spawn")
        except Exception as exc:
            raise APIException(
                "Failed to start registration process.\n"
                "Original exception follows:\n"
                "{}".format(exc),
                500)

    def _register_adapter(self, args, code):
        try:
            adapters = Adapters()
            metadata = {'name': args.name,
                        'version': args.version or '0.1',
                        'requirements': args.requirements or '',
                        'url': args.url,
                        'notify': args.notify}
            app.logger.debug('Starting adapter registration')
            adapter = Adapter(args.code.filename, code, metadata)
            app.logger.debug(' created object')
            adapter.register()
            app.logger.debug(' registered')
            adapter.start_workers()
            app.logger.debug(' workers started')
            adapter.check_health()
            app.logger.debug(' all healthy')
            adapters.add(adapter)
            app.logger.debug(' recorded')
            data = {
                'status': 'success',
                'result': adapter.to_json()
            }
            print("success")
        except Exception as exc:
            data = {
                'status': 'error',
                'result': str(exc)
            }
            print ("exception")
            print("-->", exc)
        requests.post(args.notify,
                      headers={"Content-Type": "application/json"},
                      data=json.dumps(data))

    @swagger.operation(
        notes='List all registered adapters',
        nickname='list',
        responseClass=AdaptersResponse.__name__,
        parameters=[]
    )
    def get(self):
        adapters = Adapters()
        app.logger.debug('/register received GET')
        return {'status': 'success',
                'adapters': adapters.list_all()}

    def validate(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='name of the adapter is required')
        parser.add_argument('version', type=str)
        parser.add_argument('description', type=str)
        parser.add_argument('url', type=str, required=True,
                            help='url of the data service is required')
        parser.add_argument('requirements', type=str)
        parser.add_argument('notify', type=str)
        parser.add_argument('code', type=FileStorage, required=True,
                            location='files',
                            help='a file, tarball, or zip, must be uploaded')
        try:
            args = parser.parse_args()
        except ClientDisconnected as exc:
            raise APIException(exc.data['message'], 400)

        return args
