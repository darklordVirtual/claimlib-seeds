# SPDX-License-Identifier: Apache-2.0
"""Assurance-case checker — makes a GSN-style case falsifiable.

An assurance case is only worth something if its evidence nodes point at real,
checkable things. This verifies, fail-closed, that a case:

  - is fully scoped (use_case, risk_tier, data_domain, model, and BOTH permitted
    and prohibited action types — a bounded claim, not a general one);
  - has a top_claim, strategy and residual_risk with a named acceptor;
  - resolves EVERY evidence.ref to a real control (controls.json), a real
    local claim (../claims/register.yaml), or a documented external claim
    (CLAIM-LIB-RAG-*, REMORA-CLAIM-*, DEMO-* — verified in the library, not this
    repo's register);
  - mitigates EVERY counterclaim with a control that resolves, or explicitly
    carries it as accepted residual risk.

It raises rather than passing a case with a dangling reference — the difference
between a theory of assurance and a case a reviewer can attack.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# Claims verified in the library but not in this repo's register (documented
# external namespace). Referencing them is allowed and marked external.
_EXTERNAL = (re.compile(r"^CLAIM-LIB-RAG-\d+$"),
             re.compile(r"^REMORA-CLAIM-\d+$"),
             re.compile(r"^DEMO-\d+$"))
_SCOPE_FIELDS = ("use_case", "risk_tier", "data_domain", "model",
                 "permitted_action_types", "prohibited_action_types")


def _control_ids() -> set[str]:
    data = json.loads((HERE / "controls.json").read_text())
    return {c["id"] for c in data["controls"]}


def _local_claim_ids() -> set[str]:
    reg = ROOT / "claims" / "register.yaml"
    if not reg.exists():
        return set()
    return set(re.findall(r"^\s*-\s*id:\s*(\S+)\s*$", reg.read_text(),
                          re.MULTILINE))


def _resolves(ref: str, kind: str, controls: set[str], claims: set[str]) -> bool:
    if kind == "control":
        return ref in controls
    if ref in claims:
        return True
    return any(p.match(ref) for p in _EXTERNAL)


def check(case_path: Path) -> dict:
    case = json.loads(case_path.read_text())
    controls, claims = _control_ids(), _local_claim_ids()

    for f in ("id", "top_claim", "scope", "strategy", "evidence",
              "assumptions", "counterclaims", "residual_risk"):
        if not case.get(f):
            raise ValueError(f"{case_path.name}: missing {f!r}")
    for f in _SCOPE_FIELDS:
        if not case["scope"].get(f):
            raise ValueError(f"{case_path.name}: scope missing {f!r}")
    if not case["residual_risk"].get("accepted_by"):
        raise ValueError(f"{case_path.name}: residual_risk has no accepted_by")

    dangling = []
    for e in case["evidence"]:
        if not _resolves(e["ref"], e.get("kind", "claim"), controls, claims):
            dangling.append(e["ref"])
    if dangling:
        raise ValueError(f"{case_path.name}: evidence refs do not resolve: "
                         f"{dangling}")

    for cc in case["counterclaims"]:
        mit = cc.get("mitigation")
        accepted = cc.get("residual") is True
        if mit and mit not in controls and mit not in claims \
                and not any(p.match(mit) for p in _EXTERNAL):
            raise ValueError(f"{case_path.name}: counterclaim mitigation "
                             f"{mit!r} does not resolve")
        if not mit and not accepted:
            raise ValueError(f"{case_path.name}: counterclaim {cc['claim']!r} "
                             f"has neither a mitigation nor accepted residual")

    return {
        "id": case["id"],
        "risk_tier": case["scope"]["risk_tier"],
        "evidence_nodes": len(case["evidence"]),
        "evidence_resolved": len(case["evidence"]),
        "counterclaims": len(case["counterclaims"]),
        "counterclaims_mitigated": sum(
            1 for cc in case["counterclaims"] if cc.get("mitigation")),
        "residual_accepted_by": case["residual_risk"]["accepted_by"],
    }
