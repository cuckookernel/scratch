# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 13:34:47 2019

@author: mrestrepo
"""
from collections import defaultdict 
import bisect 

LOOK_UP = {}

def count_triplets( arr, r ) : 
    
    dic = defaultdict(list)
    
    for i, v in enumerate(arr) :
        dic[v].append(i)
    
    if r == 1 : 
        return count_triplets1( dic )
        
    count = 0 
    for i, v in enumerate(arr) : 
        v_l = v // r
        
        if v_l in dic :
            a0 = dic[v_l]
            idx0 = bisect.bisect_left( a0, i ) 
            f1 = idx0 
        else :
            continue 
        
        v_r =  v * r        
        if v_r in dic : 
            a1 = dic[v_r]
            idx1 = bisect.bisect( a1, i ) 
            f2 = len( a1 )  - idx1 
        else : 
            continue 
        
        count  += f1 * f2 
                    
    return count




def count_triplets1( dic ) :
    count = 0 
    for arr in dic.values() :
        n = len(arr)
        count += n * (n - 1) * (n - 2) // 6 
    return count

#%%
def test() : 
     #%% 
    count_triplets( [1, 3, 9, 9, 27, 81], 3 )
    #%%
    count_triplets( [1, 5, 5 ,25, 125 ], 5 )
    #%%
    count_triplets( [1227] * 100000, 1 )
    #%%
    
def to_arr( a_str, typ=int ) : 
    return [ typ(x) for x in a_str.split() ]

def main() : 
    pars = to_arr( input() )
    r = pars[1]
    
    arr = to_arr(input())
    
    print ( count_triplets(arr, r) )

main( )
        