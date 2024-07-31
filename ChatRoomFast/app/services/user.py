from sqlalchemy.orm import Session
from app.models import User
import math

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: dict):
        try:
            new_user = User(**user_data)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            return new_user.to_dict(), None
        except Exception as e:
            db.rollback()
            return None, str(e)

    @staticmethod
    def get_users(db: Session, page: int, per_page: int, sort_by: str, sort_order: str):
        try:
            query = db.query(User)
            
            if sort_order == 'desc':
                query = query.order_by(getattr(User, sort_by).desc())
            else:
                query = query.order_by(getattr(User, sort_by))
            
            total =  query.count()
            pages = math.ceil(total / per_page)
            users = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'items': [user.to_dict() for user in users],
                'total': total,
                'page': page,
                'pages': pages,
                'per_page': per_page
            }, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_user(db: Session, user_id: int):
        try:
            id=user_id
            user = db.query(User).get(id)
            return user.to_dict() if user else None, None
        
        except Exception as e:
            return None, str(e)

    @staticmethod
    def update_user(db: Session, user_id: int, data: dict):
        try:
            user = db.query(User).get(user_id)
            if user:
                for key, value in data.items():
                    setattr(user, key, value)
                db.commit()
                return user.to_dict(), None
            return None, None
        except Exception as e:
            db.rollback()
            return None, str(e)

    @staticmethod
    def delete_user(db: Session, user_id: int):
        try:
            user = db.query(User).get(user_id)
            if user:
                db.delete(user)
                db.commit()
                return True, None
            return False, None
        except Exception as e:
            db.rollback()
            return False, str(e)