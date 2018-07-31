# -*- coding: UTF-8 -*-
from .fetchers.redmine import fetch_tickets as fetch_redmine_tickets
from .fetchers.trac import fetch_tickets as fetch_trac_tickets
from flask.cli import with_appcontext
from flask.globals import _app_ctx_stack

import click


@click.command('fetch-tickets')
@with_appcontext
def fetch_tickets_command():
    """
    """
    app = _app_ctx_stack.top.app
    click.echo('Start fetching tickets.')
    fetch_redmine_tickets(app)
    fetch_trac_tickets(app)


def init_app_fetcher(app):
    app.cli.add_command(fetch_tickets_command)
