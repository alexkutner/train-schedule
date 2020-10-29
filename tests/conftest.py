import os
import tempfile
import shutil

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db


@pytest.fixture
def app():
    db_path = tempfile.mkdtemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': os.path.join(db_path, "tempdb")
    })

    with app.app_context():
        init_db()

    yield app
    shutil.rmtree(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
