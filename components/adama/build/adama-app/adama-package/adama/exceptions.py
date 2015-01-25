import typing


class AdamaError(Exception):

    def __init__(self, message: str, exc: Exception = None) -> None:
        msg = message + ('\n{}'.format(exc) if exc is not None else '')
        super(AdamaError, self).__init__(msg)


class APIException(AdamaError):

    def __init__(self, message, code=400):
        Exception.__init__(self, message)
        self.message = message
        self.code = code


class RegisterException(AdamaError):

    def __init__(self, total_workers, logs):
        super(Exception, self).__init__(
            'register failed (see "logs" attribute)')
        self.total_workers = total_workers
        self.failed_count = len(logs)
        self.logs = logs

    def __str__(self):
        s = super(RegisterException, self).__str__()
        return s + '\n\nLogs:\n' + '\n'.join(self.logs)


