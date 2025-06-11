from langchain_milvus import Milvus
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, NVIDIARerank

from quenassist_app.config import settings

# connect to an embedding NIM running at localhost:8080
embeddings = NVIDIAEmbeddings(
    base_url="http://localhost:8000/v1", 
    model="nvidia/nv-embedqa-e5-v5",
    truncate="END"
)

connection_args = {
    'host': settings.VECTORDATABASE.get('HOST', None),
    'port': settings.VECTORDATABASE.get('PORT', None),
    # 'user': settings.VECTORDATABASE.get('USER', None),
    # 'password': settings.VECTORDATABASE.get('PASSWORD', None),
}

vector_store_global = Milvus(
    embedding_function=embeddings,
    connection_args=connection_args,
    drop_old=True,
    collection_name="global",
)

vector_store_user = Milvus(
    embedding_function=embeddings,
    connection_args=connection_args,
    partition_key_field="user_id",
    drop_old=True,
    collection_name="user",
    )
