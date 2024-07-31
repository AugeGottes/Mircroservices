from flask import Blueprint, request, jsonify
from app.services.chatroom import ChatroomService
from app.services.chatroom_user import ChatroomUserService
from app.services.message import MessageService
from werkzeug.exceptions import BadRequest, NotFound
import uuid
from flask import g
from app.authentication.auth import auth


bp = Blueprint('chatrooms', __name__)

def generate_error_id():
    return str(uuid.uuid4())

@bp.route('/api/chatrooms', methods=['POST'])
def create_chatroom():
    tenant_id=int(g.tenant_id)
    data = request.json
    if 'name' not in data:
        return jsonify({"error": "Missing required field: name"}), 400

    result, error = ChatroomService.create_chatroom(int(tenant_id), data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(result.to_dict()), 201

@bp.route('/api/chatrooms', methods=['GET'])
def get_chatrooms():
    tenant_id=int(g.tenant_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pagesize', 10, type=int)
    sort_by = request.args.get('sortby', 'created_at')
    sort_order = request.args.get('sortorder', 'desc')

    chatrooms, error = ChatroomService.get_chatrooms(int(tenant_id), page, per_page, sort_by, sort_order)

    if error:
        return jsonify({"error": error}), 400
    if not chatrooms:
        raise NotFound("No chatrooms found")
    return jsonify(chatrooms.to_dict()), 200

@bp.route('/api/chatrooms/<int:chatroom_id>', methods=['GET'])
def get_chatroom(chatroom_id):
    tenant_id=int(g.tenant_id)
    chatroom, error = ChatroomService.get_chatroom(int(tenant_id), chatroom_id)
    if error:
        return jsonify({"error": error}), 400
    if not chatroom:
        raise NotFound("Chatroom with particular ID found")
    return jsonify(chatroom), 200

@bp.route('/api/chatrooms/<int:chatroom_id>', methods=['PUT'])
def update_chatroom(chatroom_id):
    tenant_id=int(g.tenant_id)
    data = request.json
    updated_chatroom, error = ChatroomService.update_chatroom(int(tenant_id), chatroom_id, data)
    if error:
        return jsonify({"error": error}), 400
    if not updated_chatroom:
        raise NotFound("Chatroom with particular ID not found")
    return jsonify(updated_chatroom), 200

@bp.route('/api/chatrooms/<int:chatroom_id>', methods=['DELETE'])
def delete_chatroom(chatroom_id):
    tenant_id=int(g.tenant_id)
    success, error = ChatroomService.delete_chatroom(int(tenant_id), chatroom_id)
    if error:
        return jsonify({"error": error}), 400
    if not success:
        return jsonify({"error": "Chatroom not found"}), 404
    return '', 204

@bp.route('/api/chatrooms/<int:chatroom_id>/users', methods=['POST'])
@auth.login_required
def add_user_to_chatroom(chatroom_id):
    tenant_id=int(g.tenant_id)
    data = request.json
    user_id = data.get('user_id')
    role = data.get('role', 'member')

    result, error = ChatroomUserService.add_user_to_chatroom(int(tenant_id), chatroom_id, user_id, role)
    if error:
        raise BadRequest("Bad Request ")
    return jsonify(result), 201

@bp.route('/api/chatrooms/<int:chatroom_id>/users', methods=['GET'])
@auth.login_required
def get_users_in_chatroom(chatroom_id):
    tenant_id=int(g.tenant_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pagesize', 10, type=int)
    sort_by = request.args.get('sortby', 'joined_at')
    sort_order = request.args.get('sortorder', 'desc')
    name = request.args.get('name')

    result, error = ChatroomUserService.get_users_in_chatroom(int(tenant_id), chatroom_id, page, per_page, sort_by, sort_order, name)
    if error:
        return jsonify({"error": error}), 400
    if not result:
        raise NotFound("No users found in chatroom")
    return jsonify(result), 200

@bp.route('/api/chatrooms/<int:chatroom_id>/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
def remove_user_from_chatroom(chatroom_id, user_id):
    tenant_id=int(g.tenant_id)
    success, error = ChatroomUserService.remove_user_from_chatroom(int(tenant_id), chatroom_id, user_id)
    if error:
        return jsonify({"error": error}), 400
    if not success:
        return jsonify({"error": "User or Chatroom not found"}), 404
    return '', 204

@bp.route('/api/chatrooms/<int:chatroom_id>/messages', methods=['POST'])
@auth.login_required
def send_message(chatroom_id):
    tenant_id=int(g.tenant_id)
    data = request.json
    user_id = data.get('user_id')
    content = data.get('content')

    result, error = MessageService.send_message(int(tenant_id), chatroom_id, user_id, content)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(result), 201

@bp.route('/api/chatrooms/<int:chatroom_id>/messages', methods=['GET'])
@auth.login_required
def get_messages(chatroom_id):
    tenant_id=int(g.tenant_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pagesize', 10, type=int)
    sort_by = request.args.get('sortby', 'timestamp')
    sort_order = request.args.get('sortorder', 'desc')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search')

    result, error = MessageService.get_messages(int(tenant_id), chatroom_id, page, per_page, sort_by, sort_order, start_date, end_date, search)
    if error:
        return jsonify({"error": error}), 400
    if not result:
        raise NotFound("No messages found")
    return jsonify(result), 200

@bp.route('/api/users/<int:user_id>/messages', methods=['GET'])
@auth.login_required
def get_user_messages(user_id):
    tenant_id=int(g.tenant_id)
    if not tenant_id:
        return jsonify({"error": "In fetching the tenant session"}), 400

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('pagesize', 10, type=int)
    sort_by = request.args.get('sortby', 'timestamp')
    sort_order = request.args.get('sortorder', 'desc')

    result, error = MessageService.get_user_messages(int(tenant_id), user_id, page, per_page, sort_by, sort_order)
    if error:
        return jsonify({"error": error}), 400
    if not result:
        raise NotFound("No message found for user ")
    return jsonify(result), 200