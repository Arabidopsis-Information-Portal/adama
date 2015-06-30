import docker

from ..config import Config
from .tools import workers_of
from ..tasks import QueueConnection


def is_up(cid):
    """True if container is running.

    :type cid: str
    :rtype: bool
    """
    client = docker.Client(version='auto')
    try:
        info = client.inspect_container(cid)
    except docker.errors.APIError:
        return False
    return info['State']['Running']


def is_ready(cid):
    """True if the container is 'ready'.

    Ready means able to consume messages from the queue.

    :type cid: str
    :rtype: bool
    """
    if not is_up(cid):
        return False
    client = docker.Client(version='auto')
    cat = client.exec_create(
        cid, ['cat', '/busy'], stdout=True, stderr=True)
    client.exec_start(cat['Id'])
    exit_code = client.exec_inspect(cat['Id'])['ExitCode']
    # if there is no file /busy, the worker is ready
    return exit_code != 0


def workers_ready_for(service_name):
    """Return number of workers currently ready for the service.

     `srv` is the full service name (namespace + service + version).

    :type service_name: str
    :rtype: int
    """
    return len(filter(is_ready, workers_of(service_name)))


def workers_total(service_name):
    """Total of workers running as containers for the service.

    :type service_name: str
    :rtype: int
    """
    return len(filter(is_up, workers_of(service_name)))


def queue_size(service_name):
    """Approximate size of queued messages directed to a service.

    :type service_name: str
    :rtype: int
    """
    queue = QueueConnection(
        Config.get('queue', 'host'),
        Config.getint('queue', 'port'),
        service_name)
    return queue.size()