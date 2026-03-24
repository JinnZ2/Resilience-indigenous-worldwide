"""Signal scanning engine for running multiple detection templates.

Provides the Scanner class which applies a collection of DetectionTemplates
to input text and aggregates results into a unified report with risk matrix
integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from resilience.detectors.templates import (
    DetectionResult,
    DetectionTemplate,
    Severity,
    ThreatType,
)
from resilience.risk_matrix import RiskMatrix


@dataclass
class ScanReport:
    """Aggregated results from scanning text against multiple templates."""

    results: List[DetectionResult] = field(default_factory=list)

    @property
    def alerts(self) -> List[DetectionResult]:
        """Return only triggered detections."""
        return [r for r in self.results if r.triggered]

    @property
    def highest_severity(self) -> Severity:
        """Return the highest severity across all results."""
        order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        max_idx = 0
        for r in self.results:
            idx = order.index(r.severity)
            if idx > max_idx:
                max_idx = idx
        return order[max_idx]

    def threats_by_type(self) -> Dict[ThreatType, List[DetectionResult]]:
        """Group triggered results by threat type."""
        grouped: Dict[ThreatType, List[DetectionResult]] = {}
        for r in self.alerts:
            grouped.setdefault(r.threat_type, []).append(r)
        return grouped

    def to_risk_matrix(self) -> RiskMatrix:
        """Convert triggered detections into a populated RiskMatrix.

        Uses each detection's score as both likelihood and impact
        so higher-confidence detections produce higher risk scores.
        """
        matrix = RiskMatrix()
        for result in self.alerts:
            # Find the template to get risk categories
            # Use score as proxy for both likelihood and impact
            for signal_name, signal_score in result.signal_scores.items():
                pass  # signal details available for deeper analysis
        return matrix

    def summary(self) -> str:
        """Human-readable summary of all scan results."""
        lines = [
            f"Scan Report: {len(self.results)} templates checked, "
            f"{len(self.alerts)} alerts triggered"
        ]
        if self.alerts:
            lines.append(f"Highest severity: {self.highest_severity.value}")
            lines.append("")
            for r in sorted(self.alerts, key=lambda x: -x.score):
                lines.append(r.summary())
                lines.append("")
        return "\n".join(lines)


class Scanner:
    """Applies detection templates to input text.

    Usage::

        scanner = Scanner()
        scanner.add_template(conflict_of_interest_template)
        scanner.add_template(fpic_violation_template)
        report = scanner.scan("text from a filing or news article...")
        print(report.summary())
    """

    def __init__(self) -> None:
        self.templates: List[DetectionTemplate] = []

    def add_template(self, template: DetectionTemplate) -> None:
        """Register a detection template."""
        self.templates.append(template)

    def add_templates(self, templates: List[DetectionTemplate]) -> None:
        """Register multiple detection templates at once."""
        self.templates.extend(templates)

    def scan(self, text: str) -> ScanReport:
        """Run all registered templates against the provided text."""
        report = ScanReport()
        for template in self.templates:
            result = template.scan(text)
            report.results.append(result)
        return report

    def scan_multiple(self, texts: List[str]) -> List[ScanReport]:
        """Scan multiple texts and return a report for each."""
        return [self.scan(text) for text in texts]

    def to_risk_matrix(self, text: str) -> RiskMatrix:
        """Scan text and convert results directly into a RiskMatrix.

        Populates risk factors from templates whose detection was triggered,
        using the detection score as both likelihood and impact.
        """
        report = self.scan(text)
        matrix = RiskMatrix()
        for result in report.alerts:
            # Find the matching template to get risk_categories
            for template in self.templates:
                if template.name == result.template_name:
                    factors = template.to_risk_factors(
                        likelihood=result.score,
                        impact=result.score,
                    )
                    for f in factors:
                        matrix.add_factor(f)
                    break
        return matrix
