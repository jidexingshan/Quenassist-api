from datetime import datetime
from typing import Optional, TypeVar

from pydantic import BaseModel, constr

from quenassist_app.service.mysql.models import BaseModel as DBModel
from quenassist_app.service.mysql.models import UserInfo, AdminInfo, ContextLog

ModelType = TypeVar('ModelType', bound=DBModel)
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
CompleteSchema = TypeVar('CompleteSchema', bound=BaseModel)

##
# 创建在FastAPI相关函数参数中的对象模型
##

class InDBMixin(BaseModel):
    id: int

    class Config:
        orm_mode = True # 也许会出现一些pydantic V2的警告

# 用户信息
class BaseUserInfo(BaseModel):
    pass

class UserInfoSchema(BaseUserInfo, InDBMixin):
    account: constr(max_length=50)
    password: constr(max_length=100)
    visit_count: int = 0
    username: constr(max_length=50)
    phone: Optional[constr(max_length=20)] = None
    valid: bool

class CreateUserInfoSchema(BaseUserInfo):
    password: constr(max_length=100)
    username: constr(max_length=50)
    phone: Optional[constr(max_length=20)] = None

class UpdateUserInfoSchema(BaseModel):
    account: Optional[constr(max_length=50)] = None
    password: Optional[constr(max_length=100)] = None
    visit_count: Optional[int] = None
    username: Optional[constr(max_length=50)] = None
    phone: Optional[constr(max_length=20)] = None
    valid: Optional[bool] = None

# 管理员信息
class BaseAdminInfo(BaseModel):
    pass

class AdminInfoSchema(BaseAdminInfo, InDBMixin):
    account: constr(max_length=50)
    password: constr(max_length=100)
    tackle_count: int = 0
    username: constr(max_length=50)
    valid: bool

class CreateAdminInfoSchema(BaseAdminInfo):
    password: constr(max_length=100)
    username: constr(max_length=50)

class UpdateAdminInfoSchema(BaseModel):
    password: Optional[constr(max_length=100)] = None
    tackle_count: Optional[int] = None
    username: Optional[constr(max_length=50)] = None
    valid: Optional[bool] = None

# 反馈记录
class BaseFeedbackLog(BaseModel):
    # user_account: constr(max_length=50)
    user_id: int
    feedback: str

class FeedbackLogSchema(BaseFeedbackLog, InDBMixin):
    # admin_account: Optional[constr(max_length=50)] = None
    userinfo: Optional[UserInfoSchema] = None
    admin_id: Optional[int] = None
    admininfo: Optional[AdminInfoSchema] = None
    create_time: datetime

class CreateFeedbackLogSchema(BaseFeedbackLog):
    pass

class UpdateFeedbackLogSchema(BaseModel):
    # admin_account: Optional[constr(max_length=50)] = None
    admin_id: Optional[int] = None

# 关系节点
class BaseRelationNode(BaseModel):
    # user_account: constr(max_length=50)
    user_id: int
    node_address: constr(max_length=30)
    x_axis: float
    y_axis: float

class RelationNodeSchema(BaseRelationNode, InDBMixin):
    userinfo: Optional[UserInfoSchema] = None

class CreateRelationNodeSchema(BaseRelationNode):
    pass

class UpdateRelationNodeSchema(BaseModel):
    node_address: Optional[constr(max_length=30)] = None
    x_axis: Optional[float] = None
    y_axis: Optional[float] = None

# 关系边
class BaseRelationEdge(BaseModel):
    # user_account: constr(max_length=50)
    user_id: int
    source: int
    target: int
    relation: str

class RelationEdgeSchema(BaseRelationEdge, InDBMixin):
    userinfo: Optional[UserInfoSchema] = None

class CreateRelationEdgeSchema(BaseRelationEdge):
    pass

class UpdateRelationEdgeSchema(BaseModel):
    source: Optional[int] = None
    target: Optional[int] = None
    relation: Optional[str] = None

# 上下文日志
class BaseContextLog(BaseModel):
    # user_account: constr(max_length=50)
    user_id: int

class ContextLogSchema(BaseContextLog, InDBMixin):
    userinfo: Optional[UserInfoSchema] = None
    theme: Optional[constr(max_length=30)] = None
    create_time: datetime

class CreateContextLogSchema(BaseContextLog):
    pass

class UpdateContextLogSchema(BaseModel):
    theme: Optional[constr(max_length=30)] = None

# class UpdateContextLogSchema(BaseModel):
# 在向量数据库中进行更新操作

# 聊天日志
class BaseChatLog(BaseModel):
    contextLog_id: int
    who: bool
    chat: str

class ChatLogSchema(BaseChatLog, InDBMixin):
    contextlog: Optional[ContextLogSchema] = None
    chat_time: datetime
    valid: bool

class CreateChatLogSchema(BaseChatLog):
    pass

class UpdateChatLogSchema(BaseModel):
    chat: Optional[str] = None
    valid: Optional[bool] = None