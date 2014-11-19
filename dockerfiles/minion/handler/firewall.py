import os
import socket
import subprocess

from docker_utils import docker


class Firewall(object):
    pass


def allow(worker, whitelist):
    """Allow access of worker to ip's in whitelist."""

    whitelist = list(resolve(whitelist if whitelist is not None else []))
    pid = get_pid(worker)
    host_dir = os.environ['HOST_PREFIX']
    ensure_namespace_link(host_dir, pid)
    run(pid, 'iptables -A OUTPUT -s 0/0 -d 0/0 -j DROP')
    for ip in whitelist:
        run(pid, 'iptables -I OUTPUT 1 -s 0/0 -d {0} -j ACCEPT'.format(ip))


def resolve(addresses):
    """Convert names to ip's."""

    for addr in addresses:
        _, _, ips = socket.gethostbyname_ex(addr)
        for ip in ips:
            yield ip


def get_pid(worker):
    return docker('inspect', '-f', '{{.State.Pid}}', worker).strip()


def ensure_namespace_link(host_dir, pid):
    subprocess.check_call('mkdir -p /var/run/netns'.split())
    subprocess.check_call(
        'ln -sf {host_dir}/proc/{pid}/ns/net /var/run/netns/{pid}'
        .format(**locals()).split())


def run(pid, command):
    return subprocess.check_output(
        'sudo ip netns exec {pid} {command}'
        .format(**locals()).split())
