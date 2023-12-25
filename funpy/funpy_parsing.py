"""Created on Tue Dec 18 15:11:50 2018

@author: mrestrepo
"""

#%%

from arpeggio.cleanpeg import ParserPEG

#%%

with open( "grammar1.peg" ) as f_in :
    funpy_grammar = f_in.read()


parser = ParserPEG(funpy_grammar, "program")
#%%
