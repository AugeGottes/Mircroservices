from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
UTC = timezone.utc


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    mobile = Column(String(10), unique=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    modified_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    chatrooms = relationship("ChatroomUser", back_populates="user")
    messages = relationship("Message", back_populates="user")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'mobile': self.mobile,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None
        }


class Chatroom(Base):
    __tablename__ = 'chatroom'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(128))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    modified_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    users = relationship("ChatroomUser", back_populates="chatroom")
    messages = relationship("Message", back_populates="chatroom")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None
        }


class ChatroomUser(Base):
    __tablename__ = 'chatroom_user'
    id = Column(String(32), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    chatroom_id = Column(Integer, ForeignKey('chatroom.id'), nullable=False)
    role = Column(String(32), default='member')
    joined_at = Column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="chatrooms")
    chatroom = relationship("Chatroom", back_populates="users")


    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'chatroom_id': self.chatroom_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }


class Message(Base):
    __tablename__ = 'message'
    id = Column(String(32), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    chatroom_id = Column(Integer, ForeignKey('chatroom.id'), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="messages")
    chatroom = relationship("Chatroom", back_populates="messages")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'chatroom_id': self.chatroom_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Tenant(Base):
    __tablename__ = 'tenant'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    db_name = Column(String(64), unique=True, nullable=False)
    password=Column(String(128), nullable=False)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'db_name': self.db_name,
            'password': self.password
        }