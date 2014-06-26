import functools
import json
import os
import Queue
import tarfile
import tempfile
import threading
import time
import uuid
import zipfile

import jinja2

from .tools import location_of
from .config import Config
from .docker import docker

HERE = location_of(__file__)

# Timeout to wait for output of containers at start up, before
# declaring them dead
TIMEOUT = 1  # second

STARTED = 1
ERROR = 2
EMPTY = 3


LANGUAGES = {
    'python': ('py', 'pip install {package}'),
    'ruby': ('rb', 'gem install {package}'),
    'javascript': ('js', 'npm install {package}'),
    'lua': ('lua', None),
    'java': ('jar', None)
}


def register(metadata, contents):
    """Register a user's module.

    `metadata` has the form::

        {'fileType': 'module'|'tar.gz'|'zip',
         'language': ...,
         'requirements': ...}

    `requirements` is a comma separated list of packages which should
    be installable with the standard package manager of `language`.

    `contents` is a Python file or a compressed directory with a
    `main` module.

    On success, return an identifier for the new created container.

    """
    temp_dir = create_temp_dir()
    extract_code(metadata, contents, temp_dir)
    render_template(metadata, temp_dir)
    save_metadata(metadata, temp_dir)
    iden = build_docker(metadata, temp_dir)
    return iden


def create_temp_dir():
    return tempfile.mkdtemp()


def extract_code(metadata, contents, temp_dir):
    language = metadata['language']
    file_type = metadata['fileType']

    user_code = os.path.join(temp_dir, 'user_code')
    os.mkdir(user_code)
    ext, _ = LANGUAGES[language]
    if file_type == 'module':
        main = 'main.{}'.format(ext)
        with open(os.path.join(user_code, main), 'w') as f:
            f.write(contents)
    elif file_type == 'tar.gz':
        with open(os.path.join(temp_dir, 'contents.tgz'), 'w') as f:
            f.write(contents)
        tar = tarfile.open(os.path.join(temp_dir, 'contents.tgz'))
        tar.extractall(user_code)
    elif file_type == 'zip':
        with open(os.path.join(temp_dir, 'contents.zip'), 'w') as f:
            f.write(contents)
        zip = zipfile.ZipFile(os.path.join(temp_dir, 'contents.zip'))
        zip.extractall(user_code)
    elif file_type == 'package':
        raise Exception('package support not implemented yet')


def render_template(metadata, temp_dir):
    language = metadata['language']
    requirements = metadata['requirements']

    dockerfile_template = jinja2.Template(
        open(os.path.join(HERE, 'Dockerfile.adapter')).read())
    _, installer = LANGUAGES[language]
    requirement_cmds = 'RUN ' + installer.format(package=requirements)

    dockerfile = dockerfile_template.render(language=language,
                                            requirement_cmds=requirement_cmds)
    with open(os.path.join(temp_dir, 'Dockerfile'), 'w') as f:
        f.write(dockerfile)


def save_metadata(metadata, temp_dir):
    with open(os.path.join(temp_dir, 'metadata.json'), 'w') as f:
        f.write(json.dumps(metadata))


def build_docker(metadata, temp_dir):
    prev_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        iden = str(uuid.uuid4())
        output = docker('build', '-t', iden, '.')
        print(output)
    finally:
        os.chdir(prev_cwd)
    return iden


def run_workers(identifier, n=1):
    workers = [
        docker('run', '-d', identifier,
               '--queue-host',
               Config.get('queue', 'host'),
               '--queue-port',
               Config.get('queue', 'port'),
               '--queue-name',
               identifier)
        for _ in range(n)]
    return workers


def check_health(workers):
    """Check that all workers started ok."""

    producer = functools.partial(lambda x: docker('logs', x))
    q = Queue.Queue()

    def log(worker, q):
        q.put(log_from(worker, producer))

    # Ask for logs from workers. We do it in threads so we can poll
    # for a little while the workers in parallel.
    ts = []
    for worker in workers:
        t = threading.Thread(target=log, args=(worker, q))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    logs = []
    while not q.empty():
        x = q.get()
        if x:
            logs.append(x)
    if logs:
        raise RegisterException(len(workers), logs)


def analyze(log):
    for line in log.splitlines():
        if line.startswith('*** WORKER ERROR'):
            return ERROR
        if line.startswith('*** WORKER STARTED'):
            return STARTED
    return EMPTY


def log_from(worker, producer, retry=True):
    """Return the logs from worker if start up failed."""

    log = producer(worker)
    state = analyze(log)
    if state == ERROR:
        return producer(worker)
    if state == STARTED:
        return None
    if retry:
        time.sleep(TIMEOUT)
        return log_from(worker, producer, retry=False)
    else:
        return log


class RegisterException(Exception):

    def __init__(self, total_workers, logs):
        super(Exception, self).__init__()
        self.total_workers = total_workers
        self.failed_count = len(logs)
        self.logs = logs
