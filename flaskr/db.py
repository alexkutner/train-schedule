from datetime import datetime, timedelta
import os
import socket
import threading
import time

import rocksdb
import click
from flask import current_app, g
from flask.cli import with_appcontext

VALID_LOCK_MINUTES = 5

ENCODING = 'utf_8'
LOCK_KEY = "lock_key"
LOCK_TIME_ENCODING = "%Y %m %d %H:%M:%S"

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

    locking_value =  generate_unique_identity() + "|{}".format(datetime.now().strftime(LOCK_TIME_ENCODING))

    # first make sure someone else has not locked the shared key
    counter = 0
    while is_currently_locked_by_someone_else():  # do an exp check here
        time.sleep(.05)  # sleep 50 ms and try again
        counter += 1
        if counter > 200:
            # if we can't get a lock in 10s we'll give up
            return False

    # write our lock
    set(LOCK_KEY, locking_value.encode(ENCODING))

    # sleep to make sure other writers settle and we see who claimed the lock.  Newcomers should block in the loop above
    # this should be turned off in test mode
    time.sleep(.05)

    # check to see if we got the lock.  If not recurse a few times and then give up?  Great place for a warning log or
    # dead letter workflow
    if is_currently_locked_by_someone_else():
        return lock_db(depth=depth+1)
    return True


def is_currently_locked_by_someone_else():
    unique_id = generate_unique_identity()

    current_lock_value = fetch(LOCK_KEY)
    # if there is no lock then it's not locked
    if current_lock_value is None:
        return False

    decoded_lock_value, lock_time = current_lock_value.decode(ENCODING).split('|')
    # if it is our lock then it's ours
    if decoded_lock_value == unique_id:
        return False

    lock_time = datetime.strptime(lock_time, LOCK_TIME_ENCODING)
    # if the time is expired then int's not valid
    if lock_time + timedelta(minutes=VALID_LOCK_MINUTES) < datetime.now():
        return False

    return True


def generate_unique_identity():
    return "host={} process={} thread={}".format(socket.gethostname(), os.getpid(), threading.get_ident())