import os

from doit.tools import result_dep, title_with_actions


def task__check_images():
    for img in ('serfnode', 'serf-redis'):
        yield {
            'actions': ["docker inspect -f '{{ .Id }}' " + img +
                        " 2>/dev/null || echo''"],
            'name': img
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
        'actions': ['touch .build'],
        'targets': ['.build'],
        'file_dep': all_files,
        'uptodate': [result_dep('_check_images')]
    }