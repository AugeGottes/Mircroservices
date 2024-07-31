from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.services.chatroom import ChatroomService
from app.services.chatroom_user import ChatroomUserService
import uuid
from app.services.message import MessageService
from ..dependencies import get_tenant_db
from .error_handler import NotFound,BadRequest
from pydantic import BaseModel


class ChatroomUserCreate(BaseModel):
    user_id: int
    role: str = "member"


class MessageCreate(BaseModel):
    user_id: int
    content: str



router = APIRouter()

def generate_error_id():
    return str(uuid.uuid4())

@router.post("/api/chatrooms", status_code=201)
def create_chatroom(chatroom_data: dict, db: Session = Depends(get_tenant_db)):
    new_chatroom, error = ChatroomService.create_chatroom(db, chatroom_data)
    if error:
        raise HTTPException(status_code=400, detail=str("There was an error creating the chatroom"))
    return new_chatroom

@router.get("/api/chatrooms")
def get_chatrooms(
    db: Session = Depends(get_tenant_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc")
):
    chatrooms, error = ChatroomService.get_chatrooms(db, page, per_page, sort_by, sort_order)
    if error:
        raise NotFound("No chatrooms found")
    return chatrooms

@router.get("/api/chatrooms/{chatroom_id}")
def get_chatroom(chatroom_id: int, db: Session = Depends(get_tenant_db)):
    chatroom, error = ChatroomService.get_chatroom(db, chatroom_id)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not chatroom:
        raise NotFound("Chatroom with particular ID not found")
    return chatroom

@router.put("/api/chatrooms/{chatroom_id}")
def update_chatroom(chatroom_id: int, chatroom_data: dict, db: Session = Depends(get_tenant_db)):
    updated_chatroom, error = ChatroomService.update_chatroom(db, chatroom_id, chatroom_data)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not updated_chatroom:
        raise NotFound("Chatroom with particular ID not found")
    return updated_chatroom

@router.delete("/api/chatrooms/{chatroom_id}", status_code=204)
def delete_chatroom(chatroom_id: int, db: Session = Depends(get_tenant_db)):
    success, error = ChatroomService.delete_chatroom(db, chatroom_id)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not success:
        raise NotFound("Chatroom with particular ID not found")
    

from app.dependencies import get_tenant_db



@router.post("/api/chatrooms/{chatroom_id}/users", status_code=201)
def add_user_to_chatroom(
    chatroom_id: int,
    user_data: ChatroomUserCreate,
    db: Session = Depends(get_tenant_db)
):
    new_chatroom_user, error = ChatroomUserService.add_user_to_chatroom(db, chatroom_id, user_data.user_id, user_data.role)
    if error:
        raise BadRequest("Bad Request ")
    return new_chatroom_user

@router.get("/api/chatrooms/{chatroom_id}/users")
def get_users_in_chatroom(
    chatroom_id: int,
    db: Session = Depends(get_tenant_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    sort_by: str = Query("joined_at"),
    sort_order: str = Query("desc"),
    name: str = Query(None)
):
    users, error = ChatroomUserService.get_users_in_chatroom(db, chatroom_id, page, per_page, sort_by, sort_order, name)
    if error:
        raise NotFound("No users found in chatroom")
    return users

@router.delete("/api/chatrooms/{chatroom_id}/users/{user_id}", status_code=204)
def remove_user_from_chatroom(chatroom_id: int, user_id: int, db: Session = Depends(get_tenant_db)):
    success, error = ChatroomUserService.remove_user_from_chatroom(db, chatroom_id, user_id)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if not success:
        raise HTTPException(status_code=404, detail="User not found in chatroom")
    


@router.post("/api/chatrooms/{chatroom_id}/messages", status_code=201)
def send_message(
    chatroom_id: int, 
    message: MessageCreate,
    db: Session = Depends(get_tenant_db)
):
    new_message, error = MessageService.send_message(db, chatroom_id, message.user_id, message.content)
    if error:
        raise NotFound("The requested data could not be found")
    return new_message

@router.get("/api/chatrooms/{chatroom_id}/messages")
def get_messages(
    chatroom_id: int,
    db: Session = Depends(get_tenant_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    sort_by: str = Query("timestamp"),
    sort_order: str = Query("desc"),
    start_date: str = Query(None),
    end_date: str = Query(None),
    search: str = Query(None)
):
    messages, error = MessageService.get_messages(db, chatroom_id, page, per_page, sort_by, sort_order, start_date, end_date, search)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    return messages

@router.get("/api/users/{user_id}/messages")
def get_user_messages(
    user_id: int,
    db: Session = Depends(get_tenant_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    sort_by: str = Query("timestamp"),
    sort_order: str = Query("desc")
):
    messages, error = MessageService.get_user_messages(db, user_id, page, per_page, sort_by, sort_order)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    return messages