import os
import json
import tempfile

import pytest
import flaskr 


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

    response = client.get('/routes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['routes']) == 1


def test_missing_route(client, app):
    response = client.get('/routes/H1B2')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['message']).contains('not found')