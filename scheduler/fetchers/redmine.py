# -*- coding: UTF-8 -*-
from scheduler.db import db_session
from scheduler.models import Ticket
from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout

import requests
import click


def add_or_update_ticket(ticket, project):
    old_ticket = Ticket.query.filter_by(
        ticket_id=ticket['id'],
        project=project).first()
    status = ticket.get('status', {}) and ticket['status']['name'] or ''  # noqa
    owner = ticket.get('assigned_to', {}) and ticket['assigned_to']['name'] or ''  # noqa
    title = ticket.get('subject')
    if not old_ticket:
        click.echo(
            '    Created new ticket: #{0}.'.format(
                ticket.get('id')
            )
        )

        new_ticket = Ticket(
            ticket_id=ticket.get('id'),
            title=title,
            status=status,
            owner=owner,
            project=project
        )
        db_session.add(new_ticket)
    else:
        old_ticket.title = title
        old_ticket.status = status
        old_ticket.owner = owner


def update_closed_tickets(tickets, project):
    db_tickets = Ticket.query.filter(
        Ticket.status != 'closed',
        Ticket.project == project).all()
    ticket_ids = map(lambda x: x.get('id'), tickets)
    for ticket in db_tickets:
        if ticket.ticket_id not in ticket_ids:
            click.secho('    Ticket #{0} for {1} has been closed.'.format(
                ticket.ticket_id,
                project
            ), fg='yellow')
            ticket.status = 'closed'
    db_session.commit()


def call_redmine(redmine_infos, limit=100, offset=0):
    url = '{0}&limit={1}&offset={2}'.format(
        redmine_infos.get('url'),
        limit,
        offset
    )
    username = redmine_infos.get('username')
    password = redmine_infos.get('password')
    click.echo('Fetching data from "{0}"'.format(url))
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(username, password),
            timeout=10)
    except Timeout:
        click.secho(u'  \U00002757 Timeout. Skipped.', fg='yellow')
        return
    if not response.ok or response.status_code != 200:
        click.secho(
            u'  \U00002757 Error: [{0}]{1}'.format(
                response.status_code,
                response.reason),
            fg='red')
        return
    return response.json()


def fetch_tickets(app):
    click.echo('Fetching from redmine')
    for redmine_infos in app.config.get('REDMINE_PROJECTS', []):
        infos = call_redmine(redmine_infos=redmine_infos)
        tickets = infos.get('issues')
        while len(tickets) < infos.get('total_count'):
            recursive_infos = call_redmine(
                redmine_infos=redmine_infos,
                offset=len(tickets)
            )
            tickets.extend(recursive_infos.get('issues'))
        project = redmine_infos.get('project')
        for ticket in tickets:
            add_or_update_ticket(ticket, project)
        db_session.commit()
        click.secho('  ✔ done', fg='green')

        click.echo('- Syncing closed tickets')
        update_closed_tickets(tickets, project)
        click.secho('  ✔ done', fg='green')
        db_session.commit()
