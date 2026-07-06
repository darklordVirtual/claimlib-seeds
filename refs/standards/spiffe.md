# SPIFFE — Secure Production Identity Framework For Everyone

**Canonical source:** SPIFFE specification, CNCF (`spec:spiffe`); reference
implementation SPIRE. Graduated CNCF project.
**Role in the crosswalk:** portable service-to-service workload identity.

## What it defines
A SPIFFE ID is a URI (`spiffe://trust-domain/workload/path`) naming a workload
independent of where it runs. It is delivered as a **SVID** (SPIFFE Verifiable
Identity Document) in one of two forms: an X.509-SVID (a short-lived
certificate) or a JWT-SVID. The SPIFFE Workload API lets a workload fetch and
rotate its own SVID with no baked-in secret.

## Why it is a coupling anchor
SPIFFE gives one workload-identity model that spans clouds and clusters: Istio /
Anthos Service Mesh / OpenShift Service Mesh all issue SPIFFE SVIDs, so mTLS
between services uses the same identity semantics on AWS, Azure, GCP and
OpenShift. It is the vendor-neutral answer to "which service is calling me."

## Caveat
SPIFFE identifies workloads; it does not by itself decide authorization — pair
it with policy-as-code (OPA/Rego) that reads the SPIFFE ID. Trust-domain
federation must be configured deliberately; a flat trust domain over-trusts.
