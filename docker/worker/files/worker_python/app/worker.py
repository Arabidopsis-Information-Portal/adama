"""

Needs environment variables:

- MAIN_MODULE_PATH
- MAIN_MODULE
- SERVICE_NAME

"""

import traceback
import importlib
import inspect
import sys
import os
import json

import zmq

from channelpy import Channel
from channelpy.server import server
from adamalib import Adama


HERE = os.path.abspath(os.path.dirname(__file__))
ctx = zmq.Context()


def find_main_module():
    main_module_path = os.environ.get('MAIN_MODULE_PATH', '')
    main_module = os.environ['MAIN_MODULE']
    sys.path.insert(0, os.path.join(HERE, 'user_code', main_module_path))
    return importlib.import_module(main_module)


class FetchWorker(object):
    """

    Receives:

        {
          data_port: str
          args: {
            _endpoint: str
            _headers: Dict
            _token: str
            _url: str
            _service_name: str
            ... user parameters ...
          }
        }

    Responds via ZMQ on data_port (a stream of):

        {
          type: error | metadata | data | END
          value: ...
        }

    """


    def _send_back(self, job, obj):
        socket = ctx.socket(zmq.PUSH)
        socket.connect(job['value']['data_port'])
        socket.send(json.dumps(obj))

    def _error(self, job, message):
        self._send_back(job,
                        {'type': 'error',
                         'value': {
                             'message': message
                         }})

    def handle(self, job):
        try:
            args = job['value']['args']
            endpoint = getattr(self.module, args['_endpoint'])
            adama = Adama(token=args['_token'],
                          url=args['_url'],
                          headers=args['_headers'],
                          responder=job['value']['data_port'])
            if inspect.isgeneratorfunction(endpoint):
                self._run_generator(endpoint, adama, job)
            else:
                self._run_function(endpoint, adama, job)
        except Exception as exc:
            self._error(job, traceback.format_exc())
            
    def _run_generator(self, endpoint, adama, job):
        self._send_back(job,
                        {'type': 'metadata',
                         'value': {
                             'type': 'generator'
                         }})
        g = endpoint(job['value']['args'], adama)
        first = True
        for elt in g:
            if first:
                # Before sending the first object but after the
                # generator is primed, send any metadata gathered from
                # the adama object.
                first = False
                self._send_back(job,
                                {'type': 'metadata',
                                 'value': {
                                     'object_metadata': adama._get_metadata()
                                 }})
            self._send_back(job, {'type': 'data', 'value': elt})
        self._send_back(job, {'type': 'END'})

    def _run_function(self, endpoint, adama, job):
        self._send_back(job,
                        {'type': 'metadata',
                         'value': {
                             'type': 'function'
                         }})
        result = endpoint(job['value']['args'], adama)
        self._send_back(job,
                        {'type': 'metadata',
                         'value': {
                             'object_metadata': adama._get_metadata()
                         }})
        self._send_back(job, {'type': 'END'})

    def run(self):
        self.module = find_main_module()
        with Channel(name=os.environ['SERVICE_NAME']) as listen:
            server(listen, self.handle)


class ProcessWorker(object):
    pass


