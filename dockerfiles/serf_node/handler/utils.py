from functools import wraps
import json
import subprocess
import sys
import traceback
import cStringIO


MAX_OUTPUT = 1000


def truncated_stdout(f):
    """Decorator to truncate stdout to final `MAX_OUTPUT` characters. """

    @wraps(f)
    def wrapper(*args, **kwargs):
        old_stdout = sys.stdout
        old_stdout.flush()
        sys.stdout = cStringIO.StringIO()
        out = ''
        try:
            result = f(*args, **kwargs)
            out = sys.stdout.getvalue() + '\nSUCCESS'
            return result
        except Exception:
            out = traceback.format_exc() + '\nERROR'
        finally:
            sys.stdout = old_stdout
            print out[-MAX_OUTPUT:]
    return wrapper


def with_payload(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload = json.loads(sys.stdin.read())
        kwargs.update(payload)
        return f(*args, **kwargs)
    return wrapper


def serf(*args):
    cmd = ['serf'] + list(args) + ['-format=json']
    return json.loads(subprocess.check_output(cmd))