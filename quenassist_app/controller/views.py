import json
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound

from quenassist_app.controller.dependencies import get_db

from quenassist_app.service.business.LLM.assistance import assistClient
from quenassist_app.service.mysql.models import UserInfo, RelationNode
from quenassist_app.service.mysql.schemas import (
    UserInfoSchema,
    CreateUserInfoSchema,
    UpdateUserInfoSchema,
    RelationNodeSchema,
    RelationEdgeSchema,
    ContextLogSchema,
    CreateContextLogSchema,
    UpdateContextLogSchema,
    ChatLogSchema,
    CreateChatLogSchema,
    UpdateChatLogSchema,
    UpdateRelationNodeSchema,
    UpdateRelationEdgeSchema,
    CreateRelationNodeSchema,
    CreateRelationEdgeSchema,
)
from quenassist_app.service.mysql.service import (
    UserInfoService,
    AdminInfoService,
    FeedbackLogService,
    RelationNodeService,
    RelationEdgeService,
    ChatLogService,
    ContextLogService,
)
from quenassist_app.service.milvus.knowledge import (
    PersonalKnowledgeBase,
)
from quenassist_app.service.milvus.schemas import (
    RelationSchema,
    UpdateRelationSchema,
)

router = APIRouter()

user_info_service = UserInfoService()
admin_info_service = AdminInfoService()
feedback_log_service = FeedbackLogService()
relation_node_service = RelationNodeService()
relation_edge_service = RelationEdgeService()
context_log_service = ContextLogService()
chat_log_service = ChatLogService()


def user_info_to_schema(user: UserInfo):
    user_schema = UserInfoSchema(
        id=user.id,
        account=user.account,
        password=user.password,
        visit_count=user.visit_count,
        username=user.username,
        phone=user.phone,
        valid=user.valid,
    )
    return user_schema


# @router.get("/test/1")
# def get_hello():
#     return {"Hello": "World"}


# @router.post("/test/2")
# def post_temp(temp: int):
#     return {"Temp", temp}


# @router.get("/")
# def get_user_id(user_id: int):
#     if not user_id:
#         return {"User ID", -1}
#     return {"User ID", user_id}


@router.post("/login/login/", response_model=UserInfoSchema)
async def log_in(request: Request, session: Session = Depends(get_db)):
    request_json = await request.json()
    username = request_json["username"]
    password = request_json["password"]
    if not (0 < len(username) <= 50 and 0 < len(password) <= 100):
        raise HTTPException(
            status_code=401, detail="Username or password format too long or too short"
        )
    try:
        user = user_info_service.get_by_name(session=session, name=username)
    except NoResultFound as e:
        raise HTTPException(status_code=401, detail="Incorrect username")

    if not user or not user.valid:
        raise HTTPException(status_code=401, detail="Incorrect username")
    if user.password != password:
        raise HTTPException(status_code=401, detail="Incorrect password")
    if not user.account:
        user_info_service.patch(
            session=session,
            pk=user.id,
            obj_in=UpdateUserInfoSchema(account="U" + str(user.id)),
        )
    user_schema = user_info_to_schema(user)
    return user_schema


@router.post("/register/register/")
async def register(
    request: Request,
    session: Session = Depends(get_db),
):
    request_json = await request.json() # json.loads(request)
    username = request_json["name"]
    password = request_json["password"]
    phone = request_json["tel"]
    if not (0 < len(username) <= 50 and 0 < len(password) <= 100):
        raise HTTPException(
            status_code=401, detail="Incorrect username or password format"
        )
    if not (0 < len(phone) <= 20):
        raise HTTPException(status_code=401, detail="Incorrect phone number format")
    # 发送验证码
    # 验证验证码
    try:
        user_info_service.create(
            session=session,
            obj_in=CreateUserInfoSchema(
                password=password, username=username, phone=phone
            ),
        )
    except IntegrityError as e:
        raise HTTPException(status_code=401, detail="Username already exists")
    return {"ok": True}

class ResponseUserInfo(BaseModel):
    user_info: UserInfoSchema
    ok: bool


@router.post(path="/user_info/", response_model=ResponseUserInfo)
async def get_user_info(request: Request, session: Session = Depends(get_db)):
    request_json = await request.json()
    user_id = request_json["user_id"]
    user = user_info_service.get_by_id(session=session, pk=int(user_id))
    if not user or not user.valid:
        raise HTTPException(status_code=401, detail="Invalid user id")
    user_schema = user_info_to_schema(user)
    return ResponseUserInfo(user_info=user_schema, ok=True) # {"user_info": user_schema, "ok": True}

class RequestUserInfoSchema(BaseModel):
    user_info: UpdateUserInfoSchema
    user_id: str

@router.post(path="/user_info/patch/")
async def patch_user_info(
    request: RequestUserInfoSchema,
    session: Session = Depends(get_db),
):
    user_id = request.user_id
    # user = user_info_service.get_by_id(session=session, pk=int(user_id))
    # if not password:
    #     password = user.password
    # if not username:
    #     username = user.username
    # if not phone:
    #     phone = user.phone
    # user_new = UpdateUserInfoSchema(
    #     password=password,
    #     username=username,
    #     phone=phone,
    # )
    try:
        user_info_service.patch(session=session, pk=int(user_id), obj_in=request.user_info)
    except IntegrityError as e:
        raise HTTPException(status_code=401, detail="Username already exists")
    return {"ok": True}


@router.post(
    path="/user/{user_id}/assist/relation",
    response_model=dict,
)
async def get_relationship(user_id: str, session: Session = Depends(get_db)):
    relation_nodes = user_info_service.get_by_id(
        session=session, pk=int(user_id)
    ).nodes_of_user
    nodes_schema = []
    for n in relation_nodes:
        node_schema = RelationNodeSchema(
            id=n.id,
            user_id=n.user_id,
            node_address=n.node_address,
            x_axis=n.x_axis,
            y_axis=n.y_axis,
        )
        nodes_schema.append(node_schema)
    relation_edges = user_info_service.get_by_id(
        session=session, pk=int(user_id)
    ).edges_of_user
    edges_schema = []
    for n in relation_edges:
        edge_schema = RelationEdgeSchema(
            id=n.id, user_id=n.user_id, source=n.source, target=n.target
        )
        edges_schema.append(edge_schema)
    return {"nodes_list": nodes_schema, "edges_list": edges_schema}


# 前端请求发送格式：
# {
#     "user_id": "1",
#     "delete_nodes_id": [2, 3],
#     "delete_edges_id": [1],
#     "create_nodes_schema": {
#         1: {"user_id": 3, "node_address": "1", "x_axis": 30, "y_axis": 20},
#         2: {"user_id": 3, "node_address": "2", "x_axis": 20, "y_axis": 20},
#     },
#     "create_edges_schema": [{"user_id": 3, "source": -1, "target": -2, "relation": "XXX"}],
#     "update_nodes_schema": {
#         3: {"node_address": "shit", "x_axis": 1.14514, "y_axis": 2},
#         4: {"node_address": "gosh", "x_axis": 4, "y_axis": 5},
#     },
#     "update_edges_schema": {2: {"source": 3, "target": 4, "relation": "XXX"}},
# }
@router.post(path="/user/{user_id}/assist/relation/save/")
async def save_relationship(
    user_id: str,
    request: str,
    session: Session = Depends(get_db),
):
    # data = await request.json()
    data = json.loads(request)
    # if not data:
    #     return RedirectResponse(url="/user/{user_id}/assist")

    delete_nodes_id: list[int] = data.get("delete_nodes_id", [])
    delete_edges_id: list[int] = data.get("delete_edges_id", [])
    create_nodes_schema: dict[int, Dict] = data.get("create_nodes_schema", {})
    create_edges_schema: list[Dict] = data.get("create_edges_schema", [])
    update_nodes_schema: dict[int, Dict] = data.get("update_nodes_schema", {})
    update_edges_schema: dict[int, Dict] = data.get("update_edges_schema", {})

    new_nodes: dict[int, int] = {}

    user_kb = PersonalKnowledgeBase(int(user_id))

    for n in delete_nodes_id:
        relation_node_service.delete(session=session, pk=n)
    for n in delete_edges_id:
        relation_edge_service.delete(session=session, pk=n)
        # 修改向量数据库 relationship
        user_kb.delete_relation(n)
    for n in create_nodes_schema:
        tmp_id = relation_node_service.create(
            session=session,
            obj_in=CreateRelationNodeSchema.parse_obj(create_nodes_schema[n]),
        ).id
        new_nodes[int(n)] = tmp_id
    for n in create_edges_schema:
        if n["source"] < 0:
            n["source"] = new_nodes[-n["source"]]
        if n["target"] < 0:
            n["target"] = new_nodes[-n["target"]]
        tmp_id = relation_edge_service.create(
            session=session, obj_in=CreateRelationEdgeSchema.parse_obj(n)
        ).id
        # 修改向量数据库 relationship
        user_kb.insert_relation(
            RelationSchema(
                subject="Me",
                object=relation_node_service.get_by_id(
                    session=session, pk=n["target"]
                ).node_address,
                relation=n["relation"],
                edge_id=tmp_id,
            )
        )
    for n in update_nodes_schema:
        relation_node_service.patch(
            session=session,
            pk=n,
            obj_in=UpdateRelationNodeSchema.parse_obj(update_nodes_schema[n]),
        )
    for n in update_edges_schema:
        relation_edge_service.patch(
            session=session,
            pk=n,
            obj_in=UpdateRelationEdgeSchema.parse_obj(update_edges_schema[n]),
        )
        # 修改向量数据库 relationship
        user_kb.update_relation(
            UpdateRelationSchema(
                object=relation_node_service.get_by_id(
                    session=session, pk=update_edges_schema[n]["target"]
                ).node_address,
                relation=update_edges_schema[n]["relation"],
                edge_id=n
            )
        )
    return RedirectResponse(url="/user/" + user_id + "/assist/relation/")

class ResponceContext(BaseModel):
    contexts_list: List[ContextLogSchema]
    ok: bool

@router.post(
    path="/chat/get_contexts/", response_model=ResponceContext
)
async def get_contexts(request: Request, session: Session = Depends(get_db)):
    request_json = await request.json()
    user_id = request_json["user_id"]
    contexts = user_info_service.get_by_id(
        session=session, pk=int(user_id)
    ).contexts_of_user
    contexts_schema = []
    for n in contexts:
        context_schema = ContextLogSchema(
            id=n.id,
            user_id=n.user_id,
            create_time=n.create_time,
            theme=n.theme,
        )
        contexts_schema.append(context_schema)
    return ResponceContext(contexts_list=contexts_schema, ok=True) # {"contexts_list": contexts_schema, "ok": True}


@router.post(
    path="/chat/content/",
    response_model=dict,
)
async def get_chats(request: Request, session: Session = Depends(get_db)):
    request_json = await request.json()
    # user_id = request_json["user_id"]
    context_id = request_json["context_id"]
    chats = context_log_service.get_by_id(
        session=session, pk=int(context_id)
    ).chats_of_context
    chats_schema = []
    for n in chats:
        if n.valid:
            chat_schema = ChatLogSchema(
                id=n.id,
                contextLog_id=n.contextLog_id,
                chat=n.chat,
                chat_time=n.chat_time,
                who=n.who,
                valid=n.valid,
            )
            chats_schema.append(chat_schema)
    return {"chats_list": chats_schema, "ok": True}


@router.post(path="/chat/new/")
async def new_context(request: Request, session: Session = Depends(get_db)):
    request_json = await request.json()
    user_id = request_json["user_id"]
    context_schema = CreateContextLogSchema(user_id=user_id)
    context_id = context_log_service.create(session=session, obj_in=context_schema).id
    return {"context_id": context_id, "ok": True}


@router.post(path="/chat/delete/")
async def delete_context(
    request: Request, session: Session = Depends(get_db)
):
    request_json = await request.json()
    user_id = request_json["user_id"]
    context_id = request_json["context_id"]
    context = context_log_service.get_by_id(session=session, pk=int(context_id))
    for n in context.chats_of_context:
        chat_log_service.delete(session=session, pk=n.id)
    context_log_service.delete(session=session, pk=int(context_id))
    # 删除向量数据库 context
    user_kb = PersonalKnowledgeBase(int(user_id))
    user_kb.delete_context(int(context_id))
    return {"ok": True}


@router.post(
    path="/chat/ask/", response_model=dict
)
async def ask(
    request: Request, session: Session = Depends(get_db)
):
    request_json = await request.json()
    user_id = request_json["user_id"]
    context_id = request_json["context_id"]
    q = request_json["q"]
    if context_log_service.get_by_id(session=session, pk=int(context_id)).theme == "New Session":
        context_log_service.patch(
            session=session,
            pk=int(context_id),
            obj_in=UpdateContextLogSchema(theme=q),
        )
    chat_log_service.create(
        session=session,
        obj_in=CreateChatLogSchema(
            contextLog_id=int(context_id),
            chat=q,
            chat_time=datetime.now().time(),
            who=True,
        ),
    )
    # assist_client = assistClient(user_id=int(user_id), contextLog_id=int(context_id))
    # a = assist_client.start_question(q)
    a = "this is an answer"
    chat_log_service.create(
        session=session,
        obj_in=CreateChatLogSchema(
            contextLog_id=int(context_id),
            chat=a,
            chat_time=datetime.now().time(),
            who=False,
        ),
    )
    # 加入向量数据库 q&a
    # user_kb = PersonalKnowledgeBase(int(user_id))
    # user_kb.insert_context(int(context_id), f"{{question: {q}, answer: {a}}}")
    return {"answer": a, "ok": True}


@router.post(path="/user/{user_id}/assist/knowledge_base/add/")
def add_knowledge_base(user_id: str, files: List[UploadFile] = File(...)):
    user_kb = PersonalKnowledgeBase(int(user_id))
    user_kb.insert_online(files)
    return RedirectResponse(url="/user/" + user_id + "/assist/")
