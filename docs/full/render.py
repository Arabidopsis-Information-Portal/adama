#!/usr/bin/env python
"""Use Jinja2 to render the docs templates."""

import sys
import os
import glob

import jinja2
import yaml


HERE = os.path.dirname(os.path.abspath(__file__))
env = jinja2.Environment(loader=jinja2.FileSystemLoader(HERE))


def render(filename, data):
    output_name, _ = os.path.splitext(filename)
    template = env.get_template(filename)
    out = template.render(data)
    with open(output_name, 'w') as f:
        f.write(out)


def get_data():
    return yaml.load(open('data.yml'))


if __name__ == '__main__':
    for filename in glob.glob('*.j2'):
        print('Rendering: {}'.format(filename))
        render(filename, get_data())
