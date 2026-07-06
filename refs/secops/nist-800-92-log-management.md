# NIST SP 800-92 — Guide to Computer Security Log Management

**Canonical source:** NIST Special Publication 800-92 (`doi:10.6028/NIST.SP.800-92`).
**Role:** the logging/audit domain — centralized, retained, time-synced logs.

## What it defines
Guidance for log management infrastructure: generation, transmission, storage,
analysis and disposal of security logs; the need for centralized collection,
consistent time synchronization, protected storage, and defined retention. It
frames logs as the evidentiary substrate for detection and forensics.

## Role in the crosswalk
For a governed AI system, logging is what makes accountability real: every
decision, prompt, retrieval and answer should be recorded with integrity and
time-sync so an auditor can reconstruct what happened. Paired with a
tamper-evident (hash-chained) trail, it keeps "logging & traceability".

## Caveat
800-92 is a guide, not a certifiable standard. Log volume without integrity,
retention and analysis is noise; the value is in protected, queryable,
time-consistent records — and logs themselves can contain PII that must be
scrubbed.
