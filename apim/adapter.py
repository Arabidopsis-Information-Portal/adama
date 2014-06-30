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
from .api import APIException, RegisterException

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

EXTENSIONS = {
    '.py': 'python',
    '.rb': 'ruby',
    '.jar': 'java',
    '.lua': 'lua'
}


class Adapter(object):

    def __init__(self, filename, contents, metadata):
        self.filename = filename
        self.contents = contents
        self.metadata = metadata
        self.detect_language()
        self.temp_dir = self.create_temp_dir()

    def register(self):
        """[FIX DOCS] Register a user's module.

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
        self.get_code()
        self.render_template()
        self.save_metadata()
        self.build_docker()
        return self.iden, self.language

    def create_temp_dir(self):
        return tempfile.mkdtemp()

    def extension(self):
        _, ext = os.path.splitext(self.filename)
        return ext

    def detect_language(self):
        ext = self.extension()
        try:
            self.language = EXTENSIONS[ext]
        except KeyError:
            raise APIException('unknown extension {0}'.format(ext), 400)

    def get_code(self):
        """Extract code from args.code into ``temp_dir``."""

        ext = self.extension()
        user_code_dir = os.path.join(self.temp_dir, 'user_code')
        os.mkdir(user_code_dir)
        if ext == '.zip':
            # it's a zip file
            zip_file = os.path.join(self.temp_dir, 'contents.zip')
            with open(zipfile, 'w') as f:
                f.write(self.contents)
            zip = zipfile.ZipFile(zip_file)
            zip.extractall(user_code_dir)
        elif ext in ('.tar', '.gz', '.tgz'):
            # it's a tarball
            tarball = os.path.join(self.temp_dir, 'contents.tgz')
            with open(tarball, 'w') as f:
                f.write(self.contents)
            tar = tarfile.open(tarball)
            tar.extractall(user_code_dir)
        elif ext in EXTENSIONS.keys():
            # it's a module
            module = os.path.join(user_code_dir, self.filename)
            with open(module, 'w') as f:
                f.write(self.contents)
        else:
            raise APIException(
                'unknown extension: {0}'.format(self.filename), 400)

    def render_template(self):
        """Create Dockerfile for this adapter."""

        requirements = self.metadata['requirements']

        dockerfile_template = jinja2.Template(
            open(os.path.join(HERE, 'containers/Dockerfile.adapter')).read())
        _, installer = LANGUAGES[self.language]
        requirement_cmds = 'RUN ' + installer.format(package=requirements)

        dockerfile = dockerfile_template.render(
            language=self.language, requirement_cmds=requirement_cmds)
        with open(os.path.join(self.temp_dir, 'Dockerfile'), 'w') as f:
            f.write(dockerfile)

    def save_metadata(self):
        with open(os.path.join(self.temp_dir, 'metadata.json'), 'w') as f:
            f.write(json.dumps(self.metadata))

    def build_docker(self):
        prev_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        try:
            self.iden = str(uuid.uuid4())
            output = docker('build', '-t', self.iden, '.')
            print(output)
        finally:
            os.chdir(prev_cwd)


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