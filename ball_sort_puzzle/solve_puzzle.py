
from collections import Counter, defaultdict
from typing import Dict, List

from ball_sort_puzzle import search
from ball_sort_puzzle.search import Problem

# %%
BIN_CAP = 4
IND_DESC = (3, 2, 1, 0)


class State:
    def __init__( self, contents: bytes, heights: bytes):
        self.contents = contents
        self.heights = heights
        self.color2bins = self._compute_color2bins()

    def _compute_color2bins(self) -> Dict[int, List[int]]:
        ret = defaultdict(list)
        for bin_idx, height in enumerate(self.heights):
            if height > 0:
                color = self.contents[bin_idx * BIN_CAP + height - 1]
                ret[color].append(bin_idx)

        return ret

    def actions(self):
        """Generator of tuples encoding possible moves as (origin_bin, target_bin)"""
        for color, bins in self.color2bins.items():
            for bin_i in bins:
                for bin_j in bins:
                    if bin_i != bin_j and self.heights[bin_j] < BIN_CAP:
                        yield (bin_i, bin_j)

        for bin_j, height_j in enumerate(self.heights):
            if height_j == 0:
                for bin_i, height_i in enumerate(self.heights):
                    if height_i > 0:
                        yield (bin_i, bin_j)

    def apply(self, action):  # -> State
        """Produce a new state as a result of applying action to self"""
        new_contents = bytearray( self.contents )
        new_heights = bytearray( self.heights )
        i, j = action

        # TODO: disable asserts
        assert self.heights[i] > 0 and self.heights[j] < BIN_CAP

        i_idx = i * BIN_CAP + self.heights[i] - 1
        color = self.contents[i_idx]
        j_idx = j * BIN_CAP + self.heights[j]

        assert ( self.heights[j] == 0 or
                 self.contents[j_idx - 1] == color),\
            f'j: {j}  h[{j}]={self.heights[j]} color={chr(color)} '

        new_contents[ i_idx ] = ord(' ')
        new_contents[ j_idx ] = color

        new_heights[i] -= 1
        new_heights[j] += 1

        return State( bytes(new_contents), bytes(new_heights) )

    def __str__( self ):
        return _str_from_contents(self.contents)

    def __repr__( self ):
        return str(self)

    def print( self ):
        """Print state and auxiliary data to console"""
        print( self )
        print( self.heights )
        print( self.color2bins )

    def _is_empty( self, bin_i: int ) -> bool:
        return self.heights[bin_i] == 0

    def same_color( self, bin_i: int ) -> bool:
        """Are all spaces in bin_i occupied by the same color"""
        if self.heights[bin_i] != BIN_CAP:
            return False

        return all( self.contents[idx] == self.contents[idx + 1]
                    for idx in range( bin_i * BIN_CAP, (bin_i + 1) * BIN_CAP - 1 ) )

    def goal_test( self ):
        """Is this state a solution"""
        return all( (self._is_empty( bin_i )
                     or self.same_color( bin_i )) for bin_i in range( len(self.heights) ) )

    def __eq__( self, other ):
        return self.contents == other.contents

    def __hash__( self ):
        return hash(self.contents)

    def __lt__( self, rhs ):
        return f1(self) < f1(rhs)


def make_state( bins: List[str] ) -> State:
    """Make a state from a list of strings. all should have length BIN_CAP"""
    n_bins = len(bins)
    for bin in bins:
        assert len(bin) == BIN_CAP, f'bin={bin} len={len(bin)}'

    counts = Counter()
    for bin in bins:
        counts.update( bin )

    for key, count in counts.items():
        assert key == ' ' or count == BIN_CAP, f'key={key} count={count}'

    contents = b"".join( bin.encode('ascii') for bin in bins )
    heights = _compute_heights(bins)

    return State(contents, heights)


def _str_from_contents( contents: bytes):
    n_bins = len(contents) // BIN_CAP
    pieces = ["\n"]
    pieces.extend([ f"{bin_idx:2d}|"
                    f"{contents[bin_idx * BIN_CAP: (bin_idx + 1) * BIN_CAP].decode('ascii')}"
                    for bin_idx in range(n_bins) ])
    return "\n".join(pieces)


def _compute_heights(bins: List[str]) -> bytearray:
    n_bins = len(bins)
    ret = [ 0 ] * n_bins
    for bin_idx in range(n_bins):
        for i in IND_DESC:
            if bins[bin_idx][i] != ' ':
                ret[bin_idx] = i + 1
                break

    return bytearray(ret)


class BSPuzzle(Problem):
    """Ball sort puzzle"""

    def actions( self, state ):
        "Actions from state"
        yield from state.actions()

    def result( self, state, action ) -> State:
        """Result of applying action to state"""
        return state.apply(action)

    def goal_test( self, state ) -> bool:
        """Is state a goal"""
        return state.goal_test()


def f1( state: State ) -> int:
    n_bins = len(state.heights)
    n2 = n_bins ** 2

    n_same_color = sum(1 for bin_i in range(n_bins) if state.same_color(bin_i))

    return n2 * n_bins - n2 * n_same_color - sum( 1 for _ in state.actions() )

    # %%


def print_solution(solution):
    node = solution
    reverse_path = []
    while node.parent:
        reverse_path.append( (node.parent, node.action) )
        node = node.parent

    reverse_path.reverse()

    for i, (node, action) in enumerate(reverse_path):
        print( str(node.state).replace("\n 0|", f"step {i}:\n 0|") )
        print( f"ACTION: {action}")
    # %%


def _interactive_testing():

    # %%
    easy0 = [
        'aabb',
        'bb  ',
        'aa  ',
        '    ',
    ]
    # %%
    level2 = [
        'byby',
        'yby ',
        'b   ',
    ]
    # %%
    level11 = [
        'bbbg',
        'gyvr',
        'brvy',
        'yrgy',
        'vgrv',
        '    ',
        '    ',
    ]
    # %%
    level12 = [
        'rvbb',
        'ygBy',
        'vBvo',
        'gbvg',
        'bBry',
        'oorB',
        'yorg',
        '    ',
        '    ',
    ]
    # %%
    level13 = [
        'Bygg',
        'orbr',
        'vvyv',
        'oyBo',
        'bByr',
        'rggB',
        'bobv',
        '    ',
        '    ',
    ]
    # %%
    level = [
        'cBlr',
        'rlbg',
        'c6lp',
        'yGgc',
        '6pgo',
        'ov6v',
        'pbyb',
        'gGyp',
        'rcGB',
        'yo6r',
        'vBBl',
        'ovbG',
        '    ',
        '    ',
    ]
    # %%
    level = [
        'Brtb',
        'bvyr',
        'gtrt',
        'GvyG',
        'gvog',
        'brGb',
        'BBoG',
        'Bogo',
        'ytvy',
        '    ',
        '    ',
    ]

    runfile('ball_sort_puzzle/solve_puzzle.py')

    state = make_state( level )
    problem = BSPuzzle( state )

    def f1_node( node ):
        return node.path_cost + f1( node.state )

    f = f1_node

    solution = search.best_first_graph_search( problem, f1_node, display=True )
    # %%
    print_solution(solution)

    # %%


    state = make_state(
        [ 'aabb',
          'bb  ',
          'bbc ',
          '    ',
          'cca ',
          'cc  ' ],
    )

    state.print()

    # %%
    print( list(state.actions()) )
    # %%
    print( state.apply((2, 1)) )

    # %%
    state = make_state(
        ['aaaa',
         'bbbb',
         'cccc',
         'cccc',
         '    ',
         '    '],
    )

    print( state.goal_test() )
    # %%

    # %%
    list( state.actions() )
    state1 = state.apply( (0, 1) ).apply( (0, 1) ).apply( (0, 2) ).apply( (0, 2))
    print( state1 )
    print( state1.goal_test() )
    # %%
    search.depth_first_graph_search(problem)
    # %%
