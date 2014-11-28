#!/usr/bin/env python
from textwrap import dedent
import sys

from serf_master import SerfHandler
from utils import truncated_stdout, serf, with_member_info, with_payload
from docker_utils import docker
from supervisor import start, stop


TEMPLATE = dedent(
    """
    tickTime=2000
    initLimit=10
    syncLimit=5
    dataDir=/data/zookeeper
    clientPort=2181
    {servers}
    """)


class MyHandler(SerfHandler):

    @truncated_stdout
    @with_member_info
    def update(self, members):
        if any(member['role'] == 'zookeeper' for member in members):
            update_zookeeper()

    member_join = update
    member_leave = update
    member_failed = update


def update_zookeeper():
    members = [member
               for member in serf('members')['members']
               if member['status'] == 'alive']
    myself = serf('info')['agent']['name']
    stop('zookeeper')
    sorted_members = sort_members(members)
    write_members(sorted_members)
    id_num = myid(myself, sorted_members)
    write_myid(id_num)
    start('zookeeper',
          name='{}_zookeeper'.format(myself),
          volume=data_volume_name())


def data_volume_name():
    return 'zookeeper_zookeeperdata_1'


def service_name():
    return 'zookeeper_zookeeper_1'


def write_myid(n):
    with open('/data/zookeeper/myid', 'w') as f:
        f.write(str(n))


def write_members(members):
    with open('/data/zoo.cfg', 'w') as f:
        servers = [
            'server.{i}={ip}:2888:3888'
            .format(i=i+1,
                    ip=elt['addr'].split(':')[0])
            for i, elt in enumerate(members)]
        f.write(TEMPLATE.format(servers='\n'.join(servers)))


def sort_members(members):
    assert isinstance(members, list)
    members = [elt for elt in members if elt['tags']['role'] == 'zookeeper']
    members.sort(key=lambda elt: elt['addr'])
    return members


def myid(myself, members):
    for i, elt in enumerate(members):
        if elt['name'] == myself:
            return i+1

