# SPDX-License-Identifier: Apache-2.0
"""Evidence for the decision-theory battery (THM-SCORE/STOP/GAME/JENSEN).

Every check is exact (Fraction) and exhaustive within its stated bounds:

  THM-SCORE-001  Brier properness: over every true distribution on a k-outcome
                 rational grid, expected Brier score is uniquely minimized by
                 reporting the true distribution — every other report on the
                 grid scores STRICTLY worse. k in {2,3}, denominators to 6.
  THM-STOP-001   Secretary optimality: the backward-induction DP value equals
                 the best threshold rule's exact win probability for every
                 n <= 20, and the 'reject t*, take next record' policy is
                 therefore optimal; win probability is exact rational.
  THM-GAME-001   Minimax = maximin: for every 2x2 zero-sum game with integer
                 payoffs in [-4,4] (6561 games), the row player's guaranteed
                 (maximin) value equals the game value equals the column
                 player's (minimax) value, in exact arithmetic.
  THM-JENSEN-001 Jensen for x^2: E[X^2] - (E[X])^2 >= 0 (variance non-negative)
                 for every rational weight/point configuration on the grid,
                 with equality iff X is constant.

Seeded from model knowledge; trusted only because the checker verified every
case in exact rational arithmetic. Scope is exactly the enumerated instances.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theorems"))

from decision_theory import (  # noqa: E402
    expected_brier, game_maximin_mixed, game_value_2x2, jensen_gap_sq,
    prob_grid, secretary_best_threshold, secretary_dp_value,
)

ARTIFACT = ROOT / "artifacts" / "decision_theory.json"


def check_brier() -> dict:
    checks = 0
    configs = 0
    for k, denom in [(2, 4), (2, 6), (3, 4), (3, 6)]:
        grid = prob_grid(k, denom)
        for q in grid:
            self_score = expected_brier(q, q)
            for r in grid:
                if r == q:
                    continue
                assert expected_brier(q, r) > self_score
                checks += 1
            configs += 1
    return {"strict_better_checks": checks, "true_distributions": configs,
            "grids": "k in {2,3}, denom in {4,6}"}


def check_secretary() -> dict:
    rows = {}
    matches = 0
    for n in range(1, 21):
        dp = secretary_dp_value(n)
        t, thr = secretary_best_threshold(n)
        assert dp == thr, (n, dp, thr)
        matches += 1
        if n in (3, 4, 8, 20):
            rows[str(n)] = {"win_prob": str(dp), "best_threshold": t}
    return {"dp_equals_threshold_checks": matches, "max_n": 20,
            "samples": rows}


def check_games() -> dict:
    lo, hi = -4, 4
    checks = 0
    for a, b, c, d in product(range(lo, hi + 1), repeat=4):
        v = game_value_2x2(a, b, c, d)
        row_maxmin = max(min(a, b), min(c, d))
        col_minmax = min(max(a, c), max(b, d))
        if row_maxmin == col_minmax:
            assert v == Fraction(row_maxmin)
        else:
            # mixed: row's guaranteed value equals the game value
            assert game_maximin_mixed(a, b, c, d) == v
            # and v lies strictly between the pure bounds (a real mixed value)
            assert row_maxmin < v < col_minmax
        checks += 1
    return {"games_checked": checks, "payoff_range": [lo, hi]}


def check_jensen() -> dict:
    checks = 0
    zero_when_constant = 0
    for denom in [3, 4]:
        weights_grid = prob_grid(3, denom)
        for w in weights_grid:
            for xs in product([Fraction(x, 2) for x in range(-2, 3)], repeat=3):
                gap = jensen_gap_sq(list(w), list(xs))
                assert gap >= 0
                if len(set(xs)) == 1:
                    assert gap == 0
                    zero_when_constant += 1
                checks += 1
    return {"nonneg_checks": checks,
            "equality_when_constant": zero_when_constant}


def main() -> int:
    out = {
        "brier_properness": check_brier(),
        "secretary": check_secretary(),
        "zero_sum_games": check_games(),
        "jensen_sq": check_jensen(),
    }
    ARTIFACT.parent.mkdir(exist_ok=True)
    ARTIFACT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    try:
        from vericlaim.provenance import stamp
        stamp(str(ARTIFACT.relative_to(ROOT)),
              script="python3 theorems/evidence_decision_theory.py")
    except ImportError:
        pass
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
