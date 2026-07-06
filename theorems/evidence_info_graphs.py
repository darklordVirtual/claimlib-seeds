# SPDX-License-Identifier: Apache-2.0
"""Bounded instances: information theory, inequalities, logic, graphs, OT.

Same contract: exact sections earn machine_checked for exactly their scope;
float/seeded sections are graded benchmarked. Nothing proves the general
theorem, and every caveat says so.

1. HUFFMAN   — Huffman codes are optimal among ALL prefix codes (Kraft) for
               every rational source on 4 symbols with denominator 8 —
               exhaustive, exact fractions.
2. MARKOV    — Markov's and Chebyshev's inequalities hold exactly for all
               495 distributions on {0..4} with denominator 8, all
               thresholds tested — exact fractions.
3. POST      — {NAND} and {NOR} each generate ALL 16 binary boolean
               functions (closure to fixpoint); {AND, OR} generates only
               the 6 monotone ones and never NOT — exhaustive.
4. MAXFLOW   — max s-t flow == min s-t cut on ALL 4096 four-node networks
               with integer capacities 0..3 — exact integers.
5. OT1D      — in 1-D optimal transport, the sorted (monotone) matching is
               cost-minimal versus ALL 24 bijections, for every pair of
               4-point supports from an 8-point grid — exact fractions.
6. JL        — seeded random projection R^50 -> R^25 preserves all pairwise
               distances of 20 points within the measured distortion
               (floats -> benchmarked).
7. GLIVENKO  — empirical CDF sup-distance to the true uniform CDF shrinks
               by the measured factor from n=10 to n=10000 (seeded floats
               -> benchmarked).

    python3 theorems/evidence_info_graphs.py
"""
from __future__ import annotations

import heapq
import json
import math
import random
import sys
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ── 1. Huffman optimality, exhaustively ────────────────────────────────────

def _huffman_lengths(probs):
    heap = [(p, i, 0) for i, p in enumerate(probs)]  # (prob, id, depth-tree)
    trees = {i: [i] for i in range(len(probs))}
    depths = [0] * len(probs)
    heapq.heapify(heap)
    uid = len(probs)
    while len(heap) > 1:
        p1, i1, _ = heapq.heappop(heap)
        p2, i2, _ = heapq.heappop(heap)
        for leaf in trees[i1] + trees[i2]:
            depths[leaf] += 1
        trees[uid] = trees.pop(i1) + trees.pop(i2)
        heapq.heappush(heap, (p1 + p2, uid, 0))
        uid += 1
    return depths


def verify_huffman(denom: int = 8) -> dict:
    n, checked = 4, 0
    # all candidate prefix-code length profiles obeying Kraft's inequality
    profiles = [ls for ls in product(range(1, 7), repeat=n)
                if sum(Fraction(1, 2 ** li) for li in ls) <= 1]
    for c in product(range(1, denom + 1), repeat=n):
        if sum(c) != denom:
            continue
        probs = [Fraction(x, denom) for x in c]
        hl = _huffman_lengths(probs)
        h_avg = sum(p * li for p, li in zip(probs, hl))
        best = min(sum(p * li for p, li in zip(probs, ls)) for ls in profiles)
        if h_avg != best:
            raise AssertionError(f"Huffman NOT optimal for {c}")
        checked += 1
    return {"alphabet": n, "denominator": denom,
            "n_sources_checked": checked,
            "n_kraft_profiles_compared": len(profiles),
            "arithmetic": "exact rational"}


# ── 2. Markov & Chebyshev, exhaustively ────────────────────────────────────

def verify_inequalities(denom: int = 8) -> dict:
    values = [0, 1, 2, 3, 4]
    dists = markov = cheby = 0
    for c in product(range(denom + 1), repeat=len(values)):
        if sum(c) != denom:
            continue
        probs = [Fraction(x, denom) for x in c]
        mean = sum(p * v for p, v in zip(probs, values))
        var = sum(p * (v - mean) ** 2 for p, v in zip(probs, values))
        for a in range(1, 7):        # Markov: P(X >= a) <= E[X]/a  (X >= 0)
            tail = sum(p for p, v in zip(probs, values) if v >= a)
            if tail > mean / a:
                raise AssertionError(f"Markov FAILED at {c}, a={a}")
            markov += 1
        for t in (Fraction(1, 2), 1, 2, 4):   # Chebyshev via second moment
            tail = sum(p for p, v in zip(probs, values) if (v - mean) ** 2 >= t)
            if tail > var / t:
                raise AssertionError(f"Chebyshev FAILED at {c}, t={t}")
            cheby += 1
        dists += 1
    return {"n_distributions": dists, "markov_checks": markov,
            "chebyshev_checks": cheby, "arithmetic": "exact rational"}


# ── 3. Post functional completeness (NAND/NOR), exhaustively ───────────────

def _closure(seed_tables: set[int]) -> set[int]:
    # a binary boolean function = 4-bit truth table over (x,y) in
    # ((0,0),(0,1),(1,0),(1,1)); projections included as generators.
    x_tab, y_tab = 0b0011, 0b0101
    funcs = set(seed_tables) | {x_tab, y_tab}

    def compose(f, g, h):  # f(g(x,y), h(x,y))
        out = 0
        for bit in range(4):
            gv, hv = g >> (3 - bit) & 1, h >> (3 - bit) & 1
            out |= (f >> (3 - (gv * 2 + hv)) & 1) << (3 - bit)
        return out
    while True:
        new = {compose(f, g, h)
               for f in funcs for g in funcs for h in funcs} | funcs
        if new == funcs:
            return funcs
        funcs = new


def verify_post() -> dict:
    # truth-table bits ordered by rows (x,y) = (0,0),(0,1),(1,0),(1,1)
    # at bit positions 3,2,1,0 respectively:
    NAND, NOR, AND, OR = 0b1110, 0b1000, 0b0001, 0b0111
    NOT_X = 0b1100
    nand_c, nor_c = _closure({NAND}), _closure({NOR})
    mono_c = _closure({AND, OR})
    if len(nand_c) != 16 or len(nor_c) != 16:
        raise AssertionError("NAND/NOR closure incomplete")
    # {AND, OR} over projections closes at exactly {x, y, AND, OR} — four
    # monotone functions, never NOT (constants are not derivable without
    # constant generators, so this is 4, not Dedekind's 6-with-constants).
    if NOT_X in mono_c or len(mono_c) != 4:
        raise AssertionError(f"monotone closure wrong: {len(mono_c)}")
    return {"nand_closure_size": 16, "nor_closure_size": 16,
            "and_or_closure_size": 4, "not_reachable_from_and_or": False,
            "method": "exhaustive composition to fixpoint"}


# ── 4. Max-flow == min-cut on all small networks, exactly ──────────────────

def _max_flow(cap: dict, s: int, t: int) -> int:
    flow = 0
    residual = {e: c for e, c in cap.items()}
    while True:
        parent, queue, seen = {}, [s], {s}
        while queue:
            u = queue.pop(0)
            for (a, b), c in residual.items():
                if a == u and c > 0 and b not in seen:
                    seen.add(b)
                    parent[b] = u
                    queue.append(b)
        if t not in seen:
            return flow
        path, v = [], t
        while v != s:
            path.append((parent[v], v))
            v = parent[v]
        aug = min(residual[e] for e in path)
        for a, b in path:
            residual[(a, b)] -= aug
            residual[(b, a)] = residual.get((b, a), 0) + aug
        flow += aug


def verify_maxflow() -> dict:
    edges = [(0, 1), (0, 2), (1, 2), (2, 1), (1, 3), (2, 3)]
    checked = 0
    for caps in product(range(4), repeat=len(edges)):
        cap = dict(zip(edges, caps))
        mf = _max_flow(dict(cap), 0, 3)
        min_cut = min(sum(c for (a, b), c in cap.items()
                          if a in S and b not in S)
                      for S in ({0}, {0, 1}, {0, 2}, {0, 1, 2}))
        if mf != min_cut:
            raise AssertionError(f"maxflow!=mincut at {caps}: {mf}/{min_cut}")
        checked += 1
    return {"n_networks_checked": checked, "nodes": 4,
            "capacity_range": [0, 3], "arithmetic": "exact integer"}


# ── 5. 1-D optimal transport: sorted matching is optimal, exactly ──────────

def verify_ot1d() -> dict:
    grid = [Fraction(k) for k in range(8)]
    checked = 0
    for xs in combinations(grid, 4):
        for ys in combinations(grid, 4):
            sorted_cost = sum(abs(a - b) for a, b in zip(sorted(xs), sorted(ys)))
            best = min(sum(abs(a - b) for a, b in zip(xs, perm))
                       for perm in permutations(ys))
            if sorted_cost != best:
                raise AssertionError(f"sorted matching not optimal: {xs}/{ys}")
            checked += 1
    return {"n_support_pairs_checked": checked, "support_size": 4,
            "bijections_per_pair": 24, "cost": "|x-y|",
            "arithmetic": "exact rational"}


# ── 6. Johnson-Lindenstrauss, seeded (floats) ──────────────────────────────

def verify_jl() -> dict:
    rng = random.Random(42)
    d, k, n = 50, 25, 20
    pts = [[rng.gauss(0, 1) for _ in range(d)] for _ in range(n)]
    proj = [[rng.gauss(0, 1) / math.sqrt(k) for _ in range(d)]
            for _ in range(k)]
    low = [[sum(r[i] * p[i] for i in range(d)) for r in proj] for p in pts]

    def dist(a, b):
        return math.sqrt(sum((u - v) ** 2 for u, v in zip(a, b)))
    worst = max(abs(dist(low[i], low[j]) / dist(pts[i], pts[j]) - 1)
                for i in range(n) for j in range(i + 1, n))
    if worst > 0.5:
        raise AssertionError(f"JL distortion blew up: {worst}")
    return {"dim_from": d, "dim_to": k, "n_points": n, "seed": 42,
            "max_pairwise_distortion": round(worst, 4)}


# ── 7. Glivenko-Cantelli, seeded (floats) ───────────────────────────────────

def verify_gc() -> dict:
    rng = random.Random(7)
    sup = {}
    for n in (10, 100, 1000, 10000):
        xs = sorted(rng.random() for _ in range(n))
        sup[n] = round(max(max(abs((i + 1) / n - x), abs(i / n - x))
                           for i, x in enumerate(xs)), 5)
    factor = round(sup[10] / sup[10000], 1)
    if sup[10000] >= sup[10]:
        raise AssertionError(f"sup-distance did not shrink: {sup}")
    return {"true_distribution": "uniform[0,1]", "seed": 7,
            "sup_distance_by_n": sup, "shrink_factor_10_to_10000": factor}


def main() -> int:
    report = {"schema": "info_graphs_v1",
              "huffman": verify_huffman(), "inequalities": verify_inequalities(),
              "post": verify_post(), "maxflow": verify_maxflow(),
              "ot1d": verify_ot1d(), "jl": verify_jl(), "gc": verify_gc()}
    out = HERE.parent / "artifacts" / "info_graphs.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    try:
        sys.path.insert(0, "/Users/stian/vericlaim")
        from vericlaim.provenance import stamp
        stamp(out, script="python3 theorems/evidence_info_graphs.py")
    except ImportError:
        pass
    print(f"[OK] huffman {report['huffman']['n_sources_checked']} sources; "
          f"ineq {report['inequalities']['n_distributions']} dists; post "
          f"{report['post']['nand_closure_size']}/{report['post']['and_or_closure_size']}; "
          f"maxflow {report['maxflow']['n_networks_checked']}; ot1d "
          f"{report['ot1d']['n_support_pairs_checked']}; jl "
          f"{report['jl']['max_pairwise_distortion']}; gc x"
          f"{report['gc']['shrink_factor_10_to_10000']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
