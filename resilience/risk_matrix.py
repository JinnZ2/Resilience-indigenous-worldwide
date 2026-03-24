"""Legal and financial risk scoring for extraction operations.

Translates qualitative legal risks (SEC disclosure gaps, CSDDD liability,
FPIC violations, BIT challenges) into quantitative scores that can feed
into the stress propagation model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class RiskCategory(Enum):
    """Categories of legal/financial risk."""

    SEC_DISCLOSURE = "sec_disclosure"
    CSDDD_LIABILITY = "csddd_liability"
    FPIC_VIOLATION = "fpic_violation"
    BIT_CHALLENGE = "bit_challenge"
    ESG_REPUTATIONAL = "esg_reputational"
    SOVEREIGN_DEFAULT = "sovereign_default"
    CRIMINAL_COMPLICITY = "criminal_complicity"


@dataclass
class RiskFactor:
    """A single assessed risk factor."""

    category: RiskCategory
    description: str
    likelihood: float  # 0-1
    impact: float  # 0-1
    jurisdiction: str = ""
    mitigation: str = ""

    @property
    def score(self) -> float:
        """Composite risk score (likelihood * impact)."""
        return self.likelihood * self.impact


class RiskMatrix:
    """Aggregate risk factors and compute portfolio-level scores.

    Designed to model the 'Functional Risk Matrix for Investors'
    described in the project's legal strategy documents.
    """

    def __init__(self) -> None:
        self.factors: List[RiskFactor] = []

    def add_factor(self, factor: RiskFactor) -> None:
        self.factors.append(factor)

    def total_score(self) -> float:
        """Sum of all individual risk scores."""
        return sum(f.score for f in self.factors)

    def by_category(self) -> Dict[RiskCategory, float]:
        """Aggregate scores grouped by category."""
        scores: Dict[RiskCategory, float] = {}
        for f in self.factors:
            scores[f.category] = scores.get(f.category, 0.0) + f.score
        return scores

    def high_risks(self, threshold: float = 0.5) -> List[RiskFactor]:
        """Return factors whose score exceeds the threshold."""
        return [f for f in self.factors if f.score >= threshold]

    def to_stress_input(self) -> dict:
        """Convert risk scores into hidden-variable inputs for the stress model.

        Maps risk categories to the hidden variable dimensions used by
        StressPropagator:
          - hidden_climate  <- sovereign_default (systemic instability)
          - hidden_infra    <- sec_disclosure + bit_challenge
          - hidden_community <- fpic_violation + esg_reputational
          - hidden_human    <- criminal_complicity + csddd_liability
        """
        cats = self.by_category()

        hidden_climate = cats.get(RiskCategory.SOVEREIGN_DEFAULT, 0.0)
        hidden_infra = (
            cats.get(RiskCategory.SEC_DISCLOSURE, 0.0)
            + cats.get(RiskCategory.BIT_CHALLENGE, 0.0)
        )
        hidden_community = (
            cats.get(RiskCategory.FPIC_VIOLATION, 0.0)
            + cats.get(RiskCategory.ESG_REPUTATIONAL, 0.0)
        )
        hidden_human = (
            cats.get(RiskCategory.CRIMINAL_COMPLICITY, 0.0)
            + cats.get(RiskCategory.CSDDD_LIABILITY, 0.0)
        )

        return {
            "hidden_climate": min(hidden_climate, 1.0),
            "hidden_infra": min(hidden_infra, 1.0),
            "hidden_community": min(hidden_community, 1.0),
            "hidden_human": min(hidden_human, 1.0),
        }

    def summary(self) -> str:
        """Human-readable risk summary."""
        lines = [f"Risk Matrix ({len(self.factors)} factors, total={self.total_score():.2f})"]
        for cat, score in sorted(self.by_category().items(), key=lambda x: -x[1]):
            lines.append(f"  {cat.value:25s} {score:.2f}")
        high = self.high_risks()
        if high:
            lines.append(f"\n  HIGH RISK ({len(high)} factors >= 0.50):")
            for f in high:
                lines.append(f"    - {f.description} ({f.score:.2f})")
        return "\n".join(lines)
