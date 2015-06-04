import glob
import os
import subprocess
import tarfile
import time
import tempfile

from ..stores import service_store
from ..docker import safe_docker


def rebuild_service(name):
    srv = service_store[name]['service']
    srv.make_image()


def service(name):
    srv_slot = service_store[name]
    return srv_slot['service']


def save_service(srv):
    srv_slot = service_store[srv.iden]
    srv_slot['service'] = srv
    service_store[srv.iden] = srv_slot


def stop_workers(name):
    srv = service(name)
    srv.stop_workers()
    save_service(srv)


def restart_workers(name, n=None):
    srv = service(name)
    srv.stop_workers()
    srv.start_workers(n=n)
    srv.check_health()
    save_service(srv)


def delete_iface(name):
    try:
        subprocess.check_call('ip link delete dev {}'.format(name).split())
    except subprocess.CalledProcessError:
        # ignore errors on interface removal
        pass


def veth_ifaces():
    ifaces = subprocess.check_output('ip addr'.split())
    for line in ifaces.splitlines():
        fields = line.split()
        try:
            iface = fields[1]
        except IndexError:
            continue
        if iface.startswith('A'):
            yield iface[:-1]


def firewall_flush(iface):
    """Remove all rules associated to ``iface``."""

    fw = Firewall()
    for _, target, _, dest, veth in fw._list():
        if veth == iface:
            fw.delete(dest, iface, target)


def _backup_code(srv, destination):
    """Generate a .tar.bz2 with the code used to create the adapter"""

    adapters_path = os.path.join(destination, 'adapters')
    subprocess.check_call('mkdir -p {}'.format(adapters_path).split())
    target = os.path.join(adapters_path, srv.iden+'.tar.bz2')
    try:
        worker = srv.workers[0]
        tempdir = tempfile.mkdtemp()
        safe_docker('cp', '{}:/root/user_code'.format(worker), tempdir)
    except IndexError:
        return
    with tarfile.open(target, 'w:bz2') as tar:
        tar.add(tempdir)


def backup_code(destination):
    """Backup code for all the adapters in the service store"""

    for name in service_store:
        srv = service(name)
        if srv.type != 'passthrough':
            _backup_code(srv, destination)


def backup_redis(destination):
    target = os.path.join(destination, 'redis.tar.bz2')
    with tarfile.open(target, 'w:bz2') as tar:
        tar.add('/var/lib/redis')


def backup_adapters(destination):
    """Do a full backup.

    Backup code and redis database.

    Warning: this is not synchronized. Stop registration and deletions when
    backing up.

    """
    backup_code(destination)
    backup_redis(destination)


def restore_code(directory):
    adapters_path = os.path.join(directory, 'adapters')
    for filepath in glob.glob(os.path.join(adapters_path, '*.tar.bz2')):
        filename = os.path.basename(filepath)
        name = filename[:-len('.tar.bz2')]
        slot = service_store[name]
        if slot['slot'] == 'ready':
            subprocess.check_call(
                'sudo tar jxf {0} -C /'.format(filepath).split())
            print('Rebuilding {}'.format(name))
            rebuild_service(name)
            print('  Restarting {}'.format(name))
            restart_workers(name)


def restore_redis(directory):
    tar = os.path.join(directory, 'redis.tar.bz2')
    subprocess.check_call('sudo service redis-server stop'.split())
    subprocess.check_call('sudo tar jxf {} -C /'.format(tar).split())
    subprocess.check_call('sudo service redis-server start'.split())


def restore_adapters(directory):
    """Restore adapters code and redis database."""

    restore_redis(directory)
    # give some time to redis to spin up
    time.sleep(1)
    restore_code(directory)
