import itertools
import json

from flask import request, Response
from flask.ext import restful
from flask_restful_swagger import swagger

from .tasks import Producer
from .config import Config
from .tools import interleave


@swagger.model
class AIPQueryModel(object):
    resource_fields = {
        'locus': restful.fields.String
    }
    required = ['locus']


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
        client = Producer(queue_host=Config.get('queue', 'host'),
                          queue_port=Config.getint('queue', 'port'),
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
