# Lead Operations Control Plane

A runnable proof of concept for lead intake, explainable prioritization, follow-up drafting, approval gates, and an append-only audit trail.

## Philosophy

Automate the queue, not the owner's judgment. The system can normalize, score, recommend, draft, and request approval. It does not send an external message or spend money by itself.

## Run

```bash
python -m lead_ops.demo
python -m unittest discover -s tests -v
```

## Controls shown

- source normalization into one lead model
- explainable scoring
- idempotent ingestion
- approval before outbound action
- audit events for state changes

Synthetic data only. This is a proof of design and control flow, not a production CRM. Relevant practices include least privilege, data minimization, idempotent workers, explicit consent, audit logging, WCAG-aware operator interfaces, and OWASP ASVS principles for the eventual web boundary.

## Implemented

The repository contains working code, not mockups:

- Lead intake from a plain dictionary payload into one `Lead` model with source id, name, email, service, urgency, fit, status, score, follow-up draft, and an event history (`lead_ops/core.py`).
- Idempotent ingestion: ingesting the same `source_id` twice returns the existing lead instead of creating a duplicate.
- Explainable scoring: a fixed weighted formula, `score = min(100, urgency * 5 + fit * 5)`, so any score can be traced back to its two operator-entered inputs.
- Follow-up drafting from a template that names the lead and their requested service.
- An approval gate: approval raises a `ValueError` until a draft exists, and only then moves the lead to `approved_for_send`.
- An event list on each lead records state changes (`ingested`, `drafted_follow_up`, `approved_for_send`) with UTC timestamps and the approver.
- A runnable demo (`python -m lead_ops.demo`) that walks one lead through intake, drafting, and approval.

## Limitations

- The control plane is in-memory only. Leads, drafts, and events disappear when the process exits; there is no database.
- Nothing is ever sent. The pipeline stops at `approved_for_send`; there is no email, messaging, or payment integration.
- Scoring is a simple weighted sum of two fields, not machine learning.
- The audit trail is an in-memory append-only list, not durable or tamper-evident storage.
- There is no authentication, authorization, or web interface yet, so this is not a production CRM.
- All data is synthetic demo data created for this proof of concept.

## Tests

The standard-library `unittest` suite lives in `tests/test_core.py` and verifies that:

- ingesting the same payload twice returns the same lead object;
- the score formula is applied (urgency 8 with fit 7 scores 75);
- approval is rejected before a draft exists;
- after drafting, approval sets the status to `approved_for_send`.

Run it locally with `python -m unittest discover -s tests -v`. GitHub Actions runs the same command on every push to `main` and every pull request into `main` (see `.github/workflows/tests.yml`), with read-only token permissions and no credentials stored in the workflow.
