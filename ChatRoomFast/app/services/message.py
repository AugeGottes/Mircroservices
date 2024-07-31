from sqlalchemy.orm import Session
from app.models import Message, Chatroom, User
import math
import uuid
from datetime import datetime


class MessageService:
    @staticmethod
    def send_message(db: Session, chatroom_id: int, user_id: int, content: str):
        try:
            message = Message(
                id=str(uuid.uuid4()),
                user_id=user_id,
                chatroom_id=chatroom_id,
                content=content
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            return message.to_dict(), None
        except Exception as e:
            db.rollback()
            return None, str(e)

    @staticmethod
    def get_messages(db: Session, chatroom_id: int, page: int, per_page: int, sort_by: str, sort_order: str, start_date: str = None, end_date: str = None, search: str = None):
        try:
            query = db.query(Message).filter_by(chatroom_id=chatroom_id)

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

            return {
                'total_count': total,
                'total_pages': math.ceil(total / per_page),
                'current_page': page,
                'messages': [message.to_dict() for message in messages]
            }, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_user_messages(db: Session, user_id: int, page: int, per_page: int, sort_by: str, sort_order: str):
        try:
            query = db.query(Message).filter_by(user_id=user_id)

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
            messages =  query.offset((page - 1) * per_page).limit(per_page).all()

            return {
                'total_count': total,
                'total_pages': math.ceil(total / per_page),
                'current_page': page,
                'messages': [message.to_dict() for message in messages]
            }, None
        except Exception as e:
            return None, str(e)