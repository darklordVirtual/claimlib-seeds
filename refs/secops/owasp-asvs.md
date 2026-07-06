# OWASP Application Security Verification Standard (ASVS)

**Canonical source:** OWASP ASVS (`spec:owasp-asvs`).
**Role:** application-security verification under vulnerability management.

## What it defines
A catalog of application-security requirements and verification criteria across
levels (L1–L3), covering authentication, session management, access control,
input validation, cryptography, error handling and logging, and more. It is
written as testable requirements so security can be *verified*, not asserted.

## Role in the crosswalk
For an AI application it provides the checklist against which the service layer
is verified — the same "verify, don't assert" ethos as claim-oriented
programming, applied to app security. It supports "robustness & accuracy".

## Caveat
ASVS covers application security, not model-specific risks (prompt injection,
data poisoning) — those need AI-specific controls (e.g. the control register's
injection-defense control). A passing ASVS level is a floor, not a ceiling.
