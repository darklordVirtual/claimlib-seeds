# SPDX-License-Identifier: Apache-2.0
"""A governance crosswalk — public framework structures mapped to a shared
set of control objectives, with a FAIL-CLOSED coverage checker.

This is a reusable building block for frontier AI governance: a project can
vendor it (library use_code), read which control objectives each framework
demands, and check its own control set against the crosswalk. It maps only
the STABLE, PUBLIC top-level structure of each framework — the level that is
factual and verifiable — to ten control objectives every high-standard AI
governance program must address.

WHAT THIS IS NOT (read before relying on it): it is a traceability aid, not
legal advice, not a compliance certification, and not evidence that any
specific control is correctly implemented. Article/clause specifics beyond
the well-known top-level structure are out of scope. The frameworks
themselves are preserved hash-locked in the vericlaim literature catalog
(NIST AI RMF, EU AI Act, ISO/IEC 42001, NIST CSF 2.0, NIST Privacy
Framework); this module encodes their public structure, not their text.

Stdlib only. The checker is the point: it verifies BIDIRECTIONAL coverage
(no orphan element, no uncovered objective) and referential integrity, and
raises rather than returning a partial map.
"""
from __future__ import annotations

# The shared control objectives — the themes a high-standard AI governance
# program must cover, independent of which framework it reports against.
CONTROL_OBJECTIVES: dict[str, str] = {
    "governance_accountability": "Defined roles, responsibility and oversight structures.",
    "risk_management": "Identify, assess and treat AI-specific risks.",
    "data_governance": "Data quality, provenance and bias in training/operation.",
    "transparency_documentation": "System/model documentation and disclosure.",
    "human_oversight": "Meaningful human control and intervention.",
    "robustness_accuracy": "Performance, robustness and security of the AI.",
    "logging_traceability": "Records, audit trail and event logging.",
    "monitoring_postmarket": "Ongoing monitoring, drift detection, incident response.",
    "fairness_nondiscrimination": "Bias assessment and equitable outcomes.",
    "privacy_dataprotection": "Personal-data protection and minimization.",
}

# Each framework: {element_name: [control_objective, ...]}. Elements are the
# public top-level structure of each framework.
FRAMEWORKS: dict[str, dict[str, list[str]]] = {
    "NIST_AI_RMF_1.0": {
        "GOVERN": ["governance_accountability", "risk_management"],
        "MAP": ["risk_management", "data_governance", "transparency_documentation"],
        "MEASURE": ["robustness_accuracy", "fairness_nondiscrimination",
                    "monitoring_postmarket"],
        "MANAGE": ["monitoring_postmarket", "human_oversight", "risk_management"],
    },
    "NIST_CSF_2.0": {
        "GOVERN": ["governance_accountability"],
        "IDENTIFY": ["risk_management", "data_governance"],
        "PROTECT": ["robustness_accuracy", "privacy_dataprotection"],
        "DETECT": ["monitoring_postmarket", "logging_traceability"],
        "RESPOND": ["monitoring_postmarket"],
        "RECOVER": ["monitoring_postmarket"],
    },
    "EU_AI_Act_high_risk": {  # Art. 9-15 requirement themes
        "risk_management_system": ["risk_management"],
        "data_and_data_governance": ["data_governance", "fairness_nondiscrimination"],
        "technical_documentation": ["transparency_documentation"],
        "record_keeping": ["logging_traceability"],
        "transparency": ["transparency_documentation"],
        "human_oversight": ["human_oversight"],
        "accuracy_robustness_cybersecurity": ["robustness_accuracy"],
    },
    "ISO_IEC_42001": {  # management-system clauses 4-10
        "context": ["governance_accountability"],
        "leadership": ["governance_accountability"],
        "planning": ["risk_management"],
        "support": ["governance_accountability"],
        "operation": ["robustness_accuracy", "human_oversight"],
        "performance_evaluation": ["monitoring_postmarket"],
        "improvement": ["monitoring_postmarket"],
    },
    "NIST_Privacy_Framework": {
        "IDENTIFY_P": ["data_governance", "privacy_dataprotection"],
        "GOVERN_P": ["governance_accountability"],
        "CONTROL_P": ["privacy_dataprotection"],
        "COMMUNICATE_P": ["transparency_documentation"],
        "PROTECT_P": ["privacy_dataprotection"],
    },
}


def check() -> dict:
    """Fail-closed coverage verification. Raises ValueError on any orphan
    element, uncovered objective, or dangling reference; otherwise returns a
    coverage summary."""
    objectives = set(CONTROL_OBJECTIVES)
    covered: dict[str, list[str]] = {o: [] for o in objectives}
    n_elements = 0
    n_edges = 0
    for fw, elements in FRAMEWORKS.items():
        if not elements:
            raise ValueError(f"{fw}: framework has no elements")
        for element, objs in elements.items():
            n_elements += 1
            if not objs:
                raise ValueError(f"{fw}.{element}: orphan element maps to no "
                                 f"control objective")
            for o in objs:
                if o not in objectives:
                    raise ValueError(f"{fw}.{element}: unknown objective {o!r}")
                covered[o].append(f"{fw}.{element}")
                n_edges += 1
    uncovered = sorted(o for o in objectives if not covered[o])
    if uncovered:
        raise ValueError(f"control objectives with NO framework coverage: "
                         f"{uncovered}")
    return {
        "frameworks": len(FRAMEWORKS),
        "control_objectives": len(objectives),
        "framework_elements": n_elements,
        "mapping_edges": n_edges,
        "coverage": {o: sorted(covered[o]) for o in sorted(objectives)},
        "min_frameworks_per_objective": min(
            len({e.split(".")[0] for e in covered[o]}) for o in objectives),
    }


def objectives_for(framework: str, element: str) -> list[str]:
    """The control objectives a given framework element addresses."""
    return list(FRAMEWORKS[framework][element])


def frameworks_covering(objective: str) -> list[str]:
    """Which frameworks demand a given control objective (for a project that
    must satisfy several regimes at once)."""
    if objective not in CONTROL_OBJECTIVES:
        raise KeyError(objective)
    return sorted({fw for fw, els in FRAMEWORKS.items()
                   for objs in els.values() if objective in objs})
