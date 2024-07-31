import os
import sys
from flask import Flask
from flask_migrate import Migrate
from app.models import Tenant
from app.extensions import db
from app.config import Config


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

def run_migrations():
    with app.app_context():

        if not os.path.exists(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')):
            db.create_all()

        os.makedirs(app.config['TENANT_DATABASE_DIR'], exist_ok=True)
        
        tenants = Tenant.query.all()
        for tenant in tenants:
            print(f"Migrating database for tenant: {tenant.name}")
            tenant_db_uri = Config.get_tenant_db_uri(tenant.name)
            app.config['SQLALCHEMY_DATABASE_URI'] = tenant_db_uri
            
     
            db.init_app(app)
            
            with app.app_context():
                upgrade_command = f'flask db upgrade'
                os.system(f'FLASK_APP={project_root}/run.py {upgrade_command}')

if __name__ == '__main__':
    run_migrations()