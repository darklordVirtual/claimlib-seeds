/- SPDX-License-Identifier: Apache-2.0

Fable-seeded theorems, checked by the Lean 4 kernel (core only, no mathlib).

THE SEEDING CONTRACT, now at full strength: these proofs were written from
model knowledge, and NOTHING is trusted because the model wrote it — the
Lean kernel (an independently developed, widely audited proof checker)
accepts or rejects every term. Unlike the bounded truth-table batteries,
these theorems are proved for ALL propositions / types / naturals, not for
enumerated instances.

The `#print axioms` block at the end records each theorem's axiom footprint
honestly: `[]` means fully constructive; classical results depend on
propext / Classical.choice / Quot.sound. -/

namespace ClaimLib

/- ── Propositional logic, universally quantified over Prop ─────────────── -/

theorem identity (p : Prop) : p → p := fun h => h

theorem hyp_syllogism (p q r : Prop) : (q → r) → (p → q) → (p → r) :=
  fun hqr hpq hp => hqr (hpq hp)

theorem contraposition (p q : Prop) : (p → q) → (¬q → ¬p) :=
  fun hpq hnq hp => hnq (hpq hp)

theorem contraposition_converse (p q : Prop) : (¬q → ¬p) → (p → q) :=
  fun h hp => Classical.byContradiction fun hnq => h hnq hp

theorem double_negation (p : Prop) : ¬¬p → p :=
  fun hnn => Classical.byContradiction fun hn => hnn hn

theorem excluded_middle (p : Prop) : p ∨ ¬p := Classical.em p

theorem peirce (p q : Prop) : ((p → q) → p) → p :=
  fun h => Classical.byContradiction
    fun hnp => hnp (h (fun hp => absurd hp hnp))

theorem de_morgan_or (p q : Prop) : ¬(p ∨ q) ↔ (¬p ∧ ¬q) :=
  ⟨fun h => ⟨fun hp => h (Or.inl hp), fun hq => h (Or.inr hq)⟩,
   fun ⟨hnp, hnq⟩ h => h.elim hnp hnq⟩

theorem de_morgan_and (p q : Prop) : ¬(p ∧ q) ↔ (¬p ∨ ¬q) :=
  ⟨fun h => (Classical.em p).elim
      (fun hp => Or.inr fun hq => h ⟨hp, hq⟩)
      Or.inl,
   fun h ⟨hp, hq⟩ => h.elim (fun hnp => hnp hp) (fun hnq => hnq hq)⟩

theorem material_implication (p q : Prop) : (p → q) ↔ (¬p ∨ q) :=
  ⟨fun hpq => (Classical.em p).elim (fun hp => Or.inr (hpq hp)) Or.inl,
   fun h hp => h.elim (fun hnp => absurd hp hnp) id⟩

theorem exportation (p q r : Prop) : (p ∧ q → r) ↔ (p → q → r) :=
  ⟨fun h hp hq => h ⟨hp, hq⟩, fun h ⟨hp, hq⟩ => h hp hq⟩

theorem and_distrib_or (p q r : Prop) :
    p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) :=
  ⟨fun ⟨hp, hqr⟩ => hqr.elim (fun hq => Or.inl ⟨hp, hq⟩)
                             (fun hr => Or.inr ⟨hp, hr⟩),
   fun h => h.elim (fun ⟨hp, hq⟩ => ⟨hp, Or.inl hq⟩)
                   (fun ⟨hp, hr⟩ => ⟨hp, Or.inr hr⟩)⟩

/- ── Quantifier logic (the first-order step) ────────────────────────────── -/

theorem not_exists_iff_forall_not {α : Type} (P : α → Prop) :
    (¬∃ x, P x) ↔ ∀ x, ¬P x :=
  ⟨fun h x hx => h ⟨x, hx⟩, fun h ⟨x, hx⟩ => h x hx⟩

theorem not_forall_iff_exists_not {α : Type} (P : α → Prop) :
    (¬∀ x, P x) ↔ ∃ x, ¬P x :=
  ⟨fun h => Classical.byContradiction fun hne =>
      h fun x => Classical.byContradiction fun hnp => hne ⟨x, hnp⟩,
   fun ⟨x, hnp⟩ h => hnp (h x)⟩

theorem forall_and {α : Type} (P Q : α → Prop) :
    (∀ x, P x ∧ Q x) ↔ (∀ x, P x) ∧ (∀ x, Q x) :=
  ⟨fun h => ⟨fun x => (h x).1, fun x => (h x).2⟩,
   fun ⟨hp, hq⟩ x => ⟨hp x, hq x⟩⟩

theorem exists_or {α : Type} (P Q : α → Prop) :
    (∃ x, P x ∨ Q x) ↔ (∃ x, P x) ∨ (∃ x, Q x) :=
  ⟨fun ⟨x, h⟩ => h.elim (fun hp => Or.inl ⟨x, hp⟩) (fun hq => Or.inr ⟨x, hq⟩),
   fun h => h.elim (fun ⟨x, hp⟩ => ⟨x, Or.inl hp⟩)
                   (fun ⟨x, hq⟩ => ⟨x, Or.inr hq⟩)⟩

/-- The drinker paradox: in any inhabited domain there is someone such that
if they drink, everyone drinks. Classical through and through. -/
theorem drinker {α : Type} [Nonempty α] (D : α → Prop) :
    ∃ x, D x → ∀ y, D y :=
  (Classical.em (∀ y, D y)).elim
    (fun h => ⟨Classical.choice ‹Nonempty α›, fun _ => h⟩)
    (fun h =>
      have hex : ∃ y, ¬D y := (not_forall_iff_exists_not D).mp h
      hex.elim fun y hy => ⟨y, fun hd => absurd hd hy⟩)

/- ── Natural numbers, by induction (core arithmetic) ────────────────────── -/

theorem nat_add_comm (a b : Nat) : a + b = b + a := by
  induction b with
  | zero => simp
  | succ n ih => rw [Nat.add_succ, ih, Nat.succ_add]

theorem nat_add_assoc (a b c : Nat) : a + b + c = a + (b + c) := by
  induction c with
  | zero => rfl
  | succ n ih => rw [Nat.add_succ, Nat.add_succ, ih, Nat.add_succ]

/-- Sum of the first n odd numbers. -/
def sumOdds : Nat → Nat
  | 0 => 0
  | n + 1 => sumOdds n + (2 * n + 1)

theorem sum_odds_eq_square (n : Nat) : sumOdds n = n * n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp [sumOdds, ih, Nat.succ_mul, Nat.mul_succ]
    omega

end ClaimLib

/- Axiom footprints — parsed into the evidence artifact. -/
#print axioms ClaimLib.identity
#print axioms ClaimLib.hyp_syllogism
#print axioms ClaimLib.contraposition
#print axioms ClaimLib.contraposition_converse
#print axioms ClaimLib.double_negation
#print axioms ClaimLib.excluded_middle
#print axioms ClaimLib.peirce
#print axioms ClaimLib.de_morgan_or
#print axioms ClaimLib.de_morgan_and
#print axioms ClaimLib.material_implication
#print axioms ClaimLib.exportation
#print axioms ClaimLib.and_distrib_or
#print axioms ClaimLib.not_exists_iff_forall_not
#print axioms ClaimLib.not_forall_iff_exists_not
#print axioms ClaimLib.forall_and
#print axioms ClaimLib.exists_or
#print axioms ClaimLib.drinker
#print axioms ClaimLib.nat_add_comm
#print axioms ClaimLib.nat_add_assoc
#print axioms ClaimLib.sum_odds_eq_square
