"""
Marketing Agent - Main AI agent for marketing automation
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from core.memory import MemorySystem
from core.reasoning import ReasoningEngine, ReasoningMode
from core.task import TaskManager
from core.tool import ToolManager
from core.security import SecurityManager
from core.audit import AuditSystem
from core.module import ModuleManager, ModuleType

from .content_generator import ContentGenerator
from .campaign_manager import CampaignManager
from .audience_analyzer import AudienceAnalyzer
from .performance_tracker import PerformanceTracker


class MarketingAgent:
    """
    Main AI agent for marketing automation and business solutions.
    Integrates all core systems with marketing-specific functionality.
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 enable_security: bool = True,
                 enable_auditing: bool = True):
        """
        Initialize the marketing agent.
        
        Args:
            config: Agent configuration
            enable_security: Whether to enable security features
            enable_auditing: Whether to enable auditing features
        """
        self.config = config or {}
        
        # Initialize core systems
        self.memory = MemorySystem(storage_path=self.config.get("memory_path", "./marketing_memory"))
        self.reasoning = ReasoningEngine(mode=ReasoningMode.HIERARCHICAL)
        self.task_manager = TaskManager(max_workers=self.config.get("max_workers", 4))
        self.tool_manager = ToolManager(max_workers=self.config.get("max_workers", 4))
        self.module_manager = ModuleManager(storage_path=self.config.get("module_path", "./marketing_modules"))
        
        # Initialize optional systems
        self.security = SecurityManager() if enable_security else None
        self.audit = AuditSystem() if enable_auditing else None
        
        # Initialize marketing-specific components
        self.content_generator = ContentGenerator(self.memory, self.tool_manager)
        self.campaign_manager = CampaignManager(self.memory, self.task_manager)
        self.audience_analyzer = AudienceAnalyzer(self.memory, self.reasoning)
        self.performance_tracker = PerformanceTracker(self.memory, self.audit)
        
        # Start task manager
        self.task_manager.start()
        
        # Register marketing tools
        self._register_marketing_tools()
        
        # Load marketing modules
        self._load_marketing_modules()
    
    def _register_marketing_tools(self) -> None:
        """Register marketing-specific tools."""
        # Content generation tools
        self.tool_manager.register_tool(
            name="generate_blog_post",
            function=self.content_generator.generate_blog_post,
            description="Generate a blog post on a given topic",
            parameters=[
                {"name": "topic", "type": "str", "required": True, "description": "Blog post topic"},
                {"name": "tone", "type": "str", "required": False, "description": "Writing tone"},
                {"name": "length", "type": "int", "required": False, "description": "Target word count"}
            ],
            category="content",
            tags=["content", "blog", "writing"]
        )
        
        self.tool_manager.register_tool(
            name="generate_social_media_post",
            function=self.content_generator.generate_social_media_post,
            description="Generate a social media post",
            parameters=[
                {"name": "platform", "type": "str", "required": True, "description": "Social media platform"},
                {"name": "topic", "type": "str", "required": True, "description": "Post topic"},
                {"name": "hashtags", "type": "list", "required": False, "description": "Hashtags to include"}
            ],
            category="content",
            tags=["content", "social_media", "marketing"]
        )
        
        # Campaign management tools
        self.tool_manager.register_tool(
            name="create_campaign",
            function=self.campaign_manager.create_campaign,
            description="Create a new marketing campaign",
            parameters=[
                {"name": "name", "type": "str", "required": True, "description": "Campaign name"},
                {"name": "goals", "type": "list", "required": True, "description": "Campaign goals"},
                {"name": "channels", "type": "list", "required": True, "description": "Marketing channels"}
            ],
            category="campaign",
            tags=["campaign", "marketing", "strategy"]
        )
        
        # Audience analysis tools
        self.tool_manager.register_tool(
            name="analyze_audience",
            function=self.audience_analyzer.analyze_audience,
            description="Analyze target audience characteristics",
            parameters=[
                {"name": "audience_data", "type": "dict", "required": True, "description": "Audience data"},
                {"name": "analysis_type", "type": "str", "required": False, "description": "Type of analysis"}
            ],
            category="audience",
            tags=["audience", "analytics", "insights"]
        )
        
        # Performance tracking tools
        self.tool_manager.register_tool(
            name="track_campaign_performance",
            function=self.performance_tracker.track_performance,
            description="Track marketing campaign performance",
            parameters=[
                {"name": "campaign_id", "type": "str", "required": True, "description": "Campaign ID"},
                {"name": "metrics", "type": "list", "required": True, "description": "Metrics to track"}
            ],
            category="analytics",
            tags=["performance", "analytics", "campaign"]
        )
    
    def _load_marketing_modules(self) -> None:
        """Load marketing-specific modules."""
        # Create core marketing module
        marketing_module = self.module_manager.create_module(
            name="MarketingCore",
            module_type=ModuleType.BUSINESS,
            initialize_func=self._initialize_marketing_module,
            execute_func=self._execute_marketing_module,
            shutdown_func=self._shutdown_marketing_module,
            category="marketing",
            tags=["core", "marketing", "automation"]
        )
        
        self.module_manager.load_module(marketing_module.module_id)
    
    def _initialize_marketing_module(self, config: Dict[str, Any]) -> bool:
        """Initialize the marketing module."""
        if self.audit:
            self.audit.log_event(
                event_type="module_initialization",
                source="MarketingAgent",
                details={"module": "MarketingCore"},
                severity="info"
            )
        return True
    
    def _execute_marketing_module(self, *args, **kwargs) -> Any:
        """Execute the marketing module."""
        # Default marketing module execution
        return {"status": "active", "operations": ["content_generation", "campaign_management", "analytics"]}
    
    def _shutdown_marketing_module(self) -> bool:
        """Shutdown the marketing module."""
        if self.audit:
            self.audit.log_event(
                event_type="module_shutdown",
                source="MarketingAgent",
                details={"module": "MarketingCore"},
                severity="info"
            )
        return True
    
    def plan_marketing_strategy(self, business_goals: List[str], target_audience: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan a comprehensive marketing strategy.
        
        Args:
            business_goals: List of business goals
            target_audience: Target audience information
            
        Returns:
            Marketing strategy plan
        """
        # Store context in memory
        self.memory.store(
            key="current_strategy_context",
            value={
                "business_goals": business_goals,
                "target_audience": target_audience,
                "timestamp": datetime.now().isoformat()
            },
            memory_type="long_term"
        )
        
        # Use reasoning engine to create strategy
        goal = "Create comprehensive marketing strategy"
        context = {
            "business_goals": business_goals,
            "target_audience": target_audience,
            "available_channels": ["email", "social_media", "content", "paid_ads", "seo"]
        }
        
        reasoning_result = self.reasoning.reason(goal, context)
        
        # Log strategy planning
        if self.audit:
            self.audit.log_event(
                event_type="strategy_planning",
                source="MarketingAgent",
                details={
                    "goals": business_goals,
                    "reasoning_result": reasoning_result
                },
                severity="info"
            )
        
        return reasoning_result
    
    def execute_marketing_task(self, task_description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a marketing task using the task manager.
        
        Args:
            task_description: Description of the task
            parameters: Task parameters
            
        Returns:
            Task execution result
        """
        # Create task
        task = self.task_manager.create_task(
            name=task_description,
            action=self._execute_marketing_action,
            action_args={"args": [], "kwargs": parameters},
            priority=self._determine_task_priority(task_description),
            metadata={"type": "marketing_task"}
        )
        
        # Submit task
        self.task_manager.submit_task(task)
        
        # Wait for completion
        self.task_manager.wait_for_task(task.task_id, timeout=300)
        
        # Get result
        completed_task = self.task_manager.get_task(task.task_id)
        
        return {
            "task_id": task.task_id,
            "status": completed_task.status.value if completed_task else "unknown",
            "result": completed_task.result.data if completed_task and completed_task.result else None
        }
    
    def _execute_marketing_action(self, **kwargs) -> Any:
        """Execute a marketing action based on parameters."""
        action_type = kwargs.get("action_type")
        
        if action_type == "generate_content":
            return self.content_generator.generate_content(kwargs)
        elif action_type == "analyze_campaign":
            return self.performance_tracker.analyze_campaign(kwargs)
        elif action_type == "segment_audience":
            return self.audience_analyzer.segment_audience(kwargs)
        else:
            return {"error": f"Unknown action type: {action_type}"}
    
    def _determine_task_priority(self, task_description: str) -> Any:
        """Determine task priority based on description."""
        from core.task import TaskPriority
        
        task_lower = task_description.lower()
        
        if any(keyword in task_lower for keyword in ["urgent", "critical", "immediate"]):
            return TaskPriority.CRITICAL
        elif any(keyword in task_lower for keyword in ["important", "priority"]):
            return TaskPriority.HIGH
        elif any(keyword in task_lower for keyword in ["routine", "regular"]):
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.LOW
    
    def get_marketing_insights(self, time_period: str = "7d") -> Dict[str, Any]:
        """
        Get comprehensive marketing insights.
        
        Args:
            time_period: Time period for insights (e.g., "7d", "30d", "90d")
            
        Returns:
            Marketing insights data
        """
        insights = {
            "time_period": time_period,
            "generated_at": datetime.now().isoformat(),
            "content_performance": self.content_generator.get_performance_metrics(time_period),
            "campaign_performance": self.campaign_manager.get_campaign_summary(time_period),
            "audience_insights": self.audience_analyzer.get_audience_insights(time_period),
            "overall_metrics": self.performance_tracker.get_overall_metrics(time_period)
        }
        
        return insights
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the overall status of the marketing agent.
        
        Returns:
            Agent status information
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "memory": self.memory.get_stats(),
            "reasoning": {
                "mode": self.reasoning.mode.value,
                "decision_stats": self.reasoning.decision_maker.get_decision_stats()
            },
            "tasks": self.task_manager.get_statistics(),
            "tools": self.tool_manager.get_statistics(),
            "modules": self.module_manager.get_statistics(),
            "security": self.security.get_security_stats() if self.security else {"enabled": False},
            "audit": self.audit.get_system_health() if self.audit else {"enabled": False}
        }
    
    def shutdown(self) -> None:
        """Shutdown the marketing agent."""
        # Stop task manager
        self.task_manager.stop()
        
        # Shutdown module manager
        self.module_manager.shutdown()
        
        # Shutdown tool manager
        self.tool_manager.shutdown()
        
        # Final audit log
        if self.audit:
            self.audit.log_event(
                event_type="agent_shutdown",
                source="MarketingAgent",
                details={"shutdown_time": datetime.now().isoformat()},
                severity="info"
            )