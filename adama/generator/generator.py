import os
from textwrap import dedent

from blessings import Terminal
import click
from cookiecutter.main import cookiecutter

from adama import __version__
from adama.tools import location_of


t = Terminal()
HERE = location_of(__file__)


@click.group()
def generator():
    click.echo(dedent(
        """
        {t.bold_yellow}Adama v{version}{t.normal}
        {t.cyan}Adapter generator{t.normal}
        """.format(t=t, version=__version__)))


@generator.command()
@click.option('--name',
              prompt="{t.green}Your name?{t.normal}".format(t=t))
@click.option('--email',
              prompt="{t.green}Your email?{t.normal}".format(t=t))
@click.option('--type',
              type=click.Choice(['query', 'map_filter', 'passthrough']),
              prompt=("{t.green}Type of adapter?{t.normal} "
                      "[{t.cyan}query{t.normal}, "
                      "{t.cyan}map_filter{t.normal}, "
                      "{t.cyan}passthrough{t.normal}]")
              .format(t=t))
@click.option('--language',
              type=click.Choice(['python', 'javascript']),
              prompt=("{t.green}Language of choice?{t.normal} "
                      "[{t.cyan}python{t.normal}, "
                      "{t.cyan}javascript{t.normal}]")
              .format(t=t))
@click.option('--adapter_name',
              prompt="{t.green}Name for the adapter?{t.normal}".format(t=t))
def create(**kwargs):
    directory = os.path.join(
        HERE, 'templates', kwargs['type'], kwargs['language'])
    cookiecutter(directory, no_input=True, extra_context=kwargs)
    click.echo('{t.bold_yellow}Done!{t.normal}'.format(t=t))


@generator.command()
def publish():
    click.echo('will publish')


if __name__ == '__main__':
    generator()
