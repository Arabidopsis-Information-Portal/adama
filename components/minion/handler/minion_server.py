#!/usr/bin/env python

import server
import supervisor


class MinionServer(server.Server):

    def __init__(self, ip, port):
        super(MinionServer, self).__init__(ip, port)

    def handle(self, data):
        """Start a worker.

        Message format:

            {
              'image': 'image name'
              'numprocs': number of workers,
              'args': 'extra arguments for "docker run -d image ..."'
            }

        """
        supervisor.start(
            'worker.conf',
            target='worker_{}'.format(data['image']),
            image=data['image'],
            numprocs=data.get('numprocs', 1),
            args=data.get('args', ''))
        return {'status': 'ok'}


def main():
    server = MinionServer('*', 1234)
    server.start()
    server.join()


if __name__ == '__main__':
    main()