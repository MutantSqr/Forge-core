"""
Audience Analyzer - AI-powered audience analysis and segmentation
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random


class AudienceAnalyzer:
    """
    AI-powered audience analyzer for marketing insights and segmentation.
    """
    
    def __init__(self, memory_system, reasoning_engine):
        """
        Initialize the audience analyzer.
        
        Args:
            memory_system: Memory system instance
            reasoning_engine: Reasoning engine instance
        """
        self.memory = memory_system
        self.reasoning = reasoning_engine
        self._audience_segments = {}
        self._analysis_history = []
    
    def analyze_audience(self, audience_data: Dict[str, Any], 
                       analysis_type: str = "demographic") -> Dict[str, Any]:
        """
        Analyze audience characteristics.
        
        Args:
            audience_data: Audience data to analyze
            analysis_type: Type of analysis (demographic, behavioral, psychographic)
            
        Returns:
            Audience analysis results
        """
        # Store analysis request
        analysis_id = f"audience_analysis_{datetime.now().isoformat()}"
        self.memory.store(
            key=analysis_id,
            value={
                "audience_data": audience_data,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            },
            memory_type="short_term"
        )
        
        # Perform analysis based on type
        if analysis_type == "demographic":
            results = self._analyze_demographics(audience_data)
        elif analysis_type == "behavioral":
            results = self._analyze_behavior(audience_data)
        elif analysis_type == "psychographic":
            results = self._analyze_psychographics(audience_data)
        else:
            results = self._analyze_general(audience_data)
        
        # Use reasoning engine for insights
        context = {
            "audience_data": audience_data,
            "analysis_results": results,
            "analysis_type": analysis_type
        }
        
        reasoning_result = self.reasoning.reason(
            goal="Generate audience insights and recommendations",
            context=context
        )
        
        # Combine results
        final_results = {
            "analysis_id": analysis_id,
            "analysis_type": analysis_type,
            "demographic_analysis": results if analysis_type == "demographic" else self._analyze_demographics(audience_data),
            "behavioral_analysis": results if analysis_type == "behavioral" else self._analyze_behavior(audience_data),
            "psychographic_analysis": results if analysis_type == "psychographic" else self._analyze_psychographics(audience_data),
            "insights": reasoning_result.get("decisions", []),
            "recommendations": reasoning_result.get("plan", {}).get("steps", []),
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Store analysis history
        self._analysis_history.append(final_results)
        
        return final_results
    
    def _analyze_demographics(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze demographic data."""
        demographics = audience_data.get("demographics", {})
        
        analysis = {
            "age_distribution": self._analyze_age_distribution(demographics.get("ages", [])),
            "gender_distribution": self._analyze_gender_distribution(demographics.get("genders", [])),
            "location_distribution": self._analyze_location_distribution(demographics.get("locations", [])),
            "income_levels": self._analyze_income_levels(demographics.get("income_levels", [])),
            "education_levels": self._analyze_education_levels(demographics.get("education_levels", []))
        }
        
        return analysis
    
    def _analyze_behavior(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behavioral data."""
        behavior = audience_data.get("behavior", {})
        
        analysis = {
            "purchase_patterns": self._analyze_purchase_patterns(behavior.get("purchases", [])),
            "engagement_frequency": self._analyze_engagement_frequency(behavior.get("engagement", [])),
            "channel_preferences": self._analyze_channel_preferences(behavior.get("channels", [])),
            "content_preferences": self._analyze_content_preferences(behavior.get("content", [])),
            "loyalty_segments": self._analyze_loyalty_segments(behavior.get("loyalty", []))
        }
        
        return analysis
    
    def _analyze_psychographics(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze psychographic data."""
        psychographics = audience_data.get("psychographics", {})
        
        analysis = {
            "interests": self._analyze_interests(psychographics.get("interests", [])),
            "values": self._analyze_values(psychographics.get("values", [])),
            "lifestyle": self._analyze_lifestyle(psychographics.get("lifestyle", [])),
            "personality_traits": self._analyze_personality(psychographics.get("personality", [])),
            "pain_points": self._analyze_pain_points(psychographics.get("pain_points", []))
        }
        
        return analysis
    
    def _analyze_general(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform general audience analysis."""
        return {
            "total_audience_size": audience_data.get("size", 0),
            "data_completeness": self._assess_data_completeness(audience_data),
            "key_segments": self._identify_key_segments(audience_data),
            "engagement_score": self._calculate_engagement_score(audience_data)
        }
    
    def _analyze_age_distribution(self, ages: List[int]) -> Dict[str, Any]:
        """Analyze age distribution."""
        if not ages:
            return {"message": "No age data available"}
        
        age_groups = {
            "18-24": 0, "25-34": 0, "35-44": 0, "45-54": 0, "55-64": 0, "65+": 0
        }
        
        for age in ages:
            if 18 <= age <= 24:
                age_groups["18-24"] += 1
            elif 25 <= age <= 34:
                age_groups["25-34"] += 1
            elif 35 <= age <= 44:
                age_groups["35-44"] += 1
            elif 45 <= age <= 54:
                age_groups["45-54"] += 1
            elif 55 <= age <= 64:
                age_groups["55-64"] += 1
            elif age >= 65:
                age_groups["65+"] += 1
        
        total = len(ages)
        age_percentages = {k: (v / total) * 100 for k, v in age_groups.items()}
        
        return {
            "distribution": age_groups,
            "percentages": age_percentages,
            "average_age": sum(ages) / total,
            "median_age": sorted(ages)[len(ages) // 2]
        }
    
    def _analyze_gender_distribution(self, genders: List[str]) -> Dict[str, Any]:
        """Analyze gender distribution."""
        if not genders:
            return {"message": "No gender data available"}
        
        gender_counts = {}
        for gender in genders:
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        total = len(genders)
        gender_percentages = {k: (v / total) * 100 for k, v in gender_counts.items()}
        
        return {
            "counts": gender_counts,
            "percentages": gender_percentages
        }
    
    def _analyze_location_distribution(self, locations: List[str]) -> Dict[str, Any]:
        """Analyze geographic distribution."""
        if not locations:
            return {"message": "No location data available"}
        
        location_counts = {}
        for location in locations:
            location_counts[location] = location_counts.get(location, 0) + 1
        
        # Sort by count
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "top_locations": sorted_locations[:10],
            "total_unique_locations": len(location_counts)
        }
    
    def _analyze_income_levels(self, income_levels: List[str]) -> Dict[str, Any]:
        """Analyze income level distribution."""
        if not income_levels:
            return {"message": "No income data available"}
        
        income_counts = {}
        for level in income_levels:
            income_counts[level] = income_counts.get(level, 0) + 1
        
        return {
            "distribution": income_counts,
            "dominant_segment": max(income_counts, key=income_counts.get)
        }
    
    def _analyze_education_levels(self, education_levels: List[str]) -> Dict[str, Any]:
        """Analyze education level distribution."""
        if not education_levels:
            return {"message": "No education data available"}
        
        education_counts = {}
        for level in education_levels:
            education_counts[level] = education_counts.get(level, 0) + 1
        
        return {
            "distribution": education_counts,
            "most_common": max(education_counts, key=education_counts.get)
        }
    
    def _analyze_purchase_patterns(self, purchases: List[Dict]) -> Dict[str, Any]:
        """Analyze purchase patterns."""
        if not purchases:
            return {"message": "No purchase data available"}
        
        # Calculate average purchase value
        total_value = sum(p.get("value", 0) for p in purchases)
        avg_value = total_value / len(purchases)
        
        # Analyze purchase frequency
        from datetime import datetime
        purchase_dates = [datetime.fromisoformat(p.get("date", datetime.now().isoformat())) for p in purchases]
        purchase_dates.sort()
        
        if len(purchase_dates) > 1:
            intervals = [(purchase_dates[i+1] - purchase_dates[i]).days for i in range(len(purchase_dates)-1)]
            avg_interval = sum(intervals) / len(intervals)
        else:
            avg_interval = 0
        
        return {
            "total_purchases": len(purchases),
            "average_value": avg_value,
            "average_purchase_interval_days": avg_interval,
            "total_value": total_value
        }
    
    def _analyze_engagement_frequency(self, engagement_data: List[Dict]) -> Dict[str, Any]:
        """Analyze engagement frequency."""
        if not engagement_data:
            return {"message": "No engagement data available"}
        
        # Calculate engagement metrics
        total_engagements = len(engagement_data)
        engagement_types = {}
        
        for engagement in engagement_data:
            eng_type = engagement.get("type", "unknown")
            engagement_types[eng_type] = engagement_types.get(eng_type, 0) + 1
        
        return {
            "total_engagements": total_engagements,
            "engagement_types": engagement_types,
            "most_common_type": max(engagement_types, key=engagement_types.get) if engagement_types else None
        }
    
    def _analyze_channel_preferences(self, channel_data: List[str]) -> Dict[str, Any]:
        """Analyze channel preferences."""
        if not channel_data:
            return {"message": "No channel data available"}
        
        channel_counts = {}
        for channel in channel_data:
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        sorted_channels = sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "preferences": channel_counts,
            "top_channels": sorted_channels[:5]
        }
    
    def _analyze_content_preferences(self, content_data: List[str]) -> Dict[str, Any]:
        """Analyze content preferences."""
        if not content_data:
            return {"message": "No content data available"}
        
        content_counts = {}
        for content in content_data:
            content_counts[content] = content_counts.get(content, 0) + 1
        
        return {
            "preferences": content_counts,
            "top_content": max(content_counts, key=content_counts.get) if content_counts else None
        }
    
    def _analyze_loyalty_segments(self, loyalty_data: List[Dict]) -> Dict[str, Any]:
        """Analyze customer loyalty segments."""
        if not loyalty_data:
            return {"message": "No loyalty data available"}
        
        segments = {"high": 0, "medium": 0, "low": 0}
        
        for customer in loyalty_data:
            score = customer.get("loyalty_score", 0)
            if score >= 80:
                segments["high"] += 1
            elif score >= 50:
                segments["medium"] += 1
            else:
                segments["low"] += 1
        
        return {
            "segments": segments,
            "high_value_customers": segments["high"],
            "medium_value_customers": segments["medium"],
            "low_value_customers": segments["low"]
        }
    
    def _analyze_interests(self, interests: List[str]) -> Dict[str, Any]:
        """Analyze audience interests."""
        if not interests:
            return {"message": "No interest data available"}
        
        interest_counts = {}
        for interest in interests:
            interest_counts[interest] = interest_counts.get(interest, 0) + 1
        
        sorted_interests = sorted(interest_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "top_interests": sorted_interests[:10],
            "total_unique_interests": len(interest_counts)
        }
    
    def _analyze_values(self, values: List[str]) -> Dict[str, Any]:
        """Analyze audience values."""
        if not values:
            return {"message": "No values data available"}
        
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        return {
            "value_distribution": value_counts,
            "core_values": max(value_counts, key=value_counts.get) if value_counts else None
        }
    
    def _analyze_lifestyle(self, lifestyle_data: List[str]) -> Dict[str, Any]:
        """Analyze lifestyle segments."""
        if not lifestyle_data:
            return {"message": "No lifestyle data available"}
        
        lifestyle_counts = {}
        for lifestyle in lifestyle_data:
            lifestyle_counts[lifestyle] = lifestyle_counts.get(lifestyle, 0) + 1
        
        return {
            "lifestyle_segments": lifestyle_counts,
            "dominant_lifestyle": max(lifestyle_counts, key=lifestyle_counts.get) if lifestyle_counts else None
        }
    
    def _analyze_personality(self, personality_data: List[str]) -> Dict[str, Any]:
        """Analyze personality traits."""
        if not personality_data:
            return {"message": "No personality data available"}
        
        trait_counts = {}
        for trait in personality_data:
            trait_counts[trait] = trait_counts.get(trait, 0) + 1
        
        return {
            "trait_distribution": trait_counts,
            "dominant_traits": sorted(trait_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _analyze_pain_points(self, pain_points: List[str]) -> Dict[str, Any]:
        """Analyze customer pain points."""
        if not pain_points:
            return {"message": "No pain point data available"}
        
        pain_point_counts = {}
        for pain_point in pain_points:
            pain_point_counts[pain_point] = pain_point_counts.get(pain_point, 0) + 1
        
        sorted_pain_points = sorted(pain_point_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "common_pain_points": sorted_pain_points[:10],
            "most_critical": sorted_pain_points[0] if sorted_pain_points else None
        }
    
    def _assess_data_completeness(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the completeness of audience data."""
        required_fields = ["demographics", "behavior", "psychographics"]
        present_fields = sum(1 for field in required_fields if field in audience_data)
        
        completeness_score = (present_fields / len(required_fields)) * 100
        
        return {
            "completeness_score": completeness_score,
            "present_fields": [field for field in required_fields if field in audience_data],
            "missing_fields": [field for field in required_fields if field not in audience_data]
        }
    
    def _identify_key_segments(self, audience_data: Dict[str, Any]) -> List[str]:
        """Identify key audience segments."""
        segments = []
        
        # Segment based on demographics
        demographics = audience_data.get("demographics", {})
        if demographics.get("ages"):
            segments.append("age_based")
        if demographics.get("locations"):
            segments.append("geographic")
        
        # Segment based on behavior
        behavior = audience_data.get("behavior", {})
        if behavior.get("purchases"):
            segments.append("purchase_behavior")
        if behavior.get("engagement"):
            segments.append("engagement_level")
        
        return segments if segments else ["general"]
    
    def _calculate_engagement_score(self, audience_data: Dict[str, Any]) -> float:
        """Calculate overall engagement score."""
        behavior = audience_data.get("behavior", {})
        engagement_data = behavior.get("engagement", [])
        
        if not engagement_data:
            return 0.0
        
        # Simple engagement score calculation
        total_engagements = len(engagement_data)
        max_expected = 100  # Normalize to 100
        
        score = min((total_engagements / max_expected) * 100, 100)
        
        return round(score, 2)
    
    def segment_audience(self, audience_data: Dict[str, Any], 
                       segmentation_criteria: List[str]) -> Dict[str, Any]:
        """
        Segment audience based on criteria.
        
        Args:
            audience_data: Audience data to segment
            segmentation_criteria: Criteria for segmentation
            
        Returns:
            Audience segments
        """
        segments = {}
        
        for criterion in segmentation_criteria:
            if criterion == "demographic":
                segments["demographic"] = self._analyze_demographics(audience_data.get("demographics", {}))
            elif criterion == "behavioral":
                segments["behavioral"] = self._analyze_behavior(audience_data.get("behavior", {}))
            elif criterion == "psychographic":
                segments["psychographic"] = self._analyze_psychographics(audience_data.get("psychographics", {}))
        
        return {
            "segmentation_id": f"segment_{datetime.now().isoformat()}",
            "criteria": segmentation_criteria,
            "segments": segments,
            "total_segments": len(segments)
        }
    
    def get_audience_insights(self, time_period: str = "30d") -> Dict[str, Any]:
        """
        Get audience insights for a time period.
        
        Args:
            time_period: Time period for insights
            
        Returns:
            Audience insights
        """
        # Filter analysis history by time period
        days = int(time_period.replace("d", "")) if time_period.endswith("d") else 30
        threshold_date = datetime.now() - timedelta(days=days)
        
        recent_analyses = [
            analysis for analysis in self._analysis_history
            if datetime.fromisoformat(analysis["analyzed_at"]) >= threshold_date
        ]
        
        if not recent_analyses:
            return {"message": "No recent audience analysis available"}
        
        # Aggregate insights
        total_analyses = len(recent_analyses)
        analysis_types = {}
        
        for analysis in recent_analyses:
            analysis_type = analysis["analysis_type"]
            analysis_types[analysis_type] = analysis_types.get(analysis_type, 0) + 1
        
        return {
            "time_period": time_period,
            "total_analyses": total_analyses,
            "analysis_types": analysis_types,
            "recent_analyses": recent_analyses[-10]
        }