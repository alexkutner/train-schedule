import json
import datetime as dt
from datetime import timedelta

import pytest
import flaskr

TIME_FORMAT = '%I:%M %p'


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
    assert data['times'][0] == '09:45 AM'

    response = client.get('/routes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['routes']) == 1


def test_add_route_out_of_order(client, app):
    response = client.post('/routes/H1B2',
                           json={"times":["9:45 AM", "5:45 AM", "2:45 AM", "7:45 PM"]})
    assert response.status_code == 201

    response = client.get('/routes/H1B2')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['times']) == 4
    assert data['times'][0] == '02:45 AM'
    assert data['times'][1] == '05:45 AM'


def test_add_route_with_invalid_time(client, app):
    response = client.post('/routes/H1B2',
                           json={"times":["9:45 AM", "bacon", "eggs", "7:45 PM"]})
    assert response.status_code == 400


def test_missing_route(client, app):
    response = client.get('/routes/H1B2')
    assert response.status_code == 404


def test_add_route_with_long_name(client, app):
    response = client.post('/routes/a_name_longer_then_4_chars',
                           json={"times":["9:45 AM"]})
    assert response.status_code == 400


def test_concurrent_routes(client, app):
    response = client.post('/routes/H1B2',
                           json={"times": ["9:45 AM"]})
    assert response.status_code == 201
    response = client.post('/routes/J',
                           json={"times": ["9:45 AM"]})
    assert response.status_code == 201

    response = client.get('/routes/next_concurrent_trains?time=9:40%20AM')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['time'] == '09:45 AM'


def test_empty_routes(client, app):
    response = client.post('/routes/H1B2',
                           json={"times": ["9:45 AM"]})
    assert response.status_code == 201
    response = client.post('/routes/J',
                           json={"times": ["9:46 AM"]})
    assert response.status_code == 201

    response = client.get('/routes/next_concurrent_trains?time=9:40%20AM')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['time'] == None

def test_bad_time_for_concurrent_lookup(client, app):
    response = client.get('/routes/next_concurrent_trains?time=hamburger')
    assert response.status_code == 400


def test_several_routes(client, app):
    curr_time = dt.time(4,0,0)
    times = []
    while curr_time.hour<23:
        times.append(curr_time.strftime(TIME_FORMAT))
        curr_time = (dt.datetime.combine(dt.date(1, 1, 1), curr_time)+timedelta(minutes=12)).time()

    response = client.post('/routes/H1B2',
                           json={"times": times})
    assert response.status_code == 201

    curr_time = dt.time(4,4 ,0)
    times = []
    while curr_time.hour<23:
        times.append(curr_time.strftime(TIME_FORMAT))
        curr_time = (dt.datetime.combine(dt.date(1, 1, 1), curr_time)+timedelta(minutes=20)).time()

    response = client.post('/routes/J',
                           json={"times": times})
    assert response.status_code == 201

    curr_time = dt.time(4, 1, 0)
    times = []
    while curr_time.hour < 23:
        times.append(curr_time.strftime(TIME_FORMAT))
        curr_time = (dt.datetime.combine(dt.date(1, 1, 1), curr_time) + timedelta(minutes=13)).time()

    response = client.post('/routes/Q',
                           json={"times": times})
    assert response.status_code == 201

    response = client.get('/routes/next_concurrent_trains?time=9:40%20AM')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['time'] == '10:24 AM'


# test bad formated times
# test times out of order if they get sorted
# test bad time or missing time arg for concurrent
