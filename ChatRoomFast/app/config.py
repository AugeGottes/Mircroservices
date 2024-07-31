import os

class Config:
    MAIN_DATABASE_URL = 'sqlite:///./main.db'
    TENANT_DATABASE_DIR = os.path.join(os.getcwd(), 'tenant_dbs')

config = Config()