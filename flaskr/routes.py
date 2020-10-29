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


