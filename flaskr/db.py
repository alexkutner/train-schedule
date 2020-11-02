import os
import socket
import threading
import time

import rocksdb
import click
from flask import current_app, g
from flask.cli import with_appcontext

ENCODING = 'utf_8'
LOCK_KEY = "lock_key"

# global db object.  I wanted to use flash app state but there was a rough stack trace that I couldn't figure out
g_db = None

def get_db():
    global g_db
    if not g_db:
        g_db = rocksdb.DB(current_app.config['DATABASE'],
                          rocksdb.Options(create_if_missing=True))

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


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def set(key, value_as_bytes):
    key_as_bytes = key.encode(ENCODING)
    db = get_db()
    if value_as_bytes is None:
        db.delete(key_as_bytes)
    else:
        db.put(key_as_bytes, value_as_bytes)


def fetch(key):
    value_as_json = None
    key_as_bytes = key.encode(ENCODING)
    db = get_db()
    return db.get(key_as_bytes)


def keys():
    db = get_db()
    it = db.iterkeys()
    it.seek_to_first()
    return [a.decode(ENCODING) for a in it]


def unlock_db():
    set(LOCK_KEY, None)


def lock_db(depth=0):
    # I don't think this could ever happen but want to avoid blowing out the stack and just give up
    if depth > 3:
        return False

    unique_id = "host={} process={} thread={}".format(socket.gethostname(), os.getpid(), threading.get_ident())

    # first make sure someone else has not locked the shared key
    current_lock_value = fetch(LOCK_KEY)
    while current_lock_value is not None:  # do an exp check here
        time.sleep(.05)  # sleep 50 ms and try again
        current_lock_value = fetch(LOCK_KEY)

    # write our lock
    set(LOCK_KEY, unique_id.encode(ENCODING))

    # sleep to make sure other writers settle and we see who claimed the lock.  Newcomers should block in the loop above
    # this should be turned off in test mode
    time.sleep(.05)

    # check to see if we got the lock.  If not recurse a few times and then give up?  Great place for a warning log or
    # dead letter workflow
    current_lock_value = fetch(LOCK_KEY)
    if current_lock_value.decode(ENCODING) != unique_id:
        return lock_db(depth=depth+1)
    return True