import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TENANT_DATABASE_DIR = os.path.join(basedir, 'tenant_databases')
    
    @staticmethod
    def get_tenant_db_uri(tenant_name):
        return f'sqlite:///{os.path.join(Config.TENANT_DATABASE_DIR, f"{tenant_name}.db")}'