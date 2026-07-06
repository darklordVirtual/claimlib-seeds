# SPDX-License-Identifier: Apache-2.0
"""Evidence for the verification-amplification battery (THM-VOTE/ROUTE).

Every check is exact (Fraction) and exhaustive within its stated bounds:

  THM-VOTE-001  best-of-n identity: full 2^n outcome enumeration equals
                1-(1-p)^n, for all n <= 12 and nine p values.
  THM-VOTE-002  Condorcet amplification: for p > 1/2, majority of n
                independent voters is >= p and strictly increases with n,
                for all odd n <= 15 and five p values; and for p < 1/2 it
                DEGRADES (the honest converse).
  THM-ROUTE-001 verifier-gated cascade: over every truth table of
                (small_correct, big_correct) for k <= 8 items (4^k tables at
                k=8 checked exhaustively), gated-cascade errors never exceed
                big-model-alone errors; plus the cascade cost identity vs
                explicit enumeration for every defer set with k <= 10.

Seeded from model knowledge; trusted only because the checker verified
every case. Independence of attempts and verifier perfection are MODEL
ASSUMPTIONS of the theorems — the caveats carry that scope.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theorems"))

from verifier_math import (  # noqa: E402
    best_of_n_success, best_of_n_success_enumerated, cascade_cost,
    cascade_cost_enumerated, gated_cascade_errors, majority_correct,
)

ARTIFACT = ROOT / "artifacts" / "verifier_math.json"


def check_best_of_n() -> dict:
    ps = [Fraction(k, 10) for k in range(1, 10)]
    checks = 0
    for n in range(1, 13):
        for p in ps:
            assert best_of_n_success_enumerated(p, n) == best_of_n_success(p, n)
            checks += 1
    # amplification: strictly increasing in n for 0 < p < 1
    for p in ps:
        for n in range(1, 12):
            assert best_of_n_success(p, n + 1) > best_of_n_success(p, n)
    return {"identity_checks": checks, "max_n": 12,
            "p_grid": [str(p) for p in ps]}


def check_condorcet() -> dict:
    ps_up = [Fraction(51, 100), Fraction(3, 5), Fraction(7, 10),
             Fraction(4, 5), Fraction(9, 10)]
    amplified = 0
    for p in ps_up:
        prev = Fraction(0)
        for n in range(1, 16, 2):
            m = majority_correct(p, n)
            assert m >= p or n == 1
            assert m > prev or n == 1
            prev = m
            amplified += 1
    degraded = 0
    for p in [1 - q for q in ps_up]:
        for n in range(3, 16, 2):
            assert majority_correct(p, n) < p
            degraded += 1
    return {"amplification_checks": amplified, "degradation_checks": degraded,
            "max_n": 15}


def check_gated_cascade() -> dict:
    dominance = 0
    for k in range(1, 9):
        for bits in product((False, True), repeat=2 * k):
            table = [(bits[2 * i], bits[2 * i + 1]) for i in range(k)]
            cascade, big = gated_cascade_errors(table)
            assert cascade <= big
            dominance += 1
    cs, cb = Fraction(1), Fraction(30)
    cost_checks = 0
    for k in range(1, 11):
        for defer_bits in product((False, True), repeat=k):
            deferred = list(defer_bits)
            rate = Fraction(sum(deferred), k)
            assert cascade_cost_enumerated(cs, cb, deferred) == \
                cascade_cost(cs, cb, rate)
            cost_checks += 1
    return {"dominance_tables_checked": dominance,
            "cost_identity_checks": cost_checks, "max_items": 10,
            "cost_small": str(cs), "cost_big": str(cb)}


def main() -> int:
    out = {
        "best_of_n": check_best_of_n(),
        "condorcet": check_condorcet(),
        "gated_cascade": check_gated_cascade(),
    }
    ARTIFACT.parent.mkdir(exist_ok=True)
    ARTIFACT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    try:
        from vericlaim.provenance import stamp
        stamp(str(ARTIFACT.relative_to(ROOT)),
              script="python3 theorems/evidence_verifier_math.py")
    except ImportError:
        pass  # provenance stamped when run inside the gated repo env
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
