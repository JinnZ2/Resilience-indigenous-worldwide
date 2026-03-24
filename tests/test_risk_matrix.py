"""Tests for the risk matrix module."""

from resilience.risk_matrix import RiskCategory, RiskFactor, RiskMatrix


def test_risk_score_calculation():
    f = RiskFactor(
        category=RiskCategory.SEC_DISCLOSURE,
        description="Missing Item 103 disclosure",
        likelihood=0.8,
        impact=0.9,
    )
    assert abs(f.score - 0.72) < 1e-9


def test_matrix_total_score():
    m = RiskMatrix()
    m.add_factor(RiskFactor(RiskCategory.SEC_DISCLOSURE, "test", 0.5, 0.5))
    m.add_factor(RiskFactor(RiskCategory.FPIC_VIOLATION, "test", 0.4, 0.6))
    assert abs(m.total_score() - 0.49) < 1e-9


def test_high_risks_filter():
    m = RiskMatrix()
    m.add_factor(RiskFactor(RiskCategory.SEC_DISCLOSURE, "low", 0.1, 0.1))
    m.add_factor(RiskFactor(RiskCategory.CRIMINAL_COMPLICITY, "high", 0.9, 0.9))
    high = m.high_risks(threshold=0.5)
    assert len(high) == 1
    assert high[0].category == RiskCategory.CRIMINAL_COMPLICITY


def test_to_stress_input_capped():
    m = RiskMatrix()
    m.add_factor(RiskFactor(RiskCategory.SEC_DISCLOSURE, "a", 1.0, 1.0))
    m.add_factor(RiskFactor(RiskCategory.BIT_CHALLENGE, "b", 1.0, 1.0))
    result = m.to_stress_input()
    assert result["hidden_infra"] <= 1.0


def test_summary_output():
    m = RiskMatrix()
    m.add_factor(RiskFactor(RiskCategory.FPIC_VIOLATION, "No consent obtained", 0.9, 0.8))
    text = m.summary()
    assert "fpic_violation" in text
    assert "No consent obtained" in text
