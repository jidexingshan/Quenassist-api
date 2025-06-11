from pydantic import BaseModel

class RelationSchema(BaseModel):
    subject: str
    object: str
    relation: str
    edge_id: int

class UpdateRelationSchema(BaseModel):
    object: str
    relation: str
    edge_id: int
