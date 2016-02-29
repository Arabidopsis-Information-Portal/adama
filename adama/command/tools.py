import glob
import os
import subprocess
import tarfile
import time
import tempfile

from ..stores import entity_store
from ..stores import service_store
from ..stores import namespace_store
from ..docker import safe_docker
from ..entity import Entity

def rebuild_service(name):
    srv = service_store[name]['service']
    srv.make_image()


def service(name):
    srv_slot = service_store[name]
    srv = srv_slot['service']
    if srv is None:
        raise KeyError('service {} not found'.format(name))
    return srv


def workers_of(name):
    """Return the workers for service `name`.

    :type name: str
    :rtype: List[str]
    """
    srv = service(name)
    return srv.workers


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
        try:
            srv = service(name)
        except KeyError:
            continue
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


def _adjust_code_dir(name, filepath):
    """Fix `code_dir` attribute of `name` to match contents of tarfile.

    :type name: str
    :type filepath: str
    :rtype: None
    """
    tar = tarfile.open(filepath)
    srv = service(name)
    srv.code_dir = os.path.join('/', tar.members[0].name, 'user_code')
    save_service(srv)


def restore_code(directory):
    adapters_path = os.path.join(directory, 'adapters')
    for filepath in glob.glob(os.path.join(adapters_path, '*.tar.bz2')):
        filename = os.path.basename(filepath)
        name = filename[:-len('.tar.bz2')]
        slot = service_store[name]
        if slot['slot'] == 'ready':
            subprocess.check_call(
                'sudo tar jxf {0} -C /'.format(filepath).split())
            _adjust_code_dir(name, filepath)
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
    time.sleep(180)
    restore_code(directory)


def add_admin_to_all_namespaces():
    """Iterate over all namespaces, add admin role user."""

    for ns in namespace_store.items():
        print 'Adding admin to ' + ns[1].name + '...'
        add_admin_to_namespace( ns )
        print 'Done.'

def add_admin_to_namespace( ns ):
    """Add admin group user with GET/POST/PUT/DELETE to a namespace."""

    # It's not obvious till you've coded around a bit but ns is a tuple
    ns_obj=namespace_store[ ns[1].name ]
    for u in ['admin']:
        uname = u
        ns_obj.users[uname] = ['POST', 'PUT', 'DELETE']
        namespace_store[ ns[1].name ] = ns_obj

def add_admin_to_all_services():
    """Utility. Iterate over ALL services, regardless of namespace. Add admins."""

    for name in service_store:
        try:
            srv = service(name)
        except KeyError:
            continue
        add_admin_to_service( srv )

def add_admin_to_service( srv ):
    """Add a user with GET/POST/PUT/DELETE to a service"""

    srv.users['admin'] = ['POST', 'PUT', 'DELETE']
    save_service(srv)

def manage_admin_group():
    """Edit the array of Araport usernames and run this subroutine to add users to the administrator group who have edit rights to ADAMA namespaces and services"""

    for u in ['vivek', 'eriksf', 'vaughn', 'ibelyaev', 'jmiller', 'jgentle']:
        uname = 'araport/' + u
        ue = Entity(uname, parent='admin')
        entity_store[uname] = ue
        uname_carbon = uname + '@carbon.super'
        ue = Entity(uname_carbon, parent='admin')
        entity_store[uname_carbon] = ue

def add_user_to_namespace( ns, user ):
    """Add a user with GET/POST/PUT/DELETE to a namespace."""

    # It's not obvious till you've coded around a bit but ns is a tuple
    ns_obj=namespace_store[ ns[1].name ]
    print 'Adding admin user ' + uname + ' to ' + ns[1].name + '...'
    for u in ['user']:
        uname = 'araport/' + u
        uname_carbon = uname + '@carbon.super'
        ns_obj.users[uname] = ['POST', 'PUT', 'DELETE']
        # Hack. Depending on how the JWT is generated, wso2 identifies as either
        # uname or uname@carbon.super. We will fix this eventually
        ns_obj.users[uname_carbon] = ['POST', 'PUT', 'DELETE']
        namespace_store[ ns[1].name ] = ns_obj
    print 'Done.'
