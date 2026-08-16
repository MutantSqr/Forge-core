from forge_core.contracts.models import MemoryItem
from forge_core.services.approvals import InMemoryApprovalService
from forge_core.services.audit import HashChainedAuditLog
from forge_core.services.campaigns import CampaignService
from forge_core.services.memory import InMemoryScopedMemory
from forge_core.specialists.head_of_marketing import HeadOfMarketingAI


def main() -> None:
    memory, campaigns, approvals, audit = InMemoryScopedMemory(), CampaignService(), InMemoryApprovalService(), HashChainedAuditLog()
    memory.save(MemoryItem("bowser-technologies", "company-profile", "Bowser Technologies builds dependable, human-controlled AI systems.", "founder-approved profile", "founder"))
    marketing = HeadOfMarketingAI(memory, campaigns, approvals, audit)
    campaign = marketing.create_campaign("Forge Core introduction", "Build early awareness for Forge Core", "technical founders", "qualified-demo requests", "founder")
    print(marketing.generate_brief_and_tasks(campaign))
    approval = marketing.request_external_draft_approval(campaign, "linkedin", "Forge Core helps specialist AIs work safely with human approval.", "head_of_marketing_ai")
    print(f"Pending approval: {approval.id}")
    print(marketing.weekly_report())
    print(f"Audit events: {len(audit.events())}; chain head: {audit.head_hash[:12]}")


if __name__ == "__main__":
    main()
