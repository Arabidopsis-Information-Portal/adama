from flask.ext import restful

from .api import ok


class JSONTestResource(restful.Resource):

    def get(self):
        return ok({
            'result': [
                {'key': 1},
                {'key': 2},
                {'key': 3}
            ]
        })
