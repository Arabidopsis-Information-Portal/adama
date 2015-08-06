#!/usr/bin/env python

import os
import uuid
import threading
from traceback import format_exc
import zipfile
import tarfile
import tempfile

from channelpy import Channel, RabbitConnection

from store import Store
import stores
import tools


RABBIT_URI = 'amqp://{}:{}'.format(
    os.environ.get('RABBIT_PORT_5672_TCP_ADDR', '172.17.42.1'),
    os.environ.get('RABBIT_PORT_5672_TCP_PORT', 5672)
)
EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.rb': 'ruby',
    '.jar': 'java',
    '.lua': 'lua'
}
TARBALLS = ['.tar', '.gz', '.tgz']
ZIPS = ['.zip']


def error(msg, code, ch):
    """
    :type msg: Any
    :type code: int
    :type ch: Channel
    """
    ch.put({
        'status': 'error',
        'message': msg,
        'code': code
    })


def start_registration(guid, args):
    """
    :type guid: str
    :type args: Dict
    """
    stores.registration_store[guid] = {
        'status': 'starting'
    }
    try:
        service = do_register(args)
        stores.registration_store[guid] = {
            'status': 'success',
            'service': service.iden
        }
        # notify success
    except Exception as exc:
        stores.registration_store[guid] = {
            'status': 'error',
            'message': str(exc),
            'traceback': format_exc()
        }
        # notify failure
    

def do_register(args):
    """
    :type args: Dict
    :rtype: Service
    """
    if 'code' in args or args.get('type') == 'passthrough':
        service = register_code(args)
    elif 'git_repository' in args:
        service = register_git_repository(args)
    else:
        raise Exception('no code or git repository specified')
    return service


def register_code(args):
    """
    :type args: Dict
    """
    user_code = None
    if args.get('code', None):
        filename = args['code']['filename']
        code = args['code']['file']
        tempdir = tempfile.mkdtemp()
        user_code = extract(filename, code, tempdir)
    return register(args, user_code)

    
def register(args, user_code):
    """
    :type args: Dict
    :type user_code: 
    """
    iden = tools.identifier(
        args['namespace'], args['name'], args['version'])
    make_image(iden, args, user_code)
    process_icon()
    stores.service_store[iden] = args


def make_image(iden, args, user_code):
    if args['type'] == 'passthrough':
        return


def extract(filename, code, into):
    """Extract code from string ``code``.

    ``filename`` is the name of the uploaded file.  Extract the code
    in directory ``into``.

    Return the directory where the user code is extracted (may differ from
    the original ``into``).

    """

    _, ext = os.path.splitext(filename)
    user_code_dir = os.path.join(into, 'user_code')
    os.makedirs(user_code_dir, exist_ok=True)
    contents = code

    if ext in ZIPS:
        # it's a zip file
        zip_file = os.path.join(into, 'contents.zip')
        with open(zip_file, 'wb') as f:
            f.write(contents)
        zipball = zipfile.ZipFile(zip_file)
        zipball.extractall(user_code_dir)

    elif ext in TARBALLS:
        # it's a tarball
        tarball = os.path.join(into, 'contents.tgz')
        with open(tarball, 'wb') as f:
            f.write(contents)
        tar = tarfile.open(tarball)
        tar.extractall(user_code_dir)

    elif ext in EXTENSIONS.keys():
        # it's a module
        module = os.path.join(user_code_dir, filename)
        with open(module, 'w') as f:
            f.write(contents)

    else:
        raise Exception(
            'unknown extension: {0}'.format(filename), 400)

    return user_code_dir

    
def main():
    with Channel(name='image_builder', persist=False,
                 connection_type=RabbitConnection,
                 uri=RABBIT_URI) as listen:
        while True:
            job = listen.get()
            print('will process job:', flush=True)
            print(job, flush=True)
            t = threading.Thread(target=process, args=(job,))
            t.start()


def process(job):
    """
    :type job: Dict
    """
    with job['reply_to'] as reply_to:
        try:
            args = job['value']['args']
        except KeyError:
            error("missing 'args' and/or 'namespace': {}".format(job),
                  400, reply_to)
            return

        args.setdefault('version', '0.1')
        iden = tools.identifier(
            args['namespace'], args['name'], args['version'])
        if iden in stores.service_store:
            reply_to.put({
                'message': 'service {} already registered'.format(iden),
                'status': 'error'
            })
            return
        try:
            stores.registration_store.mutex_acquire(iden)
        except StoreMutexException:
            reply_to.put({
                'message': ('service "{}" is in process of registration'
                            .format(iden)),
                'status': 'error'
            })
            return

        guid = uuid.uuid4().hex
        reply_to.put({
            'message': guid,
            'status': 'success'
        })
        try:
            start_registration(guid, args)
        finally:
            stores.registration_store.mutex_release(iden)


if __name__ == '__main__':
    main()
