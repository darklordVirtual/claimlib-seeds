# Cedar policy language

**Canonical source:** Cedar policy language (`spec:cedar-policy`), open-sourced
by AWS; the engine behind Amazon Verified Permissions.
**Role in the crosswalk:** a verifiable authorization policy language,
complementary to Rego, under authorization policy.

## What it defines
Cedar expresses authorization as `permit`/`forbid` policies over a
principal-action-resource-context model, with a schema and a formally specified
evaluation semantics. Cedar is designed for **analyzability**: its decision
procedure supports automated reasoning (the implementation has been subject to
verification), so policies can be checked for properties, not only executed.

## Why it is a coupling anchor
Cedar is open source and embeddable, so the same policy model works inside AWS
(Verified Permissions) and in a self-hosted service on any cloud. Its emphasis
on provable properties fits a claim-oriented control plane: an authorization
decision can be argued about, not just observed.

## Caveat
Cedar is younger and less ubiquitous than Rego/OPA in the Kubernetes admission
path; the two coexist (Cedar for application authorization, Rego for
infrastructure admission). Formal analyzability is a property of the engine and
schema, not a guarantee that a given policy set encodes the intended rule.
