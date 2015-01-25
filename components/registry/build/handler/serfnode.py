import supervisor


def spawn(volumes):
    supervisor.install_launcher(
        'registry',
        '{} -e STORAGE_PATH=/data registry'.format(volumes))

