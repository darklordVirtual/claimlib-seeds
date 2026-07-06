# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-CTRL-001 / CLAIM-RISK-001 — the operative control
register verifies fail-closed. Runs the checker and records the summary; the
verified property is that every control is well-formed and mapped, and that all
ten control objectives are served by at least one approved control."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "governance"))

from control_register import check  # noqa: E402

ARTIFACT = ROOT / "artifacts" / "control_register.json"


def main() -> int:
    summary = check()  # raises fail-closed on any gap
    assert summary["objectives_covered"] == summary["control_objectives"] == 10
    assert summary["min_controls_per_objective"] >= 1
    ARTIFACT.parent.mkdir(exist_ok=True)
    ARTIFACT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    try:
        from vericlaim.provenance import stamp
        stamp(str(ARTIFACT.relative_to(ROOT)),
              script="python3 governance/evidence_control_register.py")
    except ImportError:
        pass
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
