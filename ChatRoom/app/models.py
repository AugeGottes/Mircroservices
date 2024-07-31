from datetime import datetime, timezone
from .extensions import db
UTC = timezone.utc
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    modified_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'mobile': self.mobile,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None
        }


class Chatroom(db.Model):
    __tablename__ = 'chatroom'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    modified_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))


class ChatroomUser(db.Model):
    __tablename__ = 'chatroom_user'
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chatroom_id = db.Column(db.Integer, db.ForeignKey('chatroom.id'), nullable=False)
    role = db.Column(db.String(32), default='member')
    joined_at = db.Column(db.DateTime, default=datetime.now(UTC))


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chatroom_id = db.Column(db.Integer, db.ForeignKey('chatroom.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(UTC))


class Tenant(db.Model):
    """Model for tenant table"""
    __tablename__ = 'tenant'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(64), unique=True,nullable=False)
    db_name=db.Column(db.String(64), unique=True,nullable=False)
    password=db.Column(db.String(128), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'db_name': self.db_name,
        }

   


