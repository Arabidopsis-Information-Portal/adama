import json
import multiprocessing

from flask.ext import restful
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger
import requests
from werkzeug.exceptions import ClientDisconnected
from werkzeug.datastructures import FileStorage

from .adapter import Adapter
from .adapters import adapters
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
        name = self.async_register(args)
        return {
            'status': 'success',
            'message': (
                "registration started; will POST to '{}' when ready.\n"
                "GET to 'https://api.araport.org/v0.1/register/{}/state' "
                "to query for adapter state"
                .format(args.notify, name)),
            'name': name
        }

    def async_register(self, args):
        try:
            print("to spawn")
            metadata = {'name': args.name,
                        'version': args.version or '0.1',
                        'requirements': args.requirements or '',
                        'url': args.url,
                        'notify': args.notify}
            adapter = Adapter(args.code.filename, args.code.read(), metadata)
            proc = multiprocessing.Process(
                name='Async Register {}'.format(args.name),
                target=self._register_adapter, args=(adapter,))
            proc.start()
            print("after spawn")
            return adapter.iden
        except Exception as exc:
            raise APIException(
                "Failed to start registration process.\n"
                "Original exception follows:\n"
                "{}".format(exc),
                500)

    def _register_adapter(self, adapter):
        try:
            adapters.add(adapter)
            adapters.set_attr(adapter, 'state', '[1/4] Empty adapter created')
            app.logger.debug('Starting adapter registration')
            app.logger.debug(' created object')
            adapter.register()
            adapters.set_attr(adapter, 'state', '[2/4] Container for adapter created')
            app.logger.debug(' registered')
            adapter.start_workers()
            # save name of workers in the store
            adapters.set_attr(adapter, 'workers', adapter.workers)
            adapters.set_attr(adapter, 'state', '[3/4] Workers for adapter created')
            app.logger.debug(' workers started')
            adapter.check_health()
            adapters.set_attr(adapter, 'state', '[4/4] Health of all workers checked')
            app.logger.debug(' all healthy')
            app.logger.debug(' recorded')
            data = {
                'status': 'success',
                'result': adapter.to_json()
            }
            adapters.set_attr(adapter, 'state', 'Ready')
            print("success")
        except Exception as exc:
            adapters.delete(adapter.iden)
            data = {
                'status': 'error',
                'result': str(exc)
            }
            print ("exception")
            print("-->", exc)
        requests.post(adapter.notify,
                      headers={"Content-Type": "application/json"},
                      data=json.dumps(data))

    @swagger.operation(
        notes='List all registered adapters',
        nickname='list',
        responseClass=AdaptersResponse.__name__,
        parameters=[]
    )
    def get(self):
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


class Manage(restful.Resource):

    def get(self, adapter, command):
        app.logger.debug('Manage: {} {}'.format(adapter, command))
        if command == 'state':
            try:
                a = adapters[adapter]
                return {
                    'status': 'success',
                    'state': a.state
                }
            except KeyError:
                raise APIException("adapter {} not found".format(adapter), 400)
            except Exception as exc:
                raise APIException(
                    "Error retrieving state.\n"
                    "Original exception follows:\n"
                    "{}".format(exc),
                    500)
        return {}, 400