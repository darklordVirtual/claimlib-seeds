# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-ASSURE-001 — the EA Copilot assurance case is
structurally complete and every evidence/mitigation reference resolves to a
real control or claim. Runs the checker and records the summary."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "governance"))

from assurance_check import check  # noqa: E402

CASE = ROOT / "governance" / "assurance" / "ea_copilot.json"
ARTIFACT = ROOT / "artifacts" / "assurance_ea_copilot.json"


def main() -> int:
    summary = check(CASE)  # raises fail-closed on any dangling reference
    assert summary["evidence_resolved"] == summary["evidence_nodes"]
    ARTIFACT.parent.mkdir(exist_ok=True)
    ARTIFACT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    try:
        from vericlaim.provenance import stamp
        stamp(str(ARTIFACT.relative_to(ROOT)),
              script="python3 governance/evidence_assurance.py")
    except ImportError:
        pass
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
