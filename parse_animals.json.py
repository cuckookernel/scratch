
from collections import Counter
import json

with open("/home/teo/git/muid_miner/animals.json", "rt") as f_in:
    obj = json.load( f_in )
# %%
len( obj )
# %%
keys = set( obj.keys() )
# %%
cnter = Counter()

cnter.update( len(key) for key in keys )

hash = "9a19a1c0407e99a05726bc7fb68e204b"

for l in range(6, 16):
    if hash[:l] in keys:
        print( hash[:l])

with open("/home/teo/git/muid_miner/animals.txt", "wt") as f_out:
    for key in keys:
        print( key, file=f_out )
# %%
key = "71d157b442b1b405829dd98d0e149572"
# %%
from hashlib import sha256

# %%
sha256(key.encode('ascii')).hexdigest()

# %%
[ int( key[i:i+2], base=16) for i in range( 0,  len(key), 2) ]
# %%
hashl