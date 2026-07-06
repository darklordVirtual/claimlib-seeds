# SPDX-License-Identifier: Apache-2.0
"""Evidence for the cross-cloud identity/policy coupling crosswalk
(CLAIM-COUPLE-001).

Runs the fail-closed completeness checker over the committed crosswalk and
records the result. The verified property is portability completeness: every
cloud covers every coupling dimension, every cell names a concrete native
mechanism, and every dimension is anchored by at least one open standard shared
across >=2 clouds (so the seam is genuinely vendor-neutral). Deterministic
measurement over a curated artifact — graded `measured`, NOT a security review
or a certification that any deployment is correctly configured.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "governance"))

from identity_coupling import check  # noqa: E402

ARTIFACT = ROOT / "artifacts" / "identity_coupling.json"


def main() -> int:
    summary = check()  # raises fail-closed on any gap
    # Independent cross-checks of the headline invariants.
    assert summary["min_portable_standards_per_dimension"] >= 1
    assert summary["cells"] == summary["clouds"] * summary["coupling_dimensions"]
    ARTIFACT.parent.mkdir(exist_ok=True)
    ARTIFACT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    try:
        from vericlaim.provenance import stamp
        stamp(str(ARTIFACT.relative_to(ROOT)),
              script="python3 governance/evidence_identity_coupling.py")
    except ImportError:
        pass
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
