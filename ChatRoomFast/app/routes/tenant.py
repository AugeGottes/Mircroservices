from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.tenant import TenantService
from ..database import get_main_db

router = APIRouter()

@router.post("/api/tenants", status_code=201)
def create_tenant(tenant_data: dict, db: Session = Depends(get_main_db)):
    name = tenant_data.get('name')
    db_name = tenant_data.get('db_name')
    password = tenant_data.get('password')
    if not name or not db_name or not password:
        raise HTTPException(status_code=400, detail="Name and db_name and password are required")
    
    new_tenant, error = TenantService.create_tenant(db, name, db_name,password)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    return new_tenant.to_dict()