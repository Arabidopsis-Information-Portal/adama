import os
import subprocess


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


def task_build_adama_app():

    all_files = ['adama-app/Dockerfile', 'adama-app/dodo.py']
    for d, _, fs in os.walk('adama-app/adama-package'):
        for f in fs:
            if f.endswith('.pyc'):
                continue
            all_files.append(os.path.join(d, f))

    return {
        'actions': ['cd adama-app && docker build -t adama_app .',
                    'docker inspect -f "{{ .Id }}" adama_app > adama-app/.build'],
        'targets': ['adama-app/.build'],
        'file_dep': all_files,
        'uptodate': [target_image_exists('adama_app')],
        'clean': True,
        'verbosity': 2
    }


def task_build():

    all_files = ['deploy.yml', 'Dockerfile',
                 'dodo.py', 'serfnode.yml', 'adama-app/.build']
    for a_dir in ('deploy', 'handler'):
        for d, _, fs in os.walk(a_dir):
            for f in fs:
                if f.endswith('.pyc'):
                    continue
                all_files.append(os.path.join(d, f))

    return {
        'actions': ['docker build -t adama .',
                    'docker inspect -f "{{ .Id }}" adama > .build'],
        'file_dep': all_files,
        'task_dep': ['build_adama_app'],
        'targets': ['.build'],
        'uptodate': [target_image_exists('adama')],
        'verbosity': 2
    }

