import rocksdb
import json
import click
from flask import current_app, g
from flask.cli import with_appcontext

ENCODING = 'utf_8'
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
    it = db.iterkeys()
    it.seek_to_first()
    for key in it:
        db.delete(key)

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
    key_as_bytes = key.encode(ENCODING)
    value_as_bytes = json.dumps(value).encode(ENCODING)

    db = get_db()
    db.put(key_as_bytes, value_as_bytes)

def fetch(key):
    value_as_json = None
    key_as_bytes = key.encode(ENCODING)
    db = get_db()
    value_as_bytes = db.get(key_as_bytes)
    if value_as_bytes:
        value_as_json = json.loads(value_as_bytes.decode(ENCODING))

    return value_as_json


def keys():
    db = get_db()
    it = db.iterkeys()
    it.seek_to_first()

    return [a.decode(ENCODING) for a in it]
