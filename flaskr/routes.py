from flask import Blueprint, Response, request
bp = Blueprint('routes',__name__)

@bp.route('/routes/<id>', methods=['POST'])
def add_route(id):
    body = request.get_json()
    print(body)
    return Response({'status':'success'}, mimetype="application/json", status=200)
    

@bp.route('/routes/<id>', methods=['GET'])
def get_route(id):
    return {"name":"ABC","times":['9:30AM','12:00PM']}


@bp.route('/routes')
def get_list_of_routes():
    return {"routes":[]}


