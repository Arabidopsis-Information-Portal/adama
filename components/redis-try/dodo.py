import os
import subprocess

from doit.tools import result_dep, title_with_actions


def task__check_images():
    img = 'serfnode'
    return {
        'actions': ["docker inspect -f '{{{{ .Id }}}}' {} "
                    "2>/dev/null || echo ''".format(img)],
    }


def target_image_exists():
    try:
        subprocess.check_output(
            'docker inspect serf-redis 1>/dev/null 2>&1',
            shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def task_build():
    """Build serf-redis image"""

    all_files = ['dodo.py', 'Dockerfile']
    for d, _, fs in os.walk('handler'):
        for f in fs:
            all_files.append(os.path.join(d, f))

    return {
        'actions': ['docker build -t serf-redis .',
                    'touch .build'],
        'targets': ['.build'],
        'file_dep': all_files,
        'uptodate': [result_dep('_check_images'), target_image_exists]
    }