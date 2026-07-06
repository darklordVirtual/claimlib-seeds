# NIST SP 800-207 — Zero Trust Architecture

**Canonical source:** NIST Special Publication 800-207
(`doi:10.6028/NIST.SP.800-207`), August 2020.
**Role in the crosswalk:** the architectural rationale for why the coupling
seams (per-request identity, explicit policy, no implicit trust) are the right
ones.

## What it defines
Zero Trust treats no network location as trusted. Access to each resource is
granted per-request by a **Policy Decision Point (PDP)** and enforced by a
**Policy Enforcement Point (PEP)**, based on authenticated identity, device
state, and policy — continuously, not once at a perimeter. It names the logical
components (policy engine, policy administrator) and the data sources feeding
decisions.

## Why it is a coupling anchor
The PDP/PEP split maps directly onto the crosswalk: identity comes from
OIDC/SPIFFE, the PDP is policy-as-code (OPA/Cedar), the PEP is the mesh/gateway/
admission controller, and telemetry feeds continuous evaluation. It is the
reference model the multi-cloud control plane implements, and the vocabulary
regulators and enterprises expect.

## Caveat
SP 800-207 is an architecture document, not a product or a checklist; it
describes *what* must hold (explicit, per-request, least-privilege access), not
a specific implementation. Adopting the vocabulary does not by itself make a
system zero-trust.
