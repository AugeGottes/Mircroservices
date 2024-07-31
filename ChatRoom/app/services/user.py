from app.models import User,Tenant
from ..extensions import db
from typing import List, Optional
import datetime 
from app.services.tenant import TenantService
import math


class UserInfo:
    def __init__(self, id: int, username: str, email: str, mobile: Optional[str], created_at: datetime, modified_at: datetime):
        self.id = id
        self.username = username
        self.email = email
        self.mobile = mobile
        self.created_at = created_at
        self.modified_at = modified_at


class UserList:
    def __init__(self, total_count: int, total_pages: int, current_page: int, users: List[UserInfo]):
        self.total_count = total_count
        self.total_pages = total_pages
        self.current_page = current_page
        self.users = users


class UserService:
    @staticmethod
    def create_user(tenant_id, user_data):
        
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],  
                mobile=user_data.get('mobile')
            )
            session.add(new_user)
            session.commit()
            
            user = {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'mobile': new_user.mobile,
                'created_at': new_user.created_at.isoformat() if new_user.created_at else None,
                'modified_at': new_user.modified_at.isoformat() if new_user.modified_at else None
            }
            
            return user, None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()
    

    @staticmethod
    def get_users(tenant_id, page, per_page, sort_by, sort_order):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            query = session.query(User)
            if sort_order == 'desc':
                query = query.order_by((getattr(User, sort_by)))
            else:
                query = query.order_by(getattr(User, sort_by))
            total = query.count()
            pages = math.ceil(total / per_page)
            query = query.offset((page - 1) * per_page).limit(per_page)
            
            users = query.all()
            
            return {
                'items': [user.to_dict() for user in users],
                'total': total,
                'page': page,
                'pages': pages,
                'per_page': per_page
            }, None
        except Exception as e:
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def get_user(tenant_id, user_id):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            user = session.query(User).get(user_id)
            return user.to_dict() if user else None, None
        except Exception as e:
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def update_user(tenant_id, user_id, data):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            user = session.query(User).get(user_id)
            if user:
                for key, value in data.items():
                    setattr(user, key, value)
                session.commit()
                return user.to_dict(), None
            return None, None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def delete_user(tenant_id, user_id):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return False, "Tenant not found"
        try:
            user = session.query(User).get(user_id)
            if user:
                session.delete(user)
                session.commit()
                return True, None
            return False, None
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
