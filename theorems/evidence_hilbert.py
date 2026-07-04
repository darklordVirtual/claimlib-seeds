# SPDX-License-Identifier: Apache-2.0
"""Verify the committed Hilbert derivations; write the evidence artifact.

The checker (theorems/proofcheck.py) is a byte-exact copy of the one behind
the library bundle for vericlaim CLAIM-THM-001 (also vendored with a binding
test under lib/claim_thm_001/ by use_code). Fail-closed: a derivation that
does not verify aborts the artifact.

    python3 theorems/evidence_hilbert.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from proofcheck import ProofError, check_file  # noqa: E402


def main() -> int:
    results = {}
    for proof in sorted((HERE / "proofs").glob("*.json")):
        try:
            report = check_file(proof)
        except ProofError as exc:
            print(f"[FAIL] {proof.name}: {exc}")
            return 1
        results[proof.stem] = {"proof": f"theorems/proofs/{proof.name}",
                               **report}
        print(f"[OK] {proof.stem}: qed in {report['steps_verified']} steps")
    out = HERE.parent / "artifacts" / "hilbert.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"schema": "hilbert_v1",
                               "system": "Lukasiewicz A1-A3 + modus ponens",
                               "derivations": results},
                              indent=2, sort_keys=True) + "\n")
    try:
        sys.path.insert(0, "/Users/stian/vericlaim")
        from vericlaim.provenance import stamp
        stamp(out, script="python3 theorems/evidence_hilbert.py")
    except ImportError:
        pass
    print(f"[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
