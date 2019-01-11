Theorem plus_O_n' : forall n : nat, 0 + n = n.
Proof.
intros n.
simpl.
reflexivity.
Qed.
Check plus_O_n'.
Theorem eq_sum : forall n m : nat, n=m -> n + n = m + m.
Proof.
intros n m.
intros.
rewrite -> H.
reflexivity.
Qed.
Theorem plus_id_exercise : forall n m o : nat,
   n = m -> m = o -> n + m = m + o.
Proof.
intros.
rewrite-> H.
rewrite-> H0.
reflexivity.
Qed.
Theorem Pap:forall n : nat, S n = 1 + n.
Proof.
intros n.
simpl.
reflexivity.
Qed.

Theorem mult_S_1 : forall n m : nat, m = S n -> m * (1 + n) = m * m.
Proof.
intros.
rewrite<- Pap.
rewrite<-H.
reflexivity.
Qed.

Fixpoint beq_nat ( n m : nat)  : bool := 
match n with 
| O => match m with 
        | O => true 
        | S m' => false
       end
| S n' => match m with 
          | O => false 
          | S m' => beq_nat n' m'
          end
end.

Theorem plus_1_neq_0 : forall n : nat, 
        beq_nat (n+1) 0 = false.
Proof.
intros n. destruct n as [|n].
- reflexivity.
- simpl. reflexivity.
Qed.

Theorem andb_comm : forall b c : bool, 
   andb b c = andb c b.
Proof.
intros [] [].
- reflexivity.
- reflexivity.
- reflexivity.
- reflexivity.
Qed.

Theorem andb_true_elim2 : forall b c : bool,
    andb b c = true -> c = true.
Proof.
intros [][].
- reflexivity.
- simpl. intros. intros. assumption.
- simpl. intros. reflexivity.
- simpl. intros. assumption.
Qed.

Theorem zero_nbeq_ṕlus_1 : forall n : nat, 
     beq_nat 0 (n + 1) = false.
Proof.
intros.
destruct n as [ |n'].
- reflexivity.
- reflexivity.
Qed.

Theorem identity_fun_app_2ice : forall ( f : bool -> bool ), 
   ( forall x : bool, f x = x ) -> ( forall b : bool, f( f b) = b ).
Proof.
intros.
rewrite->H.
rewrite->H.
reflexivity.
Qed.

Theorem eq_comm : forall (a b : bool), a = b -> b = a.
Proof.
intros.
rewrite->H.
reflexivity.
Qed.

Theorem andb_eq_orb : forall ( b c  : bool ), (andb b c = orb b c ) -> b = c.
Proof. 
intros [].
- simpl. intros. rewrite->H. reflexivity.
- simpl. intros. rewrite->H. reflexivity.
Qed.

Inductive bin : Type := 
| Z : bin
| D : bin -> bin
| L : bin -> bin.

Fixpoint incr ( b : bin ) : bin :=
match b with 
| Z => L Z
| D b' => L b'
| L b' => D( incr b' )
end.

Fixpoint bin_to_nat ( b : bin ) : nat := 
match b with 
| Z => 0 
| D b' => 2 * (bin_to_nat b')
| L b' => S( 2 * (bin_to_nat b') )
end. 

Example test_bin_incr1 : bin_to_nat( incr( D (D (D (L Z))) ) )  = 9.
Proof. reflexivity. Qed.

Theorem plus_n_0 : forall n : nat , n = n + 0.
Proof.
intros n. induction n as [ | n'  IHn' ].
- reflexivity.
- simpl. rewrite<-IHn'. reflexivity.
Qed.

Theorem mult_n_0 : forall n : nat, n * 0 = 0.
Proof.
intros n. induction n as [ | n' IHn' ].
- reflexivity.
- simpl. rewrite->IHn'. reflexivity.
Qed.

Theorem plus_n_SM : forall m n : nat, S(n+m) = n + (S m ).
Proof.
intros. induction n as  [ | n' IHn' ].
- simpl. reflexivity.
- simpl. rewrite->IHn'. reflexivity.
Qed.

Theorem plus_Comm : forall m n : nat, n + m = m + n.
Proof.
intros. induction n as [ | n' IHn' ].
- simpl. rewrite<-plus_n_0. reflexivity.
- simpl. rewrite->IHn'. rewrite plus_n_SM. reflexivity.
Qed.

Theorem plus_assoc : forall m n p : nat, n + (m + p) = (n + m) + p.
Proof.
intros. induction n as [ | n' IHn' ].
- simpl. reflexivity.
- simpl. rewrite IHn'. reflexivity.
Qed.

Compute ( fst(3,4) ).

Definition natprod : Type := 
(nat * nat)%type.


Definition swap_pair ( p : natprod ) : natprod := 
match p with 
| pair m n => pair n m
end.

Theorem snd_fst_is_swap : forall p : natprod, (snd p, fst p) = swap_pair p.
Proof.
intros. destruct p as [ m n ]. simpl. reflexivity.
Qed.

Fixpoint alternate ( l1 l2 : list nat ) : list nat := 
match l1 with : 
| nil => l2
| x :: xs =>