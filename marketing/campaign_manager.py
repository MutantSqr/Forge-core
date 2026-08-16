"""
Campaign Manager - Marketing campaign creation and management
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid


class CampaignStatus(Enum):
    """Campaign status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignManager:
    """
    Manager for creating and managing marketing campaigns.
    """
    
    def __init__(self, memory_system, task_manager):
        """
        Initialize the campaign manager.
        
        Args:
            memory_system: Memory system instance
            task_manager: Task manager instance
        """
        self.memory = memory_system
        self.task_manager = task_manager
        self._campaigns: Dict[str, Dict[str, Any]] = {}
        self._campaign_templates = self._load_campaign_templates()
    
    def _load_campaign_templates(self) -> Dict[str, Dict]:
        """Load campaign templates."""
        return {
            "brand_awareness": {
                "goals": ["increase_brand_recognition", "expand_reach", "engagement"],
                "channels": ["social_media", "content_marketing", "influencer"],
                "duration_days": 30,
                "metrics": ["impressions", "reach", "engagement_rate", "brand_mentions"]
            },
            "lead_generation": {
                "goals": ["generate_leads", "capture_contacts", "nurture_prospects"],
                "channels": ["email", "paid_ads", "landing_pages", "webinars"],
                "duration_days": 14,
                "metrics": ["leads", "conversion_rate", "cost_per_lead", "lead_quality"]
            },
            "product_launch": {
                "goals": ["announce_product", "drive_sales", "create_buzz"],
                "channels": ["multi_channel", "pr", "email", "social_media", "paid_ads"],
                "duration_days": 21,
                "metrics": ["sales", "website_traffic", "social_shares", "media_coverage"]
            },
            "customer_retention": {
                "goals": ["retain_customers", "increase_loyalty", "upsell"],
                "channels": ["email", "loyalty_program", "personalized_offers"],
                "duration_days": 90,
                "metrics": ["retention_rate", "repeat_purchase_rate", "customer_lifetime_value", "engagement"]
            }
        }
    
    def create_campaign(self, name: str, goals: List[str], channels: List[str],
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       budget: Optional[Dict[str, float]] = None,
                       target_audience: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new marketing campaign.
        
        Args:
            name: Campaign name
            goals: Campaign goals
            channels: Marketing channels
            start_date: Campaign start date
            end_date: Campaign end date
            budget: Budget allocation
            target_audience: Target audience definition
            
        Returns:
            Created campaign data
        """
        campaign_id = str(uuid.uuid4())
        
        # Set default dates if not provided
        if not start_date:
            start_date = datetime.now() + timedelta(days=1)
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        campaign = {
            "campaign_id": campaign_id,
            "name": name,
            "goals": goals,
            "channels": channels,
            "status": CampaignStatus.DRAFT.value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "budget": budget or {},
            "target_audience": target_audience or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metrics": {},
            "tasks": []
        }
        
        # Store campaign
        self._campaigns[campaign_id] = campaign
        
        # Store in memory
        self.memory.store(
            key=f"campaign_{campaign_id}",
            value=campaign,
            memory_type="long_term"
        )
        
        # Create campaign tasks
        self._create_campaign_tasks(campaign_id, campaign)
        
        return campaign
    
    def _create_campaign_tasks(self, campaign_id: str, campaign: Dict[str, Any]) -> None:
        """Create tasks for campaign execution."""
        task_descriptions = [
            f"Plan content strategy for {campaign['name']}",
            f"Create content for {campaign['name']}",
            f"Set up {campaign['name']} channels",
            f"Launch {campaign['name']}",
            f"Monitor {campaign['name']} performance",
            f"Optimize {campaign['name']} based on data"
        ]
        
        for description in task_descriptions:
            task = self.task_manager.create_task(
                name=description,
                action=self._execute_campaign_task,
                action_args={"kwargs": {"campaign_id": campaign_id, "task": description}},
                metadata={"campaign_id": campaign_id}
            )
            campaign["tasks"].append(task.task_id)
    
    def _execute_campaign_task(self, campaign_id: str, task: str) -> Dict[str, Any]:
        """Execute a campaign task."""
        return {
            "campaign_id": campaign_id,
            "task": task,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def launch_campaign(self, campaign_id: str) -> bool:
        """
        Launch a campaign.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Success status
        """
        if campaign_id not in self._campaigns:
            return False
        
        campaign = self._campaigns[campaign_id]
        campaign["status"] = CampaignStatus.ACTIVE.value
        campaign["updated_at"] = datetime.now().isoformat()
        
        # Update memory
        self.memory.store(
            key=f"campaign_{campaign_id}",
            value=campaign,
            memory_type="long_term"
        )
        
        return True
    
    def pause_campaign(self, campaign_id: str) -> bool:
        """
        Pause a campaign.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Success status
        """
        if campaign_id not in self._campaigns:
            return False
        
        campaign = self._campaigns[campaign_id]
        campaign["status"] = CampaignStatus.PAUSED.value
        campaign["updated_at"] = datetime.now().isoformat()
        
        # Update memory
        self.memory.store(
            key=f"campaign_{campaign_id}",
            value=campaign,
            memory_type="long_term"
        )
        
        return True
    
    def complete_campaign(self, campaign_id: str) -> bool:
        """
        Mark a campaign as completed.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Success status
        """
        if campaign_id not in self._campaigns:
            return False
        
        campaign = self._campaigns[campaign_id]
        campaign["status"] = CampaignStatus.COMPLETED.value
        campaign["updated_at"] = datetime.now().isoformat()
        
        # Update memory
        self.memory.store(
            key=f"campaign_{campaign_id}",
            value=campaign,
            memory_type="long_term"
        )
        
        return True
    
    def update_campaign_metrics(self, campaign_id: str, metrics: Dict[str, float]) -> bool:
        """
        Update campaign metrics.
        
        Args:
            campaign_id: Campaign ID
            metrics: Metrics to update
            
        Returns:
            Success status
        """
        if campaign_id not in self._campaigns:
            return False
        
        campaign = self._campaigns[campaign_id]
        campaign["metrics"].update(metrics)
        campaign["updated_at"] = datetime.now().isoformat()
        
        # Update memory
        self.memory.store(
            key=f"campaign_{campaign_id}",
            value=campaign,
            memory_type="long_term"
        )
        
        return True
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get campaign details.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign data or None if not found
        """
        return self._campaigns.get(campaign_id)
    
    def get_campaigns_by_status(self, status: CampaignStatus) -> List[Dict[str, Any]]:
        """
        Get campaigns by status.
        
        Args:
            status: Campaign status
            
        Returns:
            List of campaigns with the specified status
        """
        return [
            campaign for campaign in self._campaigns.values()
            if campaign["status"] == status.value
        ]
    
    def get_campaign_summary(self, time_period: str = "30d") -> Dict[str, Any]:
        """
        Get campaign summary for a time period.
        
        Args:
            time_period: Time period for summary
            
        Returns:
            Campaign summary data
        """
        # Calculate date threshold
        days = int(time_period.replace("d", "")) if time_period.endswith("d") else 30
        threshold_date = datetime.now() - timedelta(days=days)
        
        # Filter campaigns by date
        recent_campaigns = [
            campaign for campaign in self._campaigns.values()
            if datetime.fromisoformat(campaign["created_at"]) >= threshold_date
        ]
        
        # Calculate summary statistics
        total_campaigns = len(recent_campaigns)
        active_campaigns = len([c for c in recent_campaigns if c["status"] == CampaignStatus.ACTIVE.value])
        completed_campaigns = len([c for c in recent_campaigns if c["status"] == CampaignStatus.COMPLETED.value])
        
        # Aggregate metrics
        total_budget = sum(
            sum(campaign["budget"].values()) if campaign["budget"] else 0
            for campaign in recent_campaigns
        )
        
        return {
            "time_period": time_period,
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "completed_campaigns": completed_campaigns,
            "total_budget": total_budget,
            "campaigns": recent_campaigns
        }
    
    def create_campaign_from_template(self, template_name: str, custom_name: str,
                                    custom_goals: Optional[List[str]] = None,
                                    custom_channels: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a campaign from a template.
        
        Args:
            template_name: Template name
            custom_name: Custom campaign name
            custom_goals: Custom goals (overrides template)
            custom_channels: Custom channels (overrides template)
            
        Returns:
            Created campaign or None if template not found
        """
        if template_name not in self._campaign_templates:
            return None
        
        template = self._campaign_templates[template_name]
        
        return self.create_campaign(
            name=custom_name,
            goals=custom_goals or template["goals"],
            channels=custom_channels or template["channels"],
            start_date=datetime.now() + timedelta(days=1),
            end_date=datetime.now() + timedelta(days=template["duration_days"])
        )
    
    def get_available_templates(self) -> List[str]:
        """
        Get available campaign templates.
        
        Returns:
            List of template names
        """
        return list(self._campaign_templates.keys())