from textwrap import dedent

import pytest

import apim.firewall as f



def test_insert_drop():
    table0 = dedent(
        """
        Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
        num   pkts bytes target     prot opt in     out     source               destination
        """)
    table1 = dedent(
        """
        Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
        num   pkts bytes target     prot opt in     out     source               destination
        1        0     0 ACCEPT     all  --  *      docker0  0.0.0.0/0            0.0.0.0/0            ctstate RELATED,ESTABLISHED
        2        0     0 ACCEPT     all  --  docker0 !docker0  0.0.0.0/0            0.0.0.0/0
        3        0     0 ACCEPT     all  --  docker0 docker0  0.0.0.0/0            0.0.0.0/0
        """)

    def check_insert(line, dest, iface, target):
        assert line == 1
        assert dest == '0/0'
        assert iface == 'foo'
        assert target == 'DROP'

    w = f.Firewall([],
                   get=lambda: table0,
                   insert=check_insert,
                   delete=lambda n: None)
    w._ensure_drop('foo')

    w = f.Firewall([],
                   get=lambda: table1,
                   insert=check_insert,
                   delete=lambda _: None)
    w._ensure_drop('foo')

def test_idempotence():
    table = dedent(
        """
        Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
        num   pkts bytes target     prot opt in     out     source               destination
        1        0     0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            PHYSDEV match --physdev-in foo
        2        0     0 ACCEPT     all  --  *      docker0  0.0.0.0/0            0.0.0.0/0            ctstate RELATED,ESTABLISHED
        3        0     0 ACCEPT     all  --  docker0 !docker0  0.0.0.0/0            0.0.0.0/0
        4        0     0 ACCEPT     all  --  docker0 docker0  0.0.0.0/0            0.0.0.0/0
        """)

    def check_insert(*args):
        assert False

    w = f.Firewall([],
                   get=lambda: table,
                   insert=check_insert,
                   delete=lambda _: None)
    w._ensure_drop('foo')

def test_missing():
    table = dedent(
        """
        Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
        num   pkts bytes target     prot opt in     out     source               destination
        1        0     0 ACCEPT     all  --  *      *       0.0.0.0/0            1.1.1.1              PHYSDEV match --physdev-in foo
        2        0     0 ACCEPT     all  --  *      docker0  0.0.0.0/0            0.0.0.0/0            ctstate RELATED,ESTABLISHED
        3        0     0 ACCEPT     all  --  docker0 !docker0  0.0.0.0/0            0.0.0.0/0
        4        0     0 ACCEPT     all  --  docker0 docker0  0.0.0.0/0            0.0.0.0/0
        """)

    def check_insert(line, dest, iface, target):
        assert line == 2
        assert dest == '0/0'
        assert iface == 'foo'
        assert target == 'DROP'

    w = f.Firewall([],
                   get=lambda: table,
                   insert=check_insert,
                   delete=lambda _: None)
    w._ensure_drop('foo')

def test_refresh():
    table = dedent(
        """
        Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
        num   pkts bytes target     prot opt in     out     source               destination
        1        0     0 ACCEPT     all  --  *      *       0.0.0.0/0            1.1.1.1              PHYSDEV match --physdev-in foo
        2        0     0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            PHYSDEV match --physdev-in foo
        """)

    def check_insert(line, dest, iface, target):
        assert line == 1
        assert dest == '2.2.2.2'
        assert iface == 'foo'
        assert target == 'ACCEPT'

    w = f.Firewall(['1.1.1.1', '2.2.2.2'],
                   get=lambda: table,
                   insert=check_insert,
                   delete=lambda _: None)
    w._refresh('foo')

    def check_insert(line, dest, iface, target):
        assert line == 1
        assert dest == '3.3.3.3'
        assert iface == 'foo'
        assert target == 'ACCEPT'

    def check_delete(dest, iface, target):
        assert dest == '1.1.1.1'
        assert iface == 'foo'
        assert target == 'ACCEPT'

    w = f.Firewall(['3.3.3.3'],
                   get=lambda: table,
                   insert=check_insert,
                   delete=check_delete)
    w._refresh('foo')
