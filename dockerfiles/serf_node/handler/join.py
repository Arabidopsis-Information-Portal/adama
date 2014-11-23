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
    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
