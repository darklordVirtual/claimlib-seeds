# NIST SP 800-137 — Information Security Continuous Monitoring (ISCM)

**Canonical source:** NIST Special Publication 800-137 (`doi:10.6028/NIST.SP.800-137`).
**Role:** the observability domain — ongoing awareness, not point-in-time audit.

## What it defines
A process for maintaining ongoing awareness of security posture, vulnerabilities
and threats to support risk decisions: define a strategy, establish metrics and
frequencies, collect and analyze, respond, and review/update. Security is
treated as a continuously monitored property, not an annual checkbox.

## Role in the crosswalk
For an AI system this is the rationale for observability: SLOs, drift detection,
and metric collection that keep "monitoring & post-market" and "robustness &
accuracy" alive between audits. Continuous monitoring is what turns a static
control into a living one.

## Caveat
Continuous monitoring requires that the metrics actually reflect risk;
collecting dashboards that no one acts on is theater. The standard defines the
process, not which AI-specific signals (e.g. calibration drift) matter.
