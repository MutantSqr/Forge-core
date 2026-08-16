"""
Decision Maker - Intelligent decision making with context awareness
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass


class DecisionType(Enum):
    """Types of decisions."""
    BINARY = "binary"  # Yes/No decisions
    MULTIPLE_CHOICE = "multiple_choice"  # Choose from options
    RANKING = "ranking"  # Rank options
    RESOURCE_ALLOCATION = "resource_allocation"  # Allocate resources
    STRATEGIC = "strategic"  # High-level strategic decisions


@dataclass
class Decision:
    """A decision made by the decision maker."""
    decision_id: str
    decision_type: DecisionType
    context: Dict[str, Any]
    options: List[Any]
    selected_option: Any
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]


class DecisionMaker:
    """
    Decision maker for intelligent choices based on context and goals.
    """
    
    def __init__(self):
        """Initialize the decision maker."""
        self._decision_rules = self._load_decision_rules()
        self._decision_history: List[Decision] = []
        
        # Custom decision hooks
        self._decision_hooks: List[Callable] = []
    
    def _load_decision_rules(self) -> Dict[str, Callable]:
        """Load decision rules for common scenarios."""
        return {
            "resource_allocation": self._resource_allocation_rule,
            "risk_assessment": self._risk_assessment_rule,
            "priority_setting": self._priority_setting_rule,
            "channel_selection": self._channel_selection_rule
        }
    
    def add_decision_hook(self, hook: Callable) -> None:
        """
        Add a custom decision hook.
        
        Args:
            hook: Callable that takes decision context and returns modified decision
        """
        self._decision_hooks.append(hook)
    
    def make_decision(self, step: Dict, context: Dict, plan: Dict) -> Decision:
        """
        Make a decision for a given step.
        
        Args:
            step: The step requiring a decision
            context: Current context
            plan: Overall plan
            
        Returns:
            Decision object
        """
        decision_type = self._determine_decision_type(step, context)
        options = self._generate_options(step, context, plan)
        
        # Apply decision hooks
        modified_context = context.copy()
        for hook in self._decision_hooks:
            modified_context = hook(modified_context)
        
        # Make the decision based on type
        if decision_type == DecisionType.BINARY:
            selected_option, confidence, reasoning = self._make_binary_decision(
                options, modified_context, step
            )
        elif decision_type == DecisionType.MULTIPLE_CHOICE:
            selected_option, confidence, reasoning = self._make_multiple_choice_decision(
                options, modified_context, step
            )
        elif decision_type == DecisionType.RANKING:
            selected_option, confidence, reasoning = self._make_ranking_decision(
                options, modified_context, step
            )
        elif decision_type == DecisionType.RESOURCE_ALLOCATION:
            selected_option, confidence, reasoning = self._make_resource_allocation_decision(
                options, modified_context, step
            )
        else:
            selected_option, confidence, reasoning = self._make_strategic_decision(
                options, modified_context, step
            )
        
        decision = Decision(
            decision_id=f"decision_{len(self._decision_history)}",
            decision_type=decision_type,
            context=context,
            options=options,
            selected_option=selected_option,
            confidence=confidence,
            reasoning=reasoning,
            metadata={
                "step_id": step.get("id"),
                "timestamp": self._get_timestamp()
            }
        )
        
        self._decision_history.append(decision)
        return decision
    
    def _determine_decision_type(self, step: Dict, context: Dict) -> DecisionType:
        """Determine the type of decision needed."""
        step_desc = step.get("description", "").lower()
        
        if "allocate" in step_desc or "resource" in step_desc:
            return DecisionType.RESOURCE_ALLOCATION
        elif "select" in step_desc or "choose" in step_desc:
            return DecisionType.MULTIPLE_CHOICE
        elif "rank" in step_desc or "prioritize" in step_desc:
            return DecisionType.RANKING
        elif "approve" in step_desc or "confirm" in step_desc:
            return DecisionType.BINARY
        else:
            return DecisionType.STRATEGIC
    
    def _generate_options(self, step: Dict, context: Dict, plan: Dict) -> List[Any]:
        """Generate options for the decision."""
        # Check if step provides predefined options
        if "options" in step:
            return step["options"]
        
        # Generate options based on step type
        step_desc = step.get("description", "").lower()
        
        if "channel" in step_desc:
            return ["email", "social_media", "direct_mail", "paid_ads", "content_marketing"]
        elif "priority" in step_desc:
            return ["critical", "high", "medium", "low"]
        elif "approve" in step_desc:
            return [True, False]
        else:
            # Generate generic options
            return [
                f"option_a_{step.get('id', 'unknown')}",
                f"option_b_{step.get('id', 'unknown')}",
                f"option_c_{step.get('id', 'unknown')}"
            ]
    
    def _make_binary_decision(self, options: List[Any], context: Dict, step: Dict) -> tuple:
        """Make a binary (yes/no) decision."""
        # Simple heuristic based on context
        risk_tolerance = context.get("risk_tolerance", "medium")
        success_probability = self._estimate_success_probability(step, context)
        
        if risk_tolerance == "high":
            decision = options[0] if success_probability > 0.3 else options[1]
        elif risk_tolerance == "low":
            decision = options[0] if success_probability > 0.8 else options[1]
        else:
            decision = options[0] if success_probability > 0.5 else options[1]
        
        confidence = success_probability if decision == options[0] else (1 - success_probability)
        reasoning = f"Based on success probability {success_probability:.2f} and risk tolerance {risk_tolerance}"
        
        return decision, confidence, reasoning
    
    def _make_multiple_choice_decision(self, options: List[Any], context: Dict, step: Dict) -> tuple:
        """Make a multiple choice decision."""
        # Score each option
        scored_options = []
        for option in options:
            score = self._score_option(option, context, step)
            scored_options.append((option, score))
        
        # Select highest scored option
        scored_options.sort(key=lambda x: x[1], reverse=True)
        selected = scored_options[0][0]
        confidence = scored_options[0][1]
        reasoning = f"Selected option with highest score: {confidence:.2f}"
        
        return selected, confidence, reasoning
    
    def _make_ranking_decision(self, options: List[Any], context: Dict, step: Dict) -> tuple:
        """Make a ranking decision."""
        # Score and rank all options
        scored_options = []
        for option in options:
            score = self._score_option(option, context, step)
            scored_options.append((option, score))
        
        # Sort by score
        scored_options.sort(key=lambda x: x[1], reverse=True)
        ranked_options = [option for option, score in scored_options]
        
        # Return the top-ranked option
        selected = ranked_options[0]
        confidence = scored_options[0][1]
        reasoning = f"Top-ranked option out of {len(options)} options"
        
        return selected, confidence, reasoning
    
    def _make_resource_allocation_decision(self, options: List[Any], context: Dict, step: Dict) -> tuple:
        """Make a resource allocation decision."""
        available_resources = context.get("available_resources", {})
        
        # Allocate resources based on priority and availability
        allocation = {}
        for resource in options:
            if resource in available_resources:
                allocation[resource] = available_resources[resource]
            else:
                allocation[resource] = 0
        
        confidence = 0.8 if all(allocation.values()) else 0.5
        reasoning = f"Allocated resources based on availability: {allocation}"
        
        return allocation, confidence, reasoning
    
    def _make_strategic_decision(self, options: List[Any], context: Dict, step: Dict) -> tuple:
        """Make a strategic decision."""
        # Use multiple factors to evaluate options
        best_option = None
        best_score = 0
        
        for option in options:
            score = self._score_option(option, context, step)
            if score > best_score:
                best_score = score
                best_option = option
        
        confidence = best_score
        reasoning = f"Strategic decision based on multi-factor analysis"
        
        return best_option, confidence, reasoning
    
    def _score_option(self, option: Any, context: Dict, step: Dict) -> float:
        """Score an option based on context and step requirements."""
        score = 0.5  # Base score
        
        # Check if option aligns with context goals
        context_goals = context.get("goals", [])
        if any(goal in str(option).lower() for goal in context_goals):
            score += 0.2
        
        # Check resource requirements
        required_resources = step.get("required_resources", [])
        available_resources = context.get("available_resources", [])
        if all(resource in available_resources for resource in required_resources):
            score += 0.2
        
        # Check risk level
        risk_level = step.get("risk_level", "medium")
        if risk_level == "low":
            score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_success_probability(self, step: Dict, context: Dict) -> float:
        """Estimate the probability of success for a step."""
        base_probability = step.get("feasibility", 0.7)
        
        # Adjust based on context
        if context.get("resource_availability", "high") == "high":
            base_probability += 0.1
        
        if context.get("time_pressure", "normal") == "high":
            base_probability -= 0.1
        
        return min(max(base_probability, 0.0), 1.0)
    
    def _resource_allocation_rule(self, context: Dict) -> Dict:
        """Decision rule for resource allocation."""
        total_resources = context.get("total_resources", 100)
        priorities = context.get("priorities", {})
        
        allocation = {}
        for priority, weight in priorities.items():
            allocation[priority] = int(total_resources * weight)
        
        return {"allocation": allocation}
    
    def _risk_assessment_rule(self, context: Dict) -> Dict:
        """Decision rule for risk assessment."""
        risk_factors = context.get("risk_factors", [])
        risk_level = "low"
        
        if len(risk_factors) > 5:
            risk_level = "high"
        elif len(risk_factors) > 2:
            risk_level = "medium"
        
        return {"risk_level": risk_level, "mitigation_needed": risk_level != "low"}
    
    def _priority_setting_rule(self, context: Dict) -> Dict:
        """Decision rule for setting priorities."""
        tasks = context.get("tasks", [])
        deadlines = context.get("deadlines", {})
        
        prioritized_tasks = sorted(
            tasks,
            key=lambda task: deadlines.get(task, float('inf'))
        )
        
        return {"prioritized_tasks": prioritized_tasks}
    
    def _channel_selection_rule(self, context: Dict) -> Dict:
        """Decision rule for selecting communication channels."""
        target_audience = context.get("target_audience", "general")
        budget = context.get("budget", "medium")
        
        channel_recommendations = {
            "general": ["email", "social_media"],
            "business": ["email", "linkedin", "direct_mail"],
            "consumer": ["social_media", "paid_ads", "influencer"]
        }
        
        recommended = channel_recommendations.get(target_audience, ["email"])
        
        if budget == "low":
            recommended = [ch for ch in recommended if ch in ["email", "social_media"]]
        
        return {"recommended_channels": recommended}
    
    def get_decision_history(self) -> List[Decision]:
        """Get the history of decisions made."""
        return self._decision_history
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """Get statistics about decisions made."""
        if not self._decision_history:
            return {"total_decisions": 0}
        
        total = len(self._decision_history)
        avg_confidence = sum(d.confidence for d in self._decision_history) / total
        
        decision_types = {}
        for decision in self._decision_history:
            dtype = decision.decision_type.value
            decision_types[dtype] = decision_types.get(dtype, 0) + 1
        
        return {
            "total_decisions": total,
            "average_confidence": avg_confidence,
            "decision_types": decision_types
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()