import os
import subprocess

import jinja2
env = jinja2.Environment(loader=jinja2.FileSystemLoader('/programs'))


def supervisor_install(block, **kwargs):
    """Update supervisor with `block` config.

    - `block` is the name to a .conf template file (in directory
      `/programs`)
    - `kwargs` are the key/values to use in the template

    """
    template = env.get_template(block)
    conf = template.render(kwargs)
    with open(os.path.join('/etc/supervisor/conf.d', block), 'w') as f:
        f.write(conf)


def supervisor_exec(*args):
    return subprocess.check_output(
        ['supervisorctl'] + list(args))


def supervisor_update():
    supervisor_exec('reread')
    supervisor_exec('update')
