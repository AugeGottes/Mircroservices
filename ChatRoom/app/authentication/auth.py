from app.extensions import db
from app.models import Tenant
from flask_httpauth import HTTPBasicAuth
from flask import g

auth=HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    tenant=Tenant.query.filter_by(name=username).first()
    if tenant and tenant.password==password:
        g.tenant_id=tenant.id
        return True
    return False