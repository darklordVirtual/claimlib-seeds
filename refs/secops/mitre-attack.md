# MITRE ATT&CK

**Canonical source:** MITRE ATT&CK knowledge base (`spec:mitre-attack`).
**Role:** threat-informed detection under detection & response.

## What it defines
A curated, continuously-updated knowledge base of adversary tactics (the "why":
initial access, persistence, exfiltration, …) and techniques (the "how"),
observed in real intrusions. It gives defenders a shared language to describe,
map and measure detection coverage against actual adversary behavior.

## Role in the crosswalk
Detection engineering for a governed AI system maps SIEM/SOAR detections to
ATT&CK techniques so coverage is measurable rather than anecdotal — "which
techniques can we detect?". It keeps "monitoring & post-market" threat-informed.

## Caveat
ATT&CK catalogs known techniques; it is not exhaustive and lags novel attacks,
including AI-specific ones (there is a companion ATLAS for ML threats). Mapping
detections to ATT&CK measures coverage of *known* behavior, not safety from the
unknown.
