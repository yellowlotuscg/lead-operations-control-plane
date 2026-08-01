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
