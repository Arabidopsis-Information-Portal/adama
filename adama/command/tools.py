import os
import subprocess
import tarfile

from ..service_store import service_store
from ..firewall import Firewall


def rebuild_service(name):
    srv = service_store[name]['service']
    srv.make_image()


def service(name):
    srv_slot = service_store[name]
    return srv_slot['service']


def save_service(service):
    srv_slot = service_store[service.iden]
    srv_slot['service'] = service
    service_store[service.iden] = srv_slot


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

    target = os.path.join(destination, srv.iden+'.tar.bz2')
    with tarfile.open(target, 'w:bz2') as tar:
        tar.add(srv.code_dir)


def backup_code(destination):
    """Backup code for all the adapters in the service store"""

    for name in service_store:
        srv = service(name)
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