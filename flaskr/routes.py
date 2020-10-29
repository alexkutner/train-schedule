from flask import Blueprint, Response, request
from . import db
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
    return_value = find_next_concurrent_trains(time)

    return {'time': return_value}


def find_next_concurrent_trains(time):
    concurrent_train_times = build_concurrent_table()
    start = 0
    end = len(concurrent_train_times)
    while start < end:
        mid = int(start + (start + end) / 2)
        if concurrent_train_times[mid] == time:
            return time
        elif concurrent_train_times[mid] < time:
            start = mid + 1
        else:
            end = mid
    return concurrent_train_times[mid]


# return a sorted list of times where multiple trains will be in the station at the same time
# The list is build by doing a sort of merge sort across all routes submitted
def build_concurrent_table():
    it = db.keys()
    schedules = list()
    for key in it:
        schedules.append(db.fetch(key)['times'])

    concurrent_list = []
    while len(schedules) > 1:
        popset = []
        min_val = None
        # move through sets looking for small non matches or groups of matches
        for i in range(0, len(schedules)):
            if not min_val or min_val > schedules[i][0]:
                popset = [i]
                min_val = schedules[i][0]
            elif min_val == schedules[i][0]:
                min_val == schedules[i][0]
                popset.append(i)

        # if we found a match copy it from the first schedule we saw it on
        if len(popset) > 1:
            concurrent_list.append(schedules[popset[0]][0])

        # remove smallest items in list
        deletion_adjuster = 0
        for i in popset:
            schedules[i-deletion_adjuster].pop(0)
            if len(schedules[i-deletion_adjuster]) == 0:
                schedules.pop(i-deletion_adjuster)
                deletion_adjuster += 1

        return concurrent_list


