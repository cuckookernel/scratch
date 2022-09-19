# %%
"""
process knowledge base contained in words.yaml

https://cvc.cervantes.es/lengua/thesaurus/pdf/09/TH_09_123_007_0.pdf
https://diccionario.reverso.net/espanol-frances/apretar
https://context.reverso.net/traduccion/portugues-espanol/colo

"""
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
from pprint import pprint, pformat
from pathlib import Path
from hashlib import sha256
import base64
import json
import pandas as pd

import yaml
from yaml import Loader
from jinja2 import Environment, select_autoescape, FileSystemLoader


Klass = str

# %%


def _main():
    # %%
    #runfile("etymo_graph/process_kb.py")

    kb = make_knowledge_base()

    # pprint( kb.nodes )
    kb._export_to_csvs()
    html_text = render_graph_to_html(kb, selected=['pereza@spa'])

    out_path = Path( "etymo_graph/out.html" )
    print( f'writing out: {out_path}' )
    out_path.write_text( html_text, encoding="utf8" )

    # %%


COLOR_BY_LANG = {
    "spa": "#ffa",
    "fro": "#9f9",
    "eng": "#7cf",
    ".": "#fff"
}


class Node:
    """An node in the graph"""
    def __init__( self, uri: str, klass: Klass, text: str, lang: str, data: Dict[str, Any] ):
        self.uri: str = uri

        self.text = text
        self.lang = lang

        self.klass: str = klass
        self.data: Dict[str, Any] = data
        self.edges_in: List["Edge"] = []
        self.edges_out: List["Edge"] = []

    def add_edge_in(self, edge: "Edge"):
        """Add incoming edge"""
        self.edges_in.append(edge)

    def add_edge_out(self, edge: "Edge"):
        """Add outcoming edge"""
        self.edges_out.append(edge)

    def bg_color(self):
        if self.klass in 'word':
            return COLOR_BY_LANG.get(self.lang, "#aaa")
        else:
            return "#fff"

    def border_color(self):
        return "#000"

    def __str__(self):
        return f"{self.klass}({self.uri}, '{self.text}')"

    def __repr__(self):
        return str(self)


class Edge:
    """Edge directed from a source to target node"""
    def __init__( self, source: Node, target: Node, data: Dict ):
        self.source = source
        self.target = target
        self.rel = data['rel']
        self.data = data

    def id(self):
        return f"uri-{self.source.uri}--{self.rel}--{self.target.uri}"


class KnowledgeBase:
    """contains the full knowledge base"""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}  # nodes keyed by uri
        self.nodes_by_class = defaultdict(list)
        self.edges = []

    def populate(self, recs: List[Dict]):
        """validate recs and push them into nodes and edges"""
        for rec in recs:
            if 'rel' in rec:  # rel -> Edge
                _check_rel_record( rec )

                node_a = self._proc_edge_end(rec, 'a')
                node_b = self._proc_edge_end(rec, 'b')

                edge = Edge( node_a, node_b, rec )
                node_a.add_edge_out(edge)
                node_b.add_edge_in(edge)

                self.edges.append(edge)
            else:  # Node
                assert 'uri' in rec, f"rec={rec}"
                uri = rec['uri']
                assert uri not in self.nodes, f"Can't create node again: rec={rec}"
                node  = make_node_from_uri(uri, rec)
                self._add_node(node)

    def _add_node(self, node: Node):
        assert node.uri not in self.nodes, \
            f'Node with uri: {node.uri} was already added: {self.nodes[node.uri]}'

        self.nodes[node.uri] = node
        self.nodes_by_class[node.klass].append( node )

    def _proc_edge_end(self, rec: Dict, a_or_b: str) -> Node:
        uri_key = 'uri_' + a_or_b

        if uri_key in rec:
            assert a_or_b not in rec, f"Edge cannot have both '{a_or_b}' and '{uri_key}' keys"
            uri = rec[uri_key]
            if uri not in self.nodes:
                edge_end = make_node_from_uri(uri, dict())
                self._add_node( edge_end )

            edge_end = self.nodes[uri]

        elif a_or_b in rec:
            end_rec = rec[a_or_b]
            # uri_key = _find_uri_key(end_rec)
            if 'uri' not in end_rec:
                klass = klass_from_rel(rec['rel']) or end_rec.get('klass')
                if klass is None:
                    raise ValueError(f"For edge with rel={rec['rel']}."
                                     f"Could not infer or get class of {a_or_b}: {end_rec}\n"
                                     f"full rec = {rec}")

                uri = _gen_uri(klass, end_rec)
            else:
                uri = end_rec['uri']
            # klass = _class_from_rec( end_rec ) or _class_from_rel(rec['rel'])
            # print(f"Building node: {a_or_b}")
            assert uri not in self.nodes, f"Can't create node with uri agin: rec={rec}"
            edge_end = make_node_from_uri(uri, end_rec)
            self._add_node( edge_end )
        else:
            raise ValueError(f"Did not find uri_key: {uri_key} nor '{a_or_b}' in rec = {rec}")

        return edge_end

    def _export_to_csvs( self ):

        node_dicts = []
        for uri, node in self.nodes.items():
            dic = dict(uri=uri, klass=node.klass, label=node.text, lang=node.lang)
            dic.update( {k: v for k, v in node.data.items()
                         if not k.endswith('_uri')} )
            node_dicts.append( dic )

        nodes_df = pd.DataFrame( node_dicts )
        nodes_df.to_excel( Path("nodes.xlsx"), index=False )

        edge_dicts = []
        for edge in self.edges:
            dic = dict(source=edge.source.uri, rel=edge.rel, target=edge.target.uri)
            dic.update( edge.data )
            edge_dicts.append(dic)

        edges_df = pd.DataFrame( edge_dicts )
        edges_df.to_excel( Path("edges.xlsx"), index=True )


def klass_from_rel(rel: str) -> Optional[Klass]:
    return {"means": "sense"}.get(rel)


def make_knowledge_base() -> KnowledgeBase:
    with open("etymo_graph/words.yml") as f_in:
        recs = yaml.load( f_in, Loader=Loader)

    kb = KnowledgeBase()
    kb.populate(recs)
    return kb


def _gen_uri( klass: str, data: Dict ) -> str:
    # _, lang = data["text"].split("@")

    sha = sha256( pformat(data).encode('utf-8') ).digest()
    uri_sha = base64.b64encode( sha )[:12].rstrip(b'=').decode('ascii')

    return f"{klass}:{uri_sha}@."


def _check_rel_record( rec: Dict ):
    _must_contain_one_of( rec, ['a', 'uri_a'] )
    _must_contain_one_of( rec, ['b', 'uri_b'] )


def make_node_from_uri( uri, data ) -> Node:

    parts0 = uri.split(":")
    assert len(parts0) == 2, f"bad uri: {uri}"
    klass, rest = parts0

    assert klass in {'word', 'suffix', 'prefix', 'wordsense', 'lang', 'sense', 'root'}, f"Klass = {klass}"

    parts1 = rest.split("@")
    assert len(parts1) == 2, f"bad uri: {uri}"
    text, lang = parts1

    if 'text' in data:
        text = data['text']

    return Node(uri, klass, text, lang, data)
# %%


def _must_contain_one_of(rec, keys: List[str]):
    assert len( [key in rec for key in keys] ) > 0, f"none of {keys} in rec: {rec}"


def render_graph_to_html(kb: KnowledgeBase, selected: List[str]) -> str:
    # %%
    env = Environment(loader=FileSystemLoader("etymo_graph"))
    # %%
    tmpl = env.get_template( "etymo_graph0.tmpl.html" )

    elements = []

    viz_classes = ('word', 'wordsense')

    for _, node in kb.nodes.items():
        if node.uri not in selected:
            continue
        print(f"adding node: {node.uri}")
        if node.klass in viz_classes:
            data ={"id": node.uri,
                   "label": node.text,
                   "lang": node.lang,
                   "bg_color": node.bg_color(),
                   "border_color": node.border_color()}
            elements.append({"data": data})

    for edge in kb.edges:
        source, target = edge.source, edge.target
        if source.uri not in selected or target.uri not in selected:
            continue
        if source.klass in viz_classes and target.klass in viz_classes:
            elements.append( {"data": {"label": edge.data['rel'],
                                       "source": source.uri,
                                       "target": target.uri}} )
    html_txt = tmpl.render( elements=json.dumps( elements, indent=4 ) )
    return html_txt



def color_for_lang(lang: str):
    return {"spa": "#cfcf00",
            "eng": ""}.get(lang, "#ddd")



if __name__ == "__main__":
    _main()