from flask import Blueprint, Response, request
from time import strftime
from . import db
from .concurrent_trains import find_next_concurrent_trains, build_concurrent_train_list, convert_string_to_time

TIME_FORMAT = '%I:%M %p'
bp = Blueprint('routes', __name__)


@bp.route('/routes/<key>', methods=['POST'])
def add_route(key):
    # limit the length of key's to 4
    if len(key) > 4:
        return Response(status=400)
    body = request.get_json()
    db.set(key, body)
    return Response({'status': 'success'}, mimetype="application/json", status=201)
    

@bp.route('/routes/<key>', methods=['GET'])
def get_route(key):
    route_list = db.fetch(key)
    if not route_list:
        return Response(status=404)
    return route_list


@bp.route('/routes')
def get_list_of_routes():
    keys = db.keys()
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

    # build up train list
    concurrent_train_times = build_concurrent_train_list()
    # search for next time
    next_time = find_next_concurrent_trains(concurrent_train_times, time_object)
    if next_time:
        return_value = strftime(TIME_FORMAT, next_time)
    else:
        return_value = None
    return {'time': return_value}


