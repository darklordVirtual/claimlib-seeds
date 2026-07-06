# SPDX-License-Identifier: Apache-2.0
"""Exact combinatorics of verification — when checking amplifies a weak model.

The honest route to frontier-like capability WITHOUT frontier scale is
verify-route-abstain: draw several candidates and keep one a verifier
accepts, vote across independent attempts, defer to a stronger (costlier)
model when the gate refuses. This module is the exact math of that pattern:
pure stdlib + Fraction, no floats, importable via the library's use_code.

Nothing here says a real verifier IS perfect or real attempts ARE
independent — those are the caveats the claims carry. The theorems are the
exact identities the architecture composes.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb


def best_of_n_success(p: Fraction, n: int) -> Fraction:
    """P(at least one of n independent attempts succeeds), each with
    success probability p: 1 - (1-p)^n."""
    return 1 - (1 - p) ** n


def best_of_n_success_enumerated(p: Fraction, n: int) -> Fraction:
    """The same probability computed the slow, assumption-free way: sum the
    exact probability of every outcome vector containing >= 1 success."""
    total = Fraction(0)
    for outcome in product((0, 1), repeat=n):
        if any(outcome):
            prob = Fraction(1)
            for o in outcome:
                prob *= p if o else (1 - p)
            total += prob
    return total


def majority_correct(p: Fraction, n: int) -> Fraction:
    """P(majority of n independent voters is correct), each correct with
    probability p; n odd. Exact binomial tail."""
    if n % 2 == 0:
        raise ValueError("majority needs odd n")
    k = n // 2 + 1
    return sum(Fraction(comb(n, i)) * p**i * (1 - p) ** (n - i)
               for i in range(k, n + 1))


def cascade_cost(c_small: Fraction, c_big: Fraction,
                 defer_rate: Fraction) -> Fraction:
    """Expected cost of a two-tier cascade that always runs the small model
    and defers a fraction of items to the big one."""
    return c_small + defer_rate * c_big


def cascade_cost_enumerated(c_small: Fraction, c_big: Fraction,
                            deferred: list[bool]) -> Fraction:
    """Total cost over an explicit item list, divided by item count —
    the identity's assumption-free counterpart."""
    n = len(deferred)
    total = sum(c_small + (c_big if d else Fraction(0)) for d in deferred)
    return Fraction(total, n)


def gated_cascade_errors(table: list[tuple[bool, bool]]) -> tuple[int, int]:
    """Errors of a verifier-gated cascade vs the big model alone, over an
    explicit truth table [(small_correct, big_correct), ...] with a PERFECT
    verifier: use the small answer iff it is correct, else defer.

    Returns (cascade_errors, big_alone_errors)."""
    cascade = sum(1 for s, b in table if not s and not b)
    big = sum(1 for _, b in table if not b)
    return cascade, big
