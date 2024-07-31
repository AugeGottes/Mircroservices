import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .models import User as User, Chatroom as Chatroom, ChatroomUser as ChatroomUser, \
    Message as Message, Tenant as Tenant
from .services.user import UserService
from .services.chatroom import ChatroomService
from .services.chatroom_user import ChatroomUserService
from .services.message import MessageService
from .extensions import db
import datetime
from datetime import timezone
from graphql import GraphQLError
from graphene import DateTime
from datetime import date
UTC=timezone.utc
from app.authentication.auth import auth
from flask import g
from flask_graphql import GraphQLView
from flask import request, jsonify
from dateutil import parser


class TenantType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    db_name = graphene.String()
    password = graphene.String()
    created_at = DateTime()
    modified_at = DateTime()

    

class CreateTenant(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        db_name = graphene.String(required=True)
        password = graphene.String(required=True)

    tenant = graphene.Field(TenantType)
    error = graphene.String()

    @staticmethod
    def mutate(root, info, name, db_name, password):
        try:
            new_tenant = Tenant(name=name, db_name=db_name, password=password)
            db.session.add(new_tenant)
            db.session.commit()
            return CreateTenant(tenant=new_tenant, error=None)
        except Exception as e:
            db.session.rollback()
            return CreateTenant(tenant=None, error=str(e))
        
    
class UserType(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()
    mobile = graphene.String()
    created_at = DateTime()
    modified_at = DateTime()

class UserList(graphene.ObjectType):
    total_count = graphene.Int()
    total_pages = graphene.Int()
    current_page = graphene.Int()
    users = graphene.List(UserType)

class ChatroomType(SQLAlchemyObjectType):
    class Meta:
        model = Chatroom

class ChatroomUserType(SQLAlchemyObjectType):
    class Meta:
        model = ChatroomUser

class MessageType(SQLAlchemyObjectType):
    class Meta:
        model = Message

class TenantType(SQLAlchemyObjectType):
    class Meta:
        model = Tenant

class ChatroomList(graphene.ObjectType):
    total_count = graphene.Int()
    total_pages = graphene.Int()
    current_page = graphene.Int()
    chatrooms = graphene.List(ChatroomType)

# Input Types
class UserInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    mobile = graphene.String()

# Mutations
class CreateUser(graphene.Mutation):
    class Arguments:
        user_data = UserInput(required=True)

    user = graphene.Field(UserType)
    error = graphene.String()

    def mutate(self, info, user_data):
        tenant_id = int(g.tenant_id)
        result, error = UserService.create_user(tenant_id, user_data)
        if result:
            return CreateUser(user=result, error=None)
        return CreateUser(user=None, error=error)

class UpdateUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        user_data = UserInput(required=True)

    user = graphene.Field(UserType)
    error = graphene.String()

    def mutate(self, info, user_id, user_data):
        tenant_id = int(g.tenant_id)
        result, error = UserService.update_user(tenant_id, user_id, user_data)
        if result:
            return UpdateUser(user=result, error=None)
        return UpdateUser(user=None, error=error)

class DeleteUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, user_id):
        tenant_id = int(g.tenant_id)
        success, error = UserService.delete_user(tenant_id, user_id)
        return DeleteUser(success=success, error=error)
    

class CreateChatroom(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()

    chatroom = graphene.Field(ChatroomType)
    error = graphene.String()

    def mutate(self, info, name, description=None):
        tenant_id = int(g.tenant_id)
        result, error = ChatroomService.create_chatroom(tenant_id, name, description)
        if result:
            return CreateChatroom(chatroom=result, error=None)
        return CreateChatroom(chatroom=None, error=error)


class UpdateChatroom(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.Int(required=True)
        name = graphene.String()
        description = graphene.String()

    chatroom = graphene.Field(ChatroomType)
    error = graphene.String()

    def mutate(self, info, chatroom_id, name=None, description=None):
        tenant_id = int(g.tenant_id)
        data = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        
        result, error = ChatroomService.update_chatroom(tenant_id, chatroom_id, data)
        if result:
            return UpdateChatroom(chatroom=result, error=None)
        return UpdateChatroom(chatroom=None, error=error)

class DeleteChatroom(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.Int(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, chatroom_id):
        tenant_id = int(g.tenant_id)
        success, error = ChatroomService.delete_chatroom(tenant_id, chatroom_id)
        return DeleteChatroom(success=success, error=error)


class AddUserToChatroom(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)
        role = graphene.String()

    chatroom_user = graphene.Field(ChatroomUserType)
    error = graphene.String()

    def mutate(self, chatroom_id, user_id, role="member"):
        tenant_id = int(g.tenant_id)
        result, error = ChatroomUserService.add_user_to_chatroom(tenant_id, chatroom_id, user_id, role)
        if result:
            return AddUserToChatroom(chatroom_user=result, error=None)
        return AddUserToChatroom(chatroom_user=None, error=error)

class RemoveUserFromChatroom(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    def mutate(self, chatroom_id, user_id):
        tenant_id = int(g.tenant_id)
        success, error = ChatroomUserService.remove_user_from_chatroom(tenant_id, chatroom_id, user_id)
        return RemoveUserFromChatroom(success=success, error=error)

class SendMessage(graphene.Mutation):
    class Arguments:
        chatroom_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)
        content = graphene.String(required=True)

    message = graphene.Field(MessageType)
    error = graphene.String()

    def mutate(self, chatroom_id, user_id, content):
        tenant_id = int(g.tenant_id)
        result, error = MessageService.send_message(tenant_id, chatroom_id, user_id, content)
        if result:
            return SendMessage(message=result, error=None)
        return SendMessage(message=None, error=error)




# Queries
class Query(graphene.ObjectType):
    user = graphene.Field(UserType, user_id=graphene.Int(required=True))
    users = graphene.Field(
        graphene.List(UserType),
        page=graphene.Int(default_value=1),
        per_page=graphene.Int(default_value=10),
        sort_by=graphene.String(default_value="created_at"),
        sort_order=graphene.String(default_value="desc")
    )

    def resolve_user(self, info, user_id):
        """
        Get a single user by ID
        """
        tenant_id = int(g.tenant_id)
        result, error = UserService.get_user(tenant_id, user_id)
        if error:
            raise Exception(error)
        if result:
            return UserType(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                mobile=result['mobile'],
                created_at=parser.parse(result['created_at']),
                modified_at=parser.parse(result['modified_at'])
            )
        return result

    def resolve_users(self, info,page, per_page, sort_by, sort_order):
        """
        Get all users
        """
        tenant_id = int(g.tenant_id)
        result, error = UserService.get_users(tenant_id, page, per_page, sort_by, sort_order)
        if error:
            raise Exception(error)
        return UserList(
            total_count=result['total_count'],
            total_pages=result['total_pages'],
            current_page=result['current_page'],
            users=[
                UserType(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    mobile=user['mobile'],
                    created_at=parser.parse(user['created_at']),
                    modified_at=parser.parse(user['modified_at'])
                ) for user in result['users']
            ]
        )
    
    def resolve_chatrooms(self,info, page, per_page):
        """
        Get all chatrooms
        """
        tenant_id = int(g.tenant_id)
        result, error = ChatroomService.get_chatrooms(tenant_id, page, per_page)
        if error:
            raise Exception(error)
        return ChatroomList(
            total_count=result['total_count'],
            total_pages=result['total_pages'],
            current_page=result['current_page'],
            chatrooms=[
                ChatroomType(
                    id=chatroom['id'],
                    name=chatroom['name'],
                    description=chatroom['description'],
                    created_at=parser.parse(chatroom['created_at']),
                    modified_at=parser.parse(chatroom['modified_at'])
                ) for chatroom in result['chatrooms']
            ]
        )
    
    def resolve_chatroom(self,info, chatroom_id):
        """
        Get a chatroom by ID
        """
        tenant_id = int(g.tenant_id)
        result, error = ChatroomService.get_chatroom(tenant_id, chatroom_id)
        if error:
            raise Exception(error)
        if result:
            return ChatroomType(
                id=result['id'],
                name=result['name'],
                description=result['description'],
                created_at=parser.parse(result['created_at']),
                modified_at=parser.parse(result['modified_at'])
            )
        return result
    
    def resolve_messages_in_chatroom(self,info, chatroom_id, page, per_page):
        """
        Get messages for a chatroom
        """
        tenant_id = int(g.tenant_id)
        result, error = MessageService.get_messages(tenant_id, chatroom_id, page, per_page)
        if error:
            raise Exception(error)
        return [
            MessageType(
                id=message['id'],
                chatroom_id=message['chatroom_id'],
                user_id=message['user_id'],
                content=message['content'],
                timestamp=parser.parse(message['timestamp'])
            ) for message in result
        ]
    
    def resolve_user_messages(self, info,user_id, page, per_page):
        """
        Get messages for a user
        """
        tenant_id = int(g.tenant_id)
        result, error = MessageService.get_user_messages(tenant_id, user_id, page, per_page)
        if error:
            raise Exception(error)
        return [
            MessageType(
                id=message['id'],
                chatroom_id=message['chatroom_id'],
                user_id=message['user_id'],
                content=message['content'],
                timestamp=parser.parse(message['timestamp'])
            ) for message in result
        ]
    
    def resolve_users_in_chatroom(self,info, chatroom_id, page, per_page, sort_by, sort_order, name):
        """
        Get users for  a chatroom
        """
        tenant_id = int(g.tenant_id)
        result, error = ChatroomUserService.get_users_in_chatroom(tenant_id, chatroom_id, page, per_page, sort_by, sort_order, name)
        if error:
            raise Exception(error)
        return [
            UserType(
                id=user['id'],
                username=user['username'],
                email=user['email'],
                mobile=user['mobile'],
                created_at=parser.parse(user['created_at']),
                modified_at=parser.parse(user['modified_at'])
            ) for user in result
        ]
    

class TenantMutation(graphene.ObjectType):
    create_tenant = CreateTenant.Field()
# Mutation
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

    

tenant_schema = graphene.Schema(mutation=TenantMutation)
schema = graphene.Schema(query=Query, mutation=Mutation)

class AuthenticatedGraphQLView(GraphQLView):
    decorators = [auth.login_required]

    def dispatch_request(self):
        tenant_id=g.tenant_id
        if not tenant_id:
            return jsonify({"error": "Tenant-ID  is  wrong "}), 400
        return super().dispatch_request()

def setup_graphql(app):
    app.add_url_rule(
        '/graphql',
        view_func=AuthenticatedGraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True  
        )
    )
    app.add_url_rule(
            '/tenants',
            view_func=GraphQLView.as_view(
                'create_tenant',
                schema=graphene.Schema(mutation=Mutation),
                graphiql=True
            )
        )