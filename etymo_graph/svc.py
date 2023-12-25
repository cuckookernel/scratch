"""Backend to graph visualizer"""
from http import HTTPStatus
from typing import Dict, Optional

from api_types import *
from fastapi import FastAPI, Response
from kb import KnowledgeBase, Node, make_knowledge_base, render_graph_to_html

app = FastAPI()

CACHE: Dict[str, KnowledgeBase] = {"kb": None}


@app.on_event("startup")
async def _on_startup():
    print("on startup: making knowledge base")
    CACHE["kb"] = make_knowledge_base()


def get_kb() -> KnowledgeBase:
    kb_ = CACHE["kb"]
    assert kb_ is not None
    return kb_


@app.get('/')
async def root(uris: Optional[str]):
    if uris is None:
        selected0 = ["pereza@spa"]
    else:
        selected0 = uris.split(',')

    kb = get_kb()

    selected = [x for x in selected0 if x in kb.nodes]
    if len(selected) > 0:
        return Response(render_graph_to_html(kb, selected=selected), media_type='text/html')
    else:
        return Response(f"Not found in kb: {selected0}", status_code=HTTPStatus.NOT_FOUND)


@app.get('/children')
async def ancestors(word_uri: str):
    kb = get_kb()
    node: Node = kb.nodes.get(word_uri)
    if node is None:
        return Response(f"Not found in kb: {word_uri}", status_code=HTTPStatus.NOT_FOUND)

    ret_edges = []
    ret_nodes = []
    added_node_uris = set()

    print(f"word_uri={word_uri} nodes.edges_in = {node.edges_in}")

    for edge in node.edges_out:
        show_rel = edge.data['rel'].replace('_', ' ') + ":"

        ret_edge = EdgeR(data=EdgeData(id=edge.id(),
                                       source=edge.source.uri,
                                       target=edge.target.uri,
                                       label=show_rel,
                                       length=100))
        ret_edges.append(ret_edge)

        target_uri = edge.target.uri
        if target_uri not in added_node_uris:
            node = kb.nodes[target_uri]
            data = NodeData(id=target_uri, label=node.text,
                            lang=str(node.lang),
                            bg_color=node.bg_color(),
                            border_color=node.border_color())
            ret_node = NodeR(id=target_uri, data=data)
            ret_nodes.append(ret_node)

    return GraphElemsR(nodes=ret_nodes, edges=ret_edges)
