import pytest
from tests.conftests import migrate, session, init_userInfo, init_adminInfo, init_feedbackLog
from tests.conftests import init_relationNode, init_relationEdge, init_contextLog, init_chatLog

from sqlalchemy.orm import Session

from quenassist_app.service.mysql.models import UserInfo, AdminInfo, FeedbackLog
from quenassist_app.service.mysql.models import  RelationNode, RelationEdge, ContextLog, ChatLog

from quenassist_app.service.mysql.dao import UserInfoDAO, AdminInfoDAO
from quenassist_app.service.mysql.dao import FeedbackLogDAO, RelationNodeDAO, RelationEdgeDAO
from quenassist_app.service.mysql.dao import ChatLogDAO, ContextLogDAO

from quenassist_app.service.mysql.schemas import UserInfoSchema, CreateUserInfoSchema, UpdateUserInfoSchema
from quenassist_app.service.mysql.schemas import AdminInfoSchema, CreateAdminInfoSchema, UpdateAdminInfoSchema
from quenassist_app.service.mysql.schemas import FeedbackLogSchema, CreateFeedbackLogSchema, UpdateFeedbackLogSchema
from quenassist_app.service.mysql.schemas import RelationNodeSchema, CreateRelationNodeSchema, UpdateRelationNodeSchema
from quenassist_app.service.mysql.schemas import RelationEdgeSchema, CreateRelationEdgeSchema, UpdateRelationEdgeSchema
from quenassist_app.service.mysql.schemas import ContextLogSchema, CreateContextLogSchema
from quenassist_app.service.mysql.schemas import ChatLogSchema, CreateChatLogSchema, UpdateChatLogSchema


class TestUserInfo:

    @pytest.fixture()
    def dao_basic(self):
        yield UserInfoDAO()

    def test_generate_table(self, init_chatLog):
        assert True == True

    def test_get(self, dao_basic, session):
        users = dao_basic.get(session)
        assert len(users) == 3
        users = dao_basic.get(session, limit=2)
        assert len(users) == 2
        users = dao_basic.get(session, offset=4)
        assert not users

    def test_get_by_id(self, dao_basic, session):
        user = dao_basic.get_by_id(session, 1)
        assert user.id == 1

    def test_create(self, dao_basic, session):
        origin_count = session.query(dao_basic.model).count()
        obj_in = CreateUserInfoSchema(username='test', password='test')
        dao_basic.create(session, obj_in)
        count = session.query(dao_basic.model).count()
        assert origin_count + 1 == count

    def test_patch(self, dao_basic, session):
        obj: UserInfo = session.query(dao_basic.model).first()
        username = obj.username
        obj_in = UpdateUserInfoSchema(username='test')
        updated_obj: UserInfo = dao_basic.patch(session, obj.id, obj_in)
        assert username != updated_obj.username

    def test_delete(self, dao_basic, session):
        origin_count = session.query(dao_basic.model).count()
        dao_basic.delete(session, 1)
        count = session.query(dao_basic.model).count()
        assert origin_count == count # Doesn't actually delete the object, but set the valid to false

    def test_count(self, dao_basic, session):
        count = dao_basic.count(session)
        assert count == 4

    def test_feedback_backref(self, dao_basic, session):
        user = dao_basic.get_by_id(session, 1)
        assert len(user.feedbacks_of_user) == 2

    def test_relationNode_backref(self, dao_basic, session):
        user = dao_basic.get_by_id(session, 1)
        assert len(user.nodes_of_user) == 2

    def test_relationEdge_backref(self, dao_basic, session):
        user = dao_basic.get_by_id(session, 1)
        assert len(user.edges_of_user) == 1

    def test_contextLog_backref(self, dao_basic, session):
        user = dao_basic.get_by_id(session, 1)
        assert len(user.contexts_of_user) == 2

    
# class TestAdminInfo:

#     @pytest.fixture()
#     def dao_basic(self):
#         yield AdminInfoDAO()

#     def test_get(self, dao_basic, session):
#         admins = dao_basic.get(session)
#         assert len(admins) == 3
#         admins = dao_basic.get(session, limit=2)
#         assert len(admins) == 2
#         admins = dao_basic.get(session, offset=4)
#         assert not admins

#     def test_get_by_id(self, dao_basic, session):
#         admin = dao_basic.get_by_id(session, 1)
#         assert admin.id == 1

#     def test_create(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         obj_in = CreateAdminInfoSchema(username='test', password='test')
#         dao_basic.create(session, obj_in)
#         count = session.query(dao_basic.model).count()
#         assert origin_count + 1 == count

#     def test_patch(self, dao_basic, session):
#         obj: AdminInfo = session.query(dao_basic.model).first()
#         username = obj.username
#         obj_in = UpdateAdminInfoSchema(username='test')
#         updated_obj: AdminInfo = dao_basic.patch(session, obj.id, obj_in)
#         assert username != updated_obj.username

#     def test_delete(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         dao_basic.delete(session, 1)
#         count = session.query(dao_basic.model).count()
#         assert origin_count == count # Doesn't actually delete the object, but set the valid to false

#     def test_count(self, dao_basic, session):
#         count = dao_basic.count(session)
#         assert count == 3

#     def test_feedback_backref(self, dao_basic, session):
#         admin = dao_basic.get_by_id(session, 1)
#         assert len(admin.feedbacks_of_user) == 2
        
# class TestFeedbackLog:

#     @pytest.fixture()
#     def dao_basic(self, init_feedbackLog):
#         yield FeedbackLogDAO()

#     def test_get(self, dao_basic, session):
#         feedback_logs = dao_basic.get(session)
#         assert len(feedback_logs) == 4
#         feedback_logs = dao_basic.get(session, limit=2)
#         assert len(feedback_logs) == 2
#         feedback_logs = dao_basic.get(session, offset=5)
#         assert not feedback_logs

#     def test_get_by_id(self, dao_basic, session):
#         feedback_logs = dao_basic.get_by_id(session, 1)
#         assert feedback_logs.id == 1

#     def test_create(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         obj_in = CreateFeedbackLogSchema(user_id=1, feedback='test')
#         dao_basic.create(session, obj_in)
#         count = session.query(dao_basic.model).count()
#         assert origin_count + 1 == count

#     def test_patch(self, dao_basic, session):
#         obj: FeedbackLog = session.query(dao_basic.model).first()
#         admin_id = obj.admin_id
#         obj_in = UpdateFeedbackLogSchema(admin_id=2)
#         updated_obj: FeedbackLog = dao_basic.patch(session, obj.id, obj_in)
#         assert admin_id != updated_obj.admin_id

#     def test_delete(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         dao_basic.delete(session, 1)
#         count = session.query(dao_basic.model).count()
#         assert origin_count - 1 == count

#     def test_count(self, dao_basic, session):
#         count = dao_basic.count(session)
#         assert count == 4

#     def test_foreign_key(self, dao_basic, session):
#         feedback = dao_basic.get_by_id(session, 1)
#         assert feedback.userinfo.username == "user1"
#         assert feedback.admininfo.username == "admin1"

# class TestRelationNode:

#     @pytest.fixture()
#     def dao_basic(self):
#         yield RelationNodeDAO()

#     def test_get(self, dao_basic, session):
#         relation_nodes = dao_basic.get(session)
#         assert len(relation_nodes) == 4
#         relation_nodes = dao_basic.get(session, limit=2)
#         assert len(relation_nodes) == 2
#         relation_nodes = dao_basic.get(session, offset=5)
#         assert not relation_nodes

#     def test_get_by_id(self, dao_basic, session):
#         relation_node = dao_basic.get_by_id(session, 1)
#         assert relation_node.id == 1

#     def test_create(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         obj_in = CreateRelationNodeSchema(user_id=1, node_address='test', x_axis=5.0, y_axis=5.0)
#         dao_basic.create(session, obj_in)
#         count = session.query(dao_basic.model).count()
#         assert origin_count + 1 == count

#     def test_patch(self, dao_basic, session):
#         obj: RelationNode = session.query(dao_basic.model).first()
#         node_address = obj.node_address
#         obj_in = UpdateRelationNodeSchema(node_address='test')
#         updated_obj: RelationNode = dao_basic.patch(session, obj.id, obj_in)
#         assert node_address != updated_obj.node_address

#     def test_delete(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         dao_basic.delete(session, 1)
#         count = session.query(dao_basic.model).count()
#         assert origin_count - 1 == count

#     def test_count(self, dao_basic, session):
#         count = dao_basic.count(session)
#         assert count == 4

#     def test_foreign_key(self, dao_basic, session):
#         relation_node = dao_basic.get_by_id(session, 1)
#         assert relation_node.userinfo.username == "user1"

# class TestRelationEdge:

#     @pytest.fixture()
#     def dao_basic(self):
#         yield RelationEdgeDAO()

#     def test_get(self, dao_basic, session):
#         relation_edges = dao_basic.get(session)
#         assert len(relation_edges) == 1
#         relation_edges = dao_basic.get(session, limit=2)
#         assert len(relation_edges) == 1
#         relation_edges = dao_basic.get(session, offset=5)
#         assert not relation_edges

#     def test_get_by_id(self, dao_basic, session):
#         relation_edge = dao_basic.get_by_id(session, 1)
#         assert relation_edge.id == 1

#     def test_create(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         obj_in = CreateRelationEdgeSchema(user_id=1, source=1, target=2)
#         dao_basic.create(session, obj_in)
#         count = session.query(dao_basic.model).count()
#         assert origin_count + 1 == count

#     def test_patch(self, dao_basic, session):
#         obj: RelationEdge = session.query(dao_basic.model).first()
#         source = obj.source
#         target = obj.target
#         obj_in = UpdateRelationEdgeSchema(source=2, target=1)
#         updated_obj: RelationEdge = dao_basic.patch(session, obj.id, obj_in)
#         assert source != updated_obj.source and target != updated_obj.target

#     def test_delete(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         dao_basic.delete(session, 1)
#         count = session.query(dao_basic.model).count()
#         assert origin_count - 1 == count

#     def test_count(self, dao_basic, session):
#         count = dao_basic.count(session)
#         assert count == 1

#     def test_foreign_key(self, dao_basic, session):
#         relation_edge = dao_basic.get_by_id(session, 1)
#         assert relation_edge.userinfo.username == "user1"

# class TestContextLog:

#     @pytest.fixture()
#     def dao_basic(self):
#         yield ContextLogDAO()

#     def test_get(self, dao_basic, session):
#         context_logs = dao_basic.get(session)
#         assert len(context_logs) == 4
#         context_logs = dao_basic.get(session, limit=2)
#         assert len(context_logs) == 2
#         context_logs = dao_basic.get(session, offset=5)
#         assert not context_logs

#     def test_get_by_id(self, dao_basic, session):
#         context_log = dao_basic.get_by_id(session, 1)
#         assert context_log.id == 1

#     def test_create(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         obj_in = CreateContextLogSchema(user_id=1)
#         dao_basic.create(session, obj_in)
#         count = session.query(dao_basic.model).count()
#         assert origin_count + 1 == count

#     def test_delete(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         dao_basic.delete(session, 1)
#         count = session.query(dao_basic.model).count()
#         assert origin_count - 1 == count

#     def test_count(self, dao_basic, session):
#         count = dao_basic.count(session)
#         assert count == 4

#     def test_foreign_key(self, dao_basic, session):
#         context_log = dao_basic.get_by_id(session, 1)
#         assert context_log.userinfo.username == "user1"

#     def test_chatLog_backref(self, dao_basic, session):
#         context = dao_basic.get_by_id(session, 1)
#         assert len(context.chats_of_context) == 2

# class TestChatLog:

#     @pytest.fixture()
#     def dao_basic(self):
#         yield ChatLogDAO()

#     def test_get(self, dao_basic, session):
#         chat_logs = dao_basic.get(session)
#         assert len(chat_logs) == 5
#         chat_logs = dao_basic.get(session, limit=2)
#         assert len(chat_logs) == 2
#         chat_logs = dao_basic.get(session, offset=6)
#         assert not chat_logs

#     def test_get_by_id(self, dao_basic, session):
#         chat_log = dao_basic.get_by_id(session, 1)
#         assert chat_log.id == 1

#     def test_create(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         obj_in = CreateChatLogSchema(contextLog_id=1, chat='test')
#         dao_basic.create(session, obj_in)
#         count = session.query(dao_basic.model).count()
#         assert origin_count + 1 == count

#     def test_patch(self, dao_basic, session):
#         obj: ChatLog = session.query(dao_basic.model).first()
#         chat = obj.chat
#         obj_in = UpdateChatLogSchema(chat='test')
#         updated_obj: ChatLog = dao_basic.patch(session, obj.id, obj_in)
#         assert chat != updated_obj.chat

#     def test_delete(self, dao_basic, session):
#         origin_count = session.query(dao_basic.model).count()
#         dao_basic.delete(session, 1)
#         count = session.query(dao_basic.model).count()
#         assert origin_count == count

#     def test_count(self, dao_basic, session):
#         count = dao_basic.count(session)
#         assert count == 5

#     def test_foreign_key(self, dao_basic, session):
#         chat_log = dao_basic.get_by_id(session, 1)
#         assert chat_log.contextlog.id == 1
