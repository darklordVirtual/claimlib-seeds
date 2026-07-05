# What if an AI could only say things a machine has verified?

This library is that experiment, running: every theorem, number and citation
here was PROPOSED by a model — and exists only because a proof checker,
exhaustive computation or academic registrar approved it. The proposals that
failed are documented too. Zero trust in the proposer, by construction.

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
