import sqlite3
import rocksdb
import click
from flask import current_app, g
from flask.cli import with_appcontext
g_db = None

def get_db():
    global g_db
    #if 'db' not in g:
    if not g_db:
        g_db = rocksdb.DB(current_app.config['DATABASE'],
                          rocksdb.Options(create_if_missing=True))
        #g.db = sqlite3.connect(
        #    current_app.config['DATABASE'] ,
        #    detect_types=sqlite3.PARSE_DECLTYPES
        #)
        #g.db.row_factory = sqlite3.Row

    return g_db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    #for key in db.iterkeys():
    #    db.delete(key)

    #with current_app.open_resource('schema.sql') as f:
    #    db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def set(key, value):
    db = get_db()
    db.put(key, value)

def fetch(key):
    db = get_db()
    return db.get(key)

def keys():
    db = get_db()
    return [a for a in db.keys.iterkeys()]
