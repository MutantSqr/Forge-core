from forge_core.contracts.models import Campaign, CampaignStatus, Task


class CampaignService:
    def __init__(self) -> None:
        self._campaigns: dict[str, Campaign] = {}

    def create(self, campaign: Campaign) -> Campaign:
        self._campaigns[campaign.id] = campaign
        return campaign

    def add_task(self, campaign_id: str, task: Task) -> Task:
        self._campaigns[campaign_id].tasks.append(task)
        return task

    def transition(self, campaign_id: str, status: CampaignStatus) -> Campaign:
        campaign = self._campaigns[campaign_id]
        campaign.status = status
        return campaign

    def all(self) -> list[Campaign]:
        return list(self._campaigns.values())
