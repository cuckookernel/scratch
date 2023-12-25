
import timeit

from muid.mining import create

# %%

n = 100
time = timeit.timeit( stmt=lambda: create(difficulty=9), number=n )

print( time, time / 100 )

# %%
help( timeit.timeit )
# %%
