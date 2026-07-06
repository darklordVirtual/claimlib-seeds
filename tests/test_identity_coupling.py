# SPDX-License-Identifier: Apache-2.0
"""The cross-cloud coupling checker's value IS its fail-closed behaviour, so
these tests prove it raises on the ways a crosswalk can silently rot: a missing
cell, an unknown standard, and a dimension that lost its cross-cloud anchor."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "identity_coupling",
    Path(__file__).resolve().parents[1] / "governance" / "identity_coupling.py")
ic = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ic)


def test_committed_crosswalk_passes():
    s = ic.check()
    assert s["cells"] == s["clouds"] * s["coupling_dimensions"]
    assert s["min_portable_standards_per_dimension"] >= 1
    assert s["clouds"] >= 4 and s["coupling_dimensions"] >= 6


def test_missing_cell_is_flagged(monkeypatch):
    broken = copy.deepcopy(ic.CLOUDS)
    dim = next(iter(ic.COUPLING_DIMENSIONS))
    del broken["AWS"][dim]
    monkeypatch.setattr(ic, "CLOUDS", broken)
    with pytest.raises(ValueError, match="missing coupling dimensions"):
        ic.check()


def test_unknown_standard_is_flagged(monkeypatch):
    broken = copy.deepcopy(ic.CLOUDS)
    dim = next(iter(ic.COUPLING_DIMENSIONS))
    broken["AWS"][dim]["standards"] = ["NotAStandard"]
    monkeypatch.setattr(ic, "CLOUDS", broken)
    with pytest.raises(ValueError, match="unknown standard"):
        ic.check()


def test_dimension_without_cross_cloud_anchor_is_flagged(monkeypatch):
    # Give one dimension a unique, single-cloud standard everywhere so no
    # standard is shared across >=2 clouds -> not vendor-neutral -> must raise.
    broken = copy.deepcopy(ic.CLOUDS)
    stds = copy.deepcopy(ic.OPEN_STANDARDS)
    dim = "authorization_policy"
    for i, cloud in enumerate(broken):
        key = f"SoloStd{i}"
        stds[key] = "single-cloud only"
        broken[cloud][dim]["standards"] = [key]
    monkeypatch.setattr(ic, "CLOUDS", broken)
    monkeypatch.setattr(ic, "OPEN_STANDARDS", stds)
    with pytest.raises(ValueError, match="NO cross-cloud portable standard"):
        ic.check()
