from typing import Any, Dict, cast

import subprocess
import textwrap
import traceback

from flask import url_for
from flask.ext.restful import Api
from flask_restful_swagger import swagger

from . import __version__, app
from .config import Config
from .exceptions import APIException, RegisterException


class MyApi(Api):

    def handle_error(self, exc: Exception) -> Any:
        if isinstance(exc, APIException):
            return self.with_traceback(
                {'message': 'API error: {0}'.format(exc.message)},
                exc, code=exc.code)

        if isinstance(exc, subprocess.CalledProcessError):
            return self.with_traceback(
                {'message': exc.output}, exc)

        if isinstance(exc, RegisterException):
            all_logs = '\n---\n'.join(exc.logs)
            return self.with_traceback(
                {'message': textwrap.dedent(
                    """
                    Workers failed to start: {0} out of {1}.
                    Logs follow:

                    {2}""").format(exc.failed_count,
                                   exc.total_workers,
                                   all_logs)}, exc)

        if isinstance(exc, Exception):
            child_tb = getattr(exc, 'child_traceback', None)
            message = getattr(exc, 'message', None)
            return self.with_traceback(
                {'worker_trace': child_tb,
                 'message': str(message)}, exc)

    def with_traceback(self, data: dict, exc: Exception,
                       code: int = 500) -> Any:
        data['traceback'] = traceback.format_exc()
        data['exception'] = exc.__class__.__name__
        return self.make_response(error(data), code)


def ok(obj: Dict) -> Dict:
    obj['status'] = 'success'
    return obj


def error(obj: Dict) -> Dict:
    obj['status'] = 'error'
    return obj


def api_url_for(endpoint: str, **kwargs: Any) -> str:
    status_endpoint = url_for('status')
    prefix = status_endpoint[:-len('/status')]
    api_endpoint = url_for(endpoint, **kwargs)
    return (cast(str, Config['api']['url']) +
            cast(str, Config['api']['prefix']) +
            api_endpoint[len(prefix):])


api = MyApi(app) #,
           # apiVersion=__version__,
           # basePath=(cast(str, Config['api']['url']) +
           #           cast(str, Config['api']['prefix'])),
           # resourcePath='/',
           # produces=["application/json"],
           # api_spec_url='/api/adama')
