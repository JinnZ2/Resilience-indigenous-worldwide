"""Detection templates for proactive identification of threats to indigenous communities.

Each template defines a structured pattern that an AI can use to scan
public filings, news, government actions, and corporate disclosures
to flag potential violations or escalation patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from resilience.risk_matrix import RiskCategory, RiskFactor, RiskMatrix


class ThreatType(Enum):
    """High-level threat classifications."""

    CONFLICT_OF_INTEREST = "conflict_of_interest"
    CORPORATE_LEVERAGE = "corporate_leverage"
    FPIC_VIOLATION = "fpic_violation"
    DISCLOSURE_GAP = "disclosure_gap"
    SOVEREIGNTY_THREAT = "sovereignty_threat"
    FIDUCIARY_BREACH = "fiduciary_breach"


class Severity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Signal:
    """A single observable indicator that contributes to threat detection.

    Attributes:
        name: Short identifier for the signal.
        description: What to look for in source material.
        source_types: Where this signal can be found (e.g. "SEC filing", "news").
        keywords: Terms that indicate this signal is present.
        weight: How strongly this signal contributes to detection (0-1).
    """

    name: str
    description: str
    source_types: List[str]
    keywords: List[str]
    weight: float = 0.5

    def matches(self, text: str) -> float:
        """Score how well a text matches this signal's keywords.

        Returns a score between 0 and 1 based on the fraction of
        keywords found in the text (case-insensitive).
        """
        if not self.keywords:
            return 0.0
        text_lower = text.lower()
        hits = sum(1 for kw in self.keywords if kw.lower() in text_lower)
        return (hits / len(self.keywords)) * self.weight


@dataclass
class LegalHook:
    """A legal statute or framework triggered by a detection.

    Attributes:
        statute: Citation (e.g. "18 U.S.C. § 208").
        framework: Broader legal framework (e.g. "UNDRIP").
        description: What the statute requires or prohibits.
        jurisdiction: Applicable jurisdiction.
        action: Recommended legal action when triggered.
    """

    statute: str
    framework: str
    description: str
    jurisdiction: str = ""
    action: str = ""


@dataclass
class DetectionTemplate:
    """A reusable pattern for detecting threats to indigenous communities.

    Templates combine multiple signals with red-flag thresholds and
    legal hooks to produce actionable alerts.

    Attributes:
        threat_type: The category of threat this template detects.
        name: Human-readable template name.
        description: What this template is designed to catch.
        signals: Observable indicators to scan for.
        legal_hooks: Statutes and frameworks triggered on detection.
        red_flag_threshold: Minimum combined signal score to trigger alert.
        risk_categories: Which RiskCategory values this maps to.
    """

    threat_type: ThreatType
    name: str
    description: str
    signals: List[Signal] = field(default_factory=list)
    legal_hooks: List[LegalHook] = field(default_factory=list)
    red_flag_threshold: float = 0.5
    risk_categories: List[RiskCategory] = field(default_factory=list)

    def scan(self, text: str) -> DetectionResult:
        """Scan text against all signals and produce a detection result."""
        signal_scores: Dict[str, float] = {}
        for signal in self.signals:
            score = signal.matches(text)
            if score > 0:
                signal_scores[signal.name] = score

        total_score = sum(signal_scores.values())
        max_possible = sum(s.weight for s in self.signals) if self.signals else 1.0
        normalized = min(total_score / max_possible, 1.0) if max_possible > 0 else 0.0

        triggered = normalized >= self.red_flag_threshold
        severity = self._compute_severity(normalized)
        triggered_hooks = self.legal_hooks if triggered else []

        return DetectionResult(
            template_name=self.name,
            threat_type=self.threat_type,
            score=normalized,
            severity=severity,
            triggered=triggered,
            signal_scores=signal_scores,
            applicable_hooks=triggered_hooks,
        )

    def to_risk_factors(
        self, likelihood: float, impact: float
    ) -> List[RiskFactor]:
        """Convert this template into RiskFactor instances for the RiskMatrix."""
        return [
            RiskFactor(
                category=cat,
                description=f"{self.name}: {self.description}",
                likelihood=likelihood,
                impact=impact,
            )
            for cat in self.risk_categories
        ]

    @staticmethod
    def _compute_severity(score: float) -> Severity:
        if score >= 0.75:
            return Severity.CRITICAL
        if score >= 0.5:
            return Severity.HIGH
        if score >= 0.25:
            return Severity.MEDIUM
        return Severity.LOW


@dataclass
class DetectionResult:
    """Output of scanning text against a DetectionTemplate."""

    template_name: str
    threat_type: ThreatType
    score: float
    severity: Severity
    triggered: bool
    signal_scores: Dict[str, float]
    applicable_hooks: List[LegalHook]

    def summary(self) -> str:
        """Human-readable summary of the detection result."""
        status = "ALERT" if self.triggered else "OK"
        lines = [
            f"[{status}] {self.template_name} "
            f"(score={self.score:.2f}, severity={self.severity.value})",
        ]
        if self.signal_scores:
            lines.append("  Signals matched:")
            for name, score in sorted(
                self.signal_scores.items(), key=lambda x: -x[1]
            ):
                lines.append(f"    - {name}: {score:.2f}")
        if self.applicable_hooks:
            lines.append("  Legal hooks triggered:")
            for hook in self.applicable_hooks:
                lines.append(f"    - {hook.statute} ({hook.framework})")
        return "\n".join(lines)
