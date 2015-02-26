import subprocess

from flask.ext import restful

from . import __version__
from .swagger import swagger
from .api import ok
from .tools import location_of


@swagger.model
class StatusModel(object):
    """Status response."""

    resource_fields = {
        'status': restful.fields.String(attribute='success or error'),
        'api': restful.fields.String(attribute='version of the API'),
        'hash': restful.fields.String(
            attribute='commit hash of Adama server currently running')
    }


class StatusResource(restful.Resource):

    @swagger.operation(
        notes="Return the status of the Adama server.",
        responseClass=StatusModel.__name__,
        nickname='getStatus',
        parameters=[],
        responseMessages=[
            {
                'code': 200,
                'message': 'server is running'
            },
            {
                'code': 504,
                'message': 'server is down'
            }
        ]
    )
    def get(self):
        """Return status of the server"""

        return ok({
            'api': 'Adama v{}'.format(__version__),
            'hash': head_hash()
        })


def head_hash():
    try:
        return subprocess.check_output(
            'cd {} && git rev-parse HEAD'.format(location_of(__file__)),
            shell=True).strip()
    except OSError:
        return '<could not retrieve hash of HEAD commit>'
