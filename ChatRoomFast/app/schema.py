import graphene
from datetime import datetime
from .dependencies import get_tenant_db
from sqlalchemy import desc
from contextlib import asynccontextmanager
from app.authentication.auth import verify_credentials
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials


class Tenant(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    db_name = graphene.String()

# Add this new mutation for creating a tenant
class CreateTenant(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        db_name = graphene.String(required=True)
        password = graphene.String(required=True)

    tenant = graphene.Field(lambda: Tenant)
    error = graphene.String()

    async def mutate(self, info, name, db_name, password):
        async with get_tenant_db() as db:
            try:
                new_tenant = Tenant(name=name, db_name=db_name, password=password)
                db.add(new_tenant)
                await db.commit()
                await db.refresh(new_tenant)
                return CreateTenant(tenant=Tenant(id=new_tenant.id, name=new_tenant.name, db_name=new_tenant.db_name), error=None)
            except Exception as e:
                await db.rollback()
                return CreateTenant(tenant=None, error=str(e))


class User(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()
    password = graphene.String()
    mobile = graphene.String()


class Chatroom(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    description = graphene.String()


class ChatroomUser(graphene.ObjectType):
    id = graphene.Int()
    user_id = graphene.Int()
    chatroom_id = graphene.Int()
    role = graphene.String()


class Message(graphene.ObjectType):
    id = graphene.Int()
    user_id = graphene.Int()
    chatroom_id = graphene.Int()
    content = graphene.String()
    timestamp = graphene.DateTime()


class Query(graphene.ObjectType):
    user = graphene.Field(User, id=graphene.Int(required=True))
    all_users = graphene.List(User, page=graphene.Int(), per_page=graphene.Int())
    chatroom = graphene.Field(Chatroom, id=graphene.Int(required=True))
    all_chatrooms = graphene.List(Chatroom, page=graphene.Int(), per_page=graphene.Int())
    chatroom_users = graphene.List(ChatroomUser, chatroom_id=graphene.Int(required=True))
    messages = graphene.List(Message, chatroom_id=graphene.Int(required=True), page=graphene.Int(), per_page=graphene.Int())
    user_messages = graphene.List(Message, user_id=graphene.Int(required=True), page=graphene.Int(), per_page=graphene.Int())

    async def resolve_user(self, info, id):
        """
        Get a user by id
        """
        db = next(get_tenant_db())
        user = db.query(User).filter(User.id == id).first()
        return User(id=user.id, username=user.username, email=user.email, password=user.password, mobile=user.mobile)

    async def resolve_all_users(self, info, page=1, per_page=10):
        """
        Get all users
        """
        db = next(get_tenant_db())
        users = db.query(User).offset((page - 1) * per_page).limit(per_page).all()
        return [User(id=u.id, username=u.username, email=u.email, password=u.password, mobile=u.mobile) for u in users]

    async def resolve_chatroom(self, info, id):
        """
        Get a chatroom by id
        """
        db = next(get_tenant_db())
        chatroom = db.query(Chatroom).filter(Chatroom.id == id).first()
        return Chatroom(id=chatroom.id, name=chatroom.name, description=chatroom.description)

    async def resolve_all_chatrooms(self, info, page=1, per_page=10):
        """
        Get all chatrooms
        """
        db = next(get_tenant_db())
        chatrooms = db.query(Chatroom).offset((page - 1) * per_page).limit(per_page).all()
        return [Chatroom(id=c.id, name=c.name, description=c.description) for c in chatrooms]

    async def resolve_chatroom_users(self, info, chatroom_id):
        """
        Get users for a chatroom
        """
        db = next(get_tenant_db())
        cu_list = db.query(ChatroomUser).filter(ChatroomUser.chatroom_id == chatroom_id).all()
        return [ChatroomUser(id=cu.id, user_id=cu.user_id, chatroom_id=cu.chatroom_id, role=cu.role) for cu in cu_list]

    async def resolve_messages(self, info, chatroom_id, page=1, per_page=10):
        """
        Get messages for a chatroom
        """
        db = next(get_tenant_db())
        messages = db.query(Message).filter(Message.chatroom_id == chatroom_id).order_by(desc(Message.timestamp)).offset((page - 1) * per_page).limit(per_page).all()
        return [Message(id=m.id, user_id=m.user_id, chatroom_id=m.chatroom_id, content=m.content, timestamp=m.timestamp) for m in messages]

    async def resolve_user_messages(self, info, user_id, page=1, per_page=10):
        """
        Get message for a user
        """
        db = next(get_tenant_db())
        messages = db.query(Message).filter(Message.user_id == user_id).order_by(desc(Message.timestamp)).offset((page - 1) * per_page).limit(per_page).all()
        return [Message(id=m.id, user_id=m.user_id, chatroom_id=m.chatroom_id, content=m.content, timestamp=m.timestamp) for m in messages]


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        mobile = graphene.String()

    user = graphene.Field(lambda: User)
    async def mutate(self, info, username, email, password, mobile=None):
        async with get_tenant_db() as db:
            user = User(username=username, email=email, password=password, mobile=mobile)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return CreateUser(user=user)
        


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        username = graphene.String()
        email = graphene.String()
        mobile = graphene.String()

    user = graphene.Field(lambda: User)

    async def mutate(self, info, id, username=None, email=None, mobile=None):
        
        async with get_tenant_db() as db:
            user = db.query(User).filter(User.id == id).first()
            if user:
                if username:
                    user.username = username
                if email:
                    user.email = email
                if mobile:
                    user.mobile = mobile
                await db.commit()
                await db.refresh(user)
            return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    async def mutate(self, info, id):
        
        
        async with get_tenant_db() as db:
            user = db.query(User).filter(User.id == id).first()
            if user:
                await db.delete(user)
                await db.commit()
                return DeleteUser(success=True)
            return DeleteUser(success=False)


class CreateChatroom(graphene.Mutation): 
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()

    chatroom = graphene.Field(lambda: Chatroom)

    async def mutate(self, info, name, description=None):
        async with get_tenant_db() as db:
            chatroom = Chatroom(name=name, description=description)
            db.add(chatroom)
            await db.commit()
            await db.refresh(chatroom)
            return CreateChatroom(chatroom=chatroom)

class UpdateChatroom(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        description = graphene.String()

    chatroom = graphene.Field(lambda: Chatroom)

    async def mutate(self, info, id, name=None, description=None):
        async with get_tenant_db() as db:
            chatroom = db.query(Chatroom).filter(Chatroom.id == id).first()
            if chatroom:
                if name:
                    chatroom.name = name
                if description:
                    chatroom.description = description
                await db.commit()
                await db.refresh(chatroom)
            return UpdateChatroom(chatroom=chatroom)


class DeleteChatroom(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    async def mutate(self, info, id):
        async with get_tenant_db() as db:
            chatroom = db.query(Chatroom).filter(Chatroom.id == id).first()
            if chatroom:
                await db.delete(chatroom)
                await db.commit()
                return DeleteChatroom(success=True)
            return DeleteChatroom(success=False)


class AddUserToChatroom(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        chatroom_id = graphene.Int(required=True)
        role = graphene.String()

    chatroom_user = graphene.Field(lambda: ChatroomUser)

    async def mutate(self, info, user_id, chatroom_id, role="member"):
        async with get_tenant_db() as db:
            chatroom_user = ChatroomUser(user_id=user_id, chatroom_id=chatroom_id, role=role)
            db.add(chatroom_user)
            await db.commit()
            await db.refresh(chatroom_user)
            return AddUserToChatroom(chatroom_user=chatroom_user)


class RemoveUserFromChatroom(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        chatroom_id = graphene.Int(required=True)

    success = graphene.Boolean()

    async def mutate(self, info, user_id, chatroom_id):
        async with get_tenant_db() as db:
            chatroom_user = db.query(ChatroomUser).filter(
                ChatroomUser.user_id == user_id,
                ChatroomUser.chatroom_id == chatroom_id
            ).first()
            if chatroom_user:
                await db.delete(chatroom_user)
                await db.commit()
                return RemoveUserFromChatroom(success=True)
            return RemoveUserFromChatroom(success=False)


class SendMessage(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        chatroom_id = graphene.Int(required=True)
        content = graphene.String(required=True)

    message = graphene.Field(lambda: Message)

    async def mutate(self, info, user_id, chatroom_id, content):
        async with get_tenant_db() as db:
            message = Message(user_id=user_id, chatroom_id=chatroom_id, content=content)
            db.add(message)
            await db.commit()
            await db.refresh(message)
            return SendMessage(message=message)

class TenantMutation(graphene.ObjectType):
    create_tenant = CreateTenant.Field()


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    create_chatroom = CreateChatroom.Field()
    update_chatroom = UpdateChatroom.Field()
    delete_chatroom = DeleteChatroom.Field()
    add_user_to_chatroom = AddUserToChatroom.Field()
    remove_user_from_chatroom = RemoveUserFromChatroom.Field()
    send_message = SendMessage.Field()


async def get_context(request, credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    tenant_id = verify_credentials(credentials)
    db = get_tenant_db(tenant_id)
    return {
        "request": request,
        "db": db,
        "tenant_id": tenant_id
    }

tenant_schema = graphene.Schema(mutation=TenantMutation)
schema = graphene.Schema(query=Query, mutation=Mutation,context_value=get_context)