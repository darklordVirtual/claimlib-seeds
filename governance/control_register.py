# SPDX-License-Identifier: Apache-2.0
"""The operative control register — fail-closed checker.

A control objective (framework_map.py) is a theme; a CONTROL is the runnable
thing: owned, tested, mapped, with evidence and an exception path. This module
loads controls.json + risk_tiers.json and verifies, fail-closed, that:

  - every control carries all required fields (owner.accountable, a test with a
    pass_condition, evidence_required, an exception path, residual_risk);
  - every control_objective it names EXISTS in the CLAIM-GOV-001 crosswalk;
  - every framework_mapping element EXISTS in framework_map.FRAMEWORKS
    (a control cannot cite an article the crosswalk does not know);
  - every applicability.risk_tier EXISTS in risk_tiers.json;
  - BIDIRECTIONAL coverage: every one of the ten control objectives is served
    by at least one APPROVED control (no objective is described-but-uncontrolled).

It raises rather than returning a partial register — the same discipline as the
crosswalk. This is what lets controls be used in a review, tested in CI, owned
by someone, and measured over time.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
from framework_map import CONTROL_OBJECTIVES, FRAMEWORKS  # noqa: E402

_REQUIRED = ("id", "name", "status", "risk_statement", "applicability",
             "control_objectives", "framework_mapping", "owner",
             "evidence_required", "test", "exception", "residual_risk")
_STATUS = {"approved", "proposed", "deprecated"}


def load_controls() -> list[dict]:
    return json.loads((HERE / "controls.json").read_text())["controls"]


def load_tiers() -> dict:
    return json.loads((HERE / "risk_tiers.json").read_text())


def check() -> dict:
    controls = load_controls()
    tiers = load_tiers()
    tier_ids = {t["id"] for t in tiers["tiers"]}
    objectives = set(CONTROL_OBJECTIVES)
    served: dict[str, list[str]] = {o: [] for o in objectives}
    seen_ids: set[str] = set()

    for c in controls:
        cid = c.get("id", "?")
        for f in _REQUIRED:
            if f not in c or c[f] in (None, "", [], {}):
                raise ValueError(f"{cid}: missing required field {f!r}")
        if cid in seen_ids:
            raise ValueError(f"duplicate control id {cid}")
        seen_ids.add(cid)
        if c["status"] not in _STATUS:
            raise ValueError(f"{cid}: bad status {c['status']!r}")
        if not c["owner"].get("accountable"):
            raise ValueError(f"{cid}: no accountable owner")
        if not c["test"].get("pass_condition"):
            raise ValueError(f"{cid}: test has no pass_condition")
        if not c["exception"].get("approval_required_from"):
            raise ValueError(f"{cid}: exception has no approver")
        for o in c["control_objectives"]:
            if o not in objectives:
                raise ValueError(f"{cid}: unknown control objective {o!r}")
            if c["status"] == "approved":
                served[o].append(cid)
        for fw, elems in c["framework_mapping"].items():
            if fw not in FRAMEWORKS:
                raise ValueError(f"{cid}: unknown framework {fw!r}")
            for e in elems:
                if e not in FRAMEWORKS[fw]:
                    raise ValueError(
                        f"{cid}: {fw} has no element {e!r} in the crosswalk")
        for t in c["applicability"]["risk_tiers"]:
            if t not in tier_ids:
                raise ValueError(f"{cid}: unknown risk tier {t!r}")

    uncovered = sorted(o for o in objectives if not served[o])
    if uncovered:
        raise ValueError(f"control objectives with NO approved control: "
                         f"{uncovered}")

    return {
        "controls_total": len(controls),
        "controls_approved": sum(1 for c in controls if c["status"] == "approved"),
        "control_objectives": len(objectives),
        "objectives_covered": len(objectives) - len(uncovered),
        "risk_tiers": len(tier_ids),
        "min_controls_per_objective": min(len(served[o]) for o in objectives),
        "coverage": {o: sorted(served[o]) for o in sorted(objectives)},
    }


def controls_for_tier(tier: str) -> list[str]:
    """Which controls a system at the given risk tier must satisfy."""
    return [c["id"] for c in load_controls()
            if tier in c["applicability"]["risk_tiers"]]
