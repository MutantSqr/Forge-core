"""
Context Analyzer - Analyze and understand context for reasoning
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class ContextType(Enum):
    """Types of context."""
    BUSINESS = "business"
    TECHNICAL = "technical"
    MARKETING = "marketing"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    GENERAL = "general"


@dataclass
class ContextAnalysis:
    """Result of context analysis."""
    context_type: ContextType
    key_entities: List[str]
    intent: str
    urgency: str
    complexity: str
    available_resources: List[str]
    constraints: List[str]
    confidence: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ContextAnalysis to dictionary for serialization.
        
        Returns:
            Dictionary representation of the context analysis
        """
        return {
            'context_type': self.context_type.value if isinstance(self.context_type, ContextType) else self.context_type,
            'key_entities': self.key_entities,
            'intent': self.intent,
            'urgency': self.urgency,
            'complexity': self.complexity,
            'available_resources': self.available_resources,
            'constraints': self.constraints,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


class ContextAnalyzer:
    """
    Context analyzer for understanding and processing context information.
    """
    
    def __init__(self):
        """Initialize the context analyzer."""
        self._entity_patterns = self._load_entity_patterns()
        self._intent_patterns = self._load_intent_patterns()
        
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for entity recognition."""
        return {
            "business": ["company", "revenue", "profit", "market", "customer", "client"],
            "technical": ["api", "database", "server", "code", "system", "architecture"],
            "marketing": ["campaign", "audience", "brand", "promotion", "content", "channel"],
            "financial": ["budget", "cost", "investment", "roi", "financial", "revenue"],
            "operational": ["process", "workflow", "efficiency", "productivity", "operations"]
        }
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for intent recognition."""
        return {
            "create": ["create", "build", "develop", "make", "generate"],
            "analyze": ["analyze", "examine", "study", "investigate", "review"],
            "optimize": ["optimize", "improve", "enhance", "increase", "boost"],
            "manage": ["manage", "handle", "oversee", "coordinate", "administer"],
            "report": ["report", "document", "summarize", "present", "communicate"]
        }
    
    def analyze(self, goal: str, context: Dict) -> ContextAnalysis:
        """
        Analyze the context for a given goal.
        
        Args:
            goal: The goal to analyze
            context: Additional context information
            
        Returns:
            Context analysis result
        """
        # Determine context type
        context_type = self._determine_context_type(goal, context)
        
        # Extract key entities
        key_entities = self._extract_entities(goal, context, context_type)
        
        # Determine intent
        intent = self._determine_intent(goal, context)
        
        # Assess urgency
        urgency = self._assess_urgency(goal, context)
        
        # Assess complexity
        complexity = self._assess_complexity(goal, context)
        
        # Identify available resources
        available_resources = context.get("available_resources", [])
        
        # Identify constraints
        constraints = self._identify_constraints(goal, context)
        
        # Calculate confidence
        confidence = self._calculate_confidence(goal, context)
        
        return ContextAnalysis(
            context_type=context_type,
            key_entities=key_entities,
            intent=intent,
            urgency=urgency,
            complexity=complexity,
            available_resources=available_resources,
            constraints=constraints,
            confidence=confidence,
            metadata={
                "goal": goal,
                "context_keys": list(context.keys()),
                "analysis_timestamp": self._get_timestamp()
            }
        )
    
    def _determine_context_type(self, goal: str, context: Dict) -> ContextType:
        """Determine the type of context."""
        goal_lower = goal.lower()
        context_str = str(context).lower()
        combined_text = f"{goal_lower} {context_str}"
        
        # Score each context type
        type_scores = {}
        for context_type, patterns in self._entity_patterns.items():
            score = sum(1 for pattern in patterns if pattern in combined_text)
            type_scores[context_type] = score
        
        # Find the highest scoring type
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return ContextType(best_type)
        
        return ContextType.GENERAL
    
    def _extract_entities(self, goal: str, context: Dict, context_type: ContextType) -> List[str]:
        """Extract key entities from the context."""
        entities = []
        
        # Extract from goal
        words = goal.split()
        entities.extend([word for word in words if len(word) > 3])
        
        # Extract from context based on type
        if context_type != ContextType.GENERAL:
            patterns = self._entity_patterns.get(context_type.value, [])
            context_str = str(context).lower()
            entities.extend([pattern for pattern in patterns if pattern in context_str])
        
        # Extract from context keys
        entities.extend([key for key in context.keys() if len(key) > 2])
        
        # Remove duplicates and limit
        entities = list(set(entities))
        return entities[:10]  # Limit to top 10 entities
    
    def _determine_intent(self, goal: str, context: Dict) -> str:
        """Determine the primary intent."""
        goal_lower = goal.lower()
        
        # Score each intent
        intent_scores = {}
        for intent, patterns in self._intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in goal_lower)
            intent_scores[intent] = score
        
        # Find the highest scoring intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            if intent_scores[best_intent] > 0:
                return best_intent
        
        return "general"
    
    def _assess_urgency(self, goal: str, context: Dict) -> str:
        """Assess the urgency level."""
        urgency_indicators = ["urgent", "asap", "immediately", "today", "now", "emergency"]
        goal_lower = goal.lower()
        
        if any(indicator in goal_lower for indicator in urgency_indicators):
            return "high"
        
        if context.get("deadline") or context.get("time_pressure") == "high":
            return "high"
        
        if context.get("time_pressure") == "medium":
            return "medium"
        
        return "low"
    
    def _assess_complexity(self, goal: str, context: Dict) -> str:
        """Assess the complexity level."""
        # Count entities and sub-goals
        entity_count = len(goal.split())
        context_size = len(str(context))
        
        if entity_count > 20 or context_size > 1000:
            return "high"
        elif entity_count > 10 or context_size > 500:
            return "medium"
        else:
            return "low"
    
    def _identify_constraints(self, goal: str, context: Dict) -> List[str]:
        """Identify constraints from the context."""
        constraints = []
        
        # Common constraint indicators
        constraint_patterns = ["budget", "deadline", "time", "resource", "limit", "restriction"]
        context_str = str(context).lower()
        
        for pattern in constraint_patterns:
            if pattern in context_str:
                constraints.append(pattern)
        
        # Check for specific constraint values
        if "budget" in context:
            constraints.append(f"budget_limit: {context['budget']}")
        if "deadline" in context:
            constraints.append(f"deadline: {context['deadline']}")
        
        return constraints
    
    def _calculate_confidence(self, goal: str, context: Dict) -> float:
        """Calculate confidence in the context analysis."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on context richness
        if len(context) > 5:
            confidence += 0.2
        if len(context) > 10:
            confidence += 0.1
        
        # Increase confidence based on goal clarity
        if len(goal.split()) > 3:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def compare_contexts(self, context1: Dict, context2: Dict) -> Dict[str, Any]:
        """
        Compare two contexts and identify differences.
        
        Args:
            context1: First context
            context2: Second context
            
        Returns:
            Comparison results
        """
        keys1 = set(context1.keys())
        keys2 = set(context2.keys())
        
        common_keys = keys1 & keys2
        unique_to_1 = keys1 - keys2
        unique_to_2 = keys2 - keys1
        
        differences = []
        for key in common_keys:
            if context1[key] != context2[key]:
                differences.append({
                    "key": key,
                    "value1": context1[key],
                    "value2": context2[key]
                })
        
        return {
            "common_keys": list(common_keys),
            "unique_to_context1": list(unique_to_1),
            "unique_to_context2": list(unique_to_2),
            "differences": differences,
            "similarity_score": len(common_keys) / max(len(keys1), len(keys2)) if keys1 or keys2 else 0
        }
    
    def enrich_context(self, context: Dict, additional_info: Dict) -> Dict:
        """
        Enrich the context with additional information.
        
        Args:
            context: Original context
            additional_info: Additional information to add
            
        Returns:
            Enriched context
        """
        enriched = context.copy()
        enriched.update(additional_info)
        enriched["enriched"] = True
        enriched["enrichment_timestamp"] = self._get_timestamp()
        
        return enriched