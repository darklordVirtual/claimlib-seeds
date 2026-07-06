# OAuth 2.0 Token Exchange — RFC 8693

**Canonical source:** IETF RFC 8693 (`rfc:8693`), January 2020.
**Role in the crosswalk:** the mechanism under workload identity federation —
turning one trusted token into a cloud-scoped credential.

## What it defines
A Security Token Service (STS) grant type (`grant_type=urn:ietf:params:oauth:
grant-type:token-exchange`) that exchanges a `subject_token` (e.g. an OIDC ID
token from a cluster or CI issuer) for a new token scoped to a target
`resource`/`audience`. It defines `actor_token` for delegation and impersonation
semantics and standard token-type URIs.

## Why it is a coupling anchor
GCP Workload Identity Federation is an STS token exchange; AWS
`AssumeRoleWithWebIdentity` and Azure federated credentials implement the same
shape. A governed control plane authenticates once (OIDC), then exchanges that
proof for narrowly-scoped, short-lived credentials on each cloud — the portable
alternative to distributing static access keys.

## Caveat
The security of the exchange is only as good as the trust configuration on the
target: audience restriction, subject/claim conditions, and short token TTLs.
Impersonation/delegation must be constrained or an exchanged token can widen
scope.
