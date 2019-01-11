# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 15:11:50 2018

@author: mrestrepo
"""

import arpeggio
#%%

from arpeggio.cleanpeg import ParserPEG

#%%

with open( "grammar1.peg", "rt" ) as f_in :
    funpy_grammar = f_in.read()


parser = ParserPEG(funpy_grammar, "program")
#%%