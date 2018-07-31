
from flask.cli import with_appcontext
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,
                            backref)
from sqlalchemy.ext.declarative import declarative_base

import click


engine = create_engine('sqlite:///scheduler.sqlite3', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
# We will need this for querying
Base.query = db_session.query_property()


def close_db(e=None):
    db_session.remove()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    from .models import Ticket
    Base.metadata.create_all(bind=engine)


@click.command('clean-db')
@with_appcontext
def clean_db_command():
    for table in engine.table_names():
        click.secho(
            'Clear table {0}'.format(table),
            fg='yellow'
        )
        db_session.execute('DELETE from {0}'.format(table))
    db_session.commit()


def init_app_db(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(clean_db_command)
