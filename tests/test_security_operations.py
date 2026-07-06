# SPDX-License-Identifier: Apache-2.0
"""The SecOps coverage checker's value is fail-closed behaviour: these prove it
raises when a required domain vanishes, a standard is unknown, or an operational
control objective loses its only home."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "security_operations",
    Path(__file__).resolve().parents[1] / "governance" / "security_operations.py")
so = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(so)


def test_committed_crosswalk_passes():
    s = so.check()
    assert s["required_domains"] == 6
    assert s["operational_objectives_covered"] >= 6
    assert s["domains"] >= 6


def test_missing_required_domain_is_flagged(monkeypatch):
    broken = copy.deepcopy(so.DOMAINS)
    del broken["logging_audit"]
    monkeypatch.setattr(so, "DOMAINS", broken)
    with pytest.raises(ValueError, match="required security-ops domains absent"):
        so.check()


def test_unknown_standard_is_flagged(monkeypatch):
    broken = copy.deepcopy(so.DOMAINS)
    broken["itsm"]["standards"] = ["NotAStandard"]
    monkeypatch.setattr(so, "DOMAINS", broken)
    with pytest.raises(ValueError, match="unknown standard"):
        so.check()


def test_objective_without_operational_home_is_flagged(monkeypatch):
    # Strip logging_traceability from every domain -> it has no home -> raise.
    broken = copy.deepcopy(so.DOMAINS)
    for d in broken.values():
        d["objectives"] = [o for o in d["objectives"]
                           if o != "logging_traceability"]
    monkeypatch.setattr(so, "DOMAINS", broken)
    with pytest.raises(ValueError, match="NO operational home"):
        so.check()
