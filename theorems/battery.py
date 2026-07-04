# SPDX-License-Identifier: Apache-2.0
"""The seeded theorem battery — classical propositional laws.

Seeding provenance, stated honestly: these formulas were proposed from model
knowledge (Claude Fable) as candidates. NOTHING here is trusted because the
model proposed it — every formula is exhaustively machine-verified by
tautcheck (a complete decision procedure) before it may be registered, and a
formula that fails simply never becomes a claim. The names are standard;
correctness comes from the checker alone.
"""

def IMP(a, b): return ["->", a, b]           # noqa: E704
def NOT(a): return ["not", a]                # noqa: E704
def AND(a, b): return ["and", a, b]          # noqa: E704
def OR(a, b): return ["or", a, b]            # noqa: E704
def IFF(a, b): return ["iff", a, b]          # noqa: E704

P, Q, R = "p", "q", "r"

THEOREMS = [
    ("THM-TAUT-001", "identity", IMP(P, P)),
    ("THM-TAUT-002", "excluded middle", OR(P, NOT(P))),
    ("THM-TAUT-003", "non-contradiction", NOT(AND(P, NOT(P)))),
    ("THM-TAUT-004", "double negation", IFF(NOT(NOT(P)), P)),
    ("THM-TAUT-005", "contraposition", IFF(IMP(P, Q), IMP(NOT(Q), NOT(P)))),
    ("THM-TAUT-006", "De Morgan (conjunction)",
     IFF(NOT(AND(P, Q)), OR(NOT(P), NOT(Q)))),
    ("THM-TAUT-007", "De Morgan (disjunction)",
     IFF(NOT(OR(P, Q)), AND(NOT(P), NOT(Q)))),
    ("THM-TAUT-008", "Peirce's law", IMP(IMP(IMP(P, Q), P), P)),
    ("THM-TAUT-009", "material implication", IFF(IMP(P, Q), OR(NOT(P), Q))),
    ("THM-TAUT-010", "exportation",
     IFF(IMP(AND(P, Q), R), IMP(P, IMP(Q, R)))),
    ("THM-TAUT-011", "distributivity (and over or)",
     IFF(AND(P, OR(Q, R)), OR(AND(P, Q), AND(P, R)))),
    ("THM-TAUT-012", "hypothetical syllogism (chain)",
     IMP(AND(IMP(P, Q), IMP(Q, R)), IMP(P, R))),
]
