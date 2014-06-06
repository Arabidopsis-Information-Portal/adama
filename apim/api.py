from flask import request
from flask.ext import restful

from .adapter.register import register

class Query(restful.Resource):

    def get(self):
        return {'hello': 'world'}



class Register(restful.Resource):

    def post(self):
        metadata = request.form
        try:
            code = request.files['code']
        except KeyError:
            return {'status': 'error',
                    'message': 'no file provided'}
        try:
            iden = register(metadata, code)
            return {'status': 'success',
                    'result': {
                        'identifier': iden
                    }}
        except Exception as exc:
            return {'status': 'error',
                    'message': exc.message}
