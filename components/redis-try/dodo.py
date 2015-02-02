import os

from doit.tools import result_dep, title_with_actions


def task_hello():
    """hello"""

    def python_hello(targets):
        with open(targets[0], "a") as output:
            output.write("Python says Hello World!!!\n")

    return {
        'actions': [python_hello],
        'targets': ["hello.txt"],
        }


def task__serfnode_version():
    return {
        'actions': ["docker inspect -f '{{ .Id }}' serfnode"]
    }


def task__redis_image_exists():
    """Check that serf-redis image exists"""
    return {
        'actions': ["docker inspect -f '{{ .Id }}' serf-redis "
                    "2>/dev/null || echo ''"],
        'title': lambda x: 'foo' + str(x)
    }


def task_build():
    """Build serf-redis image"""

    def hi():
        print('Hi there')

    all_files = ['dodo.py', 'Dockerfile']
    for d, _, fs in os.walk('handler'):
        for f in fs:
            all_files.append(os.path.join(d, f))

    return {
        'actions': ['touch foo'],
        'file_dep': all_files,
        'uptodate': [result_dep('_serfnode_version'),
                     result_dep('_redis_image_exists')]
    }