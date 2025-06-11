"""Models"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship


class CustomBase:
    """https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/mixins.html"""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_collate': 'utf8mb4_general_ci'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)


BaseModel = declarative_base(cls=CustomBase)

class UserInfo(BaseModel):
    """User info, account = 'U' + str(id)"""
    account = Column(String(50), nullable=True, unique=True, comment='Account')
    password = Column(String(100), nullable=False, comment='Password')
    visit_count = Column(Integer, nullable=False, default=0, comment='Visit count')
    username = Column(String(50), nullable=False, unique=True, comment='Username')
    phone = Column(String(20), nullable=True, comment='Phone')
    valid = Column(Boolean, nullable=False, default=True, comment='Vaild')
    # avatar = Column(String(100), nullable=True, comment='Avatar')

class AdminInfo(BaseModel):
    """Admin info, account = 'A' + str(id)"""
    account = Column(String(50), nullable=True, unique=True, comment='Account')
    password = Column(String(100), nullable=False, comment='Password')
    tackle_count = Column(Integer, nullable=False, default=0, comment='Tackling feedback count')
    username = Column(String(50), nullable=False, unique=True, comment='Username')
    valid = Column(Boolean, nullable=False, default=True, comment='Vaild')

class FeedbackLog(BaseModel):
    """Feedback log"""
    # user_account = Column(String(50), nullable=False, comment='User account')
    # admin_account = Column(String(50), nullable=True, comment='Admin account')
    user_id = Column(Integer, ForeignKey('userinfo.id'), nullable=False, comment='User id')
    userinfo = relationship("UserInfo", backref="feedbacks_of_user")
    admin_id = Column(Integer, ForeignKey('admininfo.id'), nullable=True, comment='Admin id')
    admininfo = relationship("AdminInfo", backref="tacklings_of_admin")
    feedback = Column(Text, nullable=False, comment='Feedback')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='Create time')
    # update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='Update time')

class RelationNode(BaseModel):
    """Relationship node"""
    # user_account = Column(String(50), nullable=False, comment='User account')
    user_id = Column(Integer, ForeignKey('userinfo.id'), nullable=False, comment='User id')
    userinfo = relationship("UserInfo", backref="nodes_of_user")
    node_address = Column(String(30), nullable=False, default="anonymous", comment='Node address')
    x_axis = Column(Float, nullable=False, comment='X-axis')
    y_axis = Column(Float, nullable=False, comment='Y-axis')

class RelationEdge(BaseModel):
    """Relationship edge"""
    # user_account = Column(String(50), nullable=False, comment='User account')
    user_id = Column(Integer, ForeignKey('userinfo.id'), nullable=False, comment='User id')
    userinfo = relationship("UserInfo", backref="edges_of_user")
    source = Column(Integer, nullable=False, comment='Source node')
    target = Column(Integer, nullable=False, comment='Target node')
    relation = Column(String(30), nullable=False, default="Unknown Relation", comment='Relation')

class ContextLog(BaseModel):
    """Context log"""
    # user_account = Column(String(50), nullable=False, comment='User account')
    user_id = Column(Integer, ForeignKey('userinfo.id'), nullable=False, comment='User id')
    userinfo = relationship("UserInfo", backref="contexts_of_user")
    theme = Column(String(30), nullable=False, default='New Session', comment='Theme')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='Create time')

class ChatLog(BaseModel):
    """Chat log"""
    # ContextLog_id = Column(Integer, nullable=False, comment='Context log id')
    contextLog_id = Column(Integer, ForeignKey('contextlog.id'), nullable=False, comment='Context log id')
    contextlog = relationship("ContextLog", backref="chats_of_context")
    chat_time = Column(DateTime, nullable=False, default=datetime.now, comment='Create time')
    chat = Column(Text, nullable=False, comment='Chat')
    who = Column(Boolean, nullable=False, default=True, comment='Who') # True: user, False: LLM
    valid = Column(Boolean, nullable=False, default=True, comment='Valid')