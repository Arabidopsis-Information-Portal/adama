#!/usr/bin/env python
from textwrap import dedent

from serf_master import SerfHandler
from utils import truncated_stdout, serf
from docker_utils import docker


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
    def member_join(self):
        members = serf('members')['members']
        myself = serf('info')['agent']['name']
        sorted_members = sort_members(members)
        write_members(sorted_members)
        id_num = myid(myself, sorted_members)
        write_myid(id_num)
        print "wrote", sorted_members
        print "my_id", id_num
        #stop_zookeeper(myself)
        #start_zookeeper(myself, id_num)


def stop_zookeeper(agent):
    try:
        docker('rm', '-f', '{}_zookeeper'.format(agent))
    except Exception:
        pass


def start_zookeeper(agent, myid):
    port1 = port(1, myid)
    port2 = port(2, myid)
    containers = docker('ps', '-a').splitlines()
    data = ''
    for cont in containers:
        data = cont.split()[-1].strip()
        if 'zookeeperdata' in data:
            break
    docker('run', '-d', '-p', '2181', '-p',
           '{0}:{0]'.format(port1), '{0}:{0]'.format(port2),
           '--name', '{}_zookeeper'.format(agent),
           '--volumes-from', data, 'jplock/zookeeper')


def write_myid(n):
    with open('/data/zookeeper/myid', 'w') as f:
        f.write(str(n))


def write_members(members):
    with open('/data/zoo.cfg', 'w') as f:
        servers = [
            'server.{i}={ip}:{port1}:{port2}'
            .format(i=i+1,
                    ip=elt['addr'].split(':')[0],
                    port1=2888+i,
                    port2=3888+i)
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


def port(n, id_num):
    if n == 1:
        return 2888 + id_num
    else:
        return 3888 + id_num

