from flask import Blueprint, request, jsonify
from app.services.user import UserService
from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed, InternalServerError
from flask_httpauth import HTTPBasicAuth
import uuid
from app.authentication.auth import auth
from flask import g


bp = Blueprint('users', __name__)
@bp.route('/api/users', methods=['POST'])
def create_user():
    tenant_id=int(g.tenant_id)
    user_data = request.json
    result, error = UserService.create_user(int(tenant_id), user_data)
    
    if result:
        return jsonify(result), 201
    else:
        raise BadRequest(result)

@bp.route('/api/users', methods=['GET'])
def get_users():
    tenant_id=int(g.tenant_id)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pagesize', 10, type=int)
    sort_by = request.args.get('sortby', 'created_at')
    sort_order = request.args.get('sortorder', 'desc')

    users, error = UserService.get_users(int(tenant_id), page, per_page, sort_by, sort_order)

    if error:
        return jsonify({"error": str(error)}), 400
    if not users or not users['items']:
        raise NotFound("No  such users found")
    return jsonify(users), 200


@bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    tenant_id=int(g.tenant_id)
    tenant_id = getattr(g, 'tenant_id', None)

    user, error = UserService.get_user(int(tenant_id), user_id)
    if error:
        return jsonify({"error": str(error)}), 400
    if user is None:
       raise NotFound("User with the particular ID  not found")
    return jsonify(user), 200

@bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    tenant_id=int(g.tenant_id)
    data = request.json
    updated_user, error = UserService.update_user(int(tenant_id), user_id, data)
    if error:
        return jsonify({"error": str(error)}), 400
    if updated_user is None:
        raise 
    return jsonify(updated_user), 200

@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    tenant_id=int(g.tenant_id)
    success, error = UserService.delete_user(int(tenant_id), user_id)
    if error:
        return jsonify({"error": str(error)}), 400
    if not success:
        return jsonify({"error": "User not found"}), 404
    return '', 204