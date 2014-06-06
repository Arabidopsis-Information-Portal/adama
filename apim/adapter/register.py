import json
import os
import subprocess
import sys
import tarfile
import tempfile
import uuid
import zipfile

import jinja2

LANGUAGES = {
    'python': ('py', 'pip install {package}'),
    'ruby': ('rb', 'gem install {package}'),
    'javascript': ('js', 'npm install {package}'),
    'lua': ('lua', None),
    'java': ('jar', None)
}


HERE = os.path.dirname(os.path.abspath(__file__))


def register(metadata, contents):
    temp_dir = create_temp_dir()
    print('temp:', temp_dir)
    extract_code(metadata, contents, temp_dir)
    render_template(metadata, temp_dir)
    save_metadata(metadata, temp_dir)
    iden = build_docker(metadata, temp_dir)
    return iden


def create_temp_dir():
    return tempfile.mkdtemp()


def extract_code(metadata, contents, temp_dir):
    language = metadata['language']
    file_type = metadata['fileType']

    user_code = os.path.join(temp_dir, 'user_code')
    os.mkdir(user_code)
    ext, _ = LANGUAGES[language]
    if file_type == 'module':
        main = 'main.{}'.format(ext)
        with open(os.path.join(user_code, main), 'w') as f:
            f.write(contents)
    elif file_type == 'tar.gz':
        with open(os.path.join(temp_dir, 'contents.tgz'), 'w') as f:
            f.write(contents)
        tar = tarfile.open(os.path.join(temp_dir, 'contents.tgz'))
        tar.extractall(user_code)
    elif file_type == 'zip':
        with open(os.path.join(temp_dir, 'contents.zip'), 'w') as f:
            f.write(contents)
        zip = zipfile.ZipFile(os.path.join(temp_dir, 'contents.zip'))
        zip.extractall(user_code)
    elif file_type == 'package':
        raise Exception('package support not implemented yet')


def render_template(metadata, temp_dir):
    language = metadata['language']
    requirements = metadata['requirements']

    dockerfile_template = jinja2.Template(
        open(os.path.join(HERE, 'Dockerfile.adapter')).read())
    _, installer = LANGUAGES[language]
    requirement_cmds = '\n'.join(
        'RUN '+installer.format(package=req) for req in requirements)

    dockerfile = dockerfile_template.render(language=language,
                                            requirement_cmds=requirement_cmds)
    with open(os.path.join(temp_dir, 'Dockerfile'), 'w') as f:
        f.write(dockerfile)


def save_metadata(metadata, temp_dir):
    with open(os.path.join(temp_dir, 'metadata.json'), 'w') as f:
        f.write(json.dumps(metadata))


def build_docker(metadata, temp_dir):
    prev_cwd = os.getcwd()
    os.chdir(temp_dir)
    try:
        iden = str(uuid.uuid4())
        print 'docker build -t {} .'.format(iden)
        output = subprocess.check_output(
            ('/usr/local/bin/docker -H tcp://127.0.0.1:4444 build -t {} .'.format(iden)).split(),
            stderr=subprocess.STDOUT)
        print(output)
    finally:
        os.chdir(prev_cwd)
    return iden