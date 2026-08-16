"""
Reasoning Engine - Main orchestration of reasoning components
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from .planner import Planner
from .decision_maker import DecisionMaker
from .context_analyzer import ContextAnalyzer


class ReasoningMode(Enum):
    """Different reasoning modes."""
    SEQUENTIAL = "sequential"  # Step-by-step reasoning
    PARALLEL = "parallel"     # Explore multiple paths
    HIERARCHICAL = "hierarchical"  # Break down into sub-goals
    CREATIVE = "creative"     # Generate multiple solutions


class ReasoningEngine:
    """
    Main reasoning engine that coordinates planning, decision making, 
    and context analysis for intelligent decision processing.
    """
    
    def __init__(self, mode: ReasoningMode = ReasoningMode.HIERARCHICAL):
        """
        Initialize the reasoning engine.
        
        Args:
            mode: Reasoning mode to use
        """
        self.mode = mode
        self.planner = Planner()
        self.decision_maker = DecisionMaker()
        self.context_analyzer = ContextAnalyzer()
        
        # Custom reasoning hooks
        self._reasoning_hooks: List[Callable] = []
        
    def add_reasoning_hook(self, hook: Callable) -> None:
        """
        Add a custom reasoning hook.
        
        Args:
            hook: Callable that takes context and returns modified context
        """
        self._reasoning_hooks.append(hook)
    
    def reason(self, goal: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform reasoning on a given goal.
        
        Args:
            goal: The goal to reason about
            context: Additional context for reasoning
            
        Returns:
            Reasoning results with plan and decisions
        """
        context = context or {}
        
        # Apply reasoning hooks
        for hook in self._reasoning_hooks:
            context = hook(context)
        
        # Analyze context
        context_analysis = self.context_analyzer.analyze(goal, context)
        
        # Generate plan based on mode
        if self.mode == ReasoningMode.SEQUENTIAL:
            plan = self.planner.create_sequential_plan(goal, context_analysis)
        elif self.mode == ReasoningMode.PARALLEL:
            plan = self.planner.create_parallel_plan(goal, context_analysis)
        elif self.mode == ReasoningMode.HIERARCHICAL:
            plan = self.planner.create_hierarchical_plan(goal, context_analysis)
        elif self.mode == ReasoningMode.CREATIVE:
            plan = self.planner.create_creative_plan(goal, context_analysis)
        else:
            plan = self.planner.create_sequential_plan(goal, context_analysis)
        
        # Make decisions for each step
        decisions = []
        for step in plan.get("steps", []):
            decision = self.decision_maker.make_decision(
                step, context_analysis, plan
            )
            decisions.append(decision)
        
        return {
            "goal": goal,
            "context_analysis": context_analysis,
            "plan": plan,
            "decisions": decisions,
            "reasoning_mode": self.mode.value
        }
    
    def evaluate_plan(self, plan: Dict, context: Dict) -> Dict[str, Any]:
        """
        Evaluate a plan's feasibility and quality.
        
        Args:
            plan: Plan to evaluate
            context: Context for evaluation
            
        Returns:
            Evaluation results
        """
        evaluation = {
            "feasibility": 0.0,
            "quality": 0.0,
            "estimated_time": 0,
            "estimated_resources": [],
            "risks": [],
            "confidence": 0.0
        }
        
        # Check feasibility
        steps = plan.get("steps", [])
        if not steps:
            evaluation["feasibility"] = 0.0
            return evaluation
        
        # Evaluate each step
        total_feasibility = 0.0
        for step in steps:
            step_feasibility = self._evaluate_step_feasibility(step, context)
            total_feasibility += step_feasibility
            
        evaluation["feasibility"] = total_feasibility / len(steps)
        
        # Assess quality
        evaluation["quality"] = self._assess_plan_quality(plan, context)
        
        # Estimate time and resources
        evaluation["estimated_time"] = self._estimate_plan_time(plan)
        evaluation["estimated_resources"] = self._estimate_resources(plan)
        
        # Identify risks
        evaluation["risks"] = self._identify_risks(plan, context)
        
        # Overall confidence
        evaluation["confidence"] = (
            evaluation["feasibility"] * 0.4 + 
            evaluation["quality"] * 0.6
        )
        
        return evaluation
    
    def _evaluate_step_feasibility(self, step: Dict, context: Dict) -> float:
        """Evaluate the feasibility of a single step."""
        # Check if required resources are available
        required_resources = step.get("required_resources", [])
        available_resources = context.get("available_resources", [])
        
        resource_score = 1.0
        for resource in required_resources:
            if resource not in available_resources:
                resource_score *= 0.5
        
        # Check if dependencies are met
        dependencies = step.get("dependencies", [])
        dependency_score = 1.0 if not dependencies else 0.8
        
        # Base feasibility
        base_feasibility = step.get("feasibility", 0.8)
        
        return base_feasibility * resource_score * dependency_score
    
    def _assess_plan_quality(self, plan: Dict, context: Dict) -> float:
        """Assess the quality of a plan."""
        steps = plan.get("steps", [])
        
        if not steps:
            return 0.0
        
        # Check for logical flow
        flow_score = 0.8
        
        # Check for completeness
        goal = plan.get("goal", "")
        completeness_score = 0.7 if goal else 0.0
        
        # Check for efficiency
        efficiency_score = 0.8
        
        return (flow_score + completeness_score + efficiency_score) / 3
    
    def _estimate_plan_time(self, plan: Dict) -> int:
        """Estimate total time for plan execution."""
        steps = plan.get("steps", [])
        total_time = 0
        
        for step in steps:
            step_time = step.get("estimated_time", 1)
            total_time += step_time
            
        return total_time
    
    def _estimate_resources(self, plan: Dict) -> List[str]:
        """Estimate required resources for the plan."""
        resources = set()
        steps = plan.get("steps", [])
        
        for step in steps:
            step_resources = step.get("required_resources", [])
            resources.update(step_resources)
            
        return list(resources)
    
    def _identify_risks(self, plan: Dict, context: Dict) -> List[str]:
        """Identify potential risks in the plan."""
        risks = []
        steps = plan.get("steps", [])
        
        for step in steps:
            step_risks = step.get("risks", [])
            risks.extend(step_risks)
            
        # Add general risks
        if len(steps) > 10:
            risks.append("Plan complexity may lead to execution issues")
            
        if not plan.get("contingency_plan"):
            risks.append("No contingency plan identified")
            
        return risks
    
    def set_mode(self, mode: ReasoningMode) -> None:
        """
        Change the reasoning mode.
        
        Args:
            mode: New reasoning mode
        """
        self.mode = mode