# SPDX-License-Identifier: Apache-2.0
"""Cross-cloud identity, authentication and policy coupling crosswalk — the
vendor-neutral seams a portable, governed AI system couples on, with a
FAIL-CLOSED completeness checker.

The problem it answers: an enterprise AI control plane must run the same
governance (who may authenticate, which workload may assume which identity,
what policy is enforced, what is audited) across more than one cloud. If every
cloud is wired with its proprietary primitives, the governance does not port —
it is re-implemented and drifts. The escape is to couple on the OPEN STANDARDS
that every major cloud already speaks, and treat each cloud's native service as
an ADAPTER to that standard.

This module encodes, for each COUPLING DIMENSION (workload federation, human
auth, authorization policy, secrets, audit/telemetry, service-to-service
identity), the native mechanism on each cloud (AWS, Azure, GCP, OpenShift) and
the open standard(s) that make it portable. The checker verifies the property
that matters for portability: every cloud covers every dimension, and every
dimension is anchored by at least one open standard shared across >=2 clouds
(so the seam is genuinely vendor-neutral, not a single-vendor convenience).

WHAT THIS IS NOT (read before relying on it): it is an architecture
traceability aid, not a security design review, not a certification, and not
evidence that any specific deployment is correctly configured. Native service
names reflect publicly documented mechanisms at authoring time; clouds rename
and add services. The checkable property is INTERNAL completeness and
cross-cloud standard-sharing — not that the mapping is exhaustive or that a
given control is implemented. The standards themselves are the authority
(preserved as hash-locked literature); this encodes their coupling structure.

Stdlib only. The checker raises rather than returning a partial map.
"""
from __future__ import annotations

# The open standards that serve as vendor-neutral coupling anchors. Each is a
# published specification; the vericlaim literature catalog holds a hash-locked
# note per standard (see refs/standards/). Key -> one-line purpose.
OPEN_STANDARDS: dict[str, str] = {
    "OIDC": "OpenID Connect Core 1.0 — federated identity via signed ID tokens.",
    "OAuth2": "RFC 6749 — delegated authorization with access tokens.",
    "OAuth2_token_exchange": "RFC 8693 — exchange one token for another (STS-style federation).",
    "SAML2": "OASIS SAML 2.0 — enterprise SSO via signed assertions.",
    "SCIM2": "RFC 7643 / 7644 — cross-domain identity provisioning.",
    "JWT": "RFC 7519 — signed, verifiable claims token.",
    "mTLS_X509": "RFC 8705 / X.509 — mutual-TLS client identity.",
    "SPIFFE": "SPIFFE/SPIRE — portable workload identity (SVID), CNCF.",
    "Rego_OPA": "Open Policy Agent / Rego — portable policy-as-code, CNCF.",
    "Cedar": "Cedar — open-sourced authorization policy language.",
    "CEL": "Common Expression Language — portable condition expressions.",
    "OpenTelemetry": "OpenTelemetry — vendor-neutral traces, metrics and logs, CNCF.",
    "CloudEvents": "CNCF CloudEvents — portable event envelope.",
}

# The coupling dimensions — the seams that must port across clouds.
COUPLING_DIMENSIONS: dict[str, str] = {
    "workload_identity_federation":
        "A workload proves identity and assumes a role WITHOUT a long-lived secret.",
    "human_authentication":
        "Human single sign-on and provisioning into the control plane.",
    "authorization_policy":
        "Policy-as-code deciding who/what may do what (externalized authorization).",
    "secrets_management":
        "Issuing and rotating secrets/keys, authenticated by workload identity.",
    "observability_audit":
        "Tamper-evident audit trail and telemetry export for accountability.",
    "service_identity_mtls":
        "Service-to-service authentication and encryption in transit.",
}

# CLOUDS[cloud][dimension] = {"native": <documented mechanism>, "standards": [...]}.
# Native names are publicly documented services; standards are the portable seam.
CLOUDS: dict[str, dict[str, dict]] = {
    "AWS": {
        "workload_identity_federation": {
            "native": "STS AssumeRoleWithWebIdentity, IAM Roles Anywhere (X.509), EKS Pod Identity / IRSA",
            "standards": ["OIDC", "OAuth2_token_exchange", "JWT", "mTLS_X509"]},
        "human_authentication": {
            "native": "IAM Identity Center (AWS SSO), Amazon Cognito",
            "standards": ["OIDC", "OAuth2", "SAML2", "SCIM2"]},
        "authorization_policy": {
            "native": "IAM policies + SCPs, Amazon Verified Permissions (Cedar), OPA Gatekeeper on EKS",
            "standards": ["Cedar", "Rego_OPA"]},
        "secrets_management": {
            "native": "Secrets Manager, Parameter Store (workload auth via IRSA/OIDC)",
            "standards": ["OIDC", "mTLS_X509"]},
        "observability_audit": {
            "native": "CloudTrail, CloudWatch, AWS Distro for OpenTelemetry",
            "standards": ["OpenTelemetry", "CloudEvents"]},
        "service_identity_mtls": {
            "native": "AWS Private CA, App Mesh, IAM Roles Anywhere",
            "standards": ["mTLS_X509", "SPIFFE"]},
    },
    "Azure": {
        "workload_identity_federation": {
            "native": "Entra Workload Identity Federation (federated credentials), Managed Identities",
            "standards": ["OIDC", "OAuth2_token_exchange", "JWT"]},
        "human_authentication": {
            "native": "Microsoft Entra ID (SSO), Entra provisioning",
            "standards": ["OIDC", "OAuth2", "SAML2", "SCIM2"]},
        "authorization_policy": {
            "native": "Azure Policy, Azure RBAC, OPA Gatekeeper on AKS",
            "standards": ["Rego_OPA", "CEL"]},
        "secrets_management": {
            "native": "Azure Key Vault (workload auth via Managed Identity / OIDC)",
            "standards": ["OIDC", "mTLS_X509"]},
        "observability_audit": {
            "native": "Azure Monitor, Activity Log, Azure Monitor OpenTelemetry exporter",
            "standards": ["OpenTelemetry", "CloudEvents"]},
        "service_identity_mtls": {
            "native": "Key Vault certificates, Istio/Open Service Mesh on AKS",
            "standards": ["mTLS_X509", "SPIFFE"]},
    },
    "GCP": {
        "workload_identity_federation": {
            "native": "Workload Identity Federation (STS token exchange), GKE Workload Identity",
            "standards": ["OIDC", "OAuth2_token_exchange", "JWT"]},
        "human_authentication": {
            "native": "Cloud Identity, Identity Platform",
            "standards": ["OIDC", "OAuth2", "SAML2", "SCIM2"]},
        "authorization_policy": {
            "native": "Cloud IAM Conditions (CEL), Organization Policy Service, OPA Gatekeeper on GKE",
            "standards": ["CEL", "Rego_OPA"]},
        "secrets_management": {
            "native": "Secret Manager (workload auth via Workload Identity / OIDC)",
            "standards": ["OIDC", "mTLS_X509"]},
        "observability_audit": {
            "native": "Cloud Audit Logs, Cloud Logging, OpenTelemetry (Google Cloud exporter)",
            "standards": ["OpenTelemetry", "CloudEvents"]},
        "service_identity_mtls": {
            "native": "Certificate Authority Service, Anthos Service Mesh / Istio",
            "standards": ["mTLS_X509", "SPIFFE"]},
    },
    "OpenShift": {
        "workload_identity_federation": {
            "native": "ServiceAccount projected tokens (OIDC issuer), external OIDC via token exchange",
            "standards": ["OIDC", "OAuth2_token_exchange", "JWT"]},
        "human_authentication": {
            "native": "OpenShift OAuth server with OIDC/LDAP/SAML identity providers",
            "standards": ["OIDC", "OAuth2", "SAML2"]},
        "authorization_policy": {
            "native": "Kubernetes RBAC, OPA Gatekeeper, Kyverno",
            "standards": ["Rego_OPA"]},
        "secrets_management": {
            "native": "Secrets + CSI Secrets Store driver, cert-manager (workload auth via SA token/OIDC)",
            "standards": ["OIDC", "mTLS_X509"]},
        "observability_audit": {
            "native": "Kubernetes audit log, OpenShift Logging, OpenTelemetry Operator",
            "standards": ["OpenTelemetry", "CloudEvents"]},
        "service_identity_mtls": {
            "native": "OpenShift Service Mesh (Istio) with SPIFFE SVIDs, cert-manager",
            "standards": ["mTLS_X509", "SPIFFE"]},
    },
}


def check() -> dict:
    """Fail-closed completeness verification. Raises ValueError on any missing
    cell, empty native mechanism, unknown standard, or dimension that is NOT
    anchored by at least one open standard shared across >=2 clouds (which
    would mean that seam is not genuinely vendor-neutral). Returns a summary."""
    dims = set(COUPLING_DIMENSIONS)
    standards = set(OPEN_STANDARDS)
    if not CLOUDS:
        raise ValueError("no clouds in the crosswalk")

    n_cells = 0
    n_std_edges = 0
    used_standards: set[str] = set()
    # For each dimension: which standards are used by which clouds.
    dim_std_clouds: dict[str, dict[str, set[str]]] = {d: {} for d in dims}

    for cloud, table in CLOUDS.items():
        missing = dims - set(table)
        if missing:
            raise ValueError(f"{cloud}: missing coupling dimensions {sorted(missing)}")
        for dim, cell in table.items():
            if dim not in dims:
                raise ValueError(f"{cloud}: unknown dimension {dim!r}")
            n_cells += 1
            if not cell.get("native", "").strip():
                raise ValueError(f"{cloud}.{dim}: empty native mechanism")
            stds = cell.get("standards") or []
            if not stds:
                raise ValueError(f"{cloud}.{dim}: no open-standard anchor")
            for s in stds:
                if s not in standards:
                    raise ValueError(f"{cloud}.{dim}: unknown standard {s!r}")
                used_standards.add(s)
                dim_std_clouds[dim].setdefault(s, set()).add(cloud)
                n_std_edges += 1

    # Every dimension must have >=1 standard shared by >=2 clouds (portable seam).
    unanchored = []
    portable_anchors: dict[str, list[str]] = {}
    for dim in sorted(dims):
        shared = sorted(s for s, cs in dim_std_clouds[dim].items() if len(cs) >= 2)
        if not shared:
            unanchored.append(dim)
        portable_anchors[dim] = shared
    if unanchored:
        raise ValueError(f"dimensions with NO cross-cloud portable standard "
                         f"(not vendor-neutral): {unanchored}")

    orphan_standards = sorted(standards - used_standards)
    if orphan_standards:
        raise ValueError(f"open standards defined but never used: {orphan_standards}")

    return {
        "clouds": len(CLOUDS),
        "coupling_dimensions": len(dims),
        "cells": n_cells,
        "open_standards": len(standards),
        "standard_edges": n_std_edges,
        "portable_anchors": portable_anchors,
        "min_portable_standards_per_dimension": min(
            len(v) for v in portable_anchors.values()),
    }


def standards_for(cloud: str, dimension: str) -> list[str]:
    """The open standards a given cloud's mechanism couples on for a dimension."""
    return list(CLOUDS[cloud][dimension]["standards"])


def clouds_speaking(standard: str) -> list[str]:
    """Which clouds have at least one mechanism that speaks a given standard."""
    if standard not in OPEN_STANDARDS:
        raise KeyError(standard)
    return sorted({c for c, table in CLOUDS.items()
                   for cell in table.values()
                   if standard in (cell.get("standards") or [])})
