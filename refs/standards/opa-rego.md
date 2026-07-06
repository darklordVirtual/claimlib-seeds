# Open Policy Agent (OPA) and the Rego policy language

**Canonical source:** Open Policy Agent, CNCF (`spec:open-policy-agent`);
policy language Rego. Graduated CNCF project.
**Role in the crosswalk:** the portable policy-as-code seam under authorization
policy.

## What it defines
OPA is a general-purpose policy engine that decides `allow/deny` (or richer
results) from structured input and a policy written in **Rego**, a declarative
query language. Policy is decoupled from the service: the service asks OPA "is
this allowed?" and OPA evaluates the same Rego regardless of the host platform.

## Why it is a coupling anchor
The identical Rego policy runs as a Kubernetes admission controller (Gatekeeper)
on EKS, AKS, GKE and OpenShift, as an API gateway/microservice sidecar, and in
CI. That is the definition of portable authorization: write the governance rule
once, enforce it the same way on every cloud. It is the natural home for
control-register checks expressed as code.

## Caveat
OPA decides; it does not identify — it consumes identity (OIDC claims, SPIFFE
IDs) from elsewhere. A policy is only as good as the input it is given and the
tests around it; unbounded or untested Rego can allow-by-omission. Bundle
signing and decision logging are needed for a tamper-evident audit trail.
