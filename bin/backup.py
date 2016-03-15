#!/usr/bin/env python
import os
import datetime
import tarfile
import ConfigParser

import adama.command.tools as t


def config():
    parser = ConfigParser.ConfigParser()
    here = os.path.dirname(os.path.abspath(__file__))
    parser.read(os.path.join(here, 'backup.conf'))
    return parser


CONFIG = config()


def directory():
    """Create directory for backup.

    :rtype: str
    """
    dirname = 'backup-{}'.format(datetime.datetime.now().isoformat())
    d = os.path.join(os.path.expanduser('~'), dirname)
    try:
        os.makedirs(d)
    except OSError:
        pass
    return d


def pack(path):
    """Create a tarball from a directory.

    :type path: str
    :rtype: str
    """
    d = os.path.basename(path)
    target = os.path.join(os.path.expanduser('~'), '{}.tar.bz2'.format(d))
    with tarfile.open(target, 'w:bz2') as tar:
        tar.add(path)
    return target


def archive(path):
    """Send a file to some persistent storage.

    :type path: str
    :rtype: None
    """
    host_login = CONFIG.get('scp', 'login')
    host_path = CONFIG.get('scp', 'path')
    backup_cmd = 'scp {} ' + host_login + ':' + host_path
    
    subprocess.check_call(backup_cmd.format(path).split(), stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT) 
    os.unlink(path)
    shutil.rmtree(directory)

def main():
    d = directory()
    t.backup_adapters(d)
    tarball = pack(d)
    archive(tarball)


if __name__ == '__main__':
    main()
