import subprocess

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
        if iface.startswith('veth'):
            yield iface[:-1]

def firewall_flush(iface):
    """Remove all rules associated to ``iface``."""

    fw = Firewall()
    for _, target, _, dest, veth in fw._list():
        if veth == iface:
            fw.delete(dest, iface, target)
