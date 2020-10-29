from flask import Blueprint, Response, request
from time import strftime
from . import db
from .concurrent_trains import find_next_concurrent_trains, build_concurrent_train_list

TIME_FORMAT = '%I:%M %p'
bp = Blueprint('routes',__name__)


@bp.route('/routes/<id>', methods=['POST'])
def add_route(id):
    # limit the lenght of key's to 4
    if(len(id)> 4):
        return Response(status=400)
    body = request.get_json()
    db.set(id, body)
    return Response({'status': 'success'}, mimetype="application/json", status=201)
    

@bp.route('/routes/<id>', methods=['GET'])
def get_route(id):
    route_list = db.fetch(id)
    if not route_list:
        return Response(status=404)
    return route_list


@bp.route('/routes')
def get_list_of_routes():
    keys = db.keys()
    return {"routes": keys}


@bp.route('/routes/next_concurrent_trains')
def next_concurrent_trains():
    time = request.args.get('time', '')
    concurrent_train_times = build_concurrent_train_list()
    next_time = find_next_concurrent_trains(concurrent_train_times, time)
    if next_time:
        return_value = strftime(TIME_FORMAT, next_time)
    else:
        return_value = None
    return {'time': return_value}


