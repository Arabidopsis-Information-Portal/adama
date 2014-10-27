import subprocess

from ..service_store import service_store


def rebuild_service(name):
    srv = service_store[name]['service']
    srv.make_image()


def restart_workers(name, n=None):
    srv_slot = service_store[name]
    srv = srv_slot['service']
    srv.stop_workers()
    srv.start_workers(n=n)
    srv.check_health()
    srv_slot['service'] = srv
    service_store[name] = srv_slot


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

