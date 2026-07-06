# OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Tokens — RFC 8705

**Canonical source:** IETF RFC 8705 (`rfc:8705`), February 2020.
**Role in the crosswalk:** sender-constrained tokens and X.509 client identity
under secrets management and service-to-service mTLS.

## What it defines
Two related mechanisms: (1) mutual-TLS client authentication, where the client
authenticates to the authorization server with an X.509 certificate; and (2)
**certificate-bound access tokens**, where the issued token is bound to the
client's certificate thumbprint (`cnf`/`x5t#S256`), so a stolen bearer token is
useless without the matching private key.

## Why it is a coupling anchor
X.509/mTLS is the lowest-common-denominator workload identity: AWS IAM Roles
Anywhere, cert-manager on OpenShift/Kubernetes, and every service mesh
(Istio/Linkerd) issue and rotate X.509 identities. Certificate-bound tokens
close the bearer-token theft gap that pure OAuth leaves open, giving a portable
proof-of-possession seam.

## Caveat
mTLS shifts the problem to certificate lifecycle: issuance, rotation, and
revocation must be automated (short-lived certs, an online CA) or it becomes an
operational liability. SPIFFE/SPIRE standardizes this for workloads.
