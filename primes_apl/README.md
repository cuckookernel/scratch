# APL solution by cuckookernel

(Optional) <Badges>

This solution is a very plain implementation of the base Eratostenes Sieve algorithm.
For eficiency a global (but dynamically allocated) numeric array `IS_PRIME` is used.

We call `N` the upper limit of the sieve. This is the only other global variable.

This array is initialized to an array of `N` `1`s by function `init_sieve`.

The outer loop is in function `run_pass` which first marks the multiples of 2
as not prime and then loops over all odd numbers up to `sqrt(N)`

The function `mark_multiples` is the one responsible for marking multiples of a prime
as not primes. It also checks whether the number it gets is already marked as non prime.
In that case, it is a non-op.

## Run instructions

Running with docker:

On the code's root directory do.
```
docker build ./ -t primes_apl
docker run primes_apl
```

Running without docker:
```

``` 

## Output

*Show the output you got on your machine(s) here, in code blocks*

```
$ docker run primes_aplPasses: 74 Time:  5.055 Avg: .068311 Limit: 1000000 Count: 78498 Valid:  True 

cuckookernel_apl;74; 5.055000;1;algorithm=base,faithful=yes,bits=8
```
