
from typing import Dict, List

# Graph as adjaceny lists  { node -> [ nodes reachable from node ] }
Graph = Dict[int, List[int]]

g1 = {
    1: [2],
    2: [3, 4],
    3: [5],
    4: [6],
    6: [4],
}


def node_is_in_cycle( graph: Graph, node0: int, node: int, visited: ):
    """
    node: the node we are currently visiting
    node0: the original node
    """
    adjacent = graph[node]  # nodes we can reach from current node

    for n in adjacent:
        if n == node0:
            return True
        else:
            return node_is_in_cycle(graph, node0, n)

    return False
