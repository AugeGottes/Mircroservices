from app.models import Message, Chatroom, User,Tenant
from ..extensions import db
import uuid
from datetime import datetime
from app.services.tenant import TenantService


class MessageInfo:
    def __init__(self, id: str, user_id: int, chatroom_id: int, tenant_id: int, timestamp: datetime, content: str):
        self.id = id
        self.user_id = user_id
        self.chatroom_id = chatroom_id
        self.tenant_id = tenant_id
        self.timestamp = timestamp
        self.content = content
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'chatroom_id': self.chatroom_id,
            'tenant_id': self.tenant_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'content': self.content
        }

class UserMessageInfo:
    def __init__(self, id: str, chatroom_id: int, chatroom_name: str, tenant_id: int, timestamp: datetime, content: str):
        self.id = id
        self.chatroom_id = chatroom_id
        self.chatroom_name = chatroom_name
        self.tenant_id = tenant_id
        self.timestamp = timestamp
        self.content = content
    
    def to_dict(self):
        return {
            'id': self.id,
            'chatroom_id': self.chatroom_id,
            'chatroom_name': self.chatroom_name,
            'tenant_id': self.tenant_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'content': self.content
        }

class MessageList:
    def __init__(self, total_count: int, total_pages: int, current_page: int, messages):
        self.total_count = total_count
        self.total_pages = total_pages
        self.current_page = current_page
        self.messages = messages


    def to_dict(self):
        return {
            'total_count': self.total_count,
            'total_pages': self.total_pages,
            'current_page': self.current_page,
            'messages': [message.to_dict() for message in self.messages]
        }
class MessageService:
    @staticmethod
    def send_message(tenant_id, chatroom_id, user_id, content):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            message = Message(
                id=str(uuid.uuid4()),
                user_id=user_id,
                chatroom_id=chatroom_id,
                content=content
            )
            session.add(message)
            session.commit()
            return MessageInfo(
                id=message.id,
                user_id=message.user_id,
                chatroom_id=message.chatroom_id,
                tenant_id=tenant_id,
                timestamp=message.timestamp,
                content=message.content
            ), None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def get_messages(tenant_id, chatroom_id, page, per_page, sort_by, sort_order, start_date=None, end_date=None, search=None):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            query = session.query(Message).filter_by(chatroom_id=chatroom_id)

            if start_date:
                query = query.filter(Message.timestamp >= datetime.fromisoformat(start_date))
            if end_date:
                query = query.filter(Message.timestamp <= datetime.fromisoformat(end_date))
            if search:
                query = query.filter(Message.content.ilike(f'%{search}%'))

            if sort_by == 'timestamp':
                sort_column = Message.timestamp
            elif sort_by == 'username':
                sort_column = User.username
            else:
                sort_column = Message.timestamp

            if sort_order == 'asc':
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

            total = query.count()
            messages = query.offset((page - 1) * per_page).limit(per_page).all()

            return MessageList(
                total_count=total,
                total_pages=(total + per_page - 1) // per_page,
                current_page=page,
                messages=[MessageInfo(
                    id=str(message.id),
                    user_id=message.user_id,
                    chatroom_id=message.chatroom_id,
                    tenant_id=tenant_id,
                    timestamp=message.timestamp,
                    content=message.content
                ) for message in messages]
            ), None
        except Exception as e:
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def get_user_messages(tenant_id, user_id, page, per_page, sort_by, sort_order):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            query = session.query(Message).filter_by(user_id=user_id)

            if sort_by == 'timestamp':
                sort_column = Message.timestamp
            elif sort_by == 'chatroom':
                sort_column = Chatroom.name
            else:
                sort_column = Message.timestamp

            if sort_order == 'asc':
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

            total = query.count()
            messages = query.offset((page - 1) * per_page).limit(per_page).all()

            return MessageList(
                total_count=total,
                total_pages=(total + per_page - 1) // per_page,
                current_page=page,
                messages=[UserMessageInfo(
                    id=str(message.id),
                    chatroom_id=message.chatroom_id,
                    chatroom_name=session.query(Chatroom).get(message.chatroom_id).name,
                    tenant_id=tenant_id,
                    timestamp=message.timestamp,
                    content=message.content
                ) for message in messages]
            ), None
        except Exception as e:
            return None, str(e)
        finally:
            session.close()