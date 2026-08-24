<!-- AUTO-GENERATED:backlink START -->
[← Back](def.md)
<!-- AUTO-GENERATED:backlink END -->
# Observability decision framework

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-24 |
| Audience | Product architects, operators, and acceptance owners |

## Purpose

The template provides portable liveness, readiness, and diagnostic boundaries without selecting a telemetry vendor. Every product that leaves local development must make an explicit observability decision before release. This document defines the minimum decision record and acceptance evidence; it does not send product data to an external service by default.

## Scope

This framework covers product-level service objectives, logs, metrics, traces, error reporting, correlation, alerts, privacy, cost, and telemetry failure behavior. It applies to production products generated from the template. It does not select a provider, transmit telemetry from the template itself, define product-specific business indicators, or replace the product ATP and operational runbooks.

## Existing baseline

- `GET /api/health` reports process liveness without contacting optional infrastructure.
- `GET /api/ready` reports whether enabled dependencies can serve traffic and returns HTTP 503 when they cannot.
- Container health checks use the stable liveness contract.
- CLI Doctor and configuration Doctor expose local setup failures without printing secrets.
- Runtime configuration, product data, and telemetry remain separate concerns.

Health responses must remain low-cardinality and must not expose hosts, credentials, driver errors, stack traces, or customer data. A platform may use readiness to route traffic, but a transient dependency outage must not create a process-restart loop.

## Required product decision

Copy the following table into the product architecture documentation and replace every placeholder before production release.

| Concern | Required decision |
| --- | --- |
| Service objectives | Define measurable availability and latency objectives, their evaluation window, and the owner of the error budget. |
| Logs | Choose text or structured JSON, required fields, retention, access controls, and redaction rules. |
| Metrics | Define request rate, errors, duration, saturation, dependency health, and business-safe product indicators. |
| Traces | Decide whether tracing is enabled, which propagation standard and sampling policy apply, and where traces are retained. |
| Error reporting | Define captured failures, environment and release identifiers, alert routing, retention, and data scrubbing. |
| Correlation | Define a validated request or trace identifier that links logs, metrics, and traces without accepting arbitrary user content. |
| Dashboards and alerts | Name the actionable symptoms, thresholds, on-call owner, escalation route, and runbook for every page. |
| Privacy | Classify telemetry fields, prohibit secrets and unnecessary personal data, and document consent or notice where required. |
| Cost and failure mode | Set volume/cardinality budgets and state how the application behaves when the telemetry backend is unavailable. |

An undecided item is a release blocker for a production product. `Not applicable` is acceptable only with a product-specific rationale and acceptance review.

## Portable telemetry boundary

Product code should emit domain-neutral events through a small application-owned interface. Provider SDKs, exporters, collectors, and credentials belong in infrastructure or deployment adapters. Domain modules must not import a monitoring vendor, FastAPI, OpenTelemetry SDK, or cloud runtime.

Use stable, bounded labels. A customer identifier, raw URL, exception message, SQL statement, file path, or free-form input must not become a metric label. Logs and traces may contain only reviewed fields and must pass through the product's redaction boundary before export.

If distributed tracing is selected, prefer W3C Trace Context at HTTP boundaries and keep sampling configurable by environment. Telemetry export must be asynchronous, time-bounded, and fail open for the product request unless the product threat model explicitly requires fail-closed auditing.

## Minimum acceptance evidence

A production ATP should record:

1. liveness and readiness behavior during a dependency outage;
2. one correlated successful request and one sanitized failure across the selected signals;
3. proof that configured secrets and representative personal data are absent from exported telemetry;
4. an alert exercise linked to an owned runbook;
5. cardinality, retention, and telemetry-backend outage checks; and
6. the dashboard, objective, and error-budget review owner.

Browser E2E, accessibility, and performance-budget checks validate user-facing behavior but are not a substitute for production service telemetry. Conversely, telemetry cannot replace deterministic tests or release gates.

## Verification

Before a production release, the acceptance owner verifies that every row in the required decision table has a product-specific answer and that the six evidence items above are recorded in the product ATP. Repository contributors verify this framework and its navigation with:

```sh
python tools/control.py docs check
```

## Related documents

- [Framework architecture](architecture.md)
- [Runtime configuration](configuration.md)
- [Deployment architecture](deployment-architecture.md)
- [Database feature](database-feature.md)
- [ATP template](../atp/ATP-TEMPLATE.md)
