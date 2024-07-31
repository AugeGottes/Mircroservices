from flask import current_app
from app.extensions import db
from app.config import Config

def bind_db_for_tenant(tenant):
    db_uri = Config.get_tenant_db_uri(tenant.name)
    current_app.config['SQLALCHEMY_BINDS'] = {tenant.name: db_uri}
    db.get_engine(current_app, bind=tenant.name)