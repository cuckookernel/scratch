import init.data.bool

#check bool
#check true
#check true == false
#eval 0

#check 0
#check nat


theorem test( p q : Prop )(hp : p)(hq : q) : p ∧ q ∧ p :=
  by apply And.intro
    exact hp
    apply And.intro
      exact hq
      exact hp

#check test

