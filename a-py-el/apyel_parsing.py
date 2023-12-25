"""
Created on Tue Dec 18 15:11:50 2018

@author: mrestrepo
"""

import arpeggio

from arpeggio.cleanpeg import ParserPEG

#%%

#https://www.dyalog.com/uploads/conference/dyalog11/presentations/D08_apl_sharp/AplSharpDescription.pdf

class Node :

    def __init__( self, arpeg_node ) :
        self.arpeg_node
    def evl( self, state) :
        raise NotImplementedError( type(self) )

class ArrayExpr( Node ) :
    def __init__( self )

class Func1( Node ) :
    def __init__( self, arpeg_node, name, arg1 ) :
        super().__init__( self, arpeg_node )

        self.name = name
        self.arg1 = arg1

    def evl( self, state ) :
        fn = state.getval( self.name )
        e1 = self.arg1.eval( state )

        return fn( e1 )

def construct( arpeg_node ) :



with open( "apl_grammar.txt", "rt", encoding='utf8' ) as f_in :
    funpy_grammar = f_in.read()

parser = ParserPEG(funpy_grammar, "program",
                   reduce_tree=True,
                   debug=1)

parser.debug = 1
#def test( parser ) :
    #parser.parse("R")
#result = parser.parse("⌽A") OK
#result = parser.parse("⌽[1]A") # OK
result = parser.parse("⊖⌽A") # OK

#result = parser.parse("")
#result = parser.parse("")
#result = parser.parse("")
#result = parser.parse("")
#result = parser.parse("")
#result = parser.parse("")
#result = parser.parse("")
#result = parser.parse("")
#result = parser.parse("")


result
#%%
#result = parser.parse( "(~R∊R∘.×R)/R←1↓ιR" )  # NOT OK!!!
