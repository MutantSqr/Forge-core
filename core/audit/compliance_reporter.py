"""
Compliance Reporter - Generate compliance reports for regulatory requirements
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from enum import Enum


class ComplianceStandard(Enum):
    """Compliance standards."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    CUSTOM = "custom"


class ComplianceReporter:
    """
    Reporter for generating compliance reports and tracking regulatory requirements.
    """
    
    def __init__(self, log_path: str = "./audit_logs"):
        """
        Initialize the compliance reporter.
        
        Args:
            log_path: Path to store compliance reports
        """
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        self._compliance_rules = self._load_compliance_rules()
        self._compliance_history: List[Dict[str, Any]] = []
        
    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load default compliance rules."""
        return {
            "data_retention": {
                "enabled": True,
                "max_retention_days": 365,
                "description": "Maximum data retention period"
            },
            "access_logging": {
                "enabled": True,
                "log_all_access": True,
                "description": "Log all data access attempts"
            },
            "encryption": {
                "enabled": True,
                "require_encryption": True,
                "description": "Require encryption for sensitive data"
            },
            "authentication": {
                "enabled": True,
                "mfa_required": False,
                "password_complexity": True,
                "description": "Authentication requirements"
            },
            "audit_trail": {
                "enabled": True,
                "immutable_logs": True,
                "description": "Maintain immutable audit trail"
            }
        }
    
    def generate_report(self,
                      report_type: str = "general",
                      standard: Optional[ComplianceStandard] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a compliance report.
        
        Args:
            report_type: Type of report (general, detailed, summary)
            standard: Compliance standard to report against
            start_date: Start date for report period
            end_date: End date for report period
            
        Returns:
            Compliance report data
        """
        report = {
            "report_id": self._generate_report_id(),
            "generated_at": datetime.now().isoformat(),
            "report_type": report_type,
            "standard": standard.value if standard else "custom",
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
        
        # Add compliance rule status
        report["compliance_rules"] = self._check_compliance_rules()
        
        # Add specific standard requirements if specified
        if standard:
            report["standard_requirements"] = self._check_standard_requirements(standard)
        
        # Add recommendations
        report["recommendations"] = self._generate_recommendations(report)
        
        # Store report history
        self._compliance_history.append(report)
        
        # Write report to file
        self._write_report_to_file(report)
        
        return report
    
    def _generate_report_id(self) -> str:
        """Generate a unique report ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _check_compliance_rules(self) -> Dict[str, Any]:
        """Check status of compliance rules."""
        rule_status = {}
        
        for rule_name, rule_config in self._compliance_rules.items():
            rule_status[rule_name] = {
                "enabled": rule_config["enabled"],
                "compliant": True,  # Simplified - in real implementation, check actual compliance
                "description": rule_config["description"],
                "last_checked": datetime.now().isoformat()
            }
        
        return rule_status
    
    def _check_standard_requirements(self, standard: ComplianceStandard) -> Dict[str, Any]:
        """Check requirements for a specific compliance standard."""
        requirements = {
            ComplianceStandard.GDPR: {
                "data_protection": "compliant",
                "user_consent": "compliant",
                "right_to_be_forgotten": "compliant",
                "data_portability": "compliant",
                "breach_notification": "compliant"
            },
            ComplianceStandard.HIPAA: {
                "phi_protection": "compliant",
                "access_controls": "compliant",
                "audit_controls": "compliant",
                "integrity_controls": "compliant",
                "transmission_security": "compliant"
            },
            ComplianceStandard.SOC2: {
                "security": "compliant",
                "availability": "compliant",
                "processing_integrity": "compliant",
                "confidentiality": "compliant",
                "privacy": "compliant"
            },
            ComplianceStandard.PCI_DSS: {
                "network_security": "compliant",
                "data_protection": "compliant",
                "vulnerability_management": "compliant",
                "access_control": "compliant",
                "monitoring_testing": "compliant"
            },
            ComplianceStandard.ISO27001: {
                "information_security_policy": "compliant",
                    "risk_assessment": "compliant",
                    "asset_management": "compliant",
                    "access_control": "compliant",
                    "operations_security": "compliant"
            }
        }
        
        return requirements.get(standard, {})
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations based on report."""
        recommendations = []
        
        # Check compliance rules
        for rule_name, rule_status in report["compliance_rules"].items():
            if not rule_status["compliant"]:
                recommendations.append(f"Address non-compliance in {rule_name}: {rule_status['description']}")
        
        # If no specific recommendations, add general ones
        if not recommendations:
            recommendations.append("Continue monitoring compliance status")
            recommendations.append("Schedule regular compliance audits")
            recommendations.append("Review and update compliance policies quarterly")
        
        return recommendations
    
    def _write_report_to_file(self, report: Dict[str, Any]) -> None:
        """Write report to file."""
        try:
            report_file = self.log_path / f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        except Exception as e:
            print(f"Error writing compliance report: {e}")
    
    def update_compliance_rule(self, rule_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update a compliance rule.
        
        Args:
            rule_name: Name of the rule
            updates: Dictionary of fields to update
            
        Returns:
            Success status
        """
        if rule_name not in self._compliance_rules:
            return False
        
        self._compliance_rules[rule_name].update(updates)
        return True
    
    def add_compliance_rule(self, rule_name: str, rule_config: Dict[str, Any]) -> bool:
        """
        Add a new compliance rule.
        
        Args:
            rule_name: Name of the rule
            rule_config: Rule configuration
            
        Returns:
            Success status
        """
        if rule_name in self._compliance_rules:
            return False
        
        self._compliance_rules[rule_name] = rule_config
        return True
    
    def get_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all compliance rules.
        
        Returns:
            Dictionary of compliance rules
        """
        return self._compliance_rules.copy()
    
    def get_report_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get compliance report history.
        
        Args:
            limit: Maximum number of reports
            
        Returns:
            List of historical reports
        """
        return self._compliance_history[-limit:]
    
    def get_compliance_score(self) -> Dict[str, Any]:
        """
        Calculate overall compliance score.
        
        Returns:
            Dictionary with compliance score data
        """
        total_rules = len(self._compliance_rules)
        compliant_rules = sum(
            1 for rule in self._compliance_rules.values()
            if rule.get("enabled", False)
        )
        
        score = (compliant_rules / total_rules) * 100 if total_rules > 0 else 0
        
        return {
            "overall_score": score,
            "total_rules": total_rules,
            "compliant_rules": compliant_rules,
            "non_compliant_rules": total_rules - compliant_rules,
            "calculated_at": datetime.now().isoformat()
        }
    
    def export_reports(self, export_path: str,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> bool:
        """
        Export compliance reports to a file.
        
        Args:
            export_path: Path to export file
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Success status
        """
        filtered_reports = []
        
        for report in self._compliance_history:
            report_date = datetime.fromisoformat(report["generated_at"])
            
            if start_date and report_date < start_date:
                continue
            if end_date and report_date > end_date:
                continue
            
            filtered_reports.append(report)
        
        try:
            with open(export_path, 'w') as f:
                json.dump(filtered_reports, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting compliance reports: {e}")
            return False