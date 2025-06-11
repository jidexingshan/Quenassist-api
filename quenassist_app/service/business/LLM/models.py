from enum import Enum
from pydantic import BaseModel
from langchain_core.pydantic_v1 import Field
from typing import List
from quenassist_app.service.milvus.knowledge import KnowledgeBase
from typing import TypedDict

class AgentActionTypes(str, Enum):
    DECOMPOSITION = "Decomposition"
    GLOBAL_SEARCH_TOOL = "Global Search Tool"
    PERSONAL_SEARCH_TOOL = "Personal Search Tool"
    GENERATEFINALLANSWER = "Generate Final Answer"

class SocialScene(BaseModel):
    """Given a user sub question, extract these four key components that \ 
    we need to find in order to answer this sub question."""
    task: str = Field(
        description="The task of the sub question"
    )
    scene: str = Field(
        description="The scene of the sub question"
    ) 
    relationShip: str = Field(
        description="The relationship between the subject and object"
    )

class SubQuery(BaseModel):
    """Given a user question, break it down into distinct sub questions that \
    you need to answer in order to answer the original question."""
    questions: List[str] = Field(description="The list of sub questions")

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

class TaskType(BaseModel):
    """Task type for the user question."""

    task_type: str = Field(
        description="Task type for the user question, '敬酒', '请客', '送礼', '送祝福', '人际交流', '化解尴尬' or '矛盾应对'"
    )

class SceneType(BaseModel):
    """Scene type for the user question."""

    scene_type: str = Field(
        description="Scene type for the task, should be one of the return value of the gradio when a task type is given"
    )

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    question: str
    sub_questions:  List[str]
    generation: str
    documents: List[str]
    context: List[str]
    social_scene: SocialScene
    # knowledge_base: KnowledgeBase

