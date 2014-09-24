import subprocess

from flask.ext import restful

from . import __version__
from .api import ok
from .tools import location_of


class StatusResource(restful.Resource):

    def get(self):
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
