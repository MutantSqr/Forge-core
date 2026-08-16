"""
Planner - Strategic planning and goal decomposition
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class StepPriority(Enum):
    """Priority levels for plan steps."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PlanStep:
    """A single step in a plan."""
    id: str
    description: str
    priority: StepPriority
    estimated_time: int
    dependencies: List[str]
    required_resources: List[str]
    risks: List[str]
    feasibility: float
    metadata: Dict[str, Any]


class Planner:
    """
    Planner for creating strategic plans to achieve goals.
    """
    
    def __init__(self):
        """Initialize the planner."""
        self._plan_templates = self._load_plan_templates()
        
    def _load_plan_templates(self) -> Dict[str, Dict]:
        """Load plan templates for common scenarios."""
        return {
            "marketing_campaign": {
                "steps": [
                    "analyze_target_audience",
                    "define_campaign_goals", 
                    "create_content_strategy",
                    "select_channels",
                    "create_content",
                    "schedule_posts",
                    "monitor_performance",
                    "optimize_campaign"
                ]
            },
            "content_creation": {
                "steps": [
                    "research_topic",
                    "outline_content",
                    "draft_content",
                    "review_content",
                    "finalize_content",
                    "publish_content"
                ]
            },
            "analysis": {
                "steps": [
                    "collect_data",
                    "clean_data",
                    "analyze_data",
                    "interpret_results",
                    "create_report"
                ]
            }
        }
    
    def create_sequential_plan(self, goal: str, context: Dict) -> Dict[str, Any]:
        """
        Create a sequential plan for achieving the goal.
        
        Args:
            goal: The goal to achieve
            context: Context information
            
        Returns:
            Sequential plan
        """
        steps = self._decompose_goal(goal, context)
        
        # Order steps sequentially
        ordered_steps = self._order_steps_sequentially(steps)
        
        return {
            "goal": goal,
            "plan_type": "sequential",
            "steps": ordered_steps,
            "estimated_total_time": sum(s.get("estimated_time", 1) for s in ordered_steps),
            "contingency_plan": self._create_contingency_plan(ordered_steps)
        }
    
    def create_parallel_plan(self, goal: str, context: Dict) -> Dict[str, Any]:
        """
        Create a parallel plan for achieving the goal.
        
        Args:
            goal: The goal to achieve
            context: Context information
            
        Returns:
            Parallel plan
        """
        steps = self._decompose_goal(goal, context)
        
        # Group steps that can run in parallel
        parallel_groups = self._group_parallel_steps(steps)
        
        return {
            "goal": goal,
            "plan_type": "parallel",
            "parallel_groups": parallel_groups,
            "estimated_total_time": self._estimate_parallel_time(parallel_groups),
            "contingency_plan": self._create_contingency_plan(steps)
        }
    
    def create_hierarchical_plan(self, goal: str, context: Dict) -> Dict[str, Any]:
        """
        Create a hierarchical plan with sub-goals.
        
        Args:
            goal: The goal to achieve
            context: Context information
            
        Returns:
            Hierarchical plan
        """
        # Break down into main sub-goals
        sub_goals = self._identify_sub_goals(goal, context)
        
        # Create plans for each sub-goal
        sub_plans = {}
        for sub_goal in sub_goals:
            sub_plan = self.create_sequential_plan(sub_goal, context)
            sub_plans[sub_goal] = sub_plan
        
        return {
            "goal": goal,
            "plan_type": "hierarchical",
            "sub_goals": sub_goals,
            "sub_plans": sub_plans,
            "estimated_total_time": sum(
                p.get("estimated_total_time", 0) for p in sub_plans.values()
            ),
            "contingency_plan": self._create_contingency_plan(sub_goals)
        }
    
    def create_creative_plan(self, goal: str, context: Dict) -> Dict[str, Any]:
        """
        Create a creative plan with multiple solution approaches.
        
        Args:
            goal: The goal to achieve
            context: Context information
            
        Returns:
            Creative plan with multiple approaches
        """
        # Generate multiple approaches
        approaches = self._generate_approaches(goal, context)
        
        # Create plans for each approach
        approach_plans = []
        for approach in approaches:
            plan = self.create_sequential_plan(f"{goal} ({approach})", context)
            approach_plans.append({
                "approach": approach,
                "plan": plan
            })
        
        return {
            "goal": goal,
            "plan_type": "creative",
            "approaches": approach_plans,
            "recommended_approach": self._recommend_approach(approach_plans, context),
            "contingency_plan": self._create_contingency_plan(approaches)
        }
    
    def _decompose_goal(self, goal: str, context: Dict) -> List[Dict]:
        """Decompose a goal into executable steps."""
        # Check if we have a template for this goal type
        for template_name, template in self._plan_templates.items():
            if template_name.lower() in goal.lower():
                return self._create_steps_from_template(template, context)
        
        # Default decomposition
        return self._default_decomposition(goal, context)
    
    def _create_steps_from_template(self, template: Dict, context: Dict) -> List[Dict]:
        """Create steps from a template."""
        steps = []
        for i, step_name in enumerate(template["steps"]):
            step = {
                "id": f"step_{i}",
                "description": step_name.replace("_", " ").title(),
                "priority": StepPriority.MEDIUM.value,
                "estimated_time": 1,
                "dependencies": [f"step_{i-1}"] if i > 0 else [],
                "required_resources": [],
                "risks": [],
                "feasibility": 0.8,
                "metadata": {}
            }
            steps.append(step)
        return steps
    
    def _default_decomposition(self, goal: str, context: Dict) -> List[Dict]:
        """Default goal decomposition when no template matches."""
        return [
            {
                "id": "step_0",
                "description": f"Analyze requirements for {goal}",
                "priority": StepPriority.HIGH.value,
                "estimated_time": 1,
                "dependencies": [],
                "required_resources": [],
                "risks": [],
                "feasibility": 0.9,
                "metadata": {}
            },
            {
                "id": "step_1", 
                "description": f"Execute {goal}",
                "priority": StepPriority.CRITICAL.value,
                "estimated_time": 2,
                "dependencies": ["step_0"],
                "required_resources": [],
                "risks": [],
                "feasibility": 0.7,
                "metadata": {}
            },
            {
                "id": "step_2",
                "description": f"Validate results for {goal}",
                "priority": StepPriority.HIGH.value,
                "estimated_time": 1,
                "dependencies": ["step_1"],
                "required_resources": [],
                "risks": [],
                "feasibility": 0.8,
                "metadata": {}
            }
        ]
    
    def _order_steps_sequentially(self, steps: List[Dict]) -> List[Dict]:
        """Order steps based on dependencies."""
        # Simple topological sort
        ordered = []
        remaining = steps.copy()
        
        while remaining:
            # Find steps with no unmet dependencies
            ready = [
                step for step in remaining 
                if all(dep in [s["id"] for s in ordered] for dep in step["dependencies"])
            ]
            
            if not ready:
                # Circular dependency or missing dependency
                ready = [remaining[0]]
            
            ordered.extend(ready)
            remaining = [s for s in remaining if s not in ready]
        
        return ordered
    
    def _group_parallel_steps(self, steps: List[Dict]) -> List[List[Dict]]:
        """Group steps that can run in parallel."""
        groups = []
        remaining = steps.copy()
        
        while remaining:
            # Find steps with no dependencies on remaining steps
            current_group = [
                step for step in remaining
                if not any(dep in [s["id"] for s in remaining] for dep in step["dependencies"])
            ]
            
            if not current_group:
                current_group = [remaining[0]]
            
            groups.append(current_group)
            remaining = [s for s in remaining if s not in current_group]
        
        return groups
    
    def _identify_sub_goals(self, goal: str, context: Dict) -> List[str]:
        """Identify sub-goals for hierarchical planning."""
        # Simple heuristic: break down by common patterns
        sub_goals = []
        
        if "marketing" in goal.lower():
            sub_goals = [
                "Analyze target audience",
                "Create marketing content",
                "Execute marketing campaign",
                "Measure results"
            ]
        elif "content" in goal.lower():
            sub_goals = [
                "Research content topic",
                "Create content outline",
                "Draft content",
                "Review and finalize"
            ]
        else:
            # Generic decomposition
            sub_goals = [
                f"Plan {goal}",
                f"Execute {goal}",
                f"Review {goal}"
            ]
        
        return sub_goals
    
    def _generate_approaches(self, goal: str, context: Dict) -> List[str]:
        """Generate multiple creative approaches."""
        approaches = [
            "Standard approach",
            "Innovative approach",
            "Conservative approach"
        ]
        
        if "marketing" in goal.lower():
            approaches = [
                "Digital-first approach",
                "Traditional media approach",
                "Hybrid approach",
                "Viral-focused approach"
            ]
        
        return approaches
    
    def _estimate_parallel_time(self, parallel_groups: List[List[Dict]]) -> int:
        """Estimate total time for parallel execution."""
        return sum(
            max(step.get("estimated_time", 1) for step in group)
            for group in parallel_groups
        )
    
    def _recommend_approach(self, approach_plans: List[Dict], context: Dict) -> str:
        """Recommend the best approach based on context."""
        # Simple recommendation logic
        if context.get("risk_tolerance") == "low":
            return approach_plans[0]["approach"]  # First approach
        else:
            return approach_plans[-1]["approach"]  # Last approach
    
    def _create_contingency_plan(self, steps_or_approaches) -> Dict[str, Any]:
        """Create a contingency plan for when things go wrong."""
        return {
            "fallback_steps": [
                "Reassess current situation",
                "Identify blockers",
                "Adjust plan accordingly",
                "Communicate changes"
            ],
            "escalation_triggers": [
                "Step fails 3 times",
                "Time exceeds 2x estimate",
                "Resource becomes unavailable"
            ]
        }