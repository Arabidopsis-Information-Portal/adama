import supervisor


def spawn(volumes):
    supervisor.install_launcher(
        'redis', '{} redis redis-server --appendonly yes'.format(volumes))
