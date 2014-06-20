import json
import itertools
import subprocess

from flask import request, Response
from flask.ext import restful
from flask_restful_swagger import swagger

from .config import Config
from .adapter.register import register, run_workers
from .tasks import Client


def interleave(a, b):
    """ '+', [1,2,3] -> [1, '+', 2, '+', 3] """
    yield next(b)
    for x, y in itertools.izip(itertools.cycle(a), b):
        yield x
        yield y


@swagger.model
class AIPQueryModel(object):
    resource_fields = {
        'locus': restful.fields.String
    }
    required = ['locus']


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


class Query(restful.Resource):

    @swagger.operation(
        notes='Greet people',
        nickname='hello'
    )
    def get(self):
        return {'hello': 'world'}

    @swagger.operation(
        notes='Query a data source',
        nickname='query',
        parameters=[
            {
                'name': 'serviceName',
                'description': 'Identifier of the data source',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'body'
            },
            {
                'name': 'query',
                'description': 'AIP formatted query',
                'required': True,
                'allowMultiple': False,
                'dataType': AIPQueryModel.__name__,
                'paramType': 'body'
            }
        ]
    )
    def post(self):
        query = request.get_json(force=True)
        service = query['serviceName']
        queue = service
        client = Client(queue_host='192.168.3.1',
                        queue_port=5555,
                        queue_name=queue)
        client.send({'query': query['query'],
                     'count': False,
                     'pageSize': 100,
                     'page': 1})
        def result_generator():
            yield '{"result": [\n'
            gen = itertools.imap(lambda x: json.dumps(x) + '\n',
                                 client.receive())
            for line in interleave([', '], gen):
                yield line
            yield '],\n'
            yield '"status": "success"}\n'
        return Response(result_generator(), mimetype='application/json')


class Register(restful.Resource):

    @swagger.operation(
        notes='Register an adapter for a data source',
        nickname='register',
        responseClass=AdapterModel.__name__,
        parameters=[
            {
                'name': 'language',
                'description': 'Language in which the adapter is written',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'fileType',
                'description': ('Type of package: \n'
                                ' module: a single file,\n'
                                ' tar.gz: a compressed tarball'),
                'required': True,
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
        metadata = request.form
        try:
            code = request.files['code']
        except KeyError:
            return {'status': 'error',
                    'message': 'no file provided'}, 400
        try:
            iden = register(metadata, code.read())
            num_instances = Config.get(
                'workers',
                '{}_instances'.format(metadata['language']))
            workers = run_workers(iden, n=num_instances)
            return {'status': 'success',
                    'result': {
                        'identifier': iden,
                        'workers': workers,
                    }}
        except subprocess.CalledProcessError as exc:
            return {'status': 'error',
                    'command': ' '.join(exc.cmd),
                    'message': exc.output}, 500
        except Exception as exc:
            return {'status': 'error',
                    'message': exc.message}, 500
