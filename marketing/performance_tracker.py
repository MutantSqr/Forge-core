"""
Performance Tracker - Track and analyze marketing performance metrics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


class MetricType(Enum):
    """Types of marketing metrics."""
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    ENGAGEMENT_RATE = "engagement_rate"
    RETURN_ON_AD_SPEND = "roas"
    COST_PER_ACQUISITION = "cpa"
    CUSTOMER_LIFETIME_VALUE = "clv"


class PerformanceTracker:
    """
    Tracker for monitoring and analyzing marketing performance metrics.
    """
    
    def __init__(self, memory_system, audit_system):
        """
        Initialize the performance tracker.
        
        Args:
            memory_system: Memory system instance
            audit_system: Audit system instance
        """
        self.memory = memory_system
        self.audit = audit_system
        self._performance_data: Dict[str, List[Dict[str, Any]]] = {}
        self._baseline_metrics: Dict[str, float] = {}
    
    def track_performance(self, campaign_id: str, metrics: List[str],
                        metric_values: Dict[str, float], 
                        timestamp: Optional[datetime] = None) -> bool:
        """
        Track performance metrics for a campaign.
        
        Args:
            campaign_id: Campaign ID
            metrics: List of metrics to track
            metric_values: Dictionary of metric values
            timestamp: Optional timestamp
            
        Returns:
            Success status
        """
        if campaign_id not in self._performance_data:
            self._performance_data[campaign_id] = []
        
        timestamp = timestamp or datetime.now()
        
        performance_entry = {
            "timestamp": timestamp.isoformat(),
            "metrics": metric_values,
            "tracked_metrics": metrics
        }
        
        self._performance_data[campaign_id].append(performance_entry)
        
        # Store in memory
        self.memory.store(
            key=f"performance_{campaign_id}_{timestamp.isoformat()}",
            value=performance_entry,
            memory_type="long_term"
        )
        
        # Log to audit if available
        if self.audit:
            self.audit.log_event(
                event_type="performance_tracking",
                source="PerformanceTracker",
                details={
                    "campaign_id": campaign_id,
                    "metrics": metrics,
                    "values": metric_values
                },
                severity="info"
            )
        
        return True
    
    def analyze_campaign(self, campaign_id: str, 
                       time_period: str = "30d") -> Dict[str, Any]:
        """
        Analyze campaign performance.
        
        Args:
            campaign_id: Campaign ID
            time_period: Time period for analysis
            
        Returns:
            Campaign analysis results
        """
        if campaign_id not in self._performance_data:
            return {"error": f"No performance data for campaign {campaign_id}"}
        
        # Filter data by time period
        days = int(time_period.replace("d", "")) if time_period.endswith("d") else 30
        threshold_date = datetime.now() - timedelta(days=days)
        
        campaign_data = [
            entry for entry in self._performance_data[campaign_id]
            if datetime.fromisoformat(entry["timestamp"]) >= threshold_date
        ]
        
        if not campaign_data:
            return {"error": f"No performance data for campaign {campaign_id} in time period {time_period}"}
        
        # Calculate metrics
        analysis = self._calculate_performance_metrics(campaign_data)
        
        # Compare with baseline
        comparison = self._compare_with_baseline(campaign_id, analysis)
        
        # Generate insights
        insights = self._generate_performance_insights(analysis, comparison)
        
        return {
            "campaign_id": campaign_id,
            "time_period": time_period,
            "analysis": analysis,
            "baseline_comparison": comparison,
            "insights": insights,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _calculate_performance_metrics(self, campaign_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics from campaign data."""
        if not campaign_data:
            return {}
        
        # Aggregate all metric values
        all_metrics = {}
        for entry in campaign_data:
            for metric, value in entry["metrics"].items():
                if metric not in all_metrics:
                    all_metrics[metric] = []
                all_metrics[metric].append(value)
        
        # Calculate statistics for each metric
        metrics_analysis = {}
        for metric, values in all_metrics.items():
            if values:
                metrics_analysis[metric] = {
                    "total": sum(values),
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1],
                    "trend": self._calculate_trend(values)
                }
        
        return metrics_analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple trend calculation
        recent_avg = sum(values[-5:]) / min(5, len(values))
        earlier_avg = sum(values[:-5]) / max(1, len(values) - 5)
        
        if recent_avg > earlier_avg * 1.05:
            return "increasing"
        elif recent_avg < earlier_avg * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def _compare_with_baseline(self, campaign_id: str, 
                             current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current metrics with baseline."""
        if campaign_id not in self._baseline_metrics:
            return {"message": "No baseline data available"}
        
        comparison = {}
        baseline = self._baseline_metrics[campaign_id]
        
        for metric, analysis in current_metrics.items():
            if metric in baseline:
                current_value = analysis["average"]
                baseline_value = baseline[metric]
                
                if baseline_value != 0:
                    variance = ((current_value - baseline_value) / baseline_value) * 100
                else:
                    variance = 0
                
                comparison[metric] = {
                    "baseline": baseline_value,
                    "current": current_value,
                    "variance_percent": variance,
                    "performance": "above_baseline" if variance > 0 else "below_baseline"
                }
        
        return comparison
    
    def _generate_performance_insights(self, analysis: Dict[str, Any],
                                     comparison: Dict[str, Any]) -> List[str]:
        """Generate performance insights."""
        insights = []
        
        # Analyze metric trends
        for metric, metric_data in analysis.items():
            trend = metric_data.get("trend", "unknown")
            
            if trend == "increasing":
                insights.append(f"{metric} is showing positive growth trend")
            elif trend == "decreasing":
                insights.append(f"{metric} is declining and may require attention")
            else:
                insights.append(f"{metric} is stable")
        
        # Analyze baseline comparison
        if comparison and comparison.get("message") != "No baseline data available":
            for metric, comp_data in comparison.items():
                if comp_data["variance_percent"] > 10:
                    insights.append(f"{metric} is performing {comp_data['variance_percent']:.1f}% above baseline")
                elif comp_data["variance_percent"] < -10:
                    insights.append(f"{metric} is performing {abs(comp_data['variance_percent']):.1f}% below baseline")
        
        return insights if insights else ["No significant insights available"]
    
    def set_baseline(self, campaign_id: str, baseline_metrics: Dict[str, float]) -> bool:
        """
        Set baseline metrics for a campaign.
        
        Args:
            campaign_id: Campaign ID
            baseline_metrics: Baseline metric values
            
        Returns:
            Success status
        """
        self._baseline_metrics[campaign_id] = baseline_metrics
        
        # Store in memory
        self.memory.store(
            key=f"baseline_{campaign_id}",
            value=baseline_metrics,
            memory_type="long_term"
        )
        
        return True
    
    def get_overall_metrics(self, time_period: str = "30d") -> Dict[str, Any]:
        """
        Get overall performance metrics across all campaigns.
        
        Args:
            time_period: Time period for metrics
            
        Returns:
            Overall performance metrics
        """
        # Aggregate data from all campaigns
        all_campaign_data = []
        
        days = int(time_period.replace("d", "")) if time_period.endswith("d") else 30
        threshold_date = datetime.now() - timedelta(days=days)
        
        for campaign_id, campaign_data in self._performance_data.items():
            filtered_data = [
                entry for entry in campaign_data
                if datetime.fromisoformat(entry["timestamp"]) >= threshold_date
            ]
            all_campaign_data.extend(filtered_data)
        
        if not all_campaign_data:
            return {"message": "No performance data available"}
        
        # Calculate overall metrics
        overall_analysis = self._calculate_performance_metrics(all_campaign_data)
        
        # Calculate campaign-level summary
        campaign_summary = {}
        for campaign_id in self._performance_data.keys():
            campaign_data = self._performance_data[campaign_id]
            filtered_data = [
                entry for entry in campaign_data
                if datetime.fromisoformat(entry["timestamp"]) >= threshold_date
            ]
            
            if filtered_data:
                campaign_summary[campaign_id] = self._calculate_performance_metrics(filtered_data)
        
        return {
            "time_period": time_period,
            "overall_metrics": overall_analysis,
            "campaign_summary": campaign_summary,
            "total_campaigns": len(self._performance_data),
            "total_data_points": len(all_campaign_data)
        }
    
    def get_metric_history(self, campaign_id: str, metric: str,
                         time_period: str = "30d") -> List[Dict[str, Any]]:
        """
        Get historical data for a specific metric.
        
        Args:
            campaign_id: Campaign ID
            metric: Metric name
            time_period: Time period for history
            
        Returns:
            Historical metric data
        """
        if campaign_id not in self._performance_data:
            return []
        
        days = int(time_period.replace("d", "")) if time_period.endswith("d") else 30
        threshold_date = datetime.now() - timedelta(days=days)
        
        metric_history = []
        
        for entry in self._performance_data[campaign_id]:
            if datetime.fromisoformat(entry["timestamp"]) >= threshold_date:
                if metric in entry["metrics"]:
                    metric_history.append({
                        "timestamp": entry["timestamp"],
                        "value": entry["metrics"][metric]
                    })
        
        return metric_history
    
    def compare_campaigns(self, campaign_ids: List[str], 
                         metric: str,
                         time_period: str = "30d") -> Dict[str, Any]:
        """
        Compare performance across multiple campaigns.
        
        Args:
            campaign_ids: List of campaign IDs to compare
            metric: Metric to compare
            time_period: Time period for comparison
            
        Returns:
            Campaign comparison results
        """
        comparison_data = {}
        
        for campaign_id in campaign_ids:
            metric_history = self.get_metric_history(campaign_id, metric, time_period)
            
            if metric_history:
                values = [entry["value"] for entry in metric_history]
                comparison_data[campaign_id] = {
                    "average": sum(values) / len(values),
                    "total": sum(values),
                    "min": min(values),
                    "max": max(values),
                    "data_points": len(values)
                }
        
        # Find best and worst performing campaigns
        if comparison_data:
            sorted_campaigns = sorted(
                comparison_data.items(),
                key=lambda x: x[1]["average"],
                reverse=True
            )
            
            best_campaign = sorted_campaigns[0]
            worst_campaign = sorted_campaigns[-1]
        else:
            best_campaign = None
            worst_campaign = None
        
        return {
            "metric": metric,
            "time_period": time_period,
            "campaign_data": comparison_data,
            "best_performing": best_campaign,
            "worst_performing": worst_campaign,
            "compared_at": datetime.now().isoformat()
        }
    
    def generate_performance_report(self, campaign_id: str,
                                  time_period: str = "30d") -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Args:
            campaign_id: Campaign ID
            time_period: Time period for report
            
        Returns:
            Performance report
        """
        # Get campaign analysis
        analysis = self.analyze_campaign(campaign_id, time_period)
        
        # Get metric history for key metrics
        key_metrics = ["impressions", "clicks", "conversions", "revenue"]
        metric_histories = {}
        
        for metric in key_metrics:
            metric_histories[metric] = self.get_metric_history(campaign_id, metric, time_period)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis)
        
        return {
            "campaign_id": campaign_id,
            "time_period": time_period,
            "analysis": analysis,
            "metric_histories": metric_histories,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        if "error" in analysis:
            return ["Unable to generate recommendations - insufficient data"]
        
        metrics_analysis = analysis.get("analysis", {})
        
        # Check for declining metrics
        for metric, metric_data in metrics_analysis.items():
            if metric_data.get("trend") == "decreasing":
                recommendations.append(f"Address declining {metric} - consider optimizing strategy")
        
        # Check for underperforming metrics
        baseline_comparison = analysis.get("baseline_comparison", {})
        if baseline_comparison and baseline_comparison.get("message") != "No baseline data available":
            for metric, comp_data in baseline_comparison.items():
                if comp_data.get("performance") == "below_baseline":
                    recommendations.append(f"{metric} is below baseline - investigate root causes")
        
        if not recommendations:
            recommendations.append("Campaign performance is stable - continue current strategy")
        
        return recommendations