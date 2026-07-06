# SPDX-License-Identifier: Apache-2.0
"""Security-operations coverage crosswalk — the operational domains a governed
AI system must run (service management, observability, logging, PII handling,
vulnerability management, detection & response, secrets, resilience), each
mapped to concrete practices, the public standards that define them, and the
shared control objectives they serve, with a FAIL-CLOSED coverage checker.

Governance (§15's control objectives) is a promise; security operations is how
that promise is *kept day to day*. A control objective like "logging &
traceability" or "privacy & data protection" is only real if there is an
operational domain that runs it — a log-management practice against NIST SP
800-92, a PII-scrubbing pipeline against ISO/IEC 27701. This module encodes that
link so a governance program can check it has an operational home for every
objective it claims.

WHAT THIS IS NOT: a traceability aid over the PUBLIC structure of well-known
operations standards — not an audit, not a certification, and not evidence that
any specific pipeline is correctly run. Standard clause specifics are out of
scope; the standards themselves are the authority (preserved hash-locked in the
literature catalog). The checkable property is INTERNAL coverage: every domain
has a practice, a standard and an objective, a required baseline of domains is
present, and every objective a domain claims exists in the shared set.

Stdlib only. The checker raises rather than returning a partial map.
"""
from __future__ import annotations

# The shared control objectives this crosswalk maps onto — identical to the
# governance crosswalk's set (framework_map.CONTROL_OBJECTIVES) so a program can
# join the two: which regime demands an objective, and which operational domain
# runs it.
CONTROL_OBJECTIVES = {
    "governance_accountability", "risk_management", "data_governance",
    "transparency_documentation", "human_oversight", "robustness_accuracy",
    "logging_traceability", "monitoring_postmarket",
    "fairness_nondiscrimination", "privacy_dataprotection",
}

# The operational domains that MUST be present for the crosswalk to be trusted
# as covering security operations for a governed AI system.
REQUIRED_DOMAINS = {
    "itsm", "observability", "logging_audit", "pii_data_protection",
    "vulnerability_management", "detection_response",
}

# The standards catalog — each a published specification, preserved hash-locked
# as literature. Key -> one-line purpose.
STANDARDS = {
    "ISO_IEC_27001": "Information security management system (ISMS) requirements.",
    "ISO_IEC_20000_1": "IT service management (ITSM) system requirements.",
    "ITIL_4": "IT service management practices (incident/change/problem).",
    "ISO_IEC_27701": "Privacy information management extension to 27001 (PIMS).",
    "NIST_SP_800_53": "Security and privacy controls catalog.",
    "NIST_SP_800_61": "Computer security incident handling guide.",
    "NIST_SP_800_92": "Guide to computer security log management.",
    "NIST_SP_800_137": "Information security continuous monitoring (ISCM).",
    "CIS_Controls_v8": "Prioritized safeguards for cyber defense.",
    "OWASP_ASVS": "Application security verification standard.",
    "MITRE_ATTACK": "Adversary tactics and techniques knowledge base.",
    "OpenTelemetry": "Vendor-neutral traces, metrics and logs.",
    "GDPR": "EU data-protection regulation (lawful processing, minimization).",
}

# DOMAINS[domain] = {practices: [...], standards: [...], objectives: [...]}.
DOMAINS: dict[str, dict[str, list[str]]] = {
    "itsm": {
        "practices": ["incident management", "change enablement",
                      "problem management", "service level management"],
        "standards": ["ISO_IEC_20000_1", "ITIL_4", "NIST_SP_800_61"],
        "objectives": ["governance_accountability", "monitoring_postmarket",
                       "risk_management"],
    },
    "observability": {
        "practices": ["metrics", "distributed tracing", "SLOs and error budgets",
                      "drift and anomaly detection"],
        "standards": ["OpenTelemetry", "NIST_SP_800_137"],
        "objectives": ["monitoring_postmarket", "robustness_accuracy"],
    },
    "logging_audit": {
        "practices": ["centralized log management", "tamper-evident audit trail",
                      "retention and time-sync", "log integrity"],
        "standards": ["NIST_SP_800_92", "ISO_IEC_27001", "OpenTelemetry"],
        "objectives": ["logging_traceability", "governance_accountability"],
    },
    "pii_data_protection": {
        "practices": ["PII discovery and classification", "redaction/scrubbing",
                      "minimization and retention", "DSAR handling",
                      "pseudonymization"],
        "standards": ["ISO_IEC_27701", "GDPR", "NIST_SP_800_53"],
        "objectives": ["privacy_dataprotection", "data_governance"],
    },
    "vulnerability_management": {
        "practices": ["dependency and image scanning", "patch SLAs",
                      "SBOM and provenance", "penetration testing"],
        "standards": ["CIS_Controls_v8", "OWASP_ASVS", "NIST_SP_800_53"],
        "objectives": ["robustness_accuracy", "risk_management"],
    },
    "detection_response": {
        "practices": ["SIEM detections", "SOAR playbooks",
                      "threat-informed detection", "incident response drills"],
        "standards": ["MITRE_ATTACK", "NIST_SP_800_61", "CIS_Controls_v8"],
        "objectives": ["monitoring_postmarket", "human_oversight",
                       "risk_management"],
    },
    "secrets_key_management": {
        "practices": ["secret rotation", "hardware-backed keys",
                      "short-lived credentials", "no static keys in code"],
        "standards": ["NIST_SP_800_53", "CIS_Controls_v8"],
        "objectives": ["robustness_accuracy", "governance_accountability"],
    },
    "resilience_backup_dr": {
        "practices": ["immutable backups", "restore testing",
                      "RTO/RPO objectives", "disaster-recovery runbooks"],
        "standards": ["ISO_IEC_27001", "NIST_SP_800_53"],
        "objectives": ["robustness_accuracy", "risk_management"],
    },
}


def check() -> dict:
    """Fail-closed coverage verification. Raises ValueError on any domain with no
    practice/standard/objective, an unknown standard or objective, a missing
    required domain, or a control objective with no operational home among the
    required domains. Returns a coverage summary."""
    missing_req = REQUIRED_DOMAINS - set(DOMAINS)
    if missing_req:
        raise ValueError(f"required security-ops domains absent: "
                         f"{sorted(missing_req)}")

    n_practice = 0
    used_standards: set[str] = set()
    obj_home: dict[str, set[str]] = {o: set() for o in CONTROL_OBJECTIVES}
    for domain, d in DOMAINS.items():
        for field in ("practices", "standards", "objectives"):
            if not d.get(field):
                raise ValueError(f"{domain}: empty {field}")
        n_practice += len(d["practices"])
        for s in d["standards"]:
            if s not in STANDARDS:
                raise ValueError(f"{domain}: unknown standard {s!r}")
            used_standards.add(s)
        for o in d["objectives"]:
            if o not in CONTROL_OBJECTIVES:
                raise ValueError(f"{domain}: unknown objective {o!r}")
            obj_home[o].add(domain)

    # Every objective that security operations is responsible for must have an
    # operational home. Four objectives are governance/disclosure themes owned
    # elsewhere (the control register), not operational domains — list them so
    # the exclusion is explicit, not silent.
    non_operational = {"transparency_documentation", "human_oversight",
                       "fairness_nondiscrimination", "governance_accountability"}
    uncovered = sorted(o for o in CONTROL_OBJECTIVES
                       if o not in non_operational and not obj_home[o])
    if uncovered:
        raise ValueError(f"control objectives with NO operational home: {uncovered}")

    orphan = sorted(set(STANDARDS) - used_standards)
    if orphan:
        raise ValueError(f"standards defined but never used: {orphan}")

    return {
        "domains": len(DOMAINS),
        "required_domains": len(REQUIRED_DOMAINS),
        "practices": n_practice,
        "standards": len(STANDARDS),
        "control_objectives_with_operational_home": sorted(
            o for o in CONTROL_OBJECTIVES if obj_home[o]),
        "operational_objectives_covered": len(
            [o for o in CONTROL_OBJECTIVES if obj_home[o]]),
        "domain_objectives": {d: sorted(v["objectives"])
                              for d, v in sorted(DOMAINS.items())},
    }


def standards_for(domain: str) -> list[str]:
    """The standards a security-operations domain is run against."""
    return list(DOMAINS[domain]["standards"])


def domains_for_objective(objective: str) -> list[str]:
    """Which operational domains keep a given control objective."""
    if objective not in CONTROL_OBJECTIVES:
        raise KeyError(objective)
    return sorted(d for d, v in DOMAINS.items()
                  if objective in v["objectives"])
