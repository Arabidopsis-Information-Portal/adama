import socket
import subprocess


class Firewall(object):

    def __init__(self, whitelist,
                 get=None, insert=None, delete=None):
        self.whitelist = whitelist
        # function that retuns the chain FORWARD
        if get is not None:
            self.get = get
        # function to insert a rule
        if insert is not None:
            self.insert = insert
        # function to delete a rule
        if delete is not None:
            self.delete = delete
        self.workers = {}

    def _get(self):
        return subprocess.check_output(
            'sudo iptables -L FORWARD -n -v --line-number'.split())

    def _insert(self, line_no, dest, iface, target):
        subprocess.check_output(
            'sudo iptables -I FORWARD {line_no} '
            '-m physdev --physdev-in {iface} '
            '-s 0/0 -d {dest} -j {target}'
            .format(**locals()).split())

    def _delete(self, dest, iface, target):
        subprocess.check_output(
            'sudo iptables -D FORWARD -s 0/0 -d {dest} '
            '-m physdev --physdev-in {iface} '
            '-j {target}'.format(**locals()).split())

    get = _get
    insert = _insert
    delete = _delete

    def register(self, worker, iface):
        """Allow worker to whitelist."""

        self.workers[worker] = iface
        self._refresh(iface)

    def unregister(self, worker):
        """Remove worker from firewall."""

        iface = self.workers[worker]
        rules = [rule for rule in self._list() if rule[-1] == iface]
        for rule in rules:
            self.delete(rule[-2], iface, rule[1])
        del self.workers[worker]

    def _refresh(self, iface):
        """Set iptables from whitelist."""

        self._ensure_drop(iface)

        new = set(self._resolve(self.whitelist))
        old = set(self._resolve(
            rule[-2] for rule in self._list()
            if rule[-1] == iface and rule[1] == 'ACCEPT'))

        for ip in new - old:
            self.insert(1, ip, iface, 'ACCEPT')

        for ip in old - new:
            self.delete(ip, iface, 'ACCEPT')

    @staticmethod
    def _resolve(addresses):
        """Convert names to ip's."""

        for addr in addresses:
            _, _, ips = socket.gethostbyname_ex(addr)
            for ip in ips:
                yield ip

    def _ensure_drop(self, iface):
        """Make sure everything is dropped at ``iface``.

        Last line of all rules for ``iface`` should be a drop from and
        to everything.

        """
        rules = [rule for rule in self._list() if rule[-1] == iface]
        insert = None
        if not rules:
            # if there are no rules for this iface
            # insert a new DROP in first position
            insert = 1
        elif self.is_drop_everything(rules[-1]):
            # if there are rules for this iface but no DROP everything
            # in last position, then insert one after them
            insert = int(rules[-1][0]) + 1
        if insert is not None:
            self.insert(1, '0/0', iface, 'DROP')


    @staticmethod
    def is_drop_everything(rule):
        return rule[3:6] == ['DROP', '0.0.0.0/0', '0.0.0.0/0']

    def _list(self):
        for line in self.get().splitlines()[2:]:
            fields = line.split()
            try:
                # extract iface if rule is a PHYSDEV match
                iface = fields[fields.index('--physdev-in') + 1]
            except ValueError:
                iface = None
            yield [fields[0], fields[3], fields[8], fields[9], iface]
