import subprocess
import textwrap
import traceback

from flask.ext import restful


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

    def handle_error(self, e):
        try:
            raise e
        except APIException as exc:
            return self.make_response(
                {'status': 'error',
                 'message': 'API error: {0}'.format(exc.message)}, exc.code)
        except subprocess.CalledProcessError as exc:
            return self.make_response(
                {'status': 'error',
                 'command': ' '.join(exc.cmd),
                 'message': exc.output}, 500)
        except RegisterException as exc:
            all_logs = '\n---\n'.join(exc.logs)
            return self.make_response(
                {'status': 'error',
                 'message': textwrap.dedent(
                     """
                     Workers failed to start: {0} out of {1}.
                     Logs follow:

                     {2}""").format(exc.failed_count,
                                    exc.total_workers,
                                    all_logs)}, 500)
        except Exception as exc:
            child_tb = getattr(exc, 'child_traceback', None)
            trace = traceback.format_exc()
            return self.make_response({'status': 'error',
                                       'trace': trace,
                                       'worker_trace': child_tb,
                                       'message': exc.message}, 500)
