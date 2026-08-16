import unittest

from forge_core.contracts.models import ApprovalRequest, ApprovalStatus, ExternalAction, MemoryItem
from forge_core.services.approvals import InMemoryApprovalService
from forge_core.services.audit import HashChainedAuditLog
from forge_core.services.campaigns import CampaignService
from forge_core.services.memory import InMemoryScopedMemory
from forge_core.specialists.head_of_marketing import HeadOfMarketingAI


class PhaseOneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.memory, self.campaigns = InMemoryScopedMemory(), CampaignService()
        self.approvals, self.audit = InMemoryApprovalService(), HashChainedAuditLog()
        self.ai = HeadOfMarketingAI(self.memory, self.campaigns, self.approvals, self.audit)
        self.memory.save(MemoryItem("bowser-technologies", "company", "Company value: human-controlled AI.", "approved-profile", "founder"))

    def test_campaign_brief_uses_scoped_approved_context(self) -> None:
        campaign = self.ai.create_campaign("Launch", "Generate interest", "founders", "demo requests", "founder")
        brief = self.ai.generate_brief_and_tasks(campaign)
        self.assertIn("human-controlled AI", brief["approved_context"])
        self.assertEqual(3, len(campaign.tasks))

    def test_external_draft_requires_matching_human_approval(self) -> None:
        action = ExternalAction("publish_content", {"copy": "Approved copy"}, "ai", "bowser-technologies")
        request = self.approvals.request(ApprovalRequest(action, "Publish draft"))
        self.assertFalse(self.approvals.is_approved(request.id, action.payload_hash))
        self.approvals.approve(request.id, "founder", "Looks good")
        self.assertEqual(ApprovalStatus.APPROVED, request.status)
        self.assertTrue(self.approvals.is_approved(request.id, action.payload_hash))
        changed_action = ExternalAction("publish_content", {"copy": "Changed after approval"}, "ai", "bowser-technologies")
        self.assertFalse(self.approvals.is_approved(request.id, changed_action.payload_hash))

    def test_audit_log_is_append_only_and_hash_chained(self) -> None:
        campaign = self.ai.create_campaign("Launch", "Generate interest", "founders", "demo requests", "founder")
        self.ai.generate_brief_and_tasks(campaign)
        self.assertEqual(2, len(self.audit.events()))
        self.assertNotEqual("GENESIS", self.audit.head_hash)


if __name__ == "__main__":
    unittest.main()
