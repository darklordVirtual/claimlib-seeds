# claimlib-seeds

Model-seeded, machine-verified knowledge for the vericlaim claims library.

**The seeding contract:** formulas, derivations and reference titles here
were proposed from model knowledge (Claude Fable). Nothing is trusted
because the model proposed it — tautologies pass an exhaustive decision
procedure, Hilbert derivations pass a fail-closed proof checker, numeric
facts are computed at evidence time, and reference titles are only search
seeds that die unless the registrar (arXiv) returns an agreeing record.
What failed verification simply is not here.

Layout: `theorems/` (checkers + proofs), `numbers/` (exhaustive
computations), `research/` (registrar-verified extracts),
`build_register.py` (the register is GENERATED from evidence, never typed).

Verify: `PYTHONPATH=<vericlaim> python3 -m vericlaim && python3 -m vericlaim reproduce`
