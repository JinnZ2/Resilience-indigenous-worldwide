"""
variance_pathway_templates.py
=============================

One-page emergency-variance request drafts for each regulatory node
identified in institutional_bottleneck_audit.py.

Pre-drafted so the calendar gate does not slip on paperwork. Each
template is generic, machine-rendered from structured fields, and
intended for adaptation by a community legal partner — not for direct
filing without local counsel.

Each template records:
  - filing authority (where the variance is filed)
  - legal basis (the statutory hook for emergency action)
  - requested action (what specifically is asked for)
  - finding of fact (the physical record the request rests on)
  - calendar urgency (the planting-window deadline that drives speed)
  - duration (how long the variance runs)
  - safeguards (what the petitioner commits to in exchange)

License: CC0 — public domain
Dependencies: stdlib only
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


# ============================================================
# Template structure
# ============================================================

@dataclass
class VariancePathway:
    node_id:          str            # matches RegulatoryNode jurisdiction
    rule:             str
    authority:        str
    legal_basis:      str
    requested_action: str
    finding_of_fact:  str
    safeguards:       List[str]
    calendar_gate:    str
    duration:         str
    notes:            str = ""

    def render(self) -> str:
        sg = "\n".join(f"    - {s}" for s in self.safeguards)
        return f"""\
================================================================
EMERGENCY VARIANCE REQUEST — TEMPLATE
================================================================
Filed with:         {self.authority}
Re:                 {self.rule}
Jurisdiction:       {self.node_id}

LEGAL BASIS
----------------------------------------------------------------
{self.legal_basis}

REQUESTED ACTION
----------------------------------------------------------------
{self.requested_action}

FINDING OF FACT (the physical record this request rests on)
----------------------------------------------------------------
{self.finding_of_fact}

CALENDAR GATE
----------------------------------------------------------------
{self.calendar_gate}

DURATION
----------------------------------------------------------------
{self.duration}

SAFEGUARDS COMMITTED BY PETITIONER
----------------------------------------------------------------
{sg}

NOTES
----------------------------------------------------------------
{self.notes or '(none)'}
================================================================
"""


# ============================================================
# Templates — one per regulatory node
# ============================================================

EPA_503_VARIANCE = VariancePathway(
    node_id          = "United States (federal)",
    rule             = "40 CFR Part 503 — Standards for the Use or "
                       "Disposal of Sewage Sludge",
    authority        = "U.S. Environmental Protection Agency, "
                       "Office of Water; copy to Regional Administrator",
    legal_basis      = (
        "Clean Water Act § 405(d); EPA's authority to issue emergency "
        "variances or alternative standards under 40 CFR 503.5 where "
        "site-specific conditions render the generic Class A/B rule "
        "either over- or under-protective. APA § 553(b)(B) good-cause "
        "exception for emergency rulemaking where notice-and-comment is "
        "'impracticable, unnecessary, or contrary to the public "
        "interest.'"
    ),
    requested_action = (
        "Issue an emergency variance permitting source-separated "
        "humanure agricultural application at the household and small-"
        "farm scale, provided thermophilic-composting protocol (>=55 C "
        "for >=3 days, followed by >=6 months curing) is documented per "
        "the attached log template. Variance covers application to "
        "non-leafy field crops only; root and leaf crops excluded for "
        "the duration of the emergency."
    ),
    finding_of_fact  = (
        "Synthetic nitrogen supply through the Strait of Hormuz "
        "(~30% of global N trade) is materially disrupted. Domestic "
        "Haber-Bosch capacity cannot close the gap within one planting "
        "cycle. The CLOSED LOOP pathway — documented in soil science "
        "since King 1909 and validated by 80+ years of WHO/FAO "
        "literature — is the only physically available redundancy. "
        "See architecture/hormuz_cascade_audit.py for the mass-balance "
        "calculation."
    ),
    safeguards       = [
        "Mandatory thermophilic-phase logging (temperature and duration)",
        "6-month minimum curing before application",
        "No application within 100 ft of surface water",
        "No application to root or leaf crops during variance period",
        "Quarterly self-reporting to EPA Regional office",
        "Variance automatically sunsets when synthetic N trade recovers "
        "to >85% of pre-disruption baseline for two consecutive quarters",
    ],
    calendar_gate    = (
        "Composting cycle minimum 6 months. NH spring 2027 planting "
        "window requires variance issued and composting begun no later "
        "than Q2 2026. Each month of delay = ~50,000 lives at risk in "
        "downstream dependent populations (per institutional audit)."
    ),
    duration         = "24 months from issuance, with automatic recovery sunset.",
    notes            = (
        "EPA 503's facility-scale chain is physics-justified at scale; "
        "this variance does not vacate that. It opens a parallel small-"
        "scale pathway with protocol-equivalent pathogen kill."
    ),
)


EU_86_278_VARIANCE = VariancePathway(
    node_id          = "European Union",
    rule             = "Council Directive 86/278/EEC (Sewage Sludge Directive)",
    authority        = "European Commission, DG Environment; with "
                       "parallel filings to member-state competent "
                       "authorities under Article 13 derogation",
    legal_basis      = (
        "Article 13 of 86/278/EEC permits member-state derogations "
        "where local conditions warrant. TFEU Article 36 permits "
        "national measures justified on grounds of 'public security' "
        "or 'protection of health and life of humans' even where they "
        "would otherwise restrict free movement. Civil Protection "
        "Mechanism (Decision 1313/2013/EU) provides an emergency frame."
    ),
    requested_action = (
        "Issue Commission guidance recognizing source-separated "
        "humanure (distinct from industrial sewage sludge by absence "
        "of heavy-metal inputs) as a permissible nutrient pathway "
        "under member-state derogation, with member states retaining "
        "authority to set treatment-protocol minima."
    ),
    finding_of_fact  = (
        "86/278/EEC's heavy-metal limits are physics-justified for "
        "industrial sludge streams that mix human, industrial, and "
        "stormwater inputs. Source-separated humanure from non-"
        "industrial households does not carry the same metal load. "
        "The Directive does not currently distinguish these streams. "
        "EU N imports through Hormuz are materially disrupted; "
        "Russian N is sanction-bound; member-state food security "
        "requires the closed-loop pathway as documented redundancy."
    ),
    safeguards       = [
        "Source separation verified by household/parcel registration",
        "Heavy-metal testing on representative samples (annual)",
        "Maintain industrial-sludge limits unchanged for mixed streams",
        "Member states publish quarterly application volumes",
        "Sunset on declaration that fertilizer trade has recovered",
    ],
    calendar_gate    = (
        "EU-level derogation pathway is 24-36 months; national "
        "emergency variance under TFEU Article 36 can be invoked "
        "within weeks. Cereal planting in NH temperate Europe "
        "requires action by Q1 2026."
    ),
    duration         = "36 months, reviewable at 18 months.",
    notes            = (
        "Heavy-metal concerns are real for industrial sludge and not "
        "vacated by this variance. The distinction the Directive does "
        "not currently make is the one this variance asks to be made."
    ),
)


MN_7080_VARIANCE = VariancePathway(
    node_id          = "Minnesota (state)",
    rule             = "Minnesota Rules Chapter 7080 / 7083 — Subsurface "
                       "Sewage Treatment Systems",
    authority        = "Minnesota Pollution Control Agency (MPCA), "
                       "Commissioner; with copy to MN Department of "
                       "Health and county-level zoning authorities",
    legal_basis      = (
        "Minn. Stat. § 115.55 subd. 5a permits MPCA variances where "
        "the rule's purpose can be met by an alternative design. "
        "Minn. Stat. § 12.31 (emergency declaration) provides "
        "additional authority during declared emergencies."
    ),
    requested_action = (
        "Expand the existing variance pathway to permit dry-composting "
        "toilets paired with graywater-only septic systems on parcels "
        "where soil/site conditions support graywater dispersion. "
        "Standardize the variance application form so individual "
        "parcels do not require case-by-case engineering review."
    ),
    finding_of_fact  = (
        "Composting toilets are demonstrably safe under published "
        "WHO/EPA protocols and have been field-deployed for decades "
        "without measured public-health harm. MN Rule 7080/7083's "
        "current effective prohibition is not physics-justified at "
        "the household scale; it is administrative."
    ),
    safeguards       = [
        "Annual self-certification of composting protocol",
        "Graywater system meets Type IV standards for separate stream",
        "No application of finished compost off-parcel without "
        "secondary permit",
        "MPCA inspection on request (no fee)",
    ],
    calendar_gate    = (
        "Local pathway; lives-per-month figure is modest (~500 in MN-"
        "local signal) but the rule serves as a demonstration that "
        "the variance pathway exists and can be replicated by other "
        "states facing the same federal-state regulatory stack."
    ),
    duration         = "Indefinite; structural rather than emergency.",
)


INDIA_DIGNITY_VARIANCE = VariancePathway(
    node_id          = "India (national + state)",
    rule             = "Prohibition of Employment as Manual Scavengers "
                       "and their Rehabilitation Act, 2013",
    authority        = "Ministry of Social Justice and Empowerment "
                       "(central); state Social Welfare departments; "
                       "Ministry of Jal Shakti for sanitation overlap",
    legal_basis      = (
        "The 2013 Act prohibits manual handling of human excreta — "
        "specifically the caste-based degradation thereof. The Act "
        "does not prohibit sealed mechanical / sealed-composting "
        "systems that do not require manual handling. A clarifying "
        "rule or executive order can make this distinction explicit."
    ),
    requested_action = (
        "Issue a clarifying notification distinguishing (a) manual "
        "scavenging, which remains prohibited as a caste-based "
        "degradation, from (b) dignified, mechanized, sealed humanure "
        "composting that does not require human contact with raw "
        "excreta. Authorize community-scale sealed-composting facilities "
        "with mechanical handling and PPE-equipped staff hired and "
        "paid on the same scale as municipal sanitation engineers."
    ),
    finding_of_fact  = (
        "The 2013 Act was a remedy against caste degradation, not "
        "against the chemistry of nutrient cycling. Sealed mechanical "
        "composting removes the caste mechanism entirely. Pre-industrial "
        "Indian agriculture used humanure routinely; the present taboo "
        "is younger than synthetic fertilizer in most of the country. "
        "India is the single largest population dependent on imported "
        "N; per the institutional audit, each month of regulatory "
        "inaction = ~200,000 lives at risk."
    ),
    safeguards       = [
        "All facility staff paid on civil-engineering pay scale",
        "No manual handling at any point in the processing chain",
        "Mandatory PPE and engineering controls",
        "Dignity-of-labor framing in all public communications",
        "Caste-monitoring on hiring (Scheduled Caste protections "
        "preserved and strengthened, not bypassed)",
    ],
    calendar_gate    = (
        "Monsoon and rabi planting windows. Sealed-composting facility "
        "lead time is 3-6 months for fabrication and 6 months for "
        "first batch — meaning the regulatory clarification must "
        "precede facility procurement, not follow it."
    ),
    duration         = "Permanent rule clarification.",
    notes            = (
        "The 2013 Act is good law. The variance is not against it; "
        "it draws the line the Act itself implies between manual "
        "scavenging (prohibited) and mechanized closed-loop nutrient "
        "recovery (the Act is silent on)."
    ),
)


SSA_GUIDELINE_VARIANCE = VariancePathway(
    node_id          = "Sub-Saharan Africa (varied)",
    rule             = "WHO Guidelines on Sanitation and Health (2018), "
                       "as operationalized through donor sanitation "
                       "frameworks (JMP 'unimproved sanitation' "
                       "indicator)",
    authority        = "WHO HQ Geneva (guidance); national health "
                       "ministries; bilateral and multilateral donors "
                       "(World Bank WSP, USAID, EU DG INTPA)",
    legal_basis      = (
        "WHO Guidelines are guidance, not binding law. The 'unimproved' "
        "classification in JMP indicators is an interpretive choice, "
        "not a treaty obligation. Reclassification is achievable through "
        "a JMP technical update."
    ),
    requested_action = (
        "Issue a WHO technical brief distinguishing 'unimproved "
        "sanitation' (open defecation, uncovered pits with health "
        "risk) from 'closed-loop sanitation' (sealed composting and "
        "urine diversion meeting WHO 2-stage protocol). Reclassify "
        "closed-loop systems in the JMP indicator framework as "
        "'improved sanitation with nutrient recovery.' Update donor "
        "country guidance accordingly."
    ),
    finding_of_fact  = (
        "Current JMP framing penalizes countries that adopt humanure "
        "pathways even when those pathways meet WHO 2-stage pathogen-"
        "kill protocol. Donor financing follows JMP indicators. The "
        "net effect is to push the most vulnerable populations onto "
        "the most fragile (import-dependent) N supply chain. Per the "
        "institutional audit, sub-Saharan Africa carries the largest "
        "per-month mortality exposure of any region."
    ),
    safeguards       = [
        "WHO 2-stage protocol remains the floor for reclassification",
        "Quarterly JMP review of national submissions",
        "Donor frameworks retain authority to set country-level minima",
        "Reclassification triggers technical support, not penalty",
    ],
    calendar_gate    = (
        "JMP technical update cycle is 0-6 months for guideline "
        "reinterpretation. SSA planting calendars vary by climate "
        "band; equatorial windows are continuous, Sahel monsoon "
        "requires action by Q2 each year."
    ),
    duration         = "Permanent guideline update.",
)


CODEX_VARIANCE = VariancePathway(
    node_id          = "Codex Alimentarius / FAO international trade",
    rule             = "Codex Alimentarius food safety standards as "
                       "applied to fertilizer source in traded food",
    authority        = "FAO / WHO Codex Commission; Codex Committee on "
                       "Food Hygiene; WTO SPS Committee for trade "
                       "implications",
    legal_basis      = (
        "Codex standards are reference standards under the WTO SPS "
        "Agreement; departures require scientific justification. "
        "Codex Commission can issue clarifying guidance distinguishing "
        "PROCESS standards (how food is grown) from OUTCOME standards "
        "(what is measurably present in food)."
    ),
    requested_action = (
        "Issue Codex Commission guidance clarifying that fertilizer "
        "source is a process attribute, not a food-safety outcome "
        "attribute, and that food grown with WHO-protocol-compliant "
        "humanure meeting outcome standards (pathogen counts, heavy "
        "metal limits, mycotoxin limits) is in compliance with Codex "
        "standards and not subject to source-based trade restriction."
    ),
    finding_of_fact  = (
        "Current standards conflate process with outcome. Food grown "
        "with WHO-compliant humanure is, by every outcome measure "
        "Codex actually specifies, equivalent to food grown with "
        "synthetic N. The conflation creates a trade barrier without "
        "scientific basis under SPS Article 5."
    ),
    safeguards       = [
        "Outcome standards (pathogen, metals, mycotoxin) unchanged",
        "Process audit available on importer request",
        "Country-level certification of WHO-protocol compliance",
        "Quarterly Commission review of disputes",
    ],
    calendar_gate    = (
        "Codex guidance update is 3-6 months. International grain "
        "trade clears in months not years; the closed-loop pathway "
        "becomes commercially viable only when trade barrier is "
        "lifted."
    ),
    duration         = "Permanent clarification.",
)


# ============================================================
# Registry
# ============================================================

TEMPLATES: List[VariancePathway] = [
    EPA_503_VARIANCE,
    EU_86_278_VARIANCE,
    MN_7080_VARIANCE,
    INDIA_DIGNITY_VARIANCE,
    SSA_GUIDELINE_VARIANCE,
    CODEX_VARIANCE,
]


def render_all() -> str:
    return "\n\n".join(t.render() for t in TEMPLATES)


def render_one(node_id: str) -> str:
    for t in TEMPLATES:
        if t.node_id == node_id:
            return t.render()
    raise KeyError(f"No template for node_id: {node_id!r}. "
                   f"Available: {[t.node_id for t in TEMPLATES]}")


if __name__ == "__main__":
    print(render_all())
