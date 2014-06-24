import subprocess

import pika

from apim.config import Config
from apim.docker import check_docker


def check_queue():
    """Check that the queue exchange is running.

    Use the info from the config file.

    Do more than just check the connection, try to register a
    queue and then delete it.

    """
    try:
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=Config.get('queue', 'host'),
                                      port=Config.getint('queue', 'port')))
        channel = conn.channel()
        channel.queue_declare(queue='test')
        channel.queue_delete(queue='test')
        return True
    except pika.AMQPError:
        return False


def run():
    """Run the http server."""
    pass


if __name__ == '__main__':
    run()