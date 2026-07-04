# SPDX-License-Identifier: Apache-2.0
"""Exhaustive exact verification of split-conformal finite-sample guarantees.

The split-conformal guarantee is combinatorial, so — unusually for ML
theory — its finite-sample core CAN be machine-checked exactly:

1. IDENTITY   — with distinct scores, exchangeable coverage equals exactly
                ceil((n+1)(1-a))/(n+1) for ALL n <= 12 and five alphas,
                verified by full enumeration (literal quantile computation,
                not the abstract rank argument).
2. BOUNDS     — that identity is >= 1-a always, and < 1-a + 1/(n+1)
                whenever the set is proper (k <= n) — exact fractions.
3. TIES       — over ALL multisets of size <= 7 from a 3-value grid,
                coverage stays >= 1-a (ties only help) — exhaustive.
4. P-VALUE    — super-uniformity P(p <= t) <= t verified exactly for all
                rank configurations and a 20-point t-grid.
5. END-TO-END — a 13-point rational regression pool with a fixed predictor:
                leave-one-out exchangeable coverage meets the guarantee in
                exact arithmetic.

    python3 theorems/evidence_conformal.py
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from conformal import (  # noqa: E402
    conformal_k, exchangeable_coverage, p_value,
)

ALPHAS = (Fraction(1, 10), Fraction(1, 5), Fraction(1, 4),
          Fraction(1, 3), Fraction(1, 2))


def verify_identity_and_bounds(n_max: int = 12) -> dict:
    identity_checks = bound_checks = upper_checks = 0
    for n in range(1, n_max + 1):
        pooled = [Fraction(i) for i in range(1, n + 2)]  # distinct WLOG ranks
        for a in ALPHAS:
            k = conformal_k(n, a)
            cov = exchangeable_coverage(pooled, a)
            expected = Fraction(min(k, n + 1), n + 1)
            if cov != expected:
                raise AssertionError(f"identity FAILED n={n} a={a}: {cov}")
            identity_checks += 1
            if cov < 1 - a:
                raise AssertionError(f"lower bound FAILED n={n} a={a}")
            bound_checks += 1
            if k <= n:
                if not cov < 1 - a + Fraction(1, n + 1):
                    raise AssertionError(f"upper bound FAILED n={n} a={a}")
                upper_checks += 1
    return {"n_max": n_max, "alphas": [str(a) for a in ALPHAS],
            "identity_checks": identity_checks,
            "lower_bound_checks": bound_checks,
            "upper_bound_checks": upper_checks,
            "arithmetic": "exact rational"}


def verify_ties(max_pool: int = 7) -> dict:
    checked = 0
    for n1 in range(2, max_pool + 1):
        for pool in combinations_with_replacement(
                (Fraction(1), Fraction(2), Fraction(3)), n1):
            for a in ALPHAS:
                if exchangeable_coverage(list(pool), a) < 1 - a:
                    raise AssertionError(f"ties broke coverage: {pool}, {a}")
                checked += 1
    return {"max_pool_size": max_pool, "value_grid": 3,
            "coverage_checks": checked, "arithmetic": "exact rational"}


def verify_p_value(n_max: int = 12) -> dict:
    checked = 0
    for n in range(1, n_max + 1):
        pooled = [Fraction(i) for i in range(1, n + 2)]
        # exact distribution of p under exchangeability: test at each position
        ps = []
        for i in range(n + 1):
            cal = pooled[:i] + pooled[i + 1:]
            ps.append(p_value(cal, pooled[i]))
        for j in range(1, 21):
            t = Fraction(j, 20)
            mass = Fraction(sum(1 for p in ps if p <= t), n + 1)
            if mass > t:
                raise AssertionError(f"super-uniformity FAILED n={n} t={t}")
            checked += 1
    return {"n_max": n_max, "t_grid_points": 20,
            "super_uniformity_checks": checked, "arithmetic": "exact rational"}


def verify_end_to_end() -> dict:
    # a rational pool and a FIXED (not refit) predictor f(x) = x/2 + 1;
    # residual scores are distinct rationals by construction.
    pts = [(Fraction(x), Fraction(x, 2) + 1 + Fraction((-1) ** x * x, 17))
           for x in range(1, 14)]
    scores = [abs(y - (x / 2 + 1)) for x, y in pts]
    if len(set(scores)) != len(scores):
        raise AssertionError("scores not distinct — construction broken")
    results = {}
    for a in (Fraction(1, 4), Fraction(1, 10)):
        cov = exchangeable_coverage(scores, a)
        k = conformal_k(len(scores) - 1, a)
        expected = Fraction(min(k, len(scores)), len(scores))
        if cov != expected or cov < 1 - a:
            raise AssertionError(f"end-to-end FAILED a={a}: {cov}")
        results[str(a)] = {"coverage": str(cov), "expected": str(expected)}
    return {"pool_size": len(pts), "predictor": "fixed f(x) = x/2 + 1",
            "alphas": results, "arithmetic": "exact rational"}


def main() -> int:
    report = {"schema": "conformal_v1",
              "identity_bounds": verify_identity_and_bounds(),
              "ties": verify_ties(),
              "p_value": verify_p_value(),
              "end_to_end": verify_end_to_end()}
    out = HERE.parent / "artifacts" / "conformal.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    try:
        sys.path.insert(0, "/Users/stian/vericlaim")
        from vericlaim.provenance import stamp
        stamp(out, script="python3 theorems/evidence_conformal.py")
    except ImportError:
        pass
    ib = report["identity_bounds"]
    print(f"[OK] identity {ib['identity_checks']} checks; ties "
          f"{report['ties']['coverage_checks']}; p-value "
          f"{report['p_value']['super_uniformity_checks']}; end-to-end "
          f"{report['end_to_end']['alphas']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
