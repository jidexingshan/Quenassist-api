import click
from .controller.server import Server
from .config import settings
from quenassist_app.system import utils

from pathlib import Path

from alembic import config
from click import Context

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('-V', '--version', is_flag=True, help='Show version and exit.')
def main(ctx, version):
    pass
    # if version:
    #     click.echo(__version__)
    # elif ctx.invoked_subcommand is None:
    #     click.echo(ctx.get_help())

@main.command()
@click.option('-h', '--host', show_default=True, help=f'Host IP. Default: {settings.HOST}')
@click.option('-p', '--port', show_default=True, type=int, help=f'Port. Default: {settings.PORT}')
@click.option('--level', help='Log level')
def server(host, port, level):
    """Start server."""
    kwargs = {
        'LOGLEVEL': level,
        'HOST': host,
        'PORT': port,
    }
    for name, value in kwargs.items():
        if value:
            settings.set(name, value)

    Server().run()

@main.command()
@click.pass_context
@click.option('-h', '--help', is_flag=True)
@click.argument('args', nargs=-1)
def migrate(ctx: Context, help, args):
    """usage migrate -- arguments    """
    with utils.chdir(Path(__file__).parent / 'system/migration'):
        argv = list(args)
        if help:
            argv.append('--help')
        config.main(prog=ctx.command_path, argv=argv)