from itertools import permutations

# %%

def main():
    # %%
    with open( "/home/teo/Downloads/Spanish_1.dic", encoding="iso-8859-1" ) as f_in:
        words1 = [ w.strip().upper() for w in f_in.readlines() ]
    # %%
    with open("/home/teo/Downloads/spanish", encoding="iso-8859-1") as f_in:
        words2 = [w.strip().upper() for w in f_in.readlines()]
    # %%
    words = set(words1 + words2)
    # %%
    letters = list( )
    # %%
    cands = candidates( "AABFGJLMORUX", words )
    # %%

def candidates( letters, words ):
    # %%
    letters = list( letters )
    perms = set( "".join( perm ) for perm in permutations(letters, 8) )

    print( f"perms has {len(perms)}" )
    # %%
    cands = [ p for p in perms if p in words]
    # %%
    return cands
