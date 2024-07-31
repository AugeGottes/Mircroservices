from app.models import ChatroomUser, User
from ..extensions import db
import uuid
from app.services.tenant import TenantService


class ChatroomUserService:
    @staticmethod
    def add_user_to_chatroom(tenant_id, chatroom_id, user_id, role='member'):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            chatroom_user = ChatroomUser(
                id=str(uuid.uuid4()),
                user_id=user_id,
                chatroom_id=chatroom_id,
                role=role
            )
            session.add(chatroom_user)
            session.commit()

            return {
                'id': chatroom_user.id,
                'user_id': chatroom_user.user_id,
                'chatroom_id': chatroom_user.chatroom_id,
                'role': chatroom_user.role,
                'joined_at': chatroom_user.joined_at
            }, None
        except Exception as e:
            session.rollback()
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def get_users_in_chatroom(tenant_id, chatroom_id, page, per_page, sort_by, sort_order, name=None):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return None, "Tenant not found"

        try:
            query = session.query(ChatroomUser).filter_by(chatroom_id=chatroom_id)

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
                'total_pages': (total + per_page - 1) // per_page,
                'current_page': page,
                'users': [{
                    'id': item.user_id,
                    'username': session.query(User).get(item.user_id).username,
                    'email': session.query(User).get(item.user_id).email,
                    'role': item.role,
                    'joined_at': item.joined_at
                } for item in chatroom_users]
            }, None
        except Exception as e:
            return None, str(e)
        finally:
            session.close()

    @staticmethod
    def remove_user_from_chatroom(tenant_id, chatroom_id, user_id):
        session = TenantService.get_tenant_session(tenant_id)
        if not session:
            return False, "Tenant not found"

        try:
            chatroom_user = session.query(ChatroomUser).filter_by(chatroom_id=chatroom_id, user_id=user_id).first()
            if chatroom_user:
                session.delete(chatroom_user)
                session.commit()
                return True, None
            return False, "User not found in chatroom"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()