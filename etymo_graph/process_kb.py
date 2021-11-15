"""
process knowledge base contained in words.yaml

https://cvc.cervantes.es/lengua/thesaurus/pdf/09/TH_09_123_007_0.pdf
https://diccionario.reverso.net/espanol-frances/apretar
https://context.reverso.net/traduccion/portugues-espanol/colo

"""
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
from pprint import pprint, pformat
from hashlib import sha256
import base64

import yaml
from yaml import Loader
# %%

Edge = Any


def _main():
    # %%
    runfile("etymo_graph/process_kb.py")

    with open("etymo_graph/words.yml") as f_in:
        recs = yaml.load( f_in, Loader=Loader)

    kb = KnowledgeBase()
    kb.populate(recs)

    pprint( kb.nodes )
    # %%


class Node:
    """An node in the graph"""
    def __init__( self, uri: str, klass: str, data: Dict[str, Any] ):
        self.uri: str = uri

        self.text = None
        self.lang = None

        if '@' in uri:
            self.text, self.lang = uri.split('@')
        elif 'text' in data:
            self.text = data['text']
        elif 'name' in data:
            self.text = data['name']

        self.klass: str = klass
        self.data: Dict[str, Any] = data
        self.edges_in: List[Edge] = []
        self.edges_out: List[Edge] = []

    def add_edge_in( self, edge: Edge ):
        """Add incoming edge"""
        self.edges_in.append(edge)

    def add_edge_out( self, edge: Edge ):
        """Add outcoming edge"""
        self.edges_out.append(edge)

    def __str__( self ):
        return f"{self.klass}({self.uri}, '{self.text}')"

    def __repr__( self ):
        return str(self)


class KnowledgeBase:
    """contains the full knowledge base"""
    def __init__( self ):
        self.nodes: Dict[str, Node] = {}  # nodes keyed by uri
        self.nodes_by_class = defaultdict(list)
        self.edges = []

    def populate( self, recs: List[Dict] ):
        """validate recs and push them into nodes and edges"""
        for rec in recs:
            if 'rel' in rec:  # rel -> Edge
                _check_rel_record( rec )

                node_a = self._proc_edge_end(rec, 'a')
                node_a.add_edge_out( rec )

                node_b = self._proc_edge_end(rec, 'b')
                node_b.add_edge_in( rec )

                self.edges.append( rec )
            else:  # Node
                klass, uri = _get_uri_and_class( rec )
                node = Node(uri, klass, rec)
                self._add_node(node)

    def _add_node( self, node: Node):
        assert node.uri not in self.nodes, \
            f'Node with uri: {node.uri} was already added: {self.nodes[node.uri]}'

        self.nodes[node.uri] = node
        self.nodes_by_class[node.klass].append( node )

    def _proc_edge_end( self, rec, a_or_b: str ) -> Node:
        uri_key = 'uri_' + a_or_b

        if uri_key in rec:
            assert a_or_b not in rec, f"Edge cannot have both '{a_or_b}' and '{uri_key}' keys"
            edge_end = self.nodes.get( rec[uri_key] )
            assert edge_end is not None, \
                f"when building edge: no node with key {uri_key}={rec[uri_key]}"

        elif a_or_b in rec:
            end_rec = rec[a_or_b]
            uri_key = _find_uri_key( end_rec )
            uri = end_rec[uri_key] if uri_key else _gen_uri(end_rec)
            klass = _class_from_rec( end_rec ) or _class_from_rel(rec['rel'])

            if klass is None:
                raise ValueError(f"For edge with rel={rec['rel']}."
                                 f"Could not infer class of {a_or_b}: {end_rec}")
            # print(f"Building node: {a_or_b}")
            edge_end = Node( uri, klass, end_rec )
            self._add_node( edge_end )
        else:
            raise RuntimeError("this can't happen")

        return edge_end


def _gen_uri( data: Dict ) -> str:
    sha = sha256( pformat(data).encode('utf-8') ).digest()
    uri = base64.b64encode( sha )[:12].rstrip(b'=').decode('ascii')

    return uri


def _check_rel_record( rec: Dict ):
    _must_contain_one_of( rec, ['a', 'uri_a'] )
    _must_contain_one_of( rec, ['b', 'uri_b'] )


def _get_uri_and_class( rec: Dict ) -> Tuple[str, str]:
    uri_key = _find_uri_key(rec)

    if uri_key is not None:
        klass, _ = uri_key.split('_')
        return klass.title(), rec[uri_key]
    else:
        raise ValueError(f'No uri_key in rec: {rec}')
# %%


def _class_from_rec( rec: Dict ) -> Optional[str]:
    uri_key = _find_uri_key(rec)
    if uri_key is None:
        return None
    else:
        return uri_key.split('_')[0].title()


def _find_uri_key(rec: Dict) -> Optional[str]:
    uri_keys = [key for key in rec.keys() if '_uri' in key]
    # node, should have only one uri...
    assert len( uri_keys ) <= 1, f'more than one uri key in node rec:{rec}'

    return uri_keys[0] if len(uri_keys) == 1 else None


def _class_from_rel( rel: str ) -> Optional[str]:
    return {"means": "Meaning"}.get(rel)


def _must_contain(rec, key: str):
    assert key in rec, f"missing required key: {key} in record:\n{rec}"


def _must_contain_one_of(rec, keys: List[str]):
    assert len( [key in rec for key in keys] ) > 0, f"none of {keys} in rec: {rec}"
