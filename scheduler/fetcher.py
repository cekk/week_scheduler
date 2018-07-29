# -*- coding: UTF-8 -*-
from flask.cli import with_appcontext
from flask.globals import _app_ctx_stack
from xmlrpc import client as xmlrpc_client
from .db import db_session
from .models import Ticket
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout

import requests
import click
import socket


def add_or_update_ticket(ticket, project):
    old_ticket = Ticket.query.filter_by(
        ticket_id=ticket['id'],
        project=project).first()
    if not old_ticket:
        click.echo('    Created new ticket: #{0}.'.format(
                ticket.get('id')
            )
        )
        new_ticket = Ticket(
            ticket_id=ticket.get('id'),
            title=ticket.get('summary'),
            status=ticket.get('status'),
            owner=ticket.get('owner'),
            project=project
        )
        db_session.add(new_ticket)
    else:
        old_ticket.title = ticket.get('summary')
        old_ticket.status = ticket.get('status')
        old_ticket.owner = ticket.get('owner')

def update_closed_tickets(server, project):
    db_tickets = Ticket.query.filter(
        Ticket.status != 'closed',
        Ticket.project == project).all()
    ticket_ids = map(lambda x: str(x.ticket_id), db_tickets)
    query_str = 'status=closed&id={0}'.format(','.join(ticket_ids))
    for ticket in server.ticket.queryWithDetails(query_str):
        old_ticket = Ticket.query.filter_by(
            ticket_id=ticket['id'],
            project=project).first()
        if old_ticket:
            click.secho('    Ticket #{0} for {1} has been closed.'.format(
                ticket.get('id'),
                project
            ), fg='yellow')
            old_ticket.status = 'closed'
            

def fetch_from_trac(app):
    click.echo('Fetching from trac')
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(10)
    for trac_infos in app.config.get('TRAC_PROJECTS', []):
        project = trac_infos.get('project')
        trac_url = trac_infos.get('url')
        parsed_url = urlparse(trac_url)
        username = trac_infos.get('username')
        password = trac_infos.get('password')
        xmlrpc_url = '{scheme}://{username}:{password}@{netloc}{path}/login/xmlrpc'.format(
            scheme=parsed_url.scheme,
            username=username,
            password=password,
            netloc=parsed_url.netloc,
            path=parsed_url.path
        )
        
        server = xmlrpc_client.ServerProxy(xmlrpc_url)
        click.echo('Fetching data from "{0}"'.format(trac_url))
        click.echo('- Creating/syncronizing open tickets')
        for ticket in server.ticket.queryWithDetails('status!=closed'):
            add_or_update_ticket(ticket, project)
        db_session.commit()
        
        click.secho('  ✔ done', fg='green')
        click.echo('- Syncing closed tickets')
        update_closed_tickets(server, project)
        click.secho('  ✔ done', fg='green')
        db_session.commit()        
    socket.setdefaulttimeout(old_timeout)
    db_session.commit()


def fetch_from_redmine(app):
    click.echo('Fetching from redmine')
    for redmine_infos in app.config.get('REDMINE_PROJECTS', []):
        project = redmine_infos.get('project')
        url = redmine_infos.get('url')
        username = redmine_infos.get('username')
        password = redmine_infos.get('password')
        click.secho('Fetching data from "{0}"'.format(url))
        try:
            tickets = requests.get(
                url,
                auth=HTTPBasicAuth(username, password),
                timeout=10)
        except Timeout:
            click.secho(u'  \U00002757 Timeout. Skipped.', fg='yellow')
            continue
        for ticket in tickets:
            new_ticket = Ticket(
                ticket_id=ticket.get('id'),
                title=ticket.get('summary'),
                status=ticket.get('status'),
                owner=ticket.get('owner'),
                project=project
            )
            db_session.add(new_ticket)
        click.secho('  ✔ done', fg='green')
    db_session.commit()

@click.command('fetch-tickets')
@with_appcontext
def fetch_tickets_command():
    """
    """
    app = _app_ctx_stack.top.app
    click.echo('Start fetching tickets.')
    fetch_from_trac(app)
    fetch_from_redmine(app)
    db_session.commit()
        


def init_app_fetcher(app):
    app.cli.add_command(fetch_tickets_command)