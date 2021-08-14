⍝ This is a comment: ⍝ symbol is the analog of # in Python or Bash

                                   ⍝  Python equivalents (using numpy)
                                   ⍝  import numpy as np
                                   ⍝
N ← 100                            ⍝  N = 1000
TIMEOUT ← 1.0                      ⍝  TIMEOUT = 1.0
SHOW ← 0                           ⍝  SHOW = False

∇main
  parse_args                       ⍝ Call parse_args niladic (i.e. no-argument) function

  ts0 ← timestamp_2_secs ⎕TS

  passes ← 0
  Loop:
    primes ← run_pass
    passes ← passes + 1
    ts1 ← timestamp_2_secs ⎕TS
    elapsed ← ts1 - ts0
    →End
    →(elapsed < TIMEOUT) / Loop

  End:
  ⍝ ⊃ 'End - primes: ',⍕primes
  num_primes ← ⍴ primes

  print_results (passes elapsed N num_primes)
∇
⍝ ∇ (gradient symbol) = "end of function def"

∇primes ← run_pass; sqrt;odd_numbers
  create_sieve N

  mark_multiples 2      ⍝  ⊣ do not echo result
  sqrt ← ⌊(N * .5)
  ⍝ odd_numbers ← 1 + 2 × ⍳ ⌊(sqrt ÷ 2)
  odd_numbers   ← 1 + 2 × ⍳ ⌊(⌈sqrt -1) ÷ 2
  mark_multiples¨ odd_numbers
  primes ← (is_prime = 1 ) / ⍳N
∇

∇create_sieve n
  ⍝ is_prime ← n / 13 ⎕CR '31'   ⍝ byte array version wasn't really any faster
  is_prime ← n / 1
  is_prime[1] ← 0
∇

∇mark_multiples p; max_k; factors
                                      ⍝  def mark_multiples(p):
  →(is_prime[p] = 0) / End           ⍝     if PRIMES1[p]: # if p is prime
     max_k ← (⌊ N÷p) - (p-1)         ⍝         max_k = np.floor(N/p) - (p-1)
     factors ← (p - 1) + ⍳ max_k     ⍝         ks = (p - 1) * np.arange(1, max_k +1)
     is_prime[p × factors] ← 0       ⍝         PRIMES[p * ks] = 0
  End:                               ⍝  # 'End:' is just a user defined label for a point
                                     ⍝  # in the code. There is no Python equivalent
    ⍝ primes ← (is_prime = '1') / ⍳N
    ⍝ ⊃ 'p: ',⍕p,'is_prime: ', ⍕is_prime,' primes: ',⍕primes

∇


⍝ print and verify results

∇print_results data ;passes;elapsed;limit;num_primes;time_per_pass
   (passes elapsed limit num_primes) ← data
   time_per_pass ← elapsed ÷ passes
   valid ← ('False' 'True')[ (num_primes = num_primes_under limit) + 1 ]
   ⊃ ('Passes: ',⍕passes,'Time: ',(3⍕elapsed),' Avg:',(6⍕time_per_pass),' Limit: ',⍕limit,'Count: ',⍕num_primes,'Valid: ',⍕valid)
   →(~SHOW)/PrintFinalLine
     print_primes primes
  PrintFinalLine:
    ⊃ ''
    ⊃ ('cuckookernel_apl;',⍕passes,';',(6⍕elapsed),';1;algorithm=base,faithful=yes,bits=8')
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
