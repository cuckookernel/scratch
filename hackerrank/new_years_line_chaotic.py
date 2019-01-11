# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 15:10:13 2019

@author: mrestrepo
"""

# Enter your code here. Read input from STDIN. Print output to STDOUT
def main() :
    t = int( input() ) 
    for i in range(t) : 
        n = int( input() )
        arr  = [int(x) for x in input().split()]
        try  :
            print( solve(n, arr) )

        except ValueError as exc : 
            print( "Too chaotic" ) # : " + str(exc) )


def solve( n, arr ) : 
    cost = 0 
    while n > 0 : 
        cost = solve1(n, arr, cost)
        n -=1
    return cost
      


def solve1( n, arr, cost ) : 
    if arr[n-1] == n :
        #arr = arr[:-1]
        return  cost 
    elif arr[n-2] == n : 
        arr[n-2] = arr[n-1]
        #arr = arr[:-1]        
        return   cost + 1

    elif arr[n-3] == n :
        arr[n-3] = arr[n-2]
        arr[n-2] = arr[n-1]
        #arr = arr[:-1]
        return  cost + 2 
    else : 
        raise ValueError("")
        
        
def test() : 
    arr = [ int(x) for x in "2 1 5 3 4".split( )]
    n = len(arr)
    
    print( solve( n, arr) )
    
#test()
main() 
    




