from fastapi import Header, HTTPException,Depends
from app.services.tenant import TenantService
from contextlib import asynccontextmanager
from app.authentication.auth import verify_credentials


# @asynccontextmanager
async def get_tenant_db(x_tenant_id: int = Depends(verify_credentials)):
    db = TenantService.get_tenant_session(x_tenant_id)
    if not db:
        raise HTTPException(status_code=400, detail=f"Invalid tenant ID or tenant database not found: {x_tenant_id}")
    try:
        yield db
    finally:
        db.close()