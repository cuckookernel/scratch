
∇mults ← gen_multiples args;p
  (N p) ← args
  ⍝ ret = [ p*p p*(p+2) p*(p+4)... p*(p + 2*M)]
  ⍝ with p * (p + 2*M) <= N , p * (p + 2*M + 1) > N
  ⍝ ret = p * [p p+2 p+4 ... p + 2*M]
  ⍝ p + 2*M <= N/p
  ⍝ 2 * M <= N/p - p
  ⍝ M <= (N/p - p) / 2
  M ← ⌊ ((N÷p) - p) ÷ 2
  max_k ← 1 + ⌊ ((N÷p) - p) ÷ 2
  mult1 ← p × ( p + 2 × M )
  mult2 ← p × ( (p + 2 × M) + p)
  ⊃''
  ⊃'N:',(⍕N),' p:',(⍕p), ' max_m: ',(⍕M),' max_k:',(⍕max_k),' mult1:',(⍕mult1),' mult2:',(⍕mult2)

  ⍝ ret = p * ( p + [ 0 2 4 ... 2 * M ])
  ⍝ ret = p * ( p + 2 * [ 0 1 2 ... M ])
  ⍝ ret = p * ( p + 2 * (-1 + [1 2 3 ... M + 1]) )

  mults ← (p×p) + (2×p)×((⍳ max_k) - 1)
  ⍝ ⊃ mults
  ⊃'     mults[1]:',(⍕mults[1]),' mults[-1]:',(⍕mults[⍴ mults]), ' max_m: ',(⍕M),' max_k:',(⍕max_k),' mult1:',(⍕mult1),' mult2:',(⍕mult2)

∇
