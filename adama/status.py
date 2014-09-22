from flask.ext import restful

from . import __version__


class StatusResource(restful.Resource):

    def get(self):
        return {
            'api': 'Adama v{}'.format(__version__),
            'status': 'success'
        }
