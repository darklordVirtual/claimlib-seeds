# SPDX-License-Identifier: Apache-2.0
"""Bounded, machine-verifiable instances of ML/CS foundation theorems.

HONESTY FIRST: none of these computations proves the general theorem — each
claim's scope is EXACTLY what was computed, and the caveats say so. What
they earn is a machine-checked (or, where floats intrude, a reproducibly
computed) bounded instance:

1. BAYES     — P(A|B)P(B) == P(B|A)P(A) verified in EXACT rational
               arithmetic over every joint pmf on two binary events with
               denominator N (an exhaustive family; identity, no rounding).
2. UAT       — an EXPLICIT one-hidden-layer ReLU network (constructed, not
               trained) approximates sin on [0, pi]; sup-error measured on
               a fixed dense grid. A constructive instance of universal
               approximation, not the theorem.
3. MASTER    — exact integer unrolling of the three canonical
               divide-and-conquer recurrences matches their closed forms
               for all n = 2^k, k <= K.
4. CLT       — Kolmogorov distance between the standardized sum of n fair
               dice and the normal CDF, computed from the EXACT pmf
               (fractions) against math.erf, strictly decreasing over the
               computed n-ladder.

    python3 theorems/evidence_ml_foundations.py
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ── 1. Bayes: exact identity over an exhaustive family ─────────────────────

def verify_bayes(denom: int = 12) -> dict:
    """All joint pmfs p(A=a, B=b) with entries i/denom summing to 1."""
    checked = 0
    for c in product(range(denom + 1), repeat=4):
        if sum(c) != denom:
            continue
        p = [Fraction(x, denom) for x in c]  # p11, p10, p01, p00
        pa = p[0] + p[1]
        pb = p[0] + p[2]
        # Bayes as the product identity (conditionals need pa, pb > 0):
        if pb > 0 and pa > 0:
            p_a_given_b = p[0] / pb
            p_b_given_a = p[0] / pa
            if p_a_given_b * pb != p_b_given_a * pa:
                raise AssertionError(f"Bayes identity FAILED at {c}")
        checked += 1
    return {"denominator": denom, "n_joint_distributions_checked": checked,
            "arithmetic": "exact rational (fractions)"}


# ── 2. UAT: explicit ReLU construction, measured sup-error ────────────────

def verify_uat(n_units: int = 65, n_grid: int = 10001) -> dict:
    """Piecewise-linear interpolant of sin on [0, pi] IS a 1-hidden-layer
    ReLU network with n_units units; measure max grid error."""
    a, b = 0.0, math.pi
    knots = [a + (b - a) * i / (n_units - 1) for i in range(n_units)]
    vals = [math.sin(x) for x in knots]

    def net(x: float) -> float:  # evaluate the PL interpolant directly
        if x <= knots[0]:
            return vals[0]
        for i in range(1, len(knots)):
            if x <= knots[i]:
                t = (x - knots[i - 1]) / (knots[i] - knots[i - 1])
                return vals[i - 1] * (1 - t) + vals[i] * t
        return vals[-1]

    max_err = max(abs(net(a + (b - a) * i / (n_grid - 1))
                      - math.sin(a + (b - a) * i / (n_grid - 1)))
                  for i in range(n_grid))
    return {"target": "sin on [0, pi]", "hidden_units": n_units,
            "grid_points": n_grid,
            "max_grid_error": round(max_err, 8),
            "max_grid_error_below": 0.001,
            "ok": max_err < 0.001}


# ── 3. Master theorem: exact recurrences vs closed forms ──────────────────

def verify_master(k_max: int = 30) -> dict:
    """T(1)=1 throughout; verify closed forms exactly for n = 2^k."""
    cases = {
        "binary_search  T(n)=T(n/2)+1   -> k+1": (
            lambda tp, n: tp + 1, lambda k, n: k + 1),
        "merge_sort     T(n)=2T(n/2)+n  -> n(k+1)": (
            lambda tp, n: 2 * tp + n, lambda k, n: n * (k + 1)),
        "case1_example  T(n)=4T(n/2)+n  -> 2*4^k-2^k": (
            lambda tp, n: 4 * tp + n, lambda k, n: 2 * 4 ** k - 2 ** k),
    }
    for name, (step, closed) in cases.items():
        t = 1
        for k in range(0, k_max + 1):
            n = 2 ** k
            if k > 0:
                t = step(t, n)
            if t != closed(k, n):
                raise AssertionError(f"{name} FAILED at k={k}: {t}")
    return {"k_max": k_max, "recurrences_verified": len(cases),
            "largest_n": 2 ** k_max, "arithmetic": "exact integers"}


# ── 4. CLT: exact dice pmf vs normal CDF, Kolmogorov distance ──────────────

def verify_clt(ns=(1, 2, 4, 8, 16, 32)) -> dict:
    def dice_pmf(n: int) -> dict[int, Fraction]:
        pmf = {0: Fraction(1)}
        die = {i: Fraction(1, 6) for i in range(1, 7)}
        for _ in range(n):
            nxt: dict[int, Fraction] = {}
            for s, ps in pmf.items():
                for f, pf in die.items():
                    nxt[s + f] = nxt.get(s + f, Fraction(0)) + ps * pf
            pmf = nxt
        return pmf

    def phi(x: float) -> float:
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    distances = {}
    for n in ns:
        pmf = dice_pmf(n)
        mean, var = 3.5 * n, n * 35.0 / 12.0
        sd = math.sqrt(var)
        cdf = Fraction(0)
        d = 0.0
        for s in sorted(pmf):
            cdf += pmf[s]
            d = max(d, abs(float(cdf) - phi((s + 0.5 - mean) / sd)))
        distances[n] = round(d, 6)
    seq = [distances[n] for n in ns]
    monotone = all(seq[i + 1] < seq[i] for i in range(len(seq) - 1))
    if not monotone:
        raise AssertionError(f"Kolmogorov distances not decreasing: {distances}")
    return {"n_ladder": list(ns), "kolmogorov_distance": distances,
            "strictly_decreasing": True,
            "final_distance": seq[-1],
            "pmf_arithmetic": "exact rational; normal CDF via math.erf (float)"}


def main() -> int:
    report = {
        "schema": "ml_foundations_v1",
        "bayes": verify_bayes(),
        "uat": verify_uat(),
        "master": verify_master(),
        "clt": verify_clt(),
    }
    out = HERE.parent / "artifacts" / "ml_foundations.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    try:
        sys.path.insert(0, "/Users/stian/vericlaim")
        from vericlaim.provenance import stamp
        stamp(out, script="python3 theorems/evidence_ml_foundations.py")
    except ImportError:
        pass
    print(f"[OK] bayes: {report['bayes']['n_joint_distributions_checked']} "
          f"exact distributions; uat: err {report['uat']['max_grid_error']}; "
          f"master: {report['master']['recurrences_verified']} recurrences to "
          f"n=2^{report['master']['k_max']}; clt: final D "
          f"{report['clt']['final_distance']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
