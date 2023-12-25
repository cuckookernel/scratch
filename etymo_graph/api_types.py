from typing import List

from pydantic import BaseModel


class NodeData(BaseModel):
    id: str
    label: str
    lang: str
    bg_color: str
    border_color: str


class NodeR(BaseModel):
    data: NodeData

class EdgeData(BaseModel):
    id: str
    source: str
    target: str
    label: str
    length: float

class EdgeR(BaseModel):
    data: EdgeData

class GraphElemsR(BaseModel):
    nodes: List[NodeR]
    edges: List[EdgeR]

