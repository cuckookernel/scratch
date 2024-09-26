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


theorem a_imp_negb_imp_b_imp_a :  (a → ¬b) -> (b → ¬a) :=
   fun h1: (a → ¬b) =>
      fun hb : b =>
      let ema : (a ∨ ¬ a) := em a
      Or.elim ema
        (fun ha =>
            let hnb := h1 ha
            absurd hb hnb)
        (fun hna => hna)

theorem nega_imp_b_IMP_negb_imp_a :  (¬ a → b) -> (¬ b → a) :=
   fun h1: (¬ a → b) =>
      fun hnb : ¬ b =>
      let ema : (a ∨ ¬ a) := em a
      Or.elim ema
        (fun ha => ha)
        (fun hna =>
          let hb := h1 hna
          absurd hb hnb)


theorem th1 :  (∀ x, q x) →  ¬ (∃ x, ¬ q x) :=
     fun h1: (∀ x, q x) =>
     fun ⟨w, npw⟩  =>
        let pw := h1 w
        absurd pw npw

theorem th1_cr : (∃ x, ¬ q x) →  ¬ (∀ x, q x) :=
      a_imp_negb_imp_b_imp_a (th1 α q)


theorem th1b: ¬ (∃ x, ¬ p x) → (∀ x, p x) :=
     fun h1 : ¬ (∃ x, ¬ p x) =>
     fun (x : α) =>
        let exm: (p x ∨ ¬ p x) := em (p x)
        Or.elim exm
          (  -- case: p x
            fun px: p x =>  px
          )
          ( -- case: ¬ p x
            fun npx =>
              let e1: (∃ x, ¬ p x) := ⟨x, npx⟩
              absurd e1 h1
          )

theorem th1b_cr: ¬ (∀ x, p x) → (∃ x, ¬ p x) :=
    nega_imp_b_IMP_negb_imp_a (th1b α p)


theorem th1_dimp: (∃ x, ¬ p x) ↔ ¬ (∀ x, p x) :=
    Iff.intro (th1_cr α p) (th1b_cr α p)

theorem th1_dimp_neq: (∃ x, ¬ ¬ p x) ↔ ¬ (∀ x, ¬ p x) :=
    let np x := ¬ p x
    Iff.intro (th1_cr α np) (th1b_cr α np)

theorem p_eq_nnp_ex : (∃ x, ¬ ¬ p x) ↔ (∃ x, p x) :=
  let imp_rl:  (∃ x, ¬ ¬ p x) → (∃ x, p x) :=
      fun ⟨w , nnpw⟩ => ⟨w , dne nnpw⟩

  let imp_lr: (∃ x, p x) → (∃ x, ¬ ¬ p x)  :=
      fun ⟨w , nnpw⟩ => ⟨w , dne0 nnpw⟩

  Iff.intro imp_rl imp_lr

theorem crec: (a → b) → (¬b → ¬a) :=
    fun h1 =>
       fun (hnb : ¬b) =>
           fun (ha : a) => absurd (h1 ha) hnb

theorem p_eq_nnp_ex_neg: ¬(∃ x, p x) ↔ ¬ (∃ x, ¬ ¬ p x) :=
      Iff.intro
        (crec (p_eq_nnp_ex α p).mp)
        (crec (p_eq_nnp_ex α p).mpr)

theorem th1_dimp_neq_s: (∃ x, p x) ↔ ¬ (∀ x, ¬ p x) :=
    let imp_lr : (∃ x, p x) →  ¬ (∀ x, ¬ p x) :=
      fun h =>
         let int := (p_eq_nnp_ex α p).mpr h
         (th1_dimp_neq α p).mp int

    let imp_rl : ¬ (∀ x, ¬ p x) → (∃ x, p x):=
      fun h =>
         let int := (th1_dimp_neq α p).mpr h
         (p_eq_nnp_ex α p).mp int

    Iff.intro imp_lr imp_rl


theorem p_eq_nnp_forall : (∀ x, ¬ ¬ p x) ↔ (∀ x, p x) :=
  let imp_rl:  (∀ x, ¬¬ p x) → (∀ x, p x) :=
      fun axnnpx =>
      fun x =>
        let nnpx := axnnpx x
        let px := dne nnpx
        px

  let imp_lr: (∀ x, p x) → (∀ x, ¬ ¬ p x)  :=
      fun axpx =>
      fun x =>
        let px := axpx x
        let nnpx := dne0 px
        nnpx

  Iff.intro imp_rl imp_lr

theorem th1b_np: ¬ (∃ x, ¬¬ p x) → (∀ x, ¬ p x) :=
     let np x := ¬ p x
     th1b α np

theorem th1nq :  ¬ (∃ x, p x) ↔ (∀ x, ¬ p x) :=
  let mp :=
     fun h1: (∀ x, ¬ p x) =>
     fun ⟨w, pw⟩  =>
        let npw : ¬ p w  := h1 w
        let nnpw := dne0 pw
        absurd npw nnpw
  let mpr :=
     fun (h1: ¬ (∃ x, p x)) =>
       let int := (p_eq_nnp_ex_neg α p).mp h1
       th1b_np α p int

  Iff.intro mpr mp


example : (∃ x, p x) ↔ ¬ (∀ x, ¬ p x) := (th1_dimp_neq_s α p)
example : (¬ ∃ x, p x) ↔ (∀ x, ¬ p x) := (th1nq α p)
example : (¬ ∀ x, p x) ↔ (∃ x, ¬ p x) :=
  Iff.intro (th1_dimp α p).mpr (th1_dimp α p).mp

example : (∀ x, p x → r) ↔ (∃ x, p x) → r :=
  let mp :=
    fun h : (∀ x, p x → r) =>
    fun h2 : (∃ x, p x) =>
    let ⟨w, pw⟩ := h2
    let imp_w : p w -> r := h w
    imp_w pw
  let mpr :=
    fun h : (∃ x, p x) → r =>
    fun (x : α) =>
      fun px : p x =>
        let expx : (∃ x, p x) := ⟨x, px⟩
        h expx
  Iff.intro mp mpr

theorem neg_imp: ¬(a → b) → (a ∨ ¬ b) :=
  fun h: ¬(a → b) =>
  let emb : b ∨ ¬ b := em b
  Or.elim emb
  (fun hb: b =>
    let h_imp_b := fun _ : a => hb
    absurd h_imp_b h
  )
  (fun hnb: ¬b =>
   Or.inr hnb)

theorem neg_rec: (a -> b) -> (¬b -> ¬a) :=
  fun h:   (a -> b) =>
  fun hnb:  ¬ b =>
  fun ha:   a =>
    absurd (h ha) hnb


theorem imp_from_disj : (¬ a ∨ b) -> (a -> b) :=
  fun h: (¬ a ∨ b) =>
  fun ha : a =>
  Or.elim h
    (fun hna: ¬a => absurd ha hna)
    (id)


theorem next_to_last_example (a : α) : (∃ x, p x → r) ↔ (∀ x, p x) → r :=
  let mp :=
    fun h : (∃ x, p x → r) =>
    fun h2 : (∀ x, p x) =>
    let ⟨w, imp_r⟩ := h
    let pw := h2 w
    imp_r pw
  let mpr : ((∀ x, p x) → r) → (∃ x, p x → r) :=
    fun h : (∀ x, p x) → r =>
    Or.elim (em r)
    (fun hr =>
      let q x := p x → r
      let wf : q a := fun _ : p a => hr
      Exists.intro a wf
    )
    (fun hnr =>
      let nfxpx : ¬(∀ x, p x) := (neg_rec h) hnr
      let exnpx : (∃ x, ¬ p x) :=  (th1_dimp α p).mpr nfxpx
      let ⟨w, hnpw⟩ := exnpx
      let np_or_r : ¬ p w ∨ r := Or.inl hnpw
      let px_imp_r : p w → r := imp_from_disj np_or_r
      ⟨ w, px_imp_r ⟩
    )
  Iff.intro mp mpr

#check next_to_last_example


theorem final_example (a : α) : (∃ x, r → p x) ↔ (r → ∃ x, p x) :=
  let mp : (∃ x, r → p x) → (r → ∃ x, p x) :=
    fun h1 : (∃ x, r → p x) =>
      let ⟨w, hw⟩ := h1
      fun hr : r => ⟨w, hw hr⟩
  let mpr : (r → ∃ x, p x) → (∃ x, r → p x) :=
     fun h : (r → ∃ x, p x) =>
     Or.elim (em r)
      (fun hr =>
        let ⟨w, pw⟩ := h hr
        ⟨w, fun _: r => pw⟩
      )
      (fun hnr : ¬r =>
        let disj: ¬ r ∨ p a := Or.inl hnr
        ⟨a, imp_from_disj disj⟩
      )

  Iff.intro mp mpr


#check final_example
