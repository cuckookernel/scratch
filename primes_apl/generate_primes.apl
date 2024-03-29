⍝ This is a comment: ⍝ symbol is the analog of # in Python or Bash

                                   ⍝  Python equivalents (using numpy)
                                   ⍝  import numpy as np
⍝ default values for global params ⍝
N ← 100                            ⍝  N = 1000
TIMEOUT ← 1.0                      ⍝  TIMEOUT = 1.0
SHOW ← 0                           ⍝  SHOW = False

∇main; ts0;ts1;primes;passes;elapsed
  parse_args                       ⍝ Call parse_args niladic (i.e. no-argument) function

  ts0 ← timestamp_2_secs ⎕TS

  passes ← 0
  Loop:
    run_pass
    passes ← passes + 1
    ts1 ← timestamp_2_secs ⎕TS
    elapsed ← ts1 - ts0
    ⍝ →End ⍝ uncomment to run only one pass

    →(elapsed < TIMEOUT) / Loop

  End:
  ⍝ ⊃ 'End - primes: ',⍕primes
  num_primes ← +/IS_PRIME

  print_results (passes elapsed N num_primes)
∇
⍝ ∇ (gradient symbol) = "end of function def"

∇run_pass; sqrt;odd_numbers
  init_sieve N
  mark_evens
  sqrt ← ⌊(N * .5)
  odd_numbers ← 1 + 2 × ⍳ ⌊(⌈sqrt -1) ÷ 2
  mark_multiples¨ odd_numbers
∇

∇init_sieve n
  IS_PRIME ← n / 1
  IS_PRIME[1] ← 0
∇

∇mark_evens; max_k;mults
  max_k ← (⌊ N÷2) - 1
  mults ← 2 × (1 + ⍳ max_k)
  ⍝ ⊃ mults
  IS_PRIME[ mults ] ← 0
∇

∇mark_multiples p; max_k;mults
                                     ⍝  def mark_multiples(p):
  →(IS_PRIME[p] = 0) / End           ⍝     if IS_PRIME[p]: # if p is prime
     max_k ← 1 + ⌊ ((N÷p) - p) ÷ 2  ⍝         max_k = np.floor(N/p) - (p-1)
     ⍝ mults ← { p2 +  twice_p × (⍵  - 1)}¨⍳ max_k
     mults ← (p×p) + (2×p)×((⍳ max_k) - 1)
     IS_PRIME[ mults ] ← 0       ⍝         IS_PRIME[p * ks] = 0
  End:                               ⍝  # 'End:' is just a user defined label for a point
                                     ⍝  # in the code. There is no Python equivalent
∇

⍝ print and verify results
∇print_results data ;passes;elapsed;limit;num_primes;time_per_pass
  (passes elapsed limit num_primes) ← data
  time_per_pass ← elapsed ÷ passes
  valid ← ('False' 'True')[ (num_primes = num_primes_under limit) + 1 ]

  →(~SHOW)/PrintFinalLines
    print_primes primes

  PrintFinalLines:
    ⊃ ('Passes: ',⍕passes,'Time: ',(3⍕elapsed),' Avg:',(6⍕time_per_pass),' Limit: ',⍕limit,'Count: ',⍕num_primes,'Valid: ',⍕valid)
    ⊃ ''
    ⊃ ('cuckookernel_apl;',(⍕passes),';',(6⍕elapsed),';1;algorithm=base,faithful=yes,bits=8')
∇
⍝ (passes, duration, duration/passes, self._size, count, self.validate_results()))

∇n_primes ← num_primes_under n; valid_ns;num_primes;idx
  valid_ns   ← 10 100 1000 10000 100000 1000000 10000000 100000000
  num_primes ←  4  25  168  1229   9592   78498   664579   5761455
  idx ← valid_ns ⍳ n

  →(idx = 1 + ⍴ valid_ns)/DontKnow
     n_primes ← num_primes[idx]
     →Return
  DontKnow:
     n_primes ← -1                        ⍝ n_primes = []
  Return:
∇

∇print_primes primes
   ⊃ ,/ { (⍕⍵),', '}¨ primes
∇

⍝ Utility functions get system clock time and parse arguments
∇nsecs ← timestamp_2_secs ts;  fff; ss; MM; HH; dd
  ⍝ Takes a timestamp of the from (yyyy mm dd HH MM SS fff)
  ⍝ e.g. as returned by system function ⎕TS
  ⍝ and return the number of seconds since the start of the given month

  ⍝ The part at then end is a way of declaring local variables; fff; ss; MM; HH; dd
  ⍝ The formula looks wrong a first sight but it is actually right, as it makes use
  ⍝ of the APL way of parsing expressions associating everything to the right
  ⍝ Thus the formula it is actully equivalent to
  ⍝ (fff ÷ 1000.0) + ss + 60×(MM + (60×(HH + 24 × dd)))

  (fff ss MM HH dd) ← ts[7 6 5 4 3]   ⍝ Multiple assignment into multiple variables!
  nsecs ← (fff ÷ 1000.0) + ss + 60 × MM + 60 × HH + 24 × dd
∇

∇parse_args ;n_args;limit_arg_pos;is_show_arg;limit_arg_po

  args_pos ← ({ ⍵ ≡ '--' }¨⎕ARG) ⍳ 1     ⍝ args_pos = [ a == '--' for a in sys.argv ].index(True)
  →(args_pos ≥ ⍴⎕ARG) / End          ⍝ if args_pos == -1: ~goto End

  my_args ← args_pos ↓ ⎕ARG
  ⍝ ⊃ 'my_args:',⍕my_args, ' #', ⍴ my_args
  n_args_p_1 ← 1 + ⍴ my_args              ⍝  n_args = len(sys.argv) + 1

  limit_arg_pos ← ({(⍵ ≡ '-l') ∨ (⍵ ≡ '--limit')}¨my_args) ⍳ 1
  ⍝ Python: limit_arg_pos = [ x == '-l' or x == '--limit' for x in my_args].index(True)
  time_arg_pos ← ({(⍵ ≡ '-t') ∨ (⍵ ≡ '--time')}¨my_args) ⍳ 1
  ⍝ ⊃ 'set time_arg_pos ',⍕time_arg_pos
  SHOW ← n_args_p_1 > ({(⍵ ≡ '-s') ∨ (⍵ ≡ '--show')}¨ my_args) ⍳ 1

  →(limit_arg_pos = n_args_p_1) / NoLimit
    N ← ⌊ ⍎⍕my_args[limit_arg_pos + 1]
    ⍝ ⊃ 'set N to ',⍕N
  NoLimit:
  →(time_arg_pos = n_args_p_1) / End
    TIMEOUT ← ⍎⍕my_args[time_arg_pos + 1]
    ⍝ ⊃ 'set TIMEOUT to ',⍕TIMEOUT
  End:
∇

main
