# SPDX-License-Identifier: Apache-2.0
"""Run the Lean 4 kernel over the seeded theorem battery; record the verdict.

The qualitative step past the bounded batteries: these theorems hold for ALL
propositions / types / naturals, and the checker is the Lean kernel — an
independently developed, widely audited proof assistant — not our own ~100
lines. Honesty artifacts captured per theorem:

- the kernel's accept/reject verdict (any error or sorryAx aborts, fail-closed);
- the AXIOM FOOTPRINT from `#print axioms` — `[]` means fully constructive,
  classical results carry propext / Classical.choice / Quot.sound;
- the exact Lean version.

    python3 theorems/evidence_lean.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAN = Path.home() / ".elan" / "bin" / "lean"

AXIOM_RE = re.compile(
    r"'ClaimLib\.([A-Za-z0-9_]+)' (?:does not depend on any axioms|"
    r"depends on axioms: \[([^\]]*)\])")

# The claim families partition the battery; recorded in the artifact so the
# per-claim counts are established by the evidence, not by the register.
CATEGORIES: dict[str, list[str]] = {
    "propositional": [
        "identity", "hyp_syllogism", "contraposition",
        "contraposition_converse", "double_negation", "excluded_middle",
        "peirce", "de_morgan_or", "de_morgan_and", "material_implication",
        "exportation", "and_distrib_or"],
    "quantifier": [
        "not_exists_iff_forall_not", "not_forall_iff_exists_not",
        "forall_and", "exists_or", "drinker"],
    "nat_induction": ["nat_add_comm", "nat_add_assoc", "sum_odds_eq_square"],
}


def main() -> int:
    if not LEAN.exists():
        print(f"[FAIL] lean not found at {LEAN} — install elan first")
        return 1
    version = subprocess.run([LEAN, "--version"], capture_output=True,
                             text=True, check=True).stdout.strip()
    proc = subprocess.run([LEAN, str(HERE / "lean" / "Theorems.lean")],
                          capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    if proc.returncode != 0 or "error" in out:
        print(f"[FAIL] Lean kernel rejected the battery:\n{out[:2000]}")
        return 1

    theorems: dict[str, dict] = {}
    for m in AXIOM_RE.finditer(out):
        name, axioms = m.group(1), m.group(2)
        ax_list = ([a.strip() for a in axioms.split(",")] if axioms else [])
        if "sorryAx" in ax_list:
            print(f"[FAIL] {name} contains sorry — refusing to write evidence")
            return 1
        theorems[name] = {"axioms": sorted(ax_list),
                          "constructive": not ax_list}
    if len(theorems) != 20:
        print(f"[FAIL] expected 20 axiom reports, parsed {len(theorems)}")
        return 1
    cat_names = [n for names in CATEGORIES.values() for n in names]
    if sorted(cat_names) != sorted(theorems):
        print("[FAIL] category lists do not partition the parsed theorems")
        return 1

    artifact = {
        "schema": "lean_theorems_v1",
        "checker": "Lean 4 kernel (core, no mathlib)",
        "lean_version": version,
        "source": "theorems/lean/Theorems.lean",
        "n_theorems": len(theorems),
        "n_constructive": sum(1 for t in theorems.values() if t["constructive"]),
        "categories": CATEGORIES,
        "n_propositional": len(CATEGORIES["propositional"]),
        "n_quantifier": len(CATEGORIES["quantifier"]),
        "n_nat_induction": len(CATEGORIES["nat_induction"]),
        "theorems": theorems,
    }
    out_path = HERE.parent / "artifacts" / "lean_theorems.json"
    out_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    try:
        sys.path.insert(0, "/Users/stian/vericlaim")
        from vericlaim.provenance import stamp
        stamp(out_path, script="python3 theorems/evidence_lean.py")
    except ImportError:
        pass
    print(f"[OK] {len(theorems)} theorems kernel-checked "
          f"({artifact['n_constructive']} constructive) — {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
