# OAuth 2.0 Authorization Framework — RFC 6749

**Canonical source:** IETF RFC 6749 (`rfc:6749`), October 2012.
**Role in the crosswalk:** the delegated-authorization substrate under human
authentication and workload federation on every cloud.

## What it defines
OAuth 2.0 lets a client obtain limited access to a resource on behalf of a
resource owner without handling the owner's credentials. It defines four grant
types (authorization code, implicit — now discouraged, resource owner password
— discouraged, client credentials), the roles (resource owner, client,
authorization server, resource server), and the bearer **access token** as the
credential presented to the resource server.

## Why it is a coupling anchor
Every major cloud IdP (AWS IAM Identity Center/Cognito, Microsoft Entra ID,
Google Cloud Identity, OpenShift OAuth server) issues and accepts OAuth 2.0
access tokens. Coupling the control plane on the authorization-code grant with
PKCE (RFC 7636) keeps the human-auth seam portable. The token itself is
typically a JWT (RFC 7519); scopes and audiences are the portable authorization
surface.

## Caveat
OAuth 2.0 is authorization, not authentication — identity is layered on top by
OpenID Connect. Bearer tokens must be transport-protected (TLS); sender-
constrained variants (mTLS RFC 8705, DPoP RFC 9449) reduce token theft.
