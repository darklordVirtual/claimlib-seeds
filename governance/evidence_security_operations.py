# SPDX-License-Identifier: Apache-2.0
"""Evidence for the security-operations coverage crosswalk (CLAIM-SECOPS-001).

Runs the fail-closed checker over the committed crosswalk and records the
result. The verified property is operational coverage: every required security-
ops domain is present, each names practices/standards/objectives, and every
operational control objective has at least one domain that keeps it.
Deterministic measurement over a curated artifact — graded `measured`, NOT an
audit or certification of any specific pipeline.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "governance"))

from security_operations import check  # noqa: E402

ARTIFACT = ROOT / "artifacts" / "security_operations.json"


def main() -> int:
    summary = check()  # raises fail-closed on any gap
    assert summary["required_domains"] >= 6
    assert summary["operational_objectives_covered"] >= 6
    ARTIFACT.parent.mkdir(exist_ok=True)
    ARTIFACT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    try:
        from vericlaim.provenance import stamp
        stamp(str(ARTIFACT.relative_to(ROOT)),
              script="python3 governance/evidence_security_operations.py")
    except ImportError:
        pass
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
