import json
import subprocess

from flask import request, Response
from flask.ext import restful

from .adapter.register import register, run_workers
from .tasks import Client

class Query(restful.Resource):

    def get(self):
        return {'hello': 'world'}

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
            for line in client.receive():
                yield json.dumps(line) + ',\n'
            yield '],\n'
            yield '"status": "success"}\n'
        return Response(result_generator(), mimetype='application/json')


class Register(restful.Resource):

    def post(self):
        metadata = request.form
        try:
            code = request.files['code']
        except KeyError:
            return {'status': 'error',
                    'message': 'no file provided'}, 400
        try:
            iden = register(metadata, code.read())
            workers = run_workers(iden, n=3)
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
