from flask import g

from .stores import stats_store


def tick(service, req, **kwargs):
    """Register a tick in stats for service.

    :type service: Service
    :type req: Request
    :type kwargs: dict
    """

    x_fwd = req.headers.get('X-Forwarded-For', None)
    remote_addr = req.remote_addr
    user = g.user
    extra = kwargs

    val = stats_store.get(service.iden, [])
    val.append({
        'remote_address': x_fwd or remote_addr,
        'user': user,
        'extra': extra
    })
    stats_store[service.iden] = val


def get_total_access(stats):
    return len(stats)


def get_unique_access(stats):
    return len(set(st['remote_address'] for st in stats))


def get_users(stats):
    return len(set(st['user'] for st in stats))


