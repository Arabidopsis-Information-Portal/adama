import subprocess
import textwrap
import traceback

from flask import url_for
from flask.ext import restful
from adama.swagger import swagger

from . import __version__, app
from .config import Config


class APIException(Exception):

    def __init__(self, message, code=400):
        Exception.__init__(self, message)
        self.message = message
        self.code = code


class RegisterException(Exception):

    def __init__(self, total_workers, logs):
        super(Exception, self).__init__(
            'register failed (see "logs" attribute)')
        self.total_workers = total_workers
        self.failed_count = len(logs)
        self.logs = logs

    def __str__(self):
        s = super(RegisterException, self).__str__()
        return s + '\n\nLogs:\n' + '\n'.join(self.logs)


class MyApi(restful.Api):

    def handle_error(self, exc):
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
            trace = traceback.format_exc()
            return self.with_traceback(
                {'trace': trace,
                 'worker_trace': child_tb,
                 'message': str(exc.message)}, exc)

    def with_traceback(self, data, exc, code=500):
        data['traceback'] = traceback.format_exc()
        data['exception'] = exc.__class__.__name__
        return self.make_response(error(data), code)


def ok(obj):
    obj['status'] = 'success'
    return obj


def error(obj):
    obj['status'] = 'error'
    return obj


def api_url_for(endpoint, **kwargs):
    status_endpoint = url_for('status')
    prefix = status_endpoint[:-len('/status')]
    api_endpoint = url_for(endpoint, **kwargs)
    return (Config.get('server', 'api_url') +
            Config.get('server', 'api_prefix') +
            api_endpoint[len(prefix):])


api = swagger.docs(MyApi(app),
                   apiVersion=__version__,
                   basePath=(Config.get('server', 'api_url') +
                             Config.get('server', 'api_prefix')),
                   resourcePath='/',
                   produces=["application/json"],
                   api_spec_url='/api/adama')
