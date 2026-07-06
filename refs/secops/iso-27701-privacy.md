# ISO/IEC 27701 and GDPR — privacy and PII handling

**Canonical sources:** ISO/IEC 27701:2019 (`spec:iso-iec-27701`); EU GDPR,
Regulation 2016/679 (`spec:eu-gdpr`).
**Role:** the PII data-protection domain — discovery, scrubbing, minimization.

## What they define
ISO/IEC 27701 extends an ISO/IEC 27001 ISMS into a Privacy Information Management
System (PIMS): controls for PII controllers and processors, mapped to GDPR
articles. GDPR sets the legal obligations — lawful basis, data minimization,
purpose limitation, data-subject rights (DSAR), and privacy by design and by
default.

## Role in the crosswalk
For an AI system, PII handling is a first-class operational domain: discover and
classify PII in prompts, context and logs; scrub/redact or pseudonymize before
storage or model input; enforce retention; service DSARs. This keeps the
"privacy & data protection" and "data governance" objectives.

## Caveat
27701 certification and GDPR compliance concern the *program*, not a guarantee
that a given scrubbing pipeline catches every identifier. Redaction is
best-effort and must be tested against realistic data; pseudonymization is not
anonymization.
