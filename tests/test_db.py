import pytest
from datetime import datetime, timedelta
import flaskr.db as db


def test_add(app):
    db.set("test_key", b"test_data_range")
    value = db.fetch("test_key")
    assert value == b"test_data_range"

def test_locks(app):
    assert not db.is_currently_locked_by_someone_else()
    db.set(db.LOCK_KEY, 'blabla|{}'.format(datetime.now().strftime(db.LOCK_TIME_ENCODING)).encode(db.ENCODING))
    assert db.is_currently_locked_by_someone_else()


def test_expired_lock(app):
    expired_lock_time = datetime.now() - timedelta(minutes=30)
    db.set(db.LOCK_KEY, 'blabla|{}'.format(expired_lock_time.strftime(db.LOCK_TIME_ENCODING)).encode(db.ENCODING))
    assert not db.is_currently_locked_by_someone_else()
