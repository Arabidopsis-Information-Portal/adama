import functools
import glob
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

TARBALLS = ['.tar', '.gz', '.tgz']
ZIPS = ['.zip']


class Adapter(object):

    def __init__(self, filename, contents, metadata):
        self.filename = filename
        self.contents = contents
        self.metadata = metadata
        self.language = None
        self.validate_metadata()
        self.temp_dir = self.create_temp_dir()

    def validate_metadata(self):
        self.requirements = self.metadata.get('requirements', {})
        self.name = self.metadata.get('name', uuid.uuid4())
        self.version = self.metadata.get('version', '0.1')
        self.iden = '{0}_v{1}'.format(self.name, self.version)

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
        self.detect_language()
        self.render_template()
        self.save_metadata()
        self.build_docker()

    def create_temp_dir(self):
        return tempfile.mkdtemp()

    def extension(self, filename):
        _, ext = os.path.splitext(filename)
        return ext

    def detect_language(self):
        ext = self.extension(self.filename)
        try:
            self.language = EXTENSIONS[ext]
        except KeyError:
            if ext in TARBALLS + ZIPS:
                main = os.path.join(self.temp_dir, 'user_code/main.*')
                try:
                    ext = self.extension(glob.glob(main)[0])
                    self.language = EXTENSIONS[ext]
                    return
                except IndexError:
                    raise APIException('compressed file does not contain '
                                       'a "main" module', 400)
            raise APIException('unknown extension {0}'.format(ext), 400)

    def get_code(self):
        """Extract code from args.code into ``temp_dir``."""

        ext = self.extension(self.filename)
        user_code_dir = os.path.join(self.temp_dir, 'user_code')
        os.mkdir(user_code_dir)
        if ext in ZIPS:
            # it's a zip file
            zip_file = os.path.join(self.temp_dir, 'contents.zip')
            with open(zip_file, 'w') as f:
                f.write(self.contents)
            zip = zipfile.ZipFile(zip_file)
            zip.extractall(user_code_dir)
        elif ext in TARBALLS:
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

        dockerfile_template = jinja2.Template(
            open(os.path.join(HERE, 'containers/Dockerfile.adapter')).read())
        _, installer = LANGUAGES[self.language]
        requirement_cmds = 'RUN ' + installer.format(package=self.requirements)

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
            output = docker('build', '-t', self.iden, '.')
            print(output)
        finally:
            os.chdir(prev_cwd)

    def start_workers(self, n=None):
        if n is None:
            n = Config.getint(
                'workers', '{}_instances'.format(self.language))
        self.workers = [
            docker('run', '-d', self.iden,
                   '--queue-host',
                   Config.get('queue', 'host'),
                   '--queue-port',
                   Config.get('queue', 'port'),
                   '--queue-name',
                   self.iden)
            for _ in range(n)]

    def check_health(self):
        """Check that all workers started ok."""

        producer = functools.partial(lambda x: docker('logs', x))
        q = Queue.Queue()

        def log(worker, q):
            q.put(log_from(worker, producer))

        # Ask for logs from workers. We do it in threads so we can poll
        # for a little while the workers in parallel.
        ts = []
        for worker in self.workers:
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
    state = EMPTY
    for line in log.splitlines():
        if line.startswith('*** WORKER ERROR'):
            return ERROR
        if line.startswith('*** WORKER STARTED'):
            state = STARTED
    return state


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
