# -*- coding: UTF-8 -*-
from scheduler.db import db_session
from scheduler.models import Ticket
from urllib.parse import urlparse
from xmlrpc import client as xmlrpc_client

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
            project=project,
            created_date=ticket.get('time'),
            modified_date=ticket.get('changetime'),
            priority=ticket.get('priority_value')
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


def generate_server(infos):
    trac_url = infos.get('url')
    parsed_url = urlparse(trac_url)
    username = infos.get('username')
    password = infos.get('password')
    xmlrpc_url = '{scheme}://{username}:{password}@{netloc}{path}/login/xmlrpc'.format(  # noqa
        scheme=parsed_url.scheme,
        username=username,
        password=password,
        netloc=parsed_url.netloc,
        path=parsed_url.path
    )
    return xmlrpc_client.ServerProxy(xmlrpc_url, use_builtin_types=True)


def fetch_tickets(app):
    """
    Call trac endpoints.
    """
    click.echo('Fetching from trac')
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(10)
    for trac in app.config.get('TRAC_PROJECTS', []):
        project = trac.get('project')
        click.echo('Fetching data from "{0}"'.format(trac.get('url')))
        server = generate_server(trac)
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
