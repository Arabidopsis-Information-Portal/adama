import traceback
import importlib
import inspect
import sys
import os
import json

import zmq

from channelpy import server, Channel


HERE = os.path.abspath(os.path.dirname(__file__))
ctx = zmq.Context()


def find_main_module():
    main_module_path = os.environ.get('MAIN_MODULE_PATH', '')
    main_module = os.environ['MAIN_MODULE']
    sys.path.insert(0, os.path.join(HERE, 'user_code', main_module_path))
    return importlib.import_module(main_module)


class FetchWorker(object):
    """
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
    """


    def _send_back(self, obj, address):
        socket = ctx.socket(zmq.PUSH)
        socket.connect(address)
        socket.send(json.dumps(obj))

    def _error(self, message, job):
        self._send_back(job['data_port'],
                        {'status': 'error',
                         'message': message})

    def handle(self, job):
        try:
            args = job['args']
            endpoint = getattr(self.module, args['_endpoint'])
            adama = Adama(token=args['_token'],
                          url=args['_url'],
                          headers=args['_headers'],
                          responder=job['data_port'])
            if inspect.isgeneratorfunction(endpoint):
                self._run_generator(endpoint, adama, job)
            else:
                self._run_function(endpoint, adama, job)
        except Exception as exc:
            self._error(traceback.format_exc(), job)
            
    def _run_generator(self, endpoint, adama, job):
        g = endpoint(job['args'], adama)

    def _run_function(self, endpoint, adama, job):
        pass

    def run(self):
        self.module = find_main_module()
        with Channel(name=SERVICE_NAME) as listen:
            server(listen, self.handle)


class ProcessWorker(object):
    pass


