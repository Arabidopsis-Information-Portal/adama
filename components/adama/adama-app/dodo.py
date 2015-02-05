import os
import subprocess


DOIT_CONFIG = {'default_tasks': ['build']}


def target_image_exists(img):
    """Check if 'img' exists in local registry"""

    def f():
        try:
            subprocess.check_output(
                'docker inspect {} 1>/dev/null 2>&1'.format(img),
                shell=True)
            return True
        except subprocess.CalledProcessError:
            return False
    return f


def task_build():
    """Build adama_app image"""

    all_files = ['Dockerfile', 'dodo.py']
    for d, _, fs in os.walk('adama-package'):
        for f in fs:
            if f.endswith('.pyc'):
                continue
            all_files.append(os.path.join(d, f))

    return {
        'actions': ['docker build -t adama_app .',
                    'docker inspect -f "{{ .Id }}" adama_app > .build'],
        'targets': ['.build'],
        'file_dep': all_files,
        'uptodate': [target_image_exists('adama_app')],
        'clean': True,
        'verbosity': 2
    }