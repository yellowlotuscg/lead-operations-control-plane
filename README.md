# Lead Operations Control Plane

A small Python proof of concept for taking in a lead, scoring it with a formula you can read, drafting a follow-up, and keeping an in-memory record of those steps. A person approves the draft before the lead is marked ready to send. Sending a message and spending money are outside this program.

## Philosophy

Automate the intake bookkeeping, and leave the send decision with the owner. The code turns one payload into a `Lead`, scores it, and drafts a follow-up. The lead stays at status `new` until someone calls `approve` and a draft is already stored.

## Get the code

```bash
git clone https://github.com/yellowlotuscg/lead-operations-control-plane.git
cd lead-operations-control-plane
```

The project uses the Python standard library only. Python 3.9 or newer is required because `Lead.events` is annotated as `list[dict]`. GitHub Actions runs the tests on Python 3.12.

## Run

From the repository root:

```bash
python -m lead_ops.demo
python -m unittest discover -s tests -v
```

Use `python3` if `python` is not on your PATH. Run the demo as a module. `lead_ops/demo.py` imports `LeadControlPlane` with a relative import, so `python lead_ops/demo.py` fails with `ImportError`.

## Demo

`python -m lead_ops.demo` creates a `LeadControlPlane` and ingests one synthetic lead:

- `source_id`: `demo-001`
- `name`: `Alex`
- `email`: `alex@example.test`
- `service`: `website redesign`
- `urgency`: `9`
- `fit`: `8`

It drafts a follow-up, prints the score, status, and draft, then approves the lead as `owner@example.test` and prints the status and event count:

```text
{'score': 85, 'status': 'new', 'draft': 'Hi Alex, thanks for reaching out about website redesign. We reviewed your request and can propose a focused next step.', 'approval_required': True}
{'status': 'approved_for_send', 'events': 3}
```

The score is `min(100, 9 * 5 + 8 * 5)`, which is 85. Status is still `new` on the first line because drafting does not change it. The three events are `ingested`, `drafted_follow_up`, and `approved_for_send`. The printed `approval_required: True` is a literal in `lead_ops/demo.py`.

## Layout

- `lead_ops/core.py` defines `Lead` and `LeadControlPlane`.
- `lead_ops/demo.py` is the runnable example.
- `lead_ops/__init__.py` is an empty package marker.
- `tests/test_core.py` is the unittest suite.
- `.github/workflows/tests.yml` runs that suite on GitHub Actions.

## Lead

A `Lead` stores `source_id`, `name`, `email`, `service`, `urgency`, and `fit`. It also stores:

- `status`, default `new`
- `score`, default `0` until ingest sets it
- `follow_up_draft`, default empty string
- `events`, a list of dicts, default empty

`email` is kept on the lead. The score and the draft do not read it. `name` and `service` appear in the draft. `urgency` and `fit` are used only for the score.

## Ingest

`LeadControlPlane.ingest(payload)` requires `source_id`, `name`, `email`, and `service`. `urgency` and `fit` pass through `int()`. A missing `urgency` or `fit` becomes `0`.

The score is set once, during ingest:

```text
score = min(100, urgency * 5 + fit * 5)
```

The plane keeps leads in a dict keyed by `source_id` and appends an `ingested` event. A later ingest with the same `source_id` returns the stored lead object and leaves its fields as they were.

## Draft

`draft_follow_up(source_id)` sets `follow_up_draft` to:

```text
Hi {name}, thanks for reaching out about {service}. We reviewed your request and can propose a focused next step.
```

It appends a `drafted_follow_up` event and returns the draft string. Status stays `new`. Calling it again replaces the draft and appends another event. An unknown `source_id` raises `KeyError`.

## Approve

`approve(source_id, approver)` raises `ValueError` with the message `draft a follow-up before approval` when `follow_up_draft` is empty. When a draft is present, it sets `status` to `approved_for_send`, appends an event that includes `approver`, and returns the lead. An unknown `source_id` raises `KeyError`.

`approved_for_send` is the last step in this code.

## Events

`_event` appends a dict to `lead.events`:

- `event`: `ingested`, `drafted_follow_up`, or `approved_for_send`
- `at`: `datetime.now(timezone.utc).isoformat()`, a UTC timestamp
- `approver`: included only on `approved_for_send`, set to the string passed to `approve`

The list is append-only for the life of the process.

## Tests

`tests/test_core.py` contains `test_idempotent_and_approval`. It checks four things:

- Ingesting the same payload twice returns the same lead object.
- Urgency 8 and fit 7 score 75 (`8 * 5 + 7 * 5`).
- `approve` raises `ValueError` before a draft exists.
- After `draft_follow_up`, `approve` sets status to `approved_for_send`.

Run it from the repository root with `python -m unittest discover -s tests -v`.

`.github/workflows/tests.yml` runs that command on `ubuntu-latest` with Python 3.12. It runs on every push to `main` and every pull request into `main`. The workflow sets `permissions: contents: read` and stores no credentials.

## Limitations

- Leads, drafts, and events live on the `LeadControlPlane` instance and disappear when the process exits.
- The pipeline ends at `approved_for_send`. This repository has no email, messaging, or payment code.
- Scoring is the weighted sum above, capped at 100, and it runs only during ingest.
- The event list is process memory. It is not stored on disk.
- Callers pass an `approver` string and the code stores it. This repository has no login, permission check, or web interface.
- The sample records are the synthetic lead in `lead_ops/demo.py` and the fixture in `tests/test_core.py`.

## License

[MIT](LICENSE). Copyright (c) 2026 Matthew Coggins.
