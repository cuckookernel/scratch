"""Created on Tue Jan  8 18:40:59 2019

@author: mrestrepo

https://www.hackerrank.com/challenges/maximum-xor/problem?h_l=interview&playlist_slugs%5B%5D=interview-preparation-kit&playlist_slugs%5B%5D=miscellaneous
"""

class Node :
    def __init__( self ) :
        self.b = [None , None ]


def solution( queries, arr ):

    tree = Node()

    for a in arr :
        put( tree, a, 31 )

    #print_tree( tree, 0 )

    for q in queries :
        m  =  query(tree, q, 31)
        print( m ^ q )

def print_tree( tree, depth ) :

    if type( tree ) == int :
        print( " " * (depth * 2) + f"{tree}" )
        return

    if tree.b[0] :
        print( " " * (depth * 2) + "0:" )
        print_tree( tree.b[0], depth + 1 )
    else :
        print( " " * (depth * 2) + "0: None" )

    if tree.b[1] :
        print( " " * (depth * 2) + "1:" )
        print_tree( tree.b[1], depth + 1 )
    else :
        print( " " * (depth * 2) + "1: None" )


def put( tree, a, bidx ) :

    b  = (a >> bidx) & 1
    if tree.b[b] is None :
        tree.b[b] = Node()

    if bidx == 0 :
        tree.b[b] = a
    else :
        put( tree.b[b], a, bidx -1  )

def query( tree, q, bidx ) :
    b = (q >> bidx) & 1
    #print( b )

    if bidx ==  0 :
        if tree.b[1-b] is not None :
            return tree.b[1-b]
        else :
            return tree.b[b]

    if tree.b[ 1 - b ] is not None :
        return query( tree.b[1 - b], q, bidx - 1)
    else :
        return query( tree.b[b], q, bidx - 1)


#%%
#def test() :
#%%
#solution( [], [3,7,15,10] )
def main() :
    inp  = ips(
            """3
0 1 2
3
3
7
2
""")

    inp = cip()

    _ = next(inp) # n
    arr = read_line_arr( inp )
    qs = read_many( inp )

    #solution( [3,3,7] , [0, 1, 2 ] )
    #print( "qs=", qs, "arr=", arr)
    solution( qs , arr )

def cip() :
    i = 0
    while True :
        line = input()
        #print( "line ", i, " : ", line )
        yield  line
        i+=1

def ips( a_str ) :
    lines = a_str.split("\n")
    for line in lines :
        yield line

def read_line_arr( inp, typ=int ) :
    return to_arr( next(inp) )

def to_arr( a_str, typ=int ) :
    return [ typ(x) for x in a_str.split() ]

def read_n( inp, n, typ  = int ) :
    return [ typ(next(inp)) for i in range( n ) ]

def read_many( inp, typ=int ) :
    n = int( next(inp) )
    return read_n(inp, n, typ=int)

main()
