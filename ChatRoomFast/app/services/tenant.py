import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from app.models import Base, Tenant
from app.config import Config
from ..database import get_main_db
import logging


class TenantService:
    @staticmethod
    def create_tenant(db: Session, name: str, db_name: str,password:str):
        try:
            new_tenant = Tenant(name=name, db_name=db_name,password=password)
            db.add(new_tenant)
            db.commit()
            db.refresh(new_tenant)

            # Create tenant database
            tenant_db_path = os.path.join(Config.TENANT_DATABASE_DIR, f"{new_tenant.id}.db")
            os.makedirs(os.path.dirname(tenant_db_path), exist_ok=True)
            engine = create_engine(f"sqlite:///{tenant_db_path}")
            Base.metadata.create_all(engine)

            return new_tenant, None
        except Exception as e:
            db.rollback()
            return None, str(e)

    @staticmethod
    def get_tenant_session(tenant_id: int):
        tenant_db_path = os.path.join(Config.TENANT_DATABASE_DIR, f"{tenant_id}.db")
        if not os.path.exists(tenant_db_path):
            return None

        engine = create_engine(f"sqlite:///{tenant_db_path}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()

    @staticmethod
    def get_tenant_engine(tenant_id: int):
        main_db = next(get_main_db())
        try:
            tenant = main_db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                raise ValueError(f"Tenant with id {tenant_id} not found")
            
            db_path = os.path.join('tenant_dbs', str(tenant.id), f"{tenant.db_name}.db")
            return create_engine(f"sqlite:///{db_path}")
        finally:
            main_db.close()
