from .core import LeadControlPlane

def main():
    plane = LeadControlPlane()
    lead = plane.ingest({"source_id":"demo-001","name":"Alex","email":"alex@example.test","service":"website redesign","urgency":9,"fit":8})
    plane.draft_follow_up(lead.source_id)
    print({"score": lead.score, "status": lead.status, "draft": lead.follow_up_draft, "approval_required": True})
    plane.approve(lead.source_id, "owner@example.test")
    print({"status": lead.status, "events": len(lead.events)})

if __name__ == "__main__": main()
