theorem test (p q : Prop) (hp: p) (hq : q) : p ∧ q ∧ p :=
   by
     apply And.intro
     exact hp
     apply And.intro
     exact hq
     exact hp

#print test


example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
  apply Iff.intro
  . intro h
    let hp := h.left
    apply Or.elim (And.right h)
    . intro hq
      apply Or.intro_left
      apply And.intro
      exact hp
      exact hq
    . intro hr
      apply Or.intro_right
      apply And.intro
      exact hp
      exact hr
  . intro h
    apply Or.elim h
    . intro hpq
      let hp := hpq.left
      let hq := hpq.right
      apply And.intro
      exact hp
      apply Or.intro_left
      exact hq
    . intro hpr
      let ⟨hp, hr⟩ := hpr
      apply And.intro
      exact hp
      exact Or.inr hr


example : ∀ a b c : Nat, a = b → a = c → c = b := by
    intro a b c a_eq_b a_eq_c
    apply Eq.trans
    . apply Eq.symm
      assumption
    . assumption


example (α : Type) (p q : α → Prop) : (∃ x, p x ∧ q x) → ∃ x, q x ∧ p x := by
   intro ⟨w, hpw, hqw⟩
   exact ⟨w, hqw, hpw⟩


example (α : Type) (p q : α → Prop) : (∃ x, p x ∨ q x) → ∃ x, q x ∨ p x := by
    intro
    | ⟨w, Or.inl h⟩ =>
      exact ⟨w, Or.inr h⟩
    | ⟨w, Or.inr h⟩ =>
      exact ⟨w, Or.inl h⟩


example (x y z w : Nat) (h₁ : x = y) (h₂ : y = z) (h₃ : z = w) : x = w := by
  apply Eq.trans
  assumption
  apply Eq.trans
  assumption
  assumption

example : ∀ a b c d : Nat, a = b → a = d → a = c → c = b := by
   intros a b c d
   intros
   rename_i h1 _ h3
   apply Eq.trans
   apply Eq.symm
   exact h3
   exact h1

example (y : Nat) : (fun x : Nat => 0) y = 0 := by
  rfl

example (x : Nat) : x = x := by
  revert x
  intro y
  rfl


example (x y : Nat) (h : x = y) : y = x := by
  apply Eq.symm
  exact h
