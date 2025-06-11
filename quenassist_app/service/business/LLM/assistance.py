# Import setting
from typing import List
from typing_extensions import TypedDict
from pprint import pprint
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, NVIDIARerank
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers import EnsembleRetriever
from langgraph.graph import END, StateGraph, START

from gradio_client import Client

from quenassist_app.service.business.LLM.models import GraphState, AgentActionTypes, SocialScene, SubQuery, GradeDocuments, GradeHallucinations, GradeAnswer, TaskType, SceneType
from quenassist_app.service.business.LLM.llama import llamaClient
from quenassist_app.service.milvus.knowledge import KnowledgeBase, GlobalKnowledgeBase, PersonalKnowledgeBase
from quenassist_app.service.business.LLM.models import GraphState

# llm = llamaClient()

reranker = NVIDIARerank(
    base_url="http://localhost:8800/v1", 
    model="nvidia/nv-rerankqa-mistral-4b-v3",
    truncate="END"
)

llm = ChatOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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",
    model="meta/llama-3.1-405b-instruct"
)

quen_llm = Client("http://120.76.130.14:6006/prompt/")

sub_question_generator = llm.with_structured_output(SubQuery)

### Getrieval_grader创建
retrieval_grader = llm.with_structured_output(GradeDocuments)
# Prompt
system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

grade_prompt = ChatPromptTemplate.from_messages(
    [
     
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)
retrieval_grader = grade_prompt | retrieval_grader

### Hallucination_grader创建
hallucination_grader = llm.with_structured_output(GradeHallucinations)
# Prompt
system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)
hallucination_grader = hallucination_prompt | hallucination_grader

### Answer Grader创建
generation_grader = llm.with_structured_output(GradeAnswer)
# Prompt
system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)
answer_grader = answer_prompt | generation_grader

### Task Decider
task_decider = llm.with_structured_output(TaskType)
# Prompt
system = """You are a task decider that determines the type of task a user question is related to. \n
     The task types are: '敬酒', '请客', '送礼', '送祝福', '人际交流', '化解尴尬' or '矛盾应对'. \n
     You should consider the underlying semantic intent / meaning of the user question and pick a task type among
     the the given task types above."""
task_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n Determine the task type."),
    ]
)
task_decider = task_prompt | task_decider

### Scene Decider
scene_decider = llm.with_structured_output(SceneType)
# Prompt
scene_system = """You are a scene decider that determines the scene type among a given scene types set. \n
        Give a scene type that is picked from the given scene types set and the most relevant one to the given task type."""

scene_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", scene_system),
        ("human", "User question: \n\n {question} \n\n Task type: \n\n {task_type} \n\n Scenes set: \n\n {scenes_set} \n\n Determine the scene type."),
    ]
)
scene_decider = scene_prompt | scene_decider

### Question Re-writer
# Prompt
system = """You a question re-writer that converts an input question to a better version that is optimized \n 
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "Here is the initial question: \n\n {question} \n Formulate an improved question.",
        ),
    ]
)
question_rewriter = re_write_prompt | llm | StrOutputParser()

# Nodes
def decide_task_type(state: GraphState) -> dict:
    """
    Decide question task type

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, social_scene, that contains task type
    """
    print("---TASK DECIDER---")
    question = state["question"]

    # Task type
    task_type = task_decider.invoke(question)
    Social_scene = SocialScene(task=task_type)
    return {"social_scene": Social_scene, "question": question}


def decide_scene(state: GraphState) -> dict:
    """
    Decide scene type

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Update social_scene, that add scene type
    """
    print("---SCENE DECIDER---")
    question = state["question"]
    social_scene = state["social_scene"]
    task_type = social_scene.task

    # Scene type
    scenes_dict = quen_llm.predict(
        task_type,
        api_name="/cls_choose_change"
    )
    scene_list = list(scenes_dict.keys())
    scenes_set = ", ".join(scene_list)
    scene_type = scene_decider.invoke(question, task_type, scenes_set)
    social_scene.scene = scene_type
    return {"social_scene": social_scene, "question": question}

def decompose(state: GraphState) -> dict:
    print("---QUERY DECOMPOSITION ---")
    question = state["question"]
    social_scene = state["social_scene"]

    # Reranking
    sub_queries = sub_question_generator.invoke(question)
    return {"sub_questions": sub_queries.questions, "question": question, "social_scene": social_scene}

### Higher order
def get_retriever(user_id: int, contextLog_id: int):
    personal_vb = PersonalKnowledgeBase(user_id=user_id)
    global_vb = GlobalKnowledgeBase()
    retrievers = [personal_vb.retriever, global_vb.retriever]
    hybrid_retriever = EnsembleRetriever(
        retrievers=retrievers, 
        weight=[0.6, 0.3],
    )

    def retriever(state: GraphState) -> dict:
        """
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        print("---RETRIEVE---")
        sub_questions = state["sub_questions"]
        question = state["question"]
        social_scene = state["social_scene"]

        # Retrieval
        documents = []
        context_documents = []
        for sub_question in sub_questions:
            docs = hybrid_retriever.get_relevant_documents(sub_question)
            documents.extend(docs)
        context_docs = personal_vb.search_context(contextLog_id)
        context_documents.extend(context_docs)
        relation = personal_vb.search_relation(contextLog_id)[0]
        social_scene.relationShip = relation.page_content
        return {"documents": documents, "question": question, "social_scene": social_scene, "context": context_documents}
    
    return retriever

def rerank(state: GraphState) -> dict:
    print("---RERANK---")
    question = state["question"]
    documents = state["documents"]
    social_scene = state["social_scene"]
    context_documents = state["context"]

    # Reranking
    documents = reranker.compress_documents(query=question, documents=documents)
    return {"documents": documents, "question": question, "social_scene": social_scene, "context": context_documents}

def generate(state: GraphState) -> dict:
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    social_scene = state["social_scene"]
    context_documents = state["context"]

    question_with_docs = question + " " + social_scene.relationShip + " ".join(documents)
    context_str = " ".join(context_documents)
    
    # Generation
    result_prompt = quen_llm.predict(
        social_scene.scene,
        api_name="/get_system_prompt_by_name",
    )

    generation = quen_llm.predict(
        result_prompt,
        question_with_docs,
        [[context_str, None]],
        api_name="/respond",
    )

    return {"generation": generation, "question": question, "social_scene": social_scene, "documents": documents, "context": context_documents}

def grade_documents(state: GraphState) -> dict:
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]
    social_scene = state["social_scene"]
    context_documents = state["context"]

    # Score each doc
    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question, "social_scene": social_scene, "context": context_documents}

def transform_query(state: GraphState) -> dict:
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]
    social_scene = state["social_scene"]
    context_documents = state["context"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    return {"documents": documents, "question": better_question, "social_scene": social_scene, "context": context_documents}

# Edges
def decide_to_generate(state: GraphState) -> str:
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    # We have relevant documents, so generate answer
    print("---DECISION: GENERATE---")
    return "generate"

def grade_generation_v_documents_and_question(state: GraphState) -> str:
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    social_scene = state["social_scene"]
    context_documents = state["context"]

    grade_docs = []
    grade_docs.extend(documents)
    grade_docs.extend(context_documents)
    grade_docs.append(social_scene.relationShip)

    score = hallucination_grader.invoke(
        {"documents": grade_docs, "generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
        return "not useful"
    print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
    return "not supported"

class assistClient:
    # 初始化社交助手
    def __init__(self, user_id: int, contextLog_id: int = None) -> None:
        self.user_id = user_id
        self.contextLog_id = contextLog_id
        self.retriever = get_retriever(user_id, contextLog_id)
        self.workflow = StateGraph(GraphState)
        self.build_workflow()
        self.app = self.workflow.compile()

    def build_workflow(self) -> bool:
        # Define the nodes
        self.workflow.add_node("decide_task_type", decide_task_type)
        self.workflow.add_node("decide_scene", decide_scene)
        self.workflow.add_node("decompose", decompose)
        self.workflow.add_node("retriever", self.retriever)
        self.workflow.add_node("rerank", rerank)
        self.workflow.add_node("grade_documents", grade_documents)
        self.workflow.add_node("generate", generate)
        self.workflow.add_node("transform_query", transform_query)

        # Build the edges
        self.workflow.add_edge(START, "decide_task_type")
        self.workflow.add_edge("decide_task_type", "decide_scene")
        self.workflow.add_edge("decide_scene", "decompose")
        self.workflow.add_edge("decompose", "retriever")
        self.workflow.add_edge("retriever", "rerank")
        self.workflow.add_edge("rerank", "grade_documents")
        self.workflow.add_conditional_edges(
            "grade_documents",
            decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
            },
        )
        self.workflow.add_conditional_edges(
            "generate",
            grade_generation_v_documents_and_question,
            {
                "useful": END,
                "not useful": "transform_query",
                "not supported": "generate",
            },
        )


    def load_history(self, contextLog_id: int) -> bool:
        pass

    def start_question(self, question: str) -> str:
        inputs = {"question": question}
        for output in self.app.stream(inputs):
            for key, value in output.items():
                # Node
                pprint(f"Node '{key}':")
                # Optional: print full state at each node
                # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
            pprint("\n---\n")
        # Final generation
        return value["generation"]
        



# # 作为
# class Ledger:
#     def __init__(self) -> None:
#         pass

# class assistClient:
#     # 初始化社交助手
#     def __init__(self, user: str) -> None:
#         pass

#     # 获取助手所属用户
#     @property
#     def assist_user() -> str:
#         pass

#     # 加载历史上下文
#     def load_history(self, contxt_id: str) -> bool:
#         pass

#     # 开始提问并获取回答
#     def start_question(self, question: str) -> str:
#         pass
    
#     # 调用代理核心判断机制，判断代理所使用工具
#     def agent_core(self, question: str, history: List) -> str:
#         pass
    
#     def update_agent_memory(self, question: str, response: str) -> None:
#         pass

#     # 搜索工具，调用知识库中的信息
#     def search_tool(self, question: str) -> str:
#         pass

#     def decompose_helper(self, question: str) -> str:
#         pass


# class assistClient:
#     def __init__(self) -> None:
#         # 初始化对话历史
#         self.memory = ConversationBufferMemory()

#         # 初始化向量数据库
#         self.vectorstore = Milvus(
#             collection_name="chat_history",
#             embedding_function=OpenAIEmbeddings()
#         )

#         # 初始化代理
#         self.agent = initialize_agent(
#             tools=load_tools(),
#             agent_type=AgentType.CHAT,
#             memory=self.memory
#         )

#     def load_history(self) -> bool:
#         # 从向量数据库加载历史记录
#         history = self.vectorstore.search("previous conversations")
#         if history:
#             self.memory.load(history)
#             return True
#         return False

#     def start_question(self, question: str):
#         # 使用代理回答问题，并记录对话历史
#         response = self.agent.run(question)
#         # 将对话历史存储到向量数据库
#         self.vectorstore.add_texts([question, response])
#         return response

# # 示例使用
# if __name__ == "__main__":
#     client = assistClient()
#     client.load_history()
#     print(client.start_question("你好，今天的天气怎么样？"))
#     print(client.start_question("明天呢？"))
