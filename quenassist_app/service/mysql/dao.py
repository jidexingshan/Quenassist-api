from typing import Generic, List
from datetime import datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound

from quenassist_app.service.mysql.models import UserInfo, AdminInfo, FeedbackLog, RelationNode
from quenassist_app.service.mysql.models import RelationEdge, ContextLog, ChatLog

from quenassist_app.service.mysql.schemas import CreateSchema, ModelType, UpdateSchema, CompleteSchema
from quenassist_app.service.mysql.schemas import UserInfoSchema, CreateUserInfoSchema, UpdateUserInfoSchema
from quenassist_app.service.mysql.schemas import AdminInfoSchema, CreateAdminInfoSchema, UpdateAdminInfoSchema
from quenassist_app.service.mysql.schemas import FeedbackLogSchema, CreateFeedbackLogSchema, UpdateFeedbackLogSchema
from quenassist_app.service.mysql.schemas import RelationNodeSchema, CreateRelationNodeSchema, UpdateRelationNodeSchema
from quenassist_app.service.mysql.schemas import RelationEdgeSchema, CreateRelationEdgeSchema, UpdateRelationEdgeSchema
from quenassist_app.service.mysql.schemas import ContextLogSchema, CreateContextLogSchema
from quenassist_app.service.mysql.schemas import ChatLogSchema, CreateChatLogSchema, UpdateChatLogSchema

##
# 数据库数据访问层
##


class BaseDAO(Generic[ModelType, CreateSchema, UpdateSchema, CompleteSchema]):
    model: ModelType

    def get(self, session: Session, offset=0, limit=10) -> List[ModelType]:
        result = session.query(self.model).offset(offset).limit(limit).all()
        return result

    def get_by_id(self, session: Session, pk: int, ) -> ModelType:
        return session.query(self.model).get(pk)

    def create(self, session: Session, obj_in: CreateSchema) -> ModelType:
        """
        Create

        Raises:
            IntegrityError: If there is a database integrity error.
        """
        obj = self.model(**jsonable_encoder(obj_in))
        session.add(obj)
        try:   
            session.commit()
            return obj
        except IntegrityError as e:
            session.rollback()
            print("Catch in DAO")
            raise e

    def patch(self, session: Session, pk: int, obj_in: UpdateSchema) -> ModelType:
        """Patch"""
        obj = self.get_by_id(session, pk)
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(obj, key, val)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, pk: int) -> None:
        """Delete"""
        obj = self.get_by_id(session, pk)
        session.delete(obj)
        session.commit()

    def count(self, session: Session):
        return session.query(self.model).count()


class UserInfoDAO(BaseDAO[UserInfo, CreateUserInfoSchema, UpdateUserInfoSchema, UserInfoSchema]):
    model = UserInfo

    def get_by_name(self, session: Session, name: str) -> UserInfo:
        try:
            return session.query(self.model).filter(self.model.username == name).first()
        except NoResultFound as e:
            raise e

    def delete(self, session: Session, pk: int) -> None:
        """Delete"""
        temp = UpdateUserInfoSchema()
        temp.valid = False
        super().patch(session, pk, temp)

class AdminInfoDAO(BaseDAO[AdminInfo, CreateAdminInfoSchema, UpdateAdminInfoSchema, AdminInfoSchema]):
    model = AdminInfo

    def get_by_name(self, session: Session, name: str) -> UserInfo:
        try:
            return session.query(self.model).filter(self.model.username == name).first()
        except NoResultFound as e:
            raise e

    def delete(self, session: Session, pk: int) -> None:
        """Delete"""
        temp = UpdateAdminInfoSchema()
        temp.valid = False
        super().patch(session, pk, temp)

class FeedbackLogDAO(BaseDAO[FeedbackLog, CreateFeedbackLogSchema, UpdateFeedbackLogSchema, FeedbackLogSchema]):
    model = FeedbackLog

    def create(self, session: Session, obj_in: CreateFeedbackLogSchema) -> FeedbackLog:
        """Create"""
        obj = self.model(**jsonable_encoder(obj_in))
        obj.userinfo = session.query(UserInfo).get(obj_in.user_id)
        # obj.create_time = datetime.now()
        session.add(obj)
        session.commit()
        return obj

    def patch(self, session: Session, pk: int, obj_in: UpdateSchema) -> ModelType:
        """Patch"""
        obj = self.get_by_id(session, pk)
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(obj, key, val)
            if key == 'admin_id':
                obj.admininfo = session.query(AdminInfo).get(val)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    
class RelationNodeDAO(BaseDAO[RelationNode, CreateRelationNodeSchema, UpdateRelationNodeSchema, RelationNodeSchema]):
    model = RelationNode

    def create(self, session: Session, obj_in: CreateRelationNodeSchema) -> RelationNode:
        """Create"""
        obj = self.model(**jsonable_encoder(obj_in))
        obj.userinfo = session.query(UserInfo).get(obj_in.user_id)
        session.add(obj)
        session.commit()
        return obj

class RelationEdgeDAO(BaseDAO[RelationEdge, CreateRelationEdgeSchema, UpdateRelationEdgeSchema, RelationEdgeSchema]):
    model = RelationEdge

    def create(self, session: Session, obj_in: CreateRelationEdgeSchema) -> RelationEdge:
        """Create"""
        obj = self.model(**jsonable_encoder(obj_in))
        obj.userinfo = session.query(UserInfo).get(obj_in.user_id)
        session.add(obj)
        session.commit()
        return obj
    
class ContextLogDAO(BaseDAO[ContextLog, CreateContextLogSchema, UpdateSchema, ContextLogSchema]):
    model = ContextLog

    def create(self, session: Session, obj_in: CreateContextLogSchema) -> ContextLog:
        """Create"""
        obj = self.model(**jsonable_encoder(obj_in))
        obj.userinfo = session.query(UserInfo).get(obj_in.user_id)
        # obj.create_time = datetime.now()
        session.add(obj)
        session.commit()
        return obj
    
    # def patch(self, session: Session, pk: int, obj_in: UpdateSchema) -> ModelType:
    #     """Patch"""
    #     pass

class ChatLogDAO(BaseDAO[ChatLog, CreateChatLogSchema, UpdateChatLogSchema, ChatLogSchema]):
    model = ChatLog

    def create(self, session: Session, obj_in: CreateChatLogSchema) -> ChatLog:
        """Create"""
        obj = self.model(**jsonable_encoder(obj_in))
        obj.contextlog = session.query(ContextLog).get(obj_in.contextLog_id)
        # obj.chat_time = datetime.now()
        obj.valid = True
        session.add(obj)
        session.commit()
        return obj

    def delete(self, session: Session, pk: int) -> None:
        """Delete"""
        temp = UpdateChatLogSchema()
        temp.valid = False
        super().patch(session, pk, temp)
