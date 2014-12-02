#!/usr/bin/env python
import pprint

from base_handler import BaseHandler
from utils import with_payload, with_member_info


class MyHandler(BaseHandler):

    def setup(self):
        """This gets run when the handler is created."""
        pass

    @with_payload
    def supervisor(self, **kwargs):
        """Event or query ``supervisor`` with JSON payload."""

        print 'Got a supervisor event with payload:'
        pprint.pprint(kwargs)

    @with_member_info
    def member_join(self, members):
        """``members`` is a dict with the nodes that joined."""

        print 'New members joined:'
        pprint.pprint(members)
