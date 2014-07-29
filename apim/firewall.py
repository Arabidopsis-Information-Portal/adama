

class Firewall(object):

    def __init__(self, whitelist):
        self.whitelist = whitelist
        self.refresh()

    def register(self, worker):
        """Allow worker to whitelist."""
        pass

    def unregister(self, worker):
        pass

    def refresh(self):
        """Set iptables from whitelist"""
        pass