from dataclasses import dataclass

from forge_core.contracts.models import ApprovalRequest, AuditEvent, Campaign, CampaignStatus, ExternalAction, MemoryItem, Task
from forge_core.services.approvals import InMemoryApprovalService
from forge_core.services.audit import HashChainedAuditLog
from forge_core.services.campaigns import CampaignService
from forge_core.services.memory import InMemoryScopedMemory


@dataclass(frozen=True)
class WeeklyReport:
    campaign_count: int
    active_campaign_count: int
    open_task_count: int
    pending_approval_count: int
    recommendations: tuple[str, ...]


class HeadOfMarketingAI:
    """Marketing business logic; Forge Core supplies the safety and platform services."""

    def __init__(self, memory: InMemoryScopedMemory, campaigns: CampaignService, approvals: InMemoryApprovalService, audit: HashChainedAuditLog) -> None:
        self.memory, self.campaigns, self.approvals, self.audit = memory, campaigns, approvals, audit

    def create_campaign(self, name: str, objective: str, audience: str, metric: str, owner: str) -> Campaign:
        campaign = self.campaigns.create(Campaign(name=name, objective=objective, audience=audience, success_metric=metric, owner=owner))
        self.campaigns.transition(campaign.id, CampaignStatus.PROPOSED)
        self.audit.record(AuditEvent("campaign_created", "head_of_marketing_ai", {"campaign_id": campaign.id, "objective": objective}))
        return campaign

    def generate_brief_and_tasks(self, campaign: Campaign) -> dict[str, object]:
        context = self.memory.search("bowser-technologies", "company")
        company_context = context[0].content if context else "No approved company context found."
        brief = {"campaign_id": campaign.id, "objective": campaign.objective, "audience": campaign.audience, "success_metric": campaign.success_metric, "approved_context": company_context}
        for title, priority in [("Review audience and message", "high"), ("Draft approved channel content", "high"), ("Define measurement plan", "normal")]:
            self.campaigns.add_task(campaign.id, Task(title=title, owner=campaign.owner, priority=priority))
        self.audit.record(AuditEvent("brief_generated", "head_of_marketing_ai", {"campaign_id": campaign.id, "context_source": context[0].source if context else None}))
        return brief

    def request_external_draft_approval(self, campaign: Campaign, channel: str, copy: str, requester: str) -> ApprovalRequest:
        action = ExternalAction("publish_content", {"campaign_id": campaign.id, "channel": channel, "copy": copy}, requester, "bowser-technologies")
        request = self.approvals.request(ApprovalRequest(action=action, summary=f"Publish {channel} draft for {campaign.name}"))
        self.audit.record(AuditEvent("approval_requested", requester, {"approval_id": request.id, "action_id": action.id, "campaign_id": campaign.id}))
        return request

    def weekly_report(self) -> WeeklyReport:
        campaigns = self.campaigns.all()
        open_tasks = sum(task.status != "complete" for campaign in campaigns for task in campaign.tasks)
        pending = sum(event.event_type == "approval_requested" for event in self.audit.events())
        return WeeklyReport(len(campaigns), sum(c.status in {CampaignStatus.IN_PROGRESS, CampaignStatus.LIVE} for c in campaigns), open_tasks, pending, ("Review pending external drafts before publishing.", "Confirm campaign metric baseline before launch."))
