from __future__ import print_function

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
            stdout = sys.stdout.getvalue()
            out = stdout + '\nSUCCESS' if stdout else ''
            return result
        except Exception:
            out = traceback.format_exc() + '\nERROR'
        finally:
            sys.stdout = old_stdout
            print(out[-MAX_OUTPUT:], end='')
    return wrapper


def with_payload(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload = json.loads(sys.stdin.read())
        kwargs.update(payload)
        return f(*args, **kwargs)
    return wrapper


def with_member_info(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs['members'] = list(member_info(sys.stdin.readlines()))
        return f(*args, **kwargs)
    return wrapper


def member_info(lines):
    for line in lines:
        member = {}
        parts = line.split()
        member['node'] = parts[0]
        member['ip'] = parts[1]
        member['role'] = parts[2]
        member['tags'] = dict(part.split('=') for part in parts[3].split(','))
        yield member


def is_self(node):
    return serf('info')['agent']['name'] == node


def serf(*args):
    cmd = ['serf'] + list(args) + ['-format=json']
    return json.loads(subprocess.check_output(cmd))


def serf_event(name, *args):
    cmd = ['serf', 'event', name] + list(args)
    subprocess.check_call(cmd, stdout=sys.stderr)
