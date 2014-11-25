import os
import subprocess


def env(image):
    """Return environment of image. """

    out = docker('inspect', '-f', '{{.Config.Env}}', image)
    return dict(map(lambda x: x.split('='), out.strip()[1:-1].split()))


def path(p):
    """Build the corresponding path `p` inside the container. """

    return os.path.normpath(os.path.join(
        os.environ.get('HOST_PREFIX', '/host'), './{}'.format(p)))


def docker(*args):
    """Execute a docker command inside the container. """

    docker_binary = path(os.environ.get('DOCKER_BINARY', '/usr/bin/docker'))
    docker_socket = path(os.environ.get('DOCKER_SOCKET', '/run/docker.sock'))
    cmd = ('{docker_binary} -H unix://{docker_socket}'
           .format(**locals()).split())
    cmd.extend(args)
    return subprocess.check_output(cmd).strip()


def fig(*args):
    docker_path = os.path.dirname(
        path(os.environ.get('DOCKER_BINARY', '/usr/bin/docker')))
    docker_socket = path(os.environ.get('DOCKER_SOCKET', '/run/docker.sock'))
    arg_list = ' '.join(args)
    cmd = ('DOCKER_HOST=unix://{docker_socket} PATH={docker_path}:$PATH '
           'fig {arg_list}'
           .format(**locals()))
    return subprocess.check_output(cmd, shell=True).strip()
