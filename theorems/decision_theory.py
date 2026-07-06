# SPDX-License-Identifier: Apache-2.0
"""Exact decision theory under uncertainty — the reasoning a strong model
leans on, verified in rational arithmetic instead of asserted.

Four load-bearing results, all EXACT (Fraction, no floats):

  brier properness   truthfully reporting your probabilities uniquely
                     minimizes expected Brier score — the formal reason
                     honest calibration beats confident guessing.
  secretary stopping the optimal explore-then-commit threshold, and its
                     exact win probability, by backward-induction DP.
  minimax = maximin  a 2x2 zero-sum game has a single value both players
                     can guarantee — the core of adversarial reasoning.
  jensen (x^2)       (E X)^2 <= E X^2, i.e. variance is non-negative —
                     the inequality behind every expectation bound.

Reusable via the library's use_code (stdlib only). The theorems are exact
identities/inequalities on bounded instances; the caveats carry the scope.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product


# --------------------------------------------------------------------------- #
# Proper scoring: honesty is optimal
# --------------------------------------------------------------------------- #

def expected_brier(true_dist: list[Fraction], report: list[Fraction]) -> Fraction:
    """Expected Brier score of reporting `report` when outcomes are drawn
    from `true_dist`: E_i[ sum_j (report_j - [i==j])^2 ]. Exact."""
    k = len(true_dist)
    total = Fraction(0)
    for i in range(k):
        loss = sum((report[j] - (1 if j == i else 0)) ** 2 for j in range(k))
        total += true_dist[i] * loss
    return total


def prob_grid(k: int, denom: int) -> list[list[Fraction]]:
    """All probability vectors on k outcomes with the given denominator:
    (a_1..a_k) with a_i >= 0 integers summing to denom, as Fractions."""
    out: list[list[Fraction]] = []
    for combo in product(range(denom + 1), repeat=k):
        if sum(combo) == denom:
            out.append([Fraction(c, denom) for c in combo])
    return out


# --------------------------------------------------------------------------- #
# Optimal stopping: the secretary problem
# --------------------------------------------------------------------------- #

def secretary_dp_value(n: int) -> Fraction:
    """Exact optimal win probability by backward induction over records.

    V_i = (1/i)*max(i/n, V_{i+1}) + (1 - 1/i)*V_{i+1}, V_{n+1}=0.
    The max encodes the optimal stop/continue choice at each record."""
    v = Fraction(0)
    for i in range(n, 0, -1):
        stop = Fraction(i, n)          # P(a record at i is the global best)
        v = Fraction(1, i) * max(stop, v) + (1 - Fraction(1, i)) * v
    return v


def secretary_threshold_value(n: int, t: int) -> Fraction:
    """Exact win probability of 'reject the first t, then take the first
    record': (t/n) * sum_{i=t+1..n} 1/(i-1)."""
    if t == 0:
        return Fraction(1, n)  # take the first candidate
    return Fraction(t, n) * sum(Fraction(1, i - 1) for i in range(t + 1, n + 1))


def secretary_best_threshold(n: int) -> tuple[int, Fraction]:
    """The threshold maximizing the win probability, and that probability."""
    best_t, best_v = 0, Fraction(1, n)
    for t in range(1, n):
        v = secretary_threshold_value(n, t)
        if v > best_v:
            best_t, best_v = t, v
    return best_t, best_v


# --------------------------------------------------------------------------- #
# Zero-sum games: minimax = maximin
# --------------------------------------------------------------------------- #

def game_value_2x2(a: int, b: int, c: int, d: int) -> Fraction:
    """Exact value of the 2x2 zero-sum game [[a,b],[c,d]] (row maximizes).
    Pure saddle point if one exists, else the mixed-strategy value."""
    row_maxmin = max(min(a, b), min(c, d))   # row picks row, col worst-cases
    col_minmax = min(max(a, c), max(b, d))   # col picks col, row best-cases
    if row_maxmin == col_minmax:
        return Fraction(row_maxmin)          # saddle point
    denom = a - b - c + d
    return Fraction(a * d - b * c, denom)


def game_maximin_mixed(a: int, b: int, c: int, d: int) -> Fraction:
    """Row's guaranteed payoff under its optimal mixed strategy (the value
    the row player can secure regardless of the column choice)."""
    row_maxmin = max(min(a, b), min(c, d))
    col_minmax = min(max(a, c), max(b, d))
    if row_maxmin == col_minmax:
        return Fraction(row_maxmin)
    denom = a - b - c + d
    p = Fraction(d - c, denom)               # P(row plays row 1)
    # row's payoff is v against EITHER column when col is indifferent:
    left = p * a + (1 - p) * c               # against column 1
    right = p * b + (1 - p) * d              # against column 2
    assert left == right
    return left


# --------------------------------------------------------------------------- #
# Jensen for x^2: variance is non-negative
# --------------------------------------------------------------------------- #

def jensen_gap_sq(weights: list[Fraction], xs: list[Fraction]) -> Fraction:
    """E[X^2] - (E[X])^2 for a discrete X, which must be >= 0 (it is the
    variance). Exact."""
    mean = sum(w * x for w, x in zip(weights, xs))
    mean_sq = sum(w * x * x for w, x in zip(weights, xs))
    return mean_sq - mean * mean
