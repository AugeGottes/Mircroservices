from sqlalchemy.orm import Session
from app.models import ChatroomUser, User
import math
import uuid


class ChatroomUserService:
    @staticmethod
    def add_user_to_chatroom(db: Session, chatroom_id: int, user_id: int, role: str = 'member'):
        try:
            chatroom_user = ChatroomUser(
                id=str(uuid.uuid4()),
                user_id=user_id,
                chatroom_id=chatroom_id,
                role=role
            )
            db.add(chatroom_user)
            db.commit()
            db.refresh(chatroom_user)

            return chatroom_user.to_dict(), None
        except Exception as e:
            db.rollback()
            return None, str(e)

    @staticmethod
    def get_users_in_chatroom(db: Session, chatroom_id: int, page: int, per_page: int, sort_by: str, sort_order: str, name: str = None):
        try:
            query = db.query(ChatroomUser).filter_by(chatroom_id=chatroom_id)

            if name:
                query = query.join(User).filter(User.username.ilike(f'%{name}%'))

            if sort_by == 'username':
                sort_column = User.username
            else:
                sort_column = ChatroomUser.joined_at

            if sort_order == 'asc':
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

            total = query.count()
            chatroom_users = query.offset((page - 1) * per_page).limit(per_page).all()

            return {
                'total_count': total,
                'total_pages': math.ceil(total / per_page),
                'current_page': page,
                'users': [item.to_dict() for item in chatroom_users]
            }, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def remove_user_from_chatroom(db: Session, chatroom_id: int, user_id: int):
        try:
            chatroom_user = db.query(ChatroomUser).filter_by(chatroom_id=chatroom_id, user_id=user_id).first()
            if chatroom_user:
                db.delete(chatroom_user)
                db.commit()
                return True, None
            return False, "User not found in chatroom"
        except Exception as e:
            db.rollback()
            return False, str(e)