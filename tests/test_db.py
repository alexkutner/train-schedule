import pytest

import flaskr.db as db


def test_add(app):
    db.set("test_key", {"test_name":"test_value"})
    value = db.fetch("test_key")
    assert value["test_name"] == "test_value"
