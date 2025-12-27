-- import init.data.bool

#check bool
#check true
#check true == false
#eval 0

#check 0
#check Nat

#check Nat -> Nat

#check (0, 1)

#check Nat.succ


def α : Type := Nat


-- def β := Nat

#check Type

#check Type 1


#check List

#check List.{1}


#check fun (x: Nat) => x + 5

#check λ (x : Nat) => x + 5


def β := fun (x : Nat) => x + 5

def γ := λ (x : Nat) => x + 5

#check β = γ


def iden (α : Type) := λ (x : α) => x

#check iden Nat 5

def greater (x y : Nat) : Nat := if x > y then x else y


#eval greater 5 3



theorem test( p q : Prop )(hp : p)(hq : q) : p ∧ q ∧ p :=
  by apply And.intro
    exact hp
    apply And.intro
      exact hq
      exact hp
    ;

#check test
