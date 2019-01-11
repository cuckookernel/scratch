# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 14:34:01 2019

@author: mrestrepo
"""

from pprint import pprint 

# http://xahlee.info/comp/unicode_math_operators.html
# http://xahlee.info/comp/unicode_APL_symbols.html


MNEMONICS = {
   # https://en.wikipedia.org/wiki/APL_syntax_and_symbols#Monadic_functions
  "add"    : "+",
  "minus"  : "-", # subtract, Traditional APL 	U+2212 '−'
  "times"  : '×', # multiply 
  "div"    : '÷',      
  "matdiv" : '⌹',
  "pow"    : '^', # Exponentiation, Traditional APL "\u22C6" == '⋆'
  "circ"   : '○', # Traditional APL uses it for trigonometric functions....
  "rand"   : '?', # produce random numbers 
  "in"     : "∊",
  'pi'     : 'π', # '\u03c0',
  'gtlt'   : '≷', # compare, greater than / less than
  '>='     : '≥',
  '<='     : '≤',
  'empty'  : '∅',
  'def'    : '≝',
  'min'    : '⋀',
  'max'    : '⋁',
  'pi_half' : '⌔',
  'sum'     : '∑',
  'Sigma'   : '∑',
  'join'    : '⨝',
  'abs'      : '∣',
  'grade_up'   : '⍋',
  'grade_down' : '⍒',
  'equiv'      : '≡',
  'circ_dot'    : '⨀',
  'circ_times'  : '⨂',
  'tensor_times' : '⨂',
  'minus_dot'    : '∸',
  'negate' : '~',
  'not'  : '~',
  'factorial' : '!',
  'iota' : 'ι',
  'neq'  : '≠',
  'not_equal'  : '≠',
  'comp' : '∘', 
  'omega' : '⍵',
  'alpha' : '⍺',
  'subset' : '⊂',
  'rho' : '#',
  'left_assign' : '←',
  '<-' : '←',
  '->' : '→',
  'right_assign' : '→',
  'drop' : '↓',
  'ceil' : '⌉',
  'format' : '⍕',
  'circ_star' : '⍟',
  'lamp' : '⍝',
  'dot' : '.',
  'reduce' : '↑',
  'up' : '↑',
  'up_arrow':  '↑',
  
  
  }

pprint( MNEMONICS )
#%%
INT_MAX = 2147483647

import re

def translate( line ) : 
    ret_pieces = [] 
    cur  = 0 
    idx  = 0
    mode = 'NORMAL'
    
    while True :
        
        if mode == 'NORMAL' :
            idx = line[cur:].find( '\\' )
            #print( f'MODE NORMAL: idx={idx}')
            if idx == -1 : 
                #idx = len(line) - cur             
                ret_pieces.append( line[cur:] )
                break
            else :
                ret_pieces.append( line[cur : cur+idx] )
                cur += idx + 1                 
                mode = 'ESCAPED'
                
        elif mode == 'ESCAPED' :               
            end = re.match( r'[A-Za-z][A-Za-z0-9_]*', line[cur:]  )
            #print( end )
            if not end  : 
                raise ValueError( f'Found \\ without a string following at pos {idx} ' )
        
            word = end.group() 
            if word not in MNEMONICS :
                raise ValueError( f'Invalid escape sequence:({word})' )
            else : 
                ret_pieces.append( MNEMONICS[word] )
            cur += len(word)
            mode = 'NORMAL'
            
    #print( "pieces:",  ret_pieces )
    return "".join( ret_pieces ).replace( " ", "" )

def find_diff( str1, str2 ) : 
    print( str1 )
    print( str2 )
    
    if len(str1) != len(str2) : 
        print(f"Strings differ in length! {len(str1)} vs {len(str2)}") 
            
    else : 
        print( "".join( " " if str1[i] == str2[i]  else "*"
                        for i in range(len(str1)) ) ) 
        

def test() : 
    print( translate(r'\rho A'))
    apl = "(~R∊R∘.×R)/R←1↓ιR"  # find prime numbers 
    ascii0 = r"(\not R \in R \comp . \times R)/R \left_assign 1 \drop\iota R"
    ascii_tr = translate( ascii0 )
    print(ascii_tr, ascii_tr == apl  )
    find_diff( apl, ascii_tr ) 
test() 
    