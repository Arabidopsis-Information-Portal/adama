import sys
from textwrap import dedent

from blessings import Terminal
import click

from adama import __version__


t = Terminal()


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
              prompt=("{t.green}Type of adapter?{t.normal} "
                      "[{t.cyan}query{t.normal}, "
                      "{t.cyan}map_filter{t.normal}]")
              .format(t=t))
@click.option('--language',
              prompt=("{t.green}Language of choice?{t.normal} "
                      "[{t.cyan}python{t.normal}, "
                      "{t.cyan}javascript{t.normal}]")
              .format(t=t))
@click.option('--adapter_name',
              prompt="{t.green}Name for the adapter?{t.normal}".format(t=t))
def create(name, email, type, language, adapter_name):
    click.echo(locals())


@generator.command()
def publish():
    click.echo('will publish')


if __name__ == '__main__':
    generator()
