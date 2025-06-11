from fastapi import UploadFile
from quenassist_app.service.milvus.knowledge import KnowledgeBase, GlobalKnowledgeBase, PersonalKnowledgeBase

# Service端处理上传个人知识库文件
def load_file_personal(file: UploadFile, user_base: PersonalKnowledgeBase) -> bool:
    pass

# Service端处理上传全局知识库文件（管理端）
def load_file_global(file: UploadFile, global_base: GlobalKnowledgeBase) -> bool:
    pass

# Service端处理上传个人关系网络
def load_personal_relationShip(relationShip: dict, user_base: PersonalKnowledgeBase) -> bool:
    pass

