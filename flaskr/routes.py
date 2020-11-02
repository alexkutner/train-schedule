import json
from flask import Blueprint, Response, request
from time import strftime
from . import db
from .concurrent_trains import find_next_concurrent_trains, build_concurrent_train_list, convert_string_to_time, convert_times_to_native_time_objects

TIME_FORMAT = '%I:%M %p'
bp = Blueprint('routes', __name__)
ENCODING = 'utf_8'

CONCURRENT_KEY = "concurrent_key"

@bp.route('/routes/<key>', methods=['POST'])
def add_route(key):
    # limit the length of key's to 4
    if len(key) > 4:
        return Response(status=400)
    body = request.get_json()
    try:
        native_times = convert_times_to_native_time_objects(body['times'])
    except ValueError:
        # if we can't parse the time return an error
        return Response(status=400)

    native_times.sort()
    body['times'] = [strftime(TIME_FORMAT, a) for a in native_times]
    value_as_bytes = json.dumps(body).encode(ENCODING)

    db.set(key, value_as_bytes)

    #lock db for lookup write
    if db.lock_db():
        # build up train list
        concurrent_train_times = build_concurrent_train_list()
        concurrent_train_times_in_bytes = b""
        for t in concurrent_train_times:
            concurrent_train_times_in_bytes += t.to_bytes(2, "big")
        db.set(CONCURRENT_KEY, concurrent_train_times_in_bytes)
        db.unlock_db()

    return Response({'status': 'success'}, mimetype="application/json", status=201)


@bp.route('/routes/<key>', methods=['GET'])
def get_route(key):
    route_list = db.fetch(key)
    if not route_list:
        return Response(status=404)
    value_as_json = json.loads(route_list.decode(ENCODING))

    return value_as_json


@bp.route('/routes')
def get_list_of_routes():
    keys = db.keys()
    keys = [key for key in keys if len(key) < 5]
    return {"routes": keys}


@bp.route('/routes/next_concurrent_trains')
def next_concurrent_trains():
    time_param = request.args.get('time', None)
    if not time_param:
        # if no time param exists return 400.
        return Response(status=400)
    try:
        time_object = convert_string_to_time(time_param)
    except ValueError:
        # if we can't parse the time return an error
        return Response(status=400)

    concurrent_train_times = load_concurrent_train_times()
    next_time = find_next_concurrent_trains(concurrent_train_times, time_object)
    if next_time:
        return_value = strftime(TIME_FORMAT, next_time)
    else:
        return_value = None
    return {'time': return_value}


def load_concurrent_train_times():
    encoded_train_times = db.fetch(CONCURRENT_KEY)
    concurrent_train_times = []
    for x in range(0, len(encoded_train_times), 2):
        concurrent_train_times.append(int.from_bytes((encoded_train_times[x], encoded_train_times[x + 1]), 'big'))
    return concurrent_train_times



