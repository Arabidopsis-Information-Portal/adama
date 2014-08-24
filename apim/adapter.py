import glob
import json
import multiprocessing
import os
import tarfile
import tempfile
import threading
import uuid
import zipfile

from enum import Enum
import jinja2

from .tools import location_of
from .config import Config
from .docker import docker_output, tail_logs
from .api import APIException, RegisterException
from . import app

HERE = location_of(__file__)

# Timeout to wait for output of containers at start up, before
# declaring them dead
TIMEOUT = 3  # second

# Timout to wait while stopping workers
STOP_TIMEOUT = 5


class WorkerState(Enum):
    started = 1
    error = 2


LANGUAGES = {
    'python': ('py', 'pip install {package}'),
    'ruby': ('rb', 'gem install {package}'),
    'javascript': ('js', 'npm install -g {package}'),
    'lua': ('lua', None),
    'java': ('jar', None)
}

EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
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
        self.state = None
        self.workers = []

    def validate_metadata(self):
        self.requirements = self.metadata.get('requirements', None)
        self.name = self.metadata.get('name', uuid.uuid4().hex)
        self.version = self.metadata.get('version', '0.1')
        self.iden = '{0}_v{1}'.format(self.name, self.version)
        self.url = self.metadata.get('url', '')
        self.notify = self.metadata.get('notify', '')

    def to_json(self):
        return {
            'identifier': self.iden,
            'name': self.name,
            'version': self.version,
            'url': self.url,
            'language': self.language,
            'workers': self.workers
        }

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
        app.logger.debug('+++ Starting to build container')
        self.build_docker()
        app.logger.debug('+++ Finished building container')

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
        requirement_cmds = (
            'RUN ' + installer.format(package=self.requirements)
            if self.requirements else '')

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
            output = docker_output('build', '-t', self.iden, '.')
            print(output)
        finally:
            os.chdir(prev_cwd)

    def start_workers(self, n=None):
        if n is None:
            n = Config.getint(
                'workers', '{}_instances'.format(self.language))
        self.workers = [
            docker_output('run', '-d', self.iden,
                          '--queue-host',
                          Config.get('queue', 'host'),
                          '--queue-port',
                          Config.get('queue', 'port'),
                          '--queue-name',
                          self.iden).strip()
            for _ in range(n)]

    def stop_workers(self):
        threads = []
        for worker in self.workers:
            threads.append(self.async_stop_worker(worker))
        for thread in threads:
            thread.join(STOP_TIMEOUT)

    def async_stop_worker(self, worker):
        thread = threading.Thread(target=docker_output,
                                  args=('stop', worker))
        thread.start()
        return thread

    def check_health(self):
        """Check that all workers started ok."""

        q = multiprocessing.Queue()

        def log(worker, q):
            producer = tail_logs(worker, timeout=TIMEOUT)
            v = (check(producer), worker)
            q.put(v)

        # Ask for logs from workers. We do it in processes so we can
        # poll for a little while the workers in parallel.
        ts = []
        for worker in self.workers:
            t = multiprocessing.Process(target=log, args=(worker, q),
                                        name='Worker log {}'.format(worker))
            t.start()
            ts.append(t)
        # wait for all processes (the timeout guarantees they'll finish)
        for t in ts:
            t.join()

        logs = []
        while not q.empty():
            state, worker = q.get()
            if state == WorkerState.error:
                logs.append(docker_output('logs', worker))

        if logs:
            raise RegisterException(len(self.workers), logs)


def check(producer):
    state = WorkerState.error
    for line in producer:
        if line.startswith('*** WORKER ERROR'):
            return WorkerState.error
        if line.startswith('*** WORKER STARTED'):
            state = WorkerState.started
    return state
