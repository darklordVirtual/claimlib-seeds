# SPDX-License-Identifier: Apache-2.0
"""Verify the seeded theorem battery and write the evidence artifact.

Fail-closed: if ANY seeded formula is not a tautology, no artifact is
written — a partially-true battery must never look like evidence.

    python3 theorems/evidence_tautologies.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from battery import THEOREMS  # noqa: E402
from tautcheck import check_tautology  # noqa: E402


def main() -> int:
    results = {}
    for cid, name, formula in THEOREMS:
        report = check_tautology(formula)
        if not report["tautology"]:
            print(f"[FAIL] {cid} ({name}) is NOT a tautology: "
                  f"countermodel {report['countermodel']} — refusing to "
                  f"write evidence")
            return 1
        results[cid] = {"name": name, "formula": formula,
                        "n_atoms": report["n_atoms"],
                        "n_assignments_checked": report["n_assignments_checked"],
                        "tautology": True}
    out = HERE.parent / "artifacts" / "tautologies.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"schema": "tautologies_v1",
                               "method": "exhaustive truth-table decision procedure",
                               "theorems": results},
                              indent=2, sort_keys=True) + "\n")
    try:
        sys.path.insert(0, "/Users/stian/vericlaim")
        from vericlaim.provenance import stamp
        stamp(out, script="python3 theorems/evidence_tautologies.py")
    except ImportError:
        pass  # provenance is best-effort here; the gate does not require it
    print(f"[OK] {len(results)} theorems machine-verified -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
