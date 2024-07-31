from flask import Blueprint, request, jsonify
from app.services.tenant import TenantService

tenant_bp = Blueprint('tenants', __name__)


@tenant_bp.route('/api/tenants', methods=['POST'])
def create_tenant():
    data = request.json
    if 'name' not in data or 'db_name' not in data:
        return jsonify({"error": "Both 'name' and 'db_name' are required"}), 400

    result = TenantService.create_tenant(data['name'], data['db_name'],data['password'])
    if isinstance(result, tuple):
        tenant, error = result
        if tenant:
            return jsonify({
                'id': tenant.id,
                'name': tenant.name,
                'db_name': tenant.db_name,
                'db_file': f"{tenant.id}.db"
            }), 201
        else:
            return jsonify({"error": error}), 400
    else:
        return jsonify({"error": "Unexpected result from TenantService"}), 500
