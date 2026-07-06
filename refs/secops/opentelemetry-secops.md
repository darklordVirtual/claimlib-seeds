# OpenTelemetry (for observability & audit)

**Canonical source:** OpenTelemetry, CNCF (`spec:opentelemetry`).
**Role:** vendor-neutral telemetry under observability and logging/audit.

## What it defines
A single set of APIs, SDKs and a wire protocol (OTLP) for traces, metrics and
logs, with semantic conventions so signals are consistent across languages and
vendors. Instrument once; export anywhere (any backend that speaks OTLP).

## Role in the crosswalk
It is the portable seam for observability and audit export across clouds: the
same instrumentation feeds monitoring on AWS, Azure, GCP and OpenShift, and the
same trace/log pipeline underpins both operational observability and the
tamper-evident audit trail. It keeps "monitoring & post-market" and "logging &
traceability" portable.

## Caveat
OpenTelemetry moves and standardizes signals; it does not decide what to
collect, retain or protect. Telemetry can carry PII and must be scrubbed;
integrity of the audit trail is a separate property (hash-chaining), not
provided by OTel itself.
