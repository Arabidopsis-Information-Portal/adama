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
    role = os.environ['ROLE']
    cmd = ('serf agent -event-handler=/handler/handler.py '
           '-log-level=debug -tag role={role}'
           .format(**locals()).split())
    contact = os.environ.get('CONTACT')
    if contact:
        cmd.extend(['-join', contact])
    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
