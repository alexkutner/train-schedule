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
    assert response.status_code == 201

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


def test_add_route_with_long_name(client, app):
    response = client.post('/routes/a_name_longer_then_4_chars',
                           json={"times":["9:45 AM"]})
    assert response.status_code == 400


def test_concurrent_routes(client, app):
    response = client.post('/routes/H1B2',
                           json={"times":["9:45 AM"]})
    assert response.status_code == 201
    response = client.post('/routes/J',
                           json={"times":["9:45 AM"]})
    assert response.status_code == 201

    response = client.get('/routes/next_concurrent_trains?time=9:40AM')
    assert response.status_code == 200
    print(response.data)
    data = json.loads(response.data)
    assert data['time'] == '9:45 AM'


# test bad formated times
# test times out of order if they get sorted
# test bad time or missing time arg for concurrent
