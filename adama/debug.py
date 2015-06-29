from flask import request, Response
from flask.ext import restful

from .api import error, ok
from .stores import debug_store


class DebugResource(restful.Resource):

    def get(self, uuid):
        tb = debug_store.get(uuid)
        if tb is None:
            return error({'message': 'traceback "{}" not found'.format(uuid)})
        if request.args.get('format', None) == 'text':
            return Response(tb['traceback'], content_type='text/plain')
        else:
            return ok(tb)

