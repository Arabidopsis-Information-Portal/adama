from flask.ext import restful

from .api import ok
from .service import get_service
from .services import all_services
from .command.worker_monitor import (workers_ready_for, workers_total,
                                     queue_size)


class ServiceHealthResource(restful.Resource):

    def get(self, namespace, service):
        srv = get_service(namespace, service)
        return ok(health(srv))


class GeneralHealthResource(restful.Resource):

    def get(self):
        return ok({
            'result': list(check_all())
        })


def check_all():
    for srv in all_services():
        stats = health(srv)
        if not healthy(stats):
            stats['service'] = srv.iden
            yield stats


def healthy(stats):
    """Decide if stats are from a healthy service.

    :type stats: Dict[str, int]
    :rtype: bool
    """
    return (stats['total_workers'] > 0 and
            (stats['workers_free'] > 0 or stats['queue_size'] <= 5))


def health(srv):
    """Return health stats for service.

    :type srv: Service
    :rtype: Dict[str, int]
    """
    return {
        'total_workers': workers_total(srv.iden),
        'workers_free': workers_ready_for(srv.iden),
        'queue_size': queue_size(srv.iden)
    }
