import unittest
from lead_ops.core import LeadControlPlane
class Tests(unittest.TestCase):
 def test_idempotent_and_approval(self):
  p=LeadControlPlane(); d={"source_id":"x","name":"A","email":"a@test","service":"seo","urgency":8,"fit":7}
  a=p.ingest(d); self.assertIs(a,p.ingest(d)); self.assertEqual(a.score,75)
  with self.assertRaises(ValueError): p.approve("x","owner")
  p.draft_follow_up("x"); p.approve("x","owner"); self.assertEqual(a.status,"approved_for_send")
if __name__=="__main__": unittest.main()
