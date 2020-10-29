from flask import Blueprint, Response, request
from . import db
bp = Blueprint('routes',__name__)


@bp.route('/routes/<id>', methods=['POST'])
def add_route(id):
    body = request.get_json()
    print(body)
    db.set(id, body)
    return Response({'status': 'success'}, mimetype="application/json", status=200)
    

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


