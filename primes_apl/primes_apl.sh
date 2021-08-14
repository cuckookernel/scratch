#!/bin/bash
# Example usage:
#     primes_apl.sh --limit 1000000 --time 5.0 --show
#
# Equivalently, using short options:
#     primes_apl.sh -l 1000000 -t 5.0 -s

apl -s -f generate_primes.apl -q --OFF -- $@

# akt apl -f generate_primes.apl -q -- -l 1000 -t 1.0 -s
