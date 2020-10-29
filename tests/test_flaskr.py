import os
import json
import tempfile

import pytest

import flaskr 

"""
@pytest.fixture
def client():
    db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    flaskr.app.config['TESTING'] = True

    with flaskr.app.test_client() as client:
        with flaskr.app.app_context():
            flaskr.init_db()
        yield client

    os.close(db_fd)
    os.unlink(flaskr.app.config['DATABASE'])
"""

def test_empty_list(client, app):
    response = client.get('/routes') 
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['routes']) == 0

def test_add_route(client, app):
    response = client.post('/routes/H1B2',
                           json={"times":["9:45 AM"]})
    assert response.status_code == 200

    response = client.get('/routes/H1B2') 
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['times']) == 1
    assert data['times'][0] == '9:45 AM'
    

