import subprocess
import textwrap

from flask.ext import restful

from .adapter.register import RegisterException


class APIException(Exception):

    def __init__(self, message, code):
        self.message = message
        self.code = code


class MyApi(restful.Api):

    def handle_error(self, e):
        try:
            raise e
        except APIException as exc:
            return self.make_response(
                {'status': 'error',
                 'message': 'API error: {0}'.format(exc.message)}, exc.code)
        except subprocess.CalledProcessError as exc:
            return self.make_respons(
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
        # except Exception as exc:
        #     child_tb = getattr(exc, 'child_traceback', None)
        #     trace = traceback.format_exc()
        #     return {'status': 'error',
        #             'trace': trace,
        #             'worker_trace': child_tb,
        #             'message': exc.message}, 500
