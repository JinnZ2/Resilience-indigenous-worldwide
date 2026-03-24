"""Tests for the detection templates module."""

from resilience.detectors import (
    ALL_TEMPLATES,
    CONFLICT_OF_INTEREST,
    CORPORATE_LEVERAGE,
    DISCLOSURE_GAP,
    FIDUCIARY_BREACH,
    FPIC_VIOLATION,
    SOVEREIGNTY_THREAT,
    DetectionResult,
    DetectionTemplate,
    LegalHook,
    Notice,
    NoticeGenerator,
    NoticeType,
    Scanner,
    Severity,
    Signal,
    ThreatType,
)
from resilience.risk_matrix import RiskCategory


# ---------------------------------------------------------------------------
# Signal tests
# ---------------------------------------------------------------------------


def test_signal_matches_keywords():
    s = Signal(
        name="test",
        description="test signal",
        source_types=["test"],
        keywords=["mining", "extraction", "permit"],
        weight=0.6,
    )
    score = s.matches("The mining permit was granted for extraction.")
    assert score > 0
    assert score <= 0.6


def test_signal_no_match():
    s = Signal(
        name="test",
        description="test signal",
        source_types=["test"],
        keywords=["mining", "extraction"],
        weight=0.5,
    )
    assert s.matches("The weather is nice today.") == 0.0


def test_signal_case_insensitive():
    s = Signal(
        name="test",
        description="test signal",
        source_types=["test"],
        keywords=["Mining"],
        weight=1.0,
    )
    assert s.matches("mining operations") > 0


def test_signal_empty_keywords():
    s = Signal(
        name="test",
        description="test signal",
        source_types=["test"],
        keywords=[],
        weight=0.5,
    )
    assert s.matches("anything") == 0.0


def test_signal_full_match():
    s = Signal(
        name="test",
        description="test signal",
        source_types=["test"],
        keywords=["alpha", "beta"],
        weight=1.0,
    )
    assert abs(s.matches("alpha and beta") - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# DetectionTemplate tests
# ---------------------------------------------------------------------------


def _simple_template() -> DetectionTemplate:
    return DetectionTemplate(
        threat_type=ThreatType.FPIC_VIOLATION,
        name="Test Template",
        description="Test detection",
        signals=[
            Signal("s1", "desc", ["test"], ["indigenous", "land"], weight=0.5),
            Signal("s2", "desc", ["test"], ["protest", "opposition"], weight=0.5),
        ],
        legal_hooks=[
            LegalHook("TEST-001", "Test Framework", "Test description"),
        ],
        red_flag_threshold=0.4,
        risk_categories=[RiskCategory.FPIC_VIOLATION],
    )


def test_template_scan_triggers_alert():
    t = _simple_template()
    result = t.scan("The indigenous land protest drew opposition from leaders.")
    assert result.triggered
    assert result.severity in (Severity.HIGH, Severity.CRITICAL)
    assert len(result.applicable_hooks) > 0


def test_template_scan_no_alert():
    t = _simple_template()
    result = t.scan("The quarterly earnings report showed growth.")
    assert not result.triggered
    assert result.severity == Severity.LOW
    assert len(result.applicable_hooks) == 0


def test_template_severity_levels():
    assert DetectionTemplate._compute_severity(0.1) == Severity.LOW
    assert DetectionTemplate._compute_severity(0.3) == Severity.MEDIUM
    assert DetectionTemplate._compute_severity(0.6) == Severity.HIGH
    assert DetectionTemplate._compute_severity(0.8) == Severity.CRITICAL


def test_template_to_risk_factors():
    t = _simple_template()
    factors = t.to_risk_factors(likelihood=0.7, impact=0.8)
    assert len(factors) == 1
    assert factors[0].category == RiskCategory.FPIC_VIOLATION
    assert abs(factors[0].score - 0.56) < 1e-9


def test_detection_result_summary():
    t = _simple_template()
    result = t.scan("The indigenous land protest was significant.")
    text = result.summary()
    assert "Test Template" in text


# ---------------------------------------------------------------------------
# Scanner tests
# ---------------------------------------------------------------------------


def test_scanner_runs_all_templates():
    scanner = Scanner()
    scanner.add_templates(ALL_TEMPLATES)
    report = scanner.scan("A routine business filing with no relevant content.")
    assert len(report.results) == len(ALL_TEMPLATES)


def test_scanner_detects_conflict_of_interest():
    scanner = Scanner()
    scanner.add_template(CONFLICT_OF_INTEREST)
    text = (
        "The secretary appointed by executive order has a beneficial owner "
        "equity stake in a company that received a mining rights contract award "
        "for critical minerals extraction permit on rare earth concession."
    )
    report = scanner.scan(text)
    assert len(report.alerts) > 0
    assert report.alerts[0].threat_type == ThreatType.CONFLICT_OF_INTEREST


def test_scanner_detects_fpic_violation():
    scanner = Scanner()
    scanner.add_template(FPIC_VIOLATION)
    text = (
        "The project was fast-tracked without consent and bypassed consultation "
        "on indigenous land via an expedited review with emergency authorization. "
        "The tribal council filed an objection, a petition, and a community statement "
        "expressing opposition and protest. The ancestral territory and traditional "
        "territory native title claims were ignored in the streamlined approval."
    )
    report = scanner.scan(text)
    assert len(report.alerts) > 0
    assert report.alerts[0].threat_type == ThreatType.FPIC_VIOLATION


def test_scanner_detects_sovereignty_threat():
    scanner = Scanner()
    scanner.add_template(SOVEREIGNTY_THREAT)
    text = (
        "The acquisition of the territory is a strategic interest. "
        "Military base troop deployment and naval presence have increased. "
        "Economic pressure through tariff and trade restriction continues. "
        "A referendum shows the population opposes annexation and supports "
        "self-determination and autonomy."
    )
    report = scanner.scan(text)
    assert len(report.alerts) > 0
    assert report.alerts[0].threat_type == ThreatType.SOVEREIGNTY_THREAT


def test_scanner_to_risk_matrix():
    scanner = Scanner()
    scanner.add_template(FPIC_VIOLATION)
    text = (
        "Without consent the project bypassed indigenous land consultation. "
        "The tribal council protest and opposition petition were ignored. "
        "The ancestral territory traditional territory was fast-tracked."
    )
    matrix = scanner.to_risk_matrix(text)
    assert matrix.total_score() > 0


def test_scanner_scan_multiple():
    scanner = Scanner()
    scanner.add_template(FPIC_VIOLATION)
    reports = scanner.scan_multiple(["nothing here", "indigenous land protest opposition"])
    assert len(reports) == 2


def test_scan_report_highest_severity():
    scanner = Scanner()
    scanner.add_templates(ALL_TEMPLATES)
    text = (
        "The secretary has a beneficial owner equity stake and approved "
        "mining rights on indigenous land without consultation. "
        "The tribal council protest was ignored."
    )
    report = scanner.scan(text)
    severity = report.highest_severity
    assert severity in (Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL)


def test_scan_report_threats_by_type():
    scanner = Scanner()
    scanner.add_templates(ALL_TEMPLATES)
    text = (
        "Without consent the project bypassed indigenous land consultation. "
        "The beneficial owner secretary approved rare earth mining rights."
    )
    report = scanner.scan(text)
    by_type = report.threats_by_type()
    assert isinstance(by_type, dict)


def test_scan_report_summary():
    scanner = Scanner()
    scanner.add_templates(ALL_TEMPLATES)
    report = scanner.scan("Nothing relevant here.")
    text = report.summary()
    assert "Scan Report" in text


# ---------------------------------------------------------------------------
# NoticeGenerator tests
# ---------------------------------------------------------------------------


def test_notice_generator_clouded_title():
    gen = NoticeGenerator()
    t = _simple_template()
    result = t.scan("The indigenous land protest drew opposition.")
    notice = gen.generate(result, notice_type=NoticeType.CLOUDED_TITLE)
    assert notice.notice_type == NoticeType.CLOUDED_TITLE
    assert "CLOUDED TITLE" in notice.title


def test_notice_generator_fiduciary():
    gen = NoticeGenerator()
    t = DetectionTemplate(
        threat_type=ThreatType.FIDUCIARY_BREACH,
        name="Test Fiduciary",
        description="Test",
        signals=[Signal("s1", "d", ["t"], ["pension fund", "ERISA"], weight=1.0)],
        legal_hooks=[LegalHook("ERISA 404", "ERISA", "Prudent person")],
        red_flag_threshold=0.3,
    )
    result = t.scan("The pension fund has ERISA obligations.")
    notice = gen.generate(result)
    assert notice.notice_type == NoticeType.FIDUCIARY_LIABILITY
    assert "FIDUCIARY" in notice.title


def test_notice_generator_press_release():
    gen = NoticeGenerator()
    t = _simple_template()
    t.threat_type = ThreatType.SOVEREIGNTY_THREAT
    result = t.scan("The indigenous land protest drew opposition.")
    notice = gen.generate(result)
    assert notice.notice_type == NoticeType.PRESS_RELEASE
    assert "IMMEDIATE RELEASE" in notice.title


def test_notice_full_text():
    gen = NoticeGenerator()
    t = _simple_template()
    result = t.scan("The indigenous land protest drew opposition.")
    notice = gen.generate(
        result,
        target_entities=["Company X", "Agency Y"],
        notice_type=NoticeType.SHAREHOLDER_LETTER,
    )
    text = notice.full_text()
    assert "LEGAL BASIS" in text
    assert "Company X" in text


def test_notice_generator_batch():
    gen = NoticeGenerator()
    scanner = Scanner()
    scanner.add_template(FPIC_VIOLATION)
    scanner.add_template(CONFLICT_OF_INTEREST)
    text = (
        "Without consent the project bypassed indigenous land consultation "
        "via expedited review and emergency authorization with streamlined approval. "
        "The tribal council protest opposition petition community statement objection "
        "on ancestral territory traditional territory native title was ignored. "
        "The beneficial owner secretary appointed by executive order with authority "
        "approved mining rights contract award for rare earth critical minerals "
        "extraction permit and equity stake concession with financial interest."
    )
    report = scanner.scan(text)
    notices = gen.generate_batch(report.alerts)
    assert len(notices) > 0
    for notice in notices:
        assert isinstance(notice, Notice)


# ---------------------------------------------------------------------------
# Pre-built template sanity checks
# ---------------------------------------------------------------------------


def test_all_templates_have_signals():
    for t in ALL_TEMPLATES:
        assert len(t.signals) > 0, f"{t.name} has no signals"


def test_all_templates_have_legal_hooks():
    for t in ALL_TEMPLATES:
        assert len(t.legal_hooks) > 0, f"{t.name} has no legal hooks"


def test_all_templates_have_risk_categories():
    for t in ALL_TEMPLATES:
        assert len(t.risk_categories) > 0, f"{t.name} has no risk categories"


def test_all_templates_have_unique_names():
    names = [t.name for t in ALL_TEMPLATES]
    assert len(names) == len(set(names)), "Template names must be unique"


def test_all_threat_types_covered():
    covered = {t.threat_type for t in ALL_TEMPLATES}
    for tt in ThreatType:
        assert tt in covered, f"ThreatType.{tt.name} has no template"
