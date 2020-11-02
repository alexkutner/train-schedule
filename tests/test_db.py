import pytest

import flaskr.db as db


def test_add(app):
    db.set("test_key", b"test_data_range")
    value = db.fetch("test_key")
    assert value == b"test_data_range"
