from app.models import Chatroom
from ..extensions import db
import datetime 
from typing import List, Any, Optional
from app.services.tenant import TenantService


class ChatroomInfo:
    def __init__(self, id: int, name: str, description: str, created_at: datetime, modified_at: datetime):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.modified_at = modified_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None
        }


class ChatroomList:
    def __init__(self, total_count: int, total_pages: int, current_page: int, chatrooms: List[ChatroomInfo]):
        self.total_count = total_count
        self.total_pages = total_pages
        self.current_page = current_page
        self.chatrooms = chatrooms

        
    def to_dict(self):
        return {
            'total_count': self.total_count,
            'total_pages': self.total_pages,
            'current_page': self.current_page,
            'chatrooms': [chatroom.to_dict() for chatroom in self.chatrooms]
        }



class ChatroomService:
    @staticmethod
    def create_chatroom(tenant_id, chatroom_data):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            new_chatroom = Chatroom(
                name=chatroom_data['name'],
                description=chatroom_data.get('description', '')
            )
            session.add(new_chatroom)
            session.commit()
            
            return ChatroomInfo(
                id=new_chatroom.id,
                name=new_chatroom.name,
                description=new_chatroom.description,
                created_at=new_chatroom.created_at,
                modified_at=new_chatroom.modified_at
            ), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def get_chatrooms(tenant_id, page, per_page, sort_by, sort_order):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            query = session.query(Chatroom)
            if sort_order == 'desc':
                query = query.order_by((getattr(Chatroom, sort_by)))
            else:
                query = query.order_by(getattr(Chatroom, sort_by))

            total = query.count()
            chatrooms = query.offset((page - 1) * per_page).limit(per_page).all()

            return ChatroomList(
                total_count=total,
                total_pages=(total + per_page - 1) // per_page,
                current_page=page,
                chatrooms=[ChatroomInfo(
                    id=chatroom.id,
                    name=chatroom.name,
                    description=chatroom.description,
                    created_at=chatroom.created_at,
                    modified_at=chatroom.modified_at
                ) for chatroom in chatrooms]
            ), None
        except Exception as e:
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def get_chatroom(tenant_id, chatroom_id):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            chatroom = session.query(Chatroom).get(chatroom_id)
            if not chatroom:
                return None, "Chatroom not found"
            return ChatroomInfo(
                id=chatroom.id,
                name=chatroom.name,
                description=chatroom.description,
                created_at=chatroom.created_at,
                modified_at=chatroom.modified_at
            ), None
        except Exception as e:
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def update_chatroom(tenant_id, chatroom_id, data):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            chatroom = session.query(Chatroom).get(chatroom_id)
            if not chatroom:
                return None, "Chatroom not found"
            chatroom.name = data.get('name', chatroom.name)
            chatroom.description = data.get('description', chatroom.description)
            session.commit()

            return ChatroomInfo(
                id=chatroom.id,
                name=chatroom.name,
                description=chatroom.description,
                created_at=chatroom.created_at,
                modified_at=chatroom.modified_at
            ), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def delete_chatroom(tenant_id, chatroom_id):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return False, "Tenant not found"

        try:
            chatroom = session.query(Chatroom).get(chatroom_id)
            if not chatroom:
                return False, "Chatroom not found"
            session.delete(chatroom)
            session.commit()
            return True, None
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()