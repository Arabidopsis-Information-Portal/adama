#!/usr/bin/env python
"""
Launch a serf node.

The role of the node is retrieved from the environment variable ``ROLE``.

The node will join a cluster, if the ``CONTACT`` variable specifies an
address.

"""

import bisect
import os
import subprocess
import uuid

from utils import save_info


def find_port(start=1234):
    """Find an unused port starting at ``start``. """

    out = subprocess.check_output('netstat -antup'.split())
    used_ports = sorted(set(int(line.split()[3].split(':')[-1])
                            for line in out.splitlines()[2:]))
    return _find(used_ports, start)


def _find(lst, x):
    if not lst:
        return x
    idx = bisect.bisect_left(lst, x)
    if len(lst) <= idx:
        return x
    if lst[idx] == x:
        return _find(lst[idx:], x+1)
    else:
        return x


def main():
    role = os.environ.get('ROLE', 'no_role')
    cmd = ('serf agent -event-handler=/handler/handler.py '
           '-log-level=debug -tag role={role}'
           .format(**locals()).split())

    contact = os.environ.get('CONTACT')
    if contact:
        cmd.extend(['-join', contact])

    advertise = os.environ.get('ADVERTISE')
    if advertise:
        cmd.extend(['-advertise', advertise])
        cmd.extend(['-tag', 'adv={}'.format(advertise)])

    bind_port = find_port(start=7946)
    try:
        _, bind_port = advertise.split(':')
    except (ValueError, AttributeError):
        pass
    cmd.extend(['-bind', '0.0.0.0:{}'.format(bind_port)])
    cmd.extend(['-tag', 'bind={}'.format(bind_port)])

    node = os.environ.get('NODE') or uuid.uuid4().hex
    cmd.extend(['-node', node])

    rpc_port = os.environ.get('RPC_PORT') or find_port(start=7373)
    cmd.extend(['-rpc-addr', '127.0.0.1:{}'.format(rpc_port)])
    cmd.extend(['-tag', 'rpc={}'.format(rpc_port)])

    save_info(node, advertise, bind_port, rpc_port)

    print('node name:   {}'.format(node))
    print('advertising: {}'.format(advertise))
    print('bound to:    0.0.0.0:{}'.format(bind_port))
    print('rpc port:    {}'.format(rpc_port))

    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
