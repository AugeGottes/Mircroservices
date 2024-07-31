import logging
import logging.config
import yaml
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from app.routes import chatroom, user
import os
from .extensions import db
import time
from flask_migrate import Migrate
from .schema import setup_graphql
from app.authentication.auth import auth

migrate = Migrate()
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)    

    os.makedirs(app.config['TENANT_DATABASE_DIR'], exist_ok=True)
    
    db.init_app(app)

    from app.routes.tenant import tenant_bp
    app.register_blueprint(tenant_bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(chatroom.bp)
    
    setup_graphql(app)

    configure_logging(app)    
    
    with app.app_context():
        db.create_all()

    return app


def configure_logging(app):
    log_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    @app.before_request
    def log_request_info():
        access_logger = logging.getLogger('access_logger')
        access_logger.info(f'{request.remote_addr} - - [{time.strftime("%d/%b/%Y:%H:%M:%S %z")}] '
                            f'"{request.method} {request.url} HTTP/{request.environ.get("SERVER_PROTOCOL")}" '
                            f'{request.content_length} -')

    @app.after_request
    def log_response_info(response):
        access_logger = logging.getLogger('access_logger')
        access_logger.info(f'{request.remote_addr} - - [{time.strftime("%d/%b/%Y:%H:%M:%S %z")}] '
                            f'"{request.method} {request.url} HTTP/{request.environ.get("SERVER_PROTOCOL")}" '
                            f'{response.status_code} {response.content_length}')
        return response
    
    debug_logger = logging.getLogger('debug_logger')
    debug_logger.setLevel(logging.DEBUG)
    debug_handler = logging.FileHandler(os.path.join(log_dir, 'debug.log'))
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    debug_handler.setFormatter(debug_formatter)
    debug_logger.addHandler(debug_handler)
    debug_logger.debug('Application startup')


    with open('logging.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    app.logger.info('Application startup')
    