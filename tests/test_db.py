import pytest

import flaskr.db as db


def test_add(app):
    db.set(b"test_key", b"test_value")
    value = db.fetch(b"test_key")
    assert value == b"test_value"
