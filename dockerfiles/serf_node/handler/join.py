#!/usr/bin/env python
"""
Launch a serf node.

The role of the node is retrieved from the environment variable ``ROLE``.

The node will join a cluster, if the ``CONTACT`` variable specifies an
address.

"""

import os
import subprocess


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
    bind_port = os.environ.get('BIND_PORT', '7946')
    if bind_port:
        cmd.extend(['-bind', '0.0.0.0:{}'.format(bind_port)])
    node = os.environ.get('NODE')
    if node:
        cmd.extend(['-node', node])
    rpc_port = os.environ.get('RPC_PORT', '7373')
    if rpc_port:
        cmd.extend(['-rpc-addr', '127.0.0.1:{}'.format(rpc_port)])
    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
