import supervisor


def spawn(volumes):
    supervisor.install_launcher(
        'redis', '{} dockerfile/rabbitmq'.format(volumes))
