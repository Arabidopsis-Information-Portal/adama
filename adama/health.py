from flask.ext import restful

from .api import ok
from .service import get_service
from .command.worker_monitor import (workers_ready_for, workers_total,
                                     queue_size)


class ServiceHealthResource(restful.Resource):

    def get(self, namespace, service):
        srv = get_service(namespace, service)
        name = srv.iden
        return ok({
            'total_workers': workers_total(name),
            'workers_free': workers_ready_for(name),
            'queue_size': queue_size(name)
        })