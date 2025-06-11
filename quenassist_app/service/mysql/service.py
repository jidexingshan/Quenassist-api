from typing import Generic, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound

from quenassist_app.service.mysql.dao import BaseDAO, UserInfoDAO, AdminInfoDAO
from quenassist_app.service.mysql.dao import FeedbackLogDAO, RelationNodeDAO, RelationEdgeDAO
from quenassist_app.service.mysql.dao import ChatLogDAO, ContextLogDAO

from quenassist_app.service.mysql.models import UserInfo, AdminInfo, FeedbackLog, RelationNode, RelationEdge
from quenassist_app.service.mysql.models import ContextLog, ChatLog

from quenassist_app.service.mysql.schemas import CreateSchema, ModelType, UpdateSchema, CompleteSchema
from quenassist_app.service.mysql.schemas import UserInfoSchema, CreateUserInfoSchema, UpdateUserInfoSchema
from quenassist_app.service.mysql.schemas import AdminInfoSchema, CreateAdminInfoSchema, UpdateAdminInfoSchema
from quenassist_app.service.mysql.schemas import FeedbackLogSchema, CreateFeedbackLogSchema, UpdateFeedbackLogSchema
from quenassist_app.service.mysql.schemas import RelationNodeSchema, CreateRelationNodeSchema, UpdateRelationNodeSchema
from quenassist_app.service.mysql.schemas import RelationEdgeSchema, CreateRelationEdgeSchema, UpdateRelationEdgeSchema
from quenassist_app.service.mysql.schemas import ContextLogSchema, CreateContextLogSchema
from quenassist_app.service.mysql.schemas import ChatLogSchema, CreateChatLogSchema, UpdateChatLogSchema

class BaseService(Generic[ModelType, CreateSchema, UpdateSchema, CompleteSchema]):
    dao: BaseDAO

    def get(self, session: Session, offset=0, limit=10) -> List[ModelType]:
        """"""
        return self.dao.get(session, offset=offset, limit=limit)

    def total(self, session: Session) -> int:
        return self.dao.count(session)

    def get_by_id(self, session: Session, pk: int) -> ModelType:
        """Get by id"""
        return self.dao.get_by_id(session, pk)

    def create(self, session: Session, obj_in: CreateSchema) -> ModelType:
        """Create a object"""
        return self.dao.create(session, obj_in)

    def patch(self, session: Session, pk: int, obj_in: UpdateSchema) -> ModelType:
        """Update"""
        return self.dao.patch(session, pk, obj_in)

    def delete(self, session: Session, pk: int) -> None:
        """Delete a object"""
        return self.dao.delete(session, pk)

class UserInfoService(BaseService[UserInfo, CreateUserInfoSchema, UpdateUserInfoSchema, UserInfoSchema]):
    dao = UserInfoDAO()

    def get_by_name(self, session: Session, name: str) -> UserInfo:
        try:
            return self.dao.get_by_name(session, name)
        except NoResultFound as e:
            raise e
    
    def create(self, session: Session, obj_in: CreateSchema) -> ModelType:
        try:
            return self.dao.create(session, obj_in)
        except IntegrityError as e:
            raise e

class AdminInfoService(BaseService[AdminInfo, CreateAdminInfoSchema, UpdateAdminInfoSchema, AdminInfoSchema]):
    dao = AdminInfoDAO()

    def get_by_name(self, session: Session, name: str) -> UserInfo:
        try:
            return self.dao.get_by_name(session, name)
        except NoResultFound as e:
            raise e
    
    def create(self, session: Session, obj_in: CreateSchema) -> ModelType:
        try:
            return self.dao.create(session, obj_in)
        except IntegrityError as e:
            raise e

class FeedbackLogService(BaseService[FeedbackLog, CreateFeedbackLogSchema, UpdateFeedbackLogSchema, FeedbackLogSchema]):
    dao = FeedbackLogDAO()

class RelationNodeService(BaseService[RelationNode, CreateRelationNodeSchema, UpdateRelationNodeSchema, RelationNodeSchema]):
    dao = RelationNodeDAO()

class RelationEdgeService(BaseService[RelationEdge, CreateRelationEdgeSchema, UpdateRelationEdgeSchema, RelationEdgeSchema]):
    dao = RelationEdgeDAO()

class ContextLogService(BaseService[ContextLog, CreateContextLogSchema, None, ContextLogSchema]):
    dao = ContextLogDAO()

    # def delete(self, session: Session, pk: int) -> None:
    #     pass

class ChatLogService(BaseService[ChatLog, CreateChatLogSchema, UpdateChatLogSchema, ChatLogSchema]):
    dao = ChatLogDAO()
