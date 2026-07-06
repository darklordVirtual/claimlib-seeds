# OpenID Connect Core 1.0

**Canonical source:** OpenID Foundation, OpenID Connect Core 1.0
(`spec:openid-connect-core-1.0`), incorporating errata set 2.
**Role in the crosswalk:** the identity layer for both human authentication and
workload identity federation.

## What it defines
OIDC is an identity layer on top of OAuth 2.0. It adds the **ID token** (a JWT
asserting who authenticated, with `iss`, `sub`, `aud`, `exp`, `iat`, `nonce`),
the `/userinfo` endpoint, and a discovery document
(`/.well-known/openid-configuration`) that publishes the issuer's endpoints and
JWKS signing keys. A relying party verifies the ID token's signature against the
issuer's published JWKS and checks issuer/audience/expiry.

## Why it is a coupling anchor
The discovery + JWKS pattern is exactly how workload identity federation works
across clouds: a Kubernetes/OpenShift cluster or CI system publishes an OIDC
issuer, and AWS (`AssumeRoleWithWebIdentity`), Azure (federated credentials),
and GCP (Workload Identity Federation) each trust that issuer and exchange its
tokens for cloud credentials — no long-lived secret. One issuer, three clouds,
same standard.

## Caveat
Trust rests on issuer discovery and key rotation being correct; a mis-scoped
`aud` or an over-broad trust policy federates more than intended. OIDC proves
*who authenticated*, not *what they may do* — authorization is separate.
