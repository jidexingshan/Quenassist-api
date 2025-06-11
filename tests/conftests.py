import os
from pathlib import Path
from alembic import command, config

import pytest

from sqlalchemy.orm import Session

from quenassist_app.system import migration
from quenassist_app.config import settings
from quenassist_app.service.mysql.mysql_db import SessionFactory
from quenassist_app.service.mysql.models import UserInfo, AdminInfo, FeedbackLog
from quenassist_app.service.mysql.models import  RelationNode, RelationEdge, ContextLog, ChatLog

@pytest.fixture()
def migrate():
    """Re-init database when run a test."""
    os.chdir(Path(migration.__file__).parent.parent / 'migration')
    alembic_config = config.Config('./alembic.ini')
    alembic_config.set_main_option('script_location', os.getcwd())
    print('\n----- RUN ALEMBIC MIGRATION: -----\n')
    command.downgrade(alembic_config, 'base')
    command.upgrade(alembic_config, 'head')
    try:
        yield
    finally:
        command.downgrade(alembic_config, 'base')
        db_name = settings.DATABASE.get('NAME')
        if settings.DATABASE.DRIVER == 'mysql' and os.path.isfile(db_name):
            try:
                os.remove(db_name)
            except FileNotFoundError:
                pass

@pytest.fixture()
def session(migrate):
    """session fixture"""
    _s = SessionFactory()
    yield _s
    _s.close()

@pytest.fixture()
def init_userInfo(session: Session):
    """Init UserInfo"""
    u_1 = UserInfo(password='user1', username='user1', phone='1234')
    u_2 = UserInfo(password='user2', username='user2', phone='2345')
    u_3 = UserInfo(password='user3', username='user3', phone='3456')
    session.add_all([u_1, u_2, u_3])
    session.commit()
    yield

@pytest.fixture()
def init_adminInfo(session: Session, init_userInfo):
    """Init AdminInfo"""
    a_1 = AdminInfo(password='admin1', username='admin1')
    a_2 = AdminInfo(password='admin2', username='admin2')
    a_3 = AdminInfo(password='admin3', username='admin3')
    session.add_all([a_1, a_2, a_3])
    session.commit()
    yield

@pytest.fixture()
def init_feedbackLog(session: Session, init_adminInfo):
    """Init FeedbackLog"""
    user1 = session.query(UserInfo).filter(UserInfo.id == 1).first()
    user2 = session.query(UserInfo).filter(UserInfo.id == 2).first()
    user3 = session.query(UserInfo).filter(UserInfo.id == 3).first()
    admin1 = session.query(AdminInfo).filter(AdminInfo.id == 1).first()
    admin2 = session.query(AdminInfo).filter(AdminInfo.id == 2).first()
    admin3 = session.query(AdminInfo).filter(AdminInfo.id == 3).first()
    f_1 = FeedbackLog(feedback='feedback1', user_id=1, userinfo=user1, admin_id=1, admininfo=admin1)
    f_2 = FeedbackLog(feedback='feedback2', user_id=2, userinfo=user2, admin_id=2, admininfo=admin2)
    f_3 = FeedbackLog(feedback='feedback3', user_id=3, userinfo=user3, admin_id=3, admininfo=admin3)
    f_4 = FeedbackLog(feedback='feedback4', user_id=1, userinfo=user1, admin_id=1, admininfo=admin1)
    session.add_all([f_1, f_2, f_3, f_4])
    session.commit()
    yield

@pytest.fixture()
def init_relationNode(session: Session, init_feedbackLog):
    """Init RelationNode"""
    user1 = session.query(UserInfo).filter(UserInfo.id == 1).first()
    user2 = session.query(UserInfo).filter(UserInfo.id == 2).first()
    user3 = session.query(UserInfo).filter(UserInfo.id == 3).first()
    n_1 = RelationNode(user_id=1, userinfo=user1, node_address='node1', x_axis=1.0, y_axis=1.0)
    n_2 = RelationNode(user_id=2, userinfo=user2, node_address='node2', x_axis=2.0, y_axis=2.0)
    n_3 = RelationNode(user_id=3, userinfo=user3, node_address='node3', x_axis=3.0, y_axis=3.0)
    n_4 = RelationNode(user_id=1, userinfo=user1, node_address='node4', x_axis=4.0, y_axis=4.0)
    session.add_all([n_1, n_2, n_3, n_4])
    session.commit()
    yield

@pytest.fixture()
def init_relationEdge(session: Session, init_relationNode):
    """Init RelationEdge"""
    node1 = session.query(RelationNode).filter(RelationNode.id == 1).first()
    node4 = session.query(RelationNode).filter(RelationNode.id == 4).first()
    user1 = node1.userinfo
    e_1 = RelationEdge(user_id=1, userinfo=user1, source=1, target=4)
    session.add_all([e_1])
    session.commit()
    yield

@pytest.fixture()
def init_contextLog(session: Session, init_relationEdge): 
    """Init ContextLog"""
    user1 = session.query(UserInfo).filter(UserInfo.id == 1).first()
    user2 = session.query(UserInfo).filter(UserInfo.id == 2).first()
    user3 = session.query(UserInfo).filter(UserInfo.id == 3).first()
    c_1 = ContextLog(user_id=1, userinfo=user1)
    c_2 = ContextLog(user_id=2, userinfo=user2)
    c_3 = ContextLog(user_id=3, userinfo=user3)
    c_4 = ContextLog(user_id=1, userinfo=user1)
    session.add_all([c_1, c_2, c_3, c_4])
    session.commit()
    yield

@pytest.fixture()
def init_chatLog(session: Session, init_contextLog):
    """Init ChatLog"""
    context1 = session.query(ContextLog).filter(ContextLog.id == 1).first()
    context2 = session.query(ContextLog).filter(ContextLog.id == 2).first()
    context3 = session.query(ContextLog).filter(ContextLog.id == 3).first()
    context4 = session.query(ContextLog).filter(ContextLog.id == 4).first()
    c_1 = ChatLog(contextLog_id=1, contextlog=context1, chat="this is the first chat of user1")
    c_2 = ChatLog(contextLog_id=2, contextlog=context2, chat="this is the first chat of user2")
    c_3 = ChatLog(contextLog_id=3, contextlog=context3, chat="this is the first chat of user3")
    c_4 = ChatLog(contextLog_id=1, contextlog=context1, chat="this is the second chat of user1")
    c_5 = ChatLog(contextLog_id=4, contextlog=context4, chat="this is the other first chat of user1")
    session.add_all([c_1, c_2, c_3, c_4, c_5])
    session.commit()
    yield