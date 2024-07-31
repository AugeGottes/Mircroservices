from sqlalchemy.orm import Session
from app.models import Chatroom
import math


class ChatroomService:
    @staticmethod
    def create_chatroom(db: Session, chatroom_data: dict):
        try:
            new_chatroom = Chatroom(**chatroom_data)
            db.add(new_chatroom)
            db.commit()
            db.refresh(new_chatroom)
            
            return new_chatroom.to_dict(), None
        except Exception as e:
            db.rollback()
            return None, str(e)

    @staticmethod
    def get_chatrooms(db: Session, page: int, per_page: int, sort_by: str, sort_order: str):
        try:
            query = db.query(Chatroom)
            
            if sort_order == 'desc':
                query = query.order_by(getattr(Chatroom, sort_by).desc())
            else:
                query = query.order_by(getattr(Chatroom, sort_by))
            
            total = query.count()
            pages = math.ceil(total / per_page)
            chatrooms = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'items': [chatroom.to_dict() for chatroom in chatrooms],
                'total': total,
                'page': page,
                'pages': pages,
                'per_page': per_page
            }, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_chatroom(db: Session, chatroom_id: int):
        try:
            chatroom = db.query(Chatroom).get(chatroom_id)
            return chatroom.to_dict() if chatroom else None, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def update_chatroom(db: Session, chatroom_id: int, data: dict):
        try:
            chatroom = db.query(Chatroom).get(chatroom_id)
            if chatroom:
                for key, value in data.items():
                    setattr(chatroom, key, value)
                db.commit()
                return chatroom.to_dict(), None
            return None, None
        except Exception as e:
            db.rollback()
            return None, str(e)

    @staticmethod
    def delete_chatroom(db: Session, chatroom_id: int):
        try:
            chatroom = db.query(Chatroom).get(chatroom_id)
            if chatroom:
                db.delete(chatroom)
                db.commit()
                return True, None
            return False, None
        except Exception as e:
            db.rollback()
            return False, str(e)