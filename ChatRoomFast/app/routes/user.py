from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.services.user import UserService
from ..dependencies import get_tenant_db
from .error_handler import BadRequest,NotFound
import uuid
from app.authentication.auth import verify_credentials

router = APIRouter()

def generate_error_id():
    return str(uuid.uuid4())


@router.post("/api/users", status_code=201)
def create_user(user_data: dict, 
                db: Session = Depends(get_tenant_db)):
    user_dict, error = UserService.create_user(db, user_data)
    if error:
        raise BadRequest(str(error))
    return user_dict

@router.get("/api/users")
def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_tenant_db),
):
    
    users, error =  UserService.get_users(db, page, per_page, sort_by, sort_order)
    if error:
        raise NotFound("No  such users found")
    return users

@router.get("/api/users/{user_id}")
def get_user(user_id: int,
                   db: Session = Depends(get_tenant_db)):
    
    user, error = UserService.get_user(db, user_id)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/api/users/{user_id}")
def update_user(user_id: int, user_data: dict, db: Session = Depends(get_tenant_db)):
    updated_user, error =  UserService.update_user(db, user_id, user_data)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not updated_user:
        raise NotFound("User with the particular ID  not found")
    return updated_user

@router.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_tenant_db)):
    success, error = UserService.delete_user(db, user_id)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not success:
        raise HTTPException(status_code=404, detail="User not found")