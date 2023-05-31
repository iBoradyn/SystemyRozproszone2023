import os

import click
import psycopg2
import psycopg2.extras
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.environ['DATABASE_HOST'],
            port=os.environ['DATABASE_PORT'],
            database=os.environ['DATABASE_NAME'],
            user=os.environ['DATABASE_USER'],
            password=os.environ['DATABASE_PASSWORD'],
        )

    return g.db


def get_cur():
    db = get_db()

    return db.cursor(cursor_factory=psycopg2.extras.DictCursor)


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    cur = get_cur()

    with current_app.open_resource('schema.sql') as f:
        cur.execute(f.read().decode('utf8'))
        db.commit()

    cur.close()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
