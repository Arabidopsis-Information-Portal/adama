import json
import subprocess

from flask.ext import restful
from typing import Tuple, Dict

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

        return ok(status())


def my_info() -> Tuple[str, str]:
    me = json.load(open('/me.json'))
    return me['Image'], me['Id']


def my_parent() -> Tuple[str, str]:
    parent = json.load(open('/serfnode/parent.json'))
    return parent['Image'], parent['Id']


def status() -> Dict[str, str]:
    my_img, my_cid = my_info()
    parent_img, parent_cid = my_parent()
    return {
        'api': 'Adama v{}'.format(__version__),
        'serfnode_image': parent_img,
        'serfnode_container': parent_cid,
        'adama_image': my_img,
        'adama_container': my_cid
    }