

def a := 1
#check Nat

#print a

#check Nat × Nat


def F: Type -> Type := List

#check F
-- variable (α: Type)

def α := Nat
#check F α

#check Type 1

#check trivial

#check True

#check Prop

def b := toString (2: Nat)

#print b

#check b

variable (p q r s: Prop)

theorem t2 (h₁: q → r) (h₂: p → q): p → r :=
   fun h₃ : p =>  show r from h₁ (h₂ h₃)

#check t2

#check p → q → p ∧ q

#check And

#check (p ∧ q → p)

variable (hp: p) (hq: q)

-- #check (⟨ hp, hq⟩: p ∧ q)

-- fun (a: u) (b: v) => ⟨a, b⟩

theorem t3 (h: p ∧ q): p :=
  h.left

#check t3

example (hp: p) : p ∨ q := Or.intro_left q hp

#check Or.elim


theorem t6 (hpq: p → q) (hnq : ¬q) : ¬p :=
   fun hp: p =>
   show False from  hnq (hpq hp)

#print t6

#check absurd

theorem t5 (h: p ∧ q): q ∧ p :=
  have hp : p := h.left
  have hq : q := h.right
  show q ∧ p from And.intro hq hp

#print t5



variable (a b c d e : Nat)

variable (h1: a = b)
variable (h2: b = c + 1)
variable (h3: c = d)
variable (h4: e = 1 + d)

theorem t7: a = e :=
  calc
    a = b := h1
    _ = c + 1 := h2
    _ = d + 1 := congrArg Nat.succ h3
    _ = 1 + d := Nat.add_comm d 1
    _ = e  := Eq.symm h4

#print t7

#check congrArg

#check trans


theorem t8: a = e :=
  calc
    a = b := by rw [h1]
    _ = c + 1 := by rw [h2]
    _ = d + 1 := by rw [h3]
    _ = 1 + d := by rw [Nat.add_comm]
    _ = e := by rw [h4]

def divides (x y: Nat): Prop :=
   ∃ k, k * x = y

def divides_trans (h1: divides x y) (h2: divides y z): divides x z :=
  let ⟨k1, d1⟩ := h1
  let ⟨k2, d2⟩ := h2
  let w := k2 * k1
  let xdz :=
    calc
      w * x = (k2 * k1) * x := by rw []
      _ =  k2 * (k1 * x) := by rw [Nat.mul_assoc]
      _ =  k2 * y := by rw [d1]
      _ =  z := by rw [d2]
   ⟨w, xdz⟩


open Classical

variable (α : Type) (p q : α → Prop)
variable (r : Prop)

example : (∃ x : α, r) → r :=
  fun ⟨_, hr⟩ => hr

example (a : α) : r → (∃ x : α, r) :=
  fun p : r  =>  Exists.intro a p

example : (∃ x, p x ∧ r) ↔ (∃ x, p x) ∧ r :=
  let imp1 :  (∃ x, p x ∧ r) → (∃ x, p x) ∧ r :=
     fun ⟨w, ⟨pw, hr⟩⟩ =>
     ⟨⟨w, pw⟩, hr⟩

  let imp2 : (∃ x, p x) ∧ r → (∃ x, p x ∧ r) :=
     fun ⟨ep, hr⟩ => let  ⟨w, hw⟩ := ep
     ⟨w, hw, hr⟩

  Iff.intro imp1 imp2

example : (∃ x, p x ∨ q x) ↔ ((∃ x, p x) ∨ (∃ x, q x)) :=
  let imp1 :  (∃ x, p x ∨ q x) → ((∃ x, p x) ∨ (∃ x, q x)) :=
     fun ⟨w, p_or_q_w⟩ =>
     Or.elim p_or_q_w
        (fun pw => Or.inl ⟨w, pw⟩)
        (fun qw => Or.inr ⟨w, qw⟩)

  let imp2 : (∃ x, p x) ∨ (∃ x, q x) → (∃ x, p x ∨ q x) :=
     fun ex_px_or_ex_qx =>
        Or.elim ex_px_or_ex_qx
          ( fun ⟨w, pw⟩ => ⟨w, Or.inl pw⟩ )
          ( fun ⟨w, qw⟩ => ⟨w, Or.inr qw⟩ )

  Iff.intro imp1 imp2


theorem dne0  {p : Prop} (hp : p) : ¬¬ p :=
  fun h1 : (p -> False) =>
        h1 hp


theorem dne {p : Prop} (h : ¬¬p) : p :=
  Or.elim (em p)
    (fun hp : p => hp)
    (fun hnp : ¬p => absurd hnp h)

example : (∀ x, p x) ↔ ¬ (∃ x, ¬ p x) :=
  let imp1 :  (∀ x, p x) →  ¬ (∃ x, ¬ p x) :=
     fun h1: (∀ x, p x) =>
     fun ⟨w, npw⟩  =>
        let pw := h1 w
        absurd pw npw

  let imp2 : ¬ (∃ x, ¬ p x) → (∀ x, p x) :=
     fun h1 : ¬ (∃ x, ¬ p x) =>
     fun (x : α) =>
        let exm: (p x ∨ ¬ p x) := em (p x)
        Or.elim exm
          (  -- case: p x
            fun px: p x =>  px
          )
          ( -- case
            fun npx =>
              let e1: (∃ x, ¬ p x) := ⟨x, npx⟩
              absurd e1 h1
          )

  Iff.intro imp1 imp2




example : (∃ x, p x) ↔ ¬ (∀ x, ¬ p x) := sorry
example : (¬ ∃ x, p x) ↔ (∀ x, ¬ p x) := sorry
example : (¬ ∀ x, p x) ↔ (∃ x, ¬ p x) := sorry

example : (∀ x, p x → r) ↔ (∃ x, p x) → r := sorry
example (a : α) : (∃ x, p x → r) ↔ (∀ x, p x) → r := sorry
example (a : α) : (∃ x, r → p x) ↔ (r → ∃ x, p x) := sorry
