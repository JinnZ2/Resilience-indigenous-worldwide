"""Detection templates for proactive threat identification.

Provides pre-built templates an AI can use to scan public filings,
news, and government records to flag threats to indigenous communities.

Quick start::

    from resilience.detectors import Scanner, ALL_TEMPLATES

    scanner = Scanner()
    scanner.add_templates(ALL_TEMPLATES)
    report = scanner.scan("text from a filing or news article...")
    print(report.summary())
"""

from __future__ import annotations

from typing import List

from resilience.detectors.templates import (
    DetectionResult,
    DetectionTemplate,
    LegalHook,
    Severity,
    Signal,
    ThreatType,
)
from resilience.detectors.signals import ScanReport, Scanner
from resilience.detectors.notices import Notice, NoticeGenerator, NoticeType
from resilience.risk_matrix import RiskCategory


# ---------------------------------------------------------------------------
# Pre-built detection templates
# ---------------------------------------------------------------------------

CONFLICT_OF_INTEREST = DetectionTemplate(
    threat_type=ThreatType.CONFLICT_OF_INTEREST,
    name="Conflict of Interest Detection",
    description=(
        "Government official with financial ties to companies benefiting "
        "from extraction decisions they influence."
    ),
    signals=[
        Signal(
            name="financial_tie",
            description="Official holds financial interest in affected company",
            source_types=["SEC filing", "financial disclosure", "lobbying record"],
            keywords=[
                "beneficial owner", "stock options", "financial interest",
                "equity stake", "board member", "advisory role",
                "consulting fee", "carried interest",
            ],
            weight=0.4,
        ),
        Signal(
            name="decision_authority",
            description="Official has authority over extraction-related decisions",
            source_types=["executive order", "appointment record", "agency action"],
            keywords=[
                "secretary", "administrator", "appointed", "authority",
                "executive order", "memorandum", "directive", "approval",
            ],
            weight=0.3,
        ),
        Signal(
            name="extraction_benefit",
            description="Decision directly benefits official's financial interests",
            source_types=["contract award", "permit", "EXIM loan"],
            keywords=[
                "mining rights", "extraction permit", "mineral lease",
                "rare earth", "critical minerals", "EXIM loan",
                "contract award", "concession",
            ],
            weight=0.3,
        ),
    ],
    legal_hooks=[
        LegalHook(
            statute="18 U.S.C. § 208",
            framework="Federal conflict of interest",
            description="Prohibits officials from participating in matters affecting their financial interests",
            jurisdiction="United States",
            action="Referral to Office of Government Ethics and Inspector General",
        ),
        LegalHook(
            statute="5 C.F.R. § 2635",
            framework="Standards of Ethical Conduct",
            description="Standards of ethical conduct for executive branch employees",
            jurisdiction="United States",
            action="File ethics complaint",
        ),
    ],
    red_flag_threshold=0.4,
    risk_categories=[RiskCategory.SEC_DISCLOSURE, RiskCategory.CRIMINAL_COMPLICITY],
)


CORPORATE_LEVERAGE = DetectionTemplate(
    threat_type=ThreatType.CORPORATE_LEVERAGE,
    name="Corporate Leverage Detection",
    description=(
        "Corporate investment used to justify military or political "
        "intervention in indigenous territory."
    ),
    signals=[
        Signal(
            name="government_backed_investment",
            description="Investment backed by government financing or guarantees",
            source_types=["EXIM record", "DFC filing", "bilateral agreement"],
            keywords=[
                "EXIM", "export-import bank", "DFC", "development finance",
                "government guarantee", "sovereign guarantee", "bilateral",
                "investment treaty", "trade agreement",
            ],
            weight=0.3,
        ),
        Signal(
            name="military_justification",
            description="Military or security language tied to commercial interests",
            source_types=["defense budget", "national security memo", "press briefing"],
            keywords=[
                "national security", "defense interest", "strategic asset",
                "military presence", "force protection", "security operation",
                "critical infrastructure", "strategic reserve",
            ],
            weight=0.35,
        ),
        Signal(
            name="contractual_dispute_escalation",
            description="Commercial dispute escalated to state-level confrontation",
            source_types=["arbitration filing", "diplomatic cable", "sanctions order"],
            keywords=[
                "arbitration", "expropriation", "breach of contract",
                "sanctions", "asset freeze", "diplomatic protest",
                "investment dispute", "ISDS",
            ],
            weight=0.35,
        ),
    ],
    legal_hooks=[
        LegalHook(
            statute="BIT/ISDS provisions",
            framework="International Investment Law",
            description="Bilateral investment treaty protections weaponized against sovereign decisions",
            jurisdiction="International",
            action="File counter-claim under UNDRIP and FPIC principles",
        ),
        LegalHook(
            statute="War Powers Resolution",
            framework="US Constitutional Law",
            description="Congressional oversight of military deployments",
            jurisdiction="United States",
            action="Congressional notification and War Powers challenge",
        ),
    ],
    red_flag_threshold=0.4,
    risk_categories=[
        RiskCategory.BIT_CHALLENGE,
        RiskCategory.SOVEREIGN_DEFAULT,
        RiskCategory.CRIMINAL_COMPLICITY,
    ],
)


FPIC_VIOLATION = DetectionTemplate(
    threat_type=ThreatType.FPIC_VIOLATION,
    name="FPIC Violation Detection",
    description=(
        "Extraction or development proceeding without Free, Prior "
        "and Informed Consent of affected indigenous communities."
    ),
    signals=[
        Signal(
            name="no_consultation",
            description="No evidence of community consultation in project records",
            source_types=["EIA report", "permit application", "project filing"],
            keywords=[
                "no consultation", "without consent", "bypassed",
                "waived", "expedited review", "emergency authorization",
                "fast-tracked", "streamlined approval",
            ],
            weight=0.35,
        ),
        Signal(
            name="community_opposition",
            description="Documented community opposition to the project",
            source_types=["community statement", "protest report", "petition"],
            keywords=[
                "protest", "opposition", "rejected", "objection",
                "petition", "referendum", "community statement",
                "indigenous leaders", "tribal council",
            ],
            weight=0.35,
        ),
        Signal(
            name="indigenous_territory",
            description="Project located on or affecting indigenous lands",
            source_types=["land registry", "treaty record", "territorial map"],
            keywords=[
                "indigenous land", "ancestral territory", "tribal land",
                "reservation", "traditional territory", "native title",
                "aboriginal land", "customary land",
            ],
            weight=0.3,
        ),
    ],
    legal_hooks=[
        LegalHook(
            statute="UNDRIP Articles 10, 19, 32",
            framework="UN Declaration on the Rights of Indigenous Peoples",
            description="Right to FPIC before relocation and before legislative/administrative measures",
            jurisdiction="International",
            action="File complaint with UN Permanent Forum on Indigenous Issues",
        ),
        LegalHook(
            statute="ILO Convention 169",
            framework="International Labour Organization",
            description="Obligation to consult indigenous peoples on decisions affecting them",
            jurisdiction="International",
            action="ILO supervisory body complaint",
        ),
        LegalHook(
            statute="EU CSDDD",
            framework="Corporate Sustainability Due Diligence Directive",
            description="Corporate obligation to identify and mitigate adverse human rights impacts",
            jurisdiction="European Union",
            action="File CSDDD non-compliance complaint in member state court",
        ),
    ],
    red_flag_threshold=0.35,
    risk_categories=[
        RiskCategory.FPIC_VIOLATION,
        RiskCategory.CSDDD_LIABILITY,
        RiskCategory.ESG_REPUTATIONAL,
    ],
)


DISCLOSURE_GAP = DetectionTemplate(
    threat_type=ThreatType.DISCLOSURE_GAP,
    name="Disclosure Gap Detection",
    description=(
        "Material risk missing from SEC or EU regulatory filings "
        "related to extraction operations on indigenous lands."
    ),
    signals=[
        Signal(
            name="missing_legal_proceedings",
            description="Active or threatened litigation not disclosed in filings",
            source_types=["10-K", "10-Q", "annual report"],
            keywords=[
                "no material litigation", "no pending proceedings",
                "not aware of any claims", "no contingent liabilities",
            ],
            weight=0.3,
        ),
        Signal(
            name="understated_risk_factors",
            description="Risk factor section omits known indigenous rights issues",
            source_types=["10-K", "prospectus", "ESG report"],
            keywords=[
                "risk factors", "forward-looking", "may be affected",
                "could impact", "subject to regulation",
            ],
            weight=0.25,
        ),
        Signal(
            name="known_controversy",
            description="Public controversy exists but is absent from disclosures",
            source_types=["news article", "NGO report", "UN communication"],
            keywords=[
                "controversy", "human rights", "environmental damage",
                "community displacement", "forced relocation",
                "water contamination", "deforestation",
            ],
            weight=0.25,
        ),
        Signal(
            name="esg_inconsistency",
            description="ESG claims contradicted by operational evidence",
            source_types=["sustainability report", "ESG rating", "audit report"],
            keywords=[
                "sustainability", "responsible mining", "community partnership",
                "stakeholder engagement", "ESG commitment", "net zero",
            ],
            weight=0.2,
        ),
    ],
    legal_hooks=[
        LegalHook(
            statute="SEC Regulation S-K Items 103, 105",
            framework="Securities regulation",
            description="Requires disclosure of material legal proceedings and risk factors",
            jurisdiction="United States",
            action="SEC enforcement complaint or shareholder derivative action",
        ),
        LegalHook(
            statute="Rule 10b-5",
            framework="Securities fraud",
            description="Prohibition on material misstatements and omissions",
            jurisdiction="United States",
            action="SEC enforcement referral",
        ),
    ],
    red_flag_threshold=0.4,
    risk_categories=[RiskCategory.SEC_DISCLOSURE, RiskCategory.ESG_REPUTATIONAL],
)


SOVEREIGNTY_THREAT = DetectionTemplate(
    threat_type=ThreatType.SOVEREIGNTY_THREAT,
    name="Sovereignty Threat Detection",
    description=(
        "Pattern of escalation toward territorial acquisition "
        "or annexation of indigenous and sovereign territories."
    ),
    signals=[
        Signal(
            name="diplomatic_pressure",
            description="Increasing diplomatic pressure on sovereign territory",
            source_types=["diplomatic cable", "press briefing", "UN communication"],
            keywords=[
                "acquisition", "purchase", "territorial", "annexation",
                "strategic interest", "sovereignty transfer",
                "security arrangement", "defense agreement",
            ],
            weight=0.3,
        ),
        Signal(
            name="military_positioning",
            description="Military assets positioned near or in sovereign territory",
            source_types=["defense report", "satellite imagery", "news report"],
            keywords=[
                "military base", "troop deployment", "naval presence",
                "air defense", "military exercise", "forward operating",
                "security forces", "coast guard",
            ],
            weight=0.3,
        ),
        Signal(
            name="economic_coercion",
            description="Economic measures used to pressure sovereignty decisions",
            source_types=["trade policy", "aid records", "sanctions order"],
            keywords=[
                "economic pressure", "trade restriction", "aid conditional",
                "sanctions threat", "tariff", "embargo", "blockade",
                "economic dependence",
            ],
            weight=0.2,
        ),
        Signal(
            name="population_opposition",
            description="Local population opposes territorial changes",
            source_types=["poll", "referendum", "community statement"],
            keywords=[
                "referendum", "oppose", "independence", "self-determination",
                "autonomy", "self-governance", "popular vote",
                "democratic mandate",
            ],
            weight=0.2,
        ),
    ],
    legal_hooks=[
        LegalHook(
            statute="UN Charter Article 2(4)",
            framework="International law",
            description="Prohibition on threat or use of force against territorial integrity",
            jurisdiction="International",
            action="UN Security Council referral",
        ),
        LegalHook(
            statute="ICCPR Article 1",
            framework="International Covenant on Civil and Political Rights",
            description="Right of peoples to self-determination",
            jurisdiction="International",
            action="UN Human Rights Committee communication",
        ),
        LegalHook(
            statute="ICJ Statute",
            framework="International Court of Justice",
            description="Judicial settlement of disputes between states",
            jurisdiction="International",
            action="ICJ advisory opinion or contentious case",
        ),
    ],
    red_flag_threshold=0.4,
    risk_categories=[
        RiskCategory.SOVEREIGN_DEFAULT,
        RiskCategory.CRIMINAL_COMPLICITY,
    ],
)


FIDUCIARY_BREACH = DetectionTemplate(
    threat_type=ThreatType.FIDUCIARY_BREACH,
    name="Fiduciary Breach Detection",
    description=(
        "Pension fund or institutional investor money flowing to "
        "high-risk extraction operations without adequate disclosure."
    ),
    signals=[
        Signal(
            name="pension_exposure",
            description="Pension fund invested in extraction company",
            source_types=["13F filing", "fund disclosure", "proxy statement"],
            keywords=[
                "pension fund", "retirement system", "endowment",
                "institutional investor", "CalPERS", "CalSTRS",
                "state retirement", "public employee",
            ],
            weight=0.3,
        ),
        Signal(
            name="esg_mandate_conflict",
            description="Fund has ESG mandates that conflict with holdings",
            source_types=["investment policy", "ESG report", "proxy voting record"],
            keywords=[
                "ESG mandate", "responsible investment", "PRI signatory",
                "sustainable investment", "exclusion list",
                "divestment policy", "climate commitment",
            ],
            weight=0.3,
        ),
        Signal(
            name="undisclosed_risk",
            description="Material extraction risks not communicated to beneficiaries",
            source_types=["beneficiary report", "annual statement", "board minutes"],
            keywords=[
                "beneficiary", "fiduciary duty", "prudent person",
                "duty of care", "duty of loyalty", "ERISA",
                "disclosure obligation", "material risk",
            ],
            weight=0.4,
        ),
    ],
    legal_hooks=[
        LegalHook(
            statute="ERISA Section 404(a)(1)(B)",
            framework="Employee Retirement Income Security Act",
            description="Prudent person standard for fiduciary conduct",
            jurisdiction="United States",
            action="ERISA fiduciary breach complaint to DOL",
        ),
        LegalHook(
            statute="State pension fiduciary statutes",
            framework="State law",
            description="State-level fiduciary obligations for public pension funds",
            jurisdiction="United States (state-level)",
            action="State attorney general complaint",
        ),
    ],
    red_flag_threshold=0.4,
    risk_categories=[
        RiskCategory.ESG_REPUTATIONAL,
        RiskCategory.SEC_DISCLOSURE,
        RiskCategory.CSDDD_LIABILITY,
    ],
)


# Convenience list of all pre-built templates
ALL_TEMPLATES: List[DetectionTemplate] = [
    CONFLICT_OF_INTEREST,
    CORPORATE_LEVERAGE,
    FPIC_VIOLATION,
    DISCLOSURE_GAP,
    SOVEREIGNTY_THREAT,
    FIDUCIARY_BREACH,
]
