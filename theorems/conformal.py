# SPDX-License-Identifier: Apache-2.0
"""Split conformal prediction — a reusable, exact-arithmetic-friendly module.

The finite-sample guarantee this implements is COMBINATORIAL: under
exchangeability, the rank of the test score among the n+1 pooled scores is
uniform, so the prediction set built from the k-th smallest calibration
score with k = ceil((n+1)(1-alpha)) covers with probability

    exactly k/(n+1)              (no ties)      >= 1 - alpha,
    and at least 1 - alpha       (with ties; conservative direction).

Everything here works on any ordered numeric type — pass ``fractions.
Fraction`` scores and every quantity (quantile, coverage, p-value) is exact.
The guarantees are machine-verified exhaustively in
evidence_conformal.py (claims THM-CONF-001..004 in the library); the caveats
there state the scope. Model-agnostic: scores come from ANY predictor.

This module is intended for reuse via the library's use_code (byte-exact
vendoring + binding test): program with the guarantee behind you.
"""
from __future__ import annotations

from fractions import Fraction


def conformal_k(n_calibration: int, alpha: Fraction) -> int:
    """k = ceil((n+1)(1-alpha)): the calibration-order-statistic index.

    If k > n_calibration the prediction set is everything (small n or tiny
    alpha) — that is the honest answer, not an error."""
    if n_calibration < 1:
        raise ValueError("need at least one calibration score")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    target = (n_calibration + 1) * (1 - Fraction(alpha))
    k = int(target)
    if k < target:
        k += 1
    return k


def conformal_quantile(cal_scores, alpha):
    """The score threshold: k-th smallest calibration score, or None when
    the guarantee forces the full set (k > n)."""
    scores = sorted(cal_scores)
    k = conformal_k(len(scores), Fraction(alpha))
    if k > len(scores):
        return None  # prediction set is everything
    return scores[k - 1]


def covers(cal_scores, test_score, alpha) -> bool:
    """Is the test score inside the conformal set? (score <= quantile;
    a None quantile covers everything.)"""
    q = conformal_quantile(cal_scores, alpha)
    return True if q is None else test_score <= q


def p_value(cal_scores, test_score) -> Fraction:
    """Conformal p-value (1 + #{cal >= test}) / (n+1) — super-uniform under
    exchangeability: P(p <= t) <= t for every t."""
    n = len(cal_scores)
    ge = sum(1 for s in cal_scores if s >= test_score)
    return Fraction(1 + ge, n + 1)


def exchangeable_coverage(pooled_scores, alpha) -> Fraction:
    """EXACT coverage under exchangeability for a concrete pool: average the
    coverage indicator over every choice of test position. This is the
    quantity the finite-sample theorem constrains, computable exactly."""
    n1 = len(pooled_scores)
    hits = 0
    for i in range(n1):
        cal = list(pooled_scores[:i]) + list(pooled_scores[i + 1:])
        if covers(cal, pooled_scores[i], alpha):
            hits += 1
    return Fraction(hits, n1)
