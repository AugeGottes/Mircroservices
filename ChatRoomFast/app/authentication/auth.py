from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
import secrets
from fastapi import FastAPI,Depends,HTTPException
from ..models import Tenant
from sqlalchemy.orm import Session
from ..database import get_main_db
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_main_db)):
    tenant = db.query(Tenant).filter(Tenant.name == credentials.username).first()
    if not tenant:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect tenant name ",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    correct_password = secrets.compare_digest(credentials.password, tenant.password)
    if not correct_password:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect  password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return tenant.id