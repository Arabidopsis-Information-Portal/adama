import supervisor


def spawn(volumes):
    supervisor.install_launcher(
            'rabbitmq',
            '{} dockerfile/rabbitmq'.format(volumes))
