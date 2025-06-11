from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import S3FileLoader, DirectoryLoader

import boto3
from botocore.config import Config
from uuid import uuid5, NAMESPACE_DNS
import json

from datetime import datetime

from fastapi import UploadFile

from quenassist_app.service.milvus.milvus_db import vector_store_global, vector_store_user
from quenassist_app.service.milvus.schemas import RelationSchema, UpdateRelationSchema

s3_bucket =  "quenassist"
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)


class KnowledgeBase:
    def __init__(self):
        pass

    def insert(self, data):
        # Insert data into collection
        pass

    def search(self, data, top_k):
        # Search data in collection
        pass

class GlobalKnowledgeBase(KnowledgeBase):
    def __init__(self):
        super().__init__()
        self.vector_store = vector_store_global
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})
        self.local_file_type = ["**/*.pdf", "**/*.doc", "**/*.docx", "**/*.txt"]


    def insert_online(self, upload_files: List[UploadFile]) -> bool:
        """Insert online uploaded files into collection"""
        session = boto3.Session()
        s3_client = session.client('s3', config=Config(signature_version='s3v4'))
        
        all_docs = []
        for file in upload_files:
            file_id = uuid5(NAMESPACE_DNS, str(datetime.now()))
            s3_client.upload_fileobj(File_obj=file, Bucket=s3_bucket, Key=file_id)
            loader = S3FileLoader(file_id, s3_bucket)
            doc = loader.load()
            all_docs.extend(doc)

        doc_splits = text_splitter.split_documents(all_docs)
        uuids = [str(uuid5(NAMESPACE_DNS, str(datetime.now()) + str(i))) for i in range(len(doc_splits))]
        self.vector_store.add_documents(ids=uuids, documents=doc_splits)
        return True


    def insert_offline(self, dir_path: str) -> bool:
        """Insert local files into collection"""
        for file_type in self.local_file_type:
            loader = DirectoryLoader(dir_path, glob=file_type)
            docs = loader.load()
            doc_splits = text_splitter.split_documents(docs)
            uuids = [str(uuid5(NAMESPACE_DNS, str(datetime.now()) + str(i))) for i in range(len(doc_splits))]
            self.vector_store.add_documents(ids=uuids, documents=doc_splits)
        return True

    def search(self, question: str) -> List[Document]:
        """Search files in collection"""
        return self.retriever.get_relevant_documents(question)

class PersonalKnowledgeBase(KnowledgeBase):
    def __init__(self, user_id: int):
        super().__init__()
        self.vector_store = vector_store_user
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 2, "expr": 'namespace == ' + str(user_id)})
        self.retriever_relation = self.vector_store.as_retriever(search_kwargs={"k": 2, "expr": 'namespace == ' + str(user_id) + ' and type == "relation"'})
        self.user_id = user_id

    def insert_online(self, upload_files: List[UploadFile]) -> bool:
        """Insert online uploaded files into collection"""
        session = boto3.Session()
        s3_client = session.client('s3', config=Config(signature_version='s3v4'))
        
        all_docs = []
        for file in upload_files:
            file_id = uuid5(NAMESPACE_DNS, str(datetime.now()))
            s3_client.upload_fileobj(File_obj=file, Bucket=s3_bucket, Key=file_id)
            loader = S3FileLoader(file_id, s3_bucket)
            doc = loader.load()
            all_docs.extend(doc)

        doc_splits = text_splitter.split_documents(all_docs)
        for doc in doc_splits:
            doc.metadata["user_id"] = self.user_id
        uuids = [str(uuid5(NAMESPACE_DNS, str(self.user_id) + str(datetime.now()) + str(i))) for i in range(len(doc_splits))]
        self.vector_store.add_documents(ids=uuids, documents=doc_splits)
        return True
    
    def insert_relation(self, relation: RelationSchema) -> bool:
        """Insert relation into collection"""
        page_content = relation.model_dump_json()
        doc = Document(page_content=page_content, metadata={"user_id": self.user_id, "type": "relation"})
        self.vector_store.add_documents(ids=[str(uuid5(NAMESPACE_DNS, str(self.user_id) + 'relation' + str(relation.edge_id)))], documents=[doc])
        return True
    
    def insert_context(self, contextLog_id: int, context: str) -> bool:
        """Insert context into collection"""
        docs = self.vector_store.get_by_ids([str(uuid5(NAMESPACE_DNS, str(self.user_id) + 'context' + str(contextLog_id)))])
        if docs:
            doc = docs[0]
            doc.page_content += "\n" + context
        else:
            doc = Document(page_content=context, metadata={"user_id": self.user_id, "contextLog_id": contextLog_id})
        self.vector_store.add_documents(ids=[str(uuid5(NAMESPACE_DNS, str(self.user_id) + 'context' + str(contextLog_id)))], documents=[doc])
        return True
    
    def update_relation(self, relation: UpdateRelationSchema) -> bool:
        """Update relation in collection"""
        update = relation.model_dump(exclude_unset=True)
        docs = self.vector_store.get_by_ids([str(uuid5(NAMESPACE_DNS, str(self.user_id) + 'relation' + str(relation.edge_id)))])
        if docs:
            doc = docs[0]
            doc_dict = json.loads(doc.page_content)
            for key, value in update.items():
                doc_dict[key] = value
            doc.page_content = json.dumps(doc_dict)
            self.vector_store.add_documents(ids=[str(uuid5(NAMESPACE_DNS, str(self.user_id) + 'relation' + str(relation.edge_id)))], documents=[doc])
            return True
        return False
    
    def delete_relation(self, edge_id: int) -> bool:
        """Delete relation from collection"""
        self.vector_store.delete(ids=[str(uuid5(NAMESPACE_DNS, str(self.user_id) + 'relation' + str(edge_id)))])
        return True

    def delete_context(self, contextLog_id: int) -> bool:
        """Delete context from collection"""
        self.vector_store.delete(ids=[str(uuid5(NAMESPACE_DNS, str(self.user_id) + 'context' + str(contextLog_id)))])
        return True

    def search(self, question: str) -> List[Document]:
        """Search files in collection"""
        return self.retriever.get_relevant_documents(question)
    
    def search_relation(self, question: str) -> List[Document]:
        """Search relation in collection"""
        return self.retriever_relation.get_relevant_documents(question)
    
    def search_context(self, contextLog_id: int) -> List[Document]:
        """Search context in collection"""
        return self.vector_store.get_by_ids([str(uuid5(NAMESPACE_DNS, str(contextLog_id)))])
    

