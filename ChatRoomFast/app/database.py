from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import Config
import logging

logger = logging.getLogger(__name__)

# Create the main database engine
main_engine = create_engine(Config.MAIN_DATABASE_URL, echo=True)

# Create a SessionLocal class
MainSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=main_engine)
Base = declarative_base()

# Dependency to get the main database session
def get_main_db():
    db = MainSessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_main_tables():
    from app.models import Tenant  # Important import don't delete it
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=main_engine)
   
    inspector = inspect(main_engine)
    tables = inspector.get_table_names()
    logger.info(f"Existing tables after creation: {tables}")
    
    if 'tenant' not in tables:
        logger.error("Tenant table was not created!")
        Tenant.__table__.create(main_engine)
        logger.info("Attempted to create tenant table directly")
        
        # Check again
        tables = inspector.get_table_names()
        logger.info(f"Existing tables after direct creation attempt: {tables}")
    
    logger.info("Tables creation process completed")