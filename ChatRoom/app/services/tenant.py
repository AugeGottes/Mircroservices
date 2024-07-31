import os
from flask import Flask
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.models import Tenant, User, Chatroom, ChatroomUser, Message
from app.extensions import db
from app.config import Config


class TenantService:
    @staticmethod
    def create_tenant(name, db_name,password):
        try:
            new_tenant = Tenant(name=name, db_name=db_name,password=password)
            db.session.add(new_tenant)
            db.session.commit()

            db_path = os.path.join(Config.TENANT_DATABASE_DIR, f"{new_tenant.id}.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            engine = create_engine(f"sqlite:///{db_path}")
            TenantService.create_tables(engine)

            return new_tenant, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_tenant_session(tenant_id):
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return None

        db_path = os.path.join(Config.TENANT_DATABASE_DIR, f"{tenant.id}.db")
        engine = create_engine(f"sqlite:///{db_path}")
        TenantService.create_tables(engine)
        Session = sessionmaker(bind=engine)
        return Session()

    @staticmethod
    def create_tables(engine):
        inspector = inspect(engine)
        tables = [User.__table__, Chatroom.__table__, ChatroomUser.__table__, Message.__table__]
        for table in tables:
            if not inspector.has_table(table.name):
                table.create(engine)