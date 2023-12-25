"""Created on Fri Jan 11 13:34:47 2019

@author: mrestrepo
"""
import bisect
from collections import defaultdict

LOOK_UP = {}

def count_triplets( arr, r ) :

    dic = defaultdict(list)

    for i, v in enumerate(arr) :
        dic[v].append(i)

    if r == 1 :
        return count_triplets1( dic )

    count = 0
    for i, v in enumerate(arr) :
        vr = v * r
        vrr =  vr * r

        a0 = dic[vr]
        idx0 = bisect.bisect( a0, i )

        for j in a0[idx0:] :
            count += cnt_bigger( dic, j, vrr )


    return count


def cnt_bigger( dic, j,  vrr ):
    if vrr in dic :
        key = (j,vrr)
        if key in LOOK_UP :
            return LOOK_UP[key]
        else:
            a = dic[vrr]
            idx1 = bisect.bisect(a, j)
            ret = len(a) - idx1
            LOOK_UP[key] = ret
            return  ret
    else :
        return 0


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
