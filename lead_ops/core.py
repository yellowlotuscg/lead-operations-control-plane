from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class Lead:
    source_id: str
    name: str
    email: str
    service: str
    urgency: int
    fit: int
    status: str = "new"
    score: int = 0
    follow_up_draft: str = ""
    events: list[dict] = field(default_factory=list)

class LeadControlPlane:
    def __init__(self): self.leads = {}
    def ingest(self, payload):
        key = payload["source_id"]
        if key in self.leads: return self.leads[key]
        lead = Lead(key, payload["name"], payload["email"], payload["service"], int(payload.get("urgency", 0)), int(payload.get("fit", 0)))
        lead.score = min(100, lead.urgency * 5 + lead.fit * 5)
        self._event(lead, "ingested"); self.leads[key] = lead; return lead
    def draft_follow_up(self, source_id):
        lead = self.leads[source_id]
        lead.follow_up_draft = f"Hi {lead.name}, thanks for reaching out about {lead.service}. We reviewed your request and can propose a focused next step."
        self._event(lead, "drafted_follow_up"); return lead.follow_up_draft
    def approve(self, source_id, approver):
        lead = self.leads[source_id]
        if not lead.follow_up_draft: raise ValueError("draft a follow-up before approval")
        lead.status = "approved_for_send"; self._event(lead, "approved_for_send", approver=approver); return lead
    def _event(self, lead, event, **extra): lead.events.append({"event":event,"at":datetime.now(timezone.utc).isoformat(),**extra})
