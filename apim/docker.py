from __future__ import print_function

import os
import random
import select
import subprocess
import sys

from .config import Config
from .tools import TimeoutFunction, TimeoutFunctionException

MAX_VETH = 100000


def docker(*args, **kwargs):
    host = Config.get('docker', 'host')
    cmd = [Config.get('docker', 'command')] + (['-H', host] if host else [])
    stderr = kwargs.get('stderr', subprocess.STDOUT)
    stdout = kwargs.get('stdout', subprocess.STDOUT)
    return subprocess.Popen(
        cmd + list(args), stdout=stdout, stderr=stderr)

def docker_output(*args):
    p = docker(*args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    return p.communicate()[0]

def tail(fd, timeout=0):
    f = os.fdopen(fd, 'r', 0)
    readline = TimeoutFunction(f.readline, timeout)
    try:
        while True:
            yield readline()
    except TimeoutFunctionException:
        return
    finally:
        f.close()

def tail_logs(container, timeout=0):
    r, w = os.pipe()
    p = docker('logs', '-f', container, stderr=subprocess.STDOUT, stdout=w)
    return tail(r, timeout)


def check_docker(display=False):
    """Check that the Docker daemon is running.

    Use the info from the config file.

    """
    try:
        docker_output('ps')
        return True
    except Exception:
        if display:
            print('No docker daemon listening at {0}'.
                  format(Config.get('docker', 'host')), file=sys.stderr)
            print('or wrong command "{0}"'.
                  format(Config.get('docker', 'command')), file=sys.stderr)
            print('Please, check ~/.apim.conf', file=sys.stderr)
        return False


def start_container(iden, *params):
    """Run container from image ``iden``.

    Create veth pair and bind them properly. Return the name of the
    interface in the inside of the container, and the ip address.

    """
    container = docker_output(
        'run', '-d', '--net=none', iden, *params).strip()
    pid = docker_output(
        'inspect', '-f', '{{.State.Pid}}', container).strip()
    n = random.randint(1, MAX_VETH)
    veth_a = 'vethA{0}'.format(n)
    veth_b = 'vethB{0}'.format(n)

    x = random.randint(1, 255)
    y = random.randint(1, 255)

    subprocess.check_call(
        ['sudo', 'sh', '-c',
         """
         mkdir -p /var/run/netns
         ln -sf /proc/{pid}/ns/net /var/run/netns/{pid}
         ip link add {veth_a} type veth peer name {veth_b}
         brctl addif docker0 {veth_a}
         ip link set {veth_a} up
         ip link set {veth_b} netns {pid}
         ip netns exec {pid} ip link set dev {veth_b} name eth0
         ip netns exec {pid} ip link set eth0 up
         ip netns exec {pid} ip addr add 172.17.{x}.{y}/16 dev eth0
         ip netns exec {pid} ip route add default via 172.17.42.1
         """.format(pid=pid, veth_a=veth_a, veth_b=veth_b, x=x, y=y)])

    return veth_a, x, y

