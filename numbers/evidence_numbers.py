# SPDX-License-Identifier: Apache-2.0
"""Compute number-theoretic facts by exhaustive verification; write evidence.

Every value here is COMPUTED at run time — never typed from memory. The
claims these back are explicitly bounded ("verified for all n <= N"), which
is what an exhaustive check honestly earns: a bounded verification is not a
proof of the general conjecture, and the caveats say so.

    python3 numbers/evidence_numbers.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

GOLDBACH_LIMIT = 100_000
PRIME_LIMIT = 10_000


def sieve(n: int) -> list[bool]:
    is_p = [True] * (n + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i:: i] = [False] * len(range(i * i, n + 1, i))
    return is_p


def main() -> int:
    is_p_small = sieve(PRIME_LIMIT)
    primes_below = sum(is_p_small)
    twin_pairs = sum(1 for i in range(3, PRIME_LIMIT - 1)
                     if is_p_small[i] and is_p_small[i + 2])

    is_p = sieve(GOLDBACH_LIMIT)
    primes = [i for i, b in enumerate(is_p) if b]
    prime_set = set(primes)
    goldbach_ok = 0
    for even in range(4, GOLDBACH_LIMIT + 1, 2):
        if not any((even - p) in prime_set for p in primes if p <= even // 2):
            print(f"[FAIL] Goldbach counterexample candidate at {even} — "
                  f"refusing to write evidence")
            return 1
        goldbach_ok += 1

    out = Path(__file__).resolve().parent.parent / "artifacts" / "numbers.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "schema": "numbers_v1",
        "method": "exhaustive computation (sieve of Eratosthenes)",
        "prime_limit": PRIME_LIMIT,
        "primes_below_limit": primes_below,
        "twin_prime_pairs_below_limit": twin_pairs,
        "goldbach_limit": GOLDBACH_LIMIT,
        "goldbach_even_numbers_verified": goldbach_ok,
    }, indent=2, sort_keys=True) + "\n")
    try:
        sys.path.insert(0, "/Users/stian/vericlaim")
        from vericlaim.provenance import stamp
        stamp(out, script="python3 numbers/evidence_numbers.py")
    except ImportError:
        pass
    print(f"[OK] primes<{PRIME_LIMIT}: {primes_below}, twin pairs: {twin_pairs}, "
          f"Goldbach verified for {goldbach_ok} even numbers <= {GOLDBACH_LIMIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
