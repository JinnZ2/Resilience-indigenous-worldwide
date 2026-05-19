"""
constraint_removal_solutions.py
================================
CC0. stdlib only. Falsifiable.

Documents the constraint-removal geometry: when REMOVING an external
constraint solves a problem better than ADDING new structure or capital.

The dominant institutional reflex is to respond to crisis by adding:
    add regulation, add investment, add programs, add oversight.

Empirical pattern across multiple domains: the failure mode is often
the imposed external constraint itself. Removing it releases adaptive
capacity that already exists in the substrate.

Falsifiable claim: regions/systems that respond to crisis by removing
external constraints recover faster and develop more resilient
distributed capacity than regions that respond by adding centralized
solutions.

Author: Kavik (JinnZ2)
License: CC0
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------
# CORE DATA STRUCTURES
# ---------------------------------------------------------------------

@dataclass
class Constraint:
    """A single external constraint imposed on a system."""
    name: str
    source: str                          # who imposed it (IMF, federal, zoning board, etc.)
    stated_purpose: str                  # what it claimed to achieve
    actual_effect: str                   # what it actually does to local adaptive capacity
    removable: bool                      # can it be removed without immediate collapse
    removal_path: Optional[str] = None   # how removal could happen


@dataclass
class AdaptiveCapacity:
    """Local capability that exists when not blocked by external constraint."""
    name: str
    embedded_in: str                     # where this capacity lives (people, geography, networks)
    blocked_by: list                     # constraints currently preventing its operation
    activation_speed: str                # how fast it scales when unblocked
    historical_evidence: list            # documented cases of this capacity operating


@dataclass
class CaseStudy:
    """A documented case of constraint removal (or failure to remove)."""
    location: str
    crisis_type: str
    constraints_imposed: list
    adaptive_capacity_blocked: list
    response_chosen: str                 # "add" or "remove" or "mixed"
    outcome: str
    timeline: str
    citations: list = field(default_factory=list)


# ---------------------------------------------------------------------
# DIAGNOSTIC: when is constraint-removal the right move?
# ---------------------------------------------------------------------

def diagnose_constraint_pattern(system_state: dict) -> dict:
    """
    Diagnoses whether a system needs constraint removal vs constraint addition.

    Returns a dict of indicators. The more indicators that fire, the stronger
    the case that the problem is the imposed constraint itself.
    """
    indicators = {
        "external_constraint_present":
            system_state.get("imposed_from_outside", False),
        "local_adaptive_capacity_exists":
            system_state.get("indigenous_knowledge_present", False),
        "constraint_destroys_capacity":
            system_state.get("regulations_block_local_solutions", False),
        "crisis_accelerating":
            system_state.get("cascade_in_progress", False),
        "centralization_at_failure_point":
            system_state.get("single_point_of_failure_visible", False),
        "elder_knowledge_still_living":
            system_state.get("generational_transmission_intact", False),
        "geographic_or_cultural_diversity":
            system_state.get("distributed_substrate_present", False),
    }
    indicators["remove_constraint_score"] = sum(1 for v in indicators.values() if v)
    indicators["max_score"] = len(indicators) - 1
    return indicators


# ---------------------------------------------------------------------
# CASE STUDIES (documented; falsifiable against historical record)
# ---------------------------------------------------------------------

BOLIVIA_FUEL_CRISIS = CaseStudy(
    location="Bolivia",
    crisis_type="fuel shortage triggering economic collapse",
    constraints_imposed=[
        "centralized fuel subsidy system requiring foreign currency",
        "export-focused economy requiring foreign exchange",
        "national currency requirement for all formal trade",
        "regulations against local energy production",
    ],
    adaptive_capacity_blocked=[
        "distributed energy generation (gravity batteries at altitude)",
        "micro-hydro in valleys",
        "regional barter networks",
        "indigenous water management knowledge",
        "local lithium processing for local battery production",
    ],
    response_chosen="add (more loans, more austerity, more central control)",
    outcome="cascade accelerating; unrest visible May 2026",
    timeline="2024-2026 crisis acceleration",
    citations=[
        "IMF Bolivia Country Reports 2024-2025",
        "Reuters Bolivia fuel crisis coverage May 2026",
    ],
)

KENYA_IMF_CONSTRAINT = CaseStudy(
    location="Kenya",
    crisis_type="inflation, food crisis, youth protests",
    constraints_imposed=[
        "IMF structural adjustment debt servicing requirements",
        "centralized currency requirement for trade",
        "export-focused agriculture (cash crops over food security)",
        "restrictions on pastoral movement patterns",
    ],
    adaptive_capacity_blocked=[
        "regional food production matched to terrain",
        "pastoral adaptation across arid zones",
        "local trade networks (susu, chama systems)",
        "traditional dispute resolution",
    ],
    response_chosen="add (more loans, tax increases, austerity)",
    outcome="Gen Z protests; government legitimacy collapsing 2024-2026",
    timeline="2023-2026 cascade",
    citations=[
        "Kenya Gen Z protest coverage 2024-2026",
        "World Bank Kenya economic updates",
        "IMF Kenya Article IV consultations",
    ],
)

ARGENTINA_2001_COLLAPSE = CaseStudy(
    location="Argentina",
    crisis_type="economic collapse, currency failure",
    constraints_imposed=[
        "peso-dollar peg",
        "IMF austerity requirements",
        "ban on alternative currencies",
    ],
    adaptive_capacity_blocked=[
        "barter networks (clubes de trueque) existed but suppressed",
    ],
    response_chosen="mixed (formal collapse forced removal of constraint)",
    outcome="barter clubs scaled to ~6 million participants within months; provided survival capacity during peak crisis",
    timeline="2001-2003 peak; declined as formal economy recovered",
    citations=[
        "Norman & Russell (2005) Argentine Trueque Networks",
        "North (2007) Money and Liberation: The Micropolitics of Alternative Currency Movements",
    ],
)

GREEK_CRISIS_BARTER = CaseStudy(
    location="Greece (Volos and other regions)",
    crisis_type="sovereign debt crisis, austerity",
    constraints_imposed=[
        "euro requirement for all formal trade",
        "EU/IMF austerity measures",
    ],
    adaptive_capacity_blocked=[
        "regional barter and time-banking",
    ],
    response_chosen="mixed (informal networks scaled despite formal constraints)",
    outcome="TEM (Local Alternative Unit) and similar networks emerged in dozens of cities; demonstrated rapid scaling from existing trust networks",
    timeline="2010-2018 active growth phase",
    citations=[
        "Sotiropoulou (2011) Alternative Exchange Systems in Contemporary Greece",
    ],
)

CASE_STUDIES = [
    BOLIVIA_FUEL_CRISIS,
    KENYA_IMF_CONSTRAINT,
    ARGENTINA_2001_COLLAPSE,
    GREEK_CRISIS_BARTER,
]


# ---------------------------------------------------------------------
# REMOVAL PATHS (ordered by implementation speed)
# ---------------------------------------------------------------------

REMOVAL_PATHS = {
    "non_enforcement": {
        "description": "government stops enforcing the constraint without changing law",
        "speed": "immediate (days)",
        "cost": "near zero",
        "political_difficulty": "low (no legislation required)",
        "example": "stopping arrests for barter trade",
        "risk": "constraint can be re-enforced later",
    },
    "municipal_authorization": {
        "description": "local government formally permits constrained activity",
        "speed": "weeks",
        "cost": "low (administrative)",
        "political_difficulty": "moderate (local political capital)",
        "example": "designating weekly regional trade fair days",
        "risk": "limited geographic scope",
    },
    "emergency_declaration": {
        "description": "executive emergency powers suspend the constraint temporarily",
        "speed": "days to weeks",
        "cost": "low",
        "political_difficulty": "moderate (requires crisis framing)",
        "example": "COVID-era suspensions of trade regulations",
        "risk": "ends when emergency ends",
    },
    "legislative_change": {
        "description": "formal law changed through legislative process",
        "speed": "months to years",
        "cost": "high (political capital, legislative time)",
        "political_difficulty": "high (full political fight)",
        "example": "repeal of zoning code",
        "risk": "slow; may not arrive before cascade completes",
    },
    "constitutional_change": {
        "description": "constitutional amendment removing constraint",
        "speed": "years",
        "cost": "very high",
        "political_difficulty": "very high",
        "example": "decentralization amendment",
        "risk": "too slow for active crises",
    },
}


# ---------------------------------------------------------------------
# CONSTRAINT-REMOVAL HEURISTIC
# ---------------------------------------------------------------------

def recommend_removal_path(case: CaseStudy, urgency: str = "high") -> list:
    """
    Recommends ordered removal paths given a case study and urgency level.

    urgency: "high" (crisis active), "medium" (cascade approaching),
             "low" (preventive)
    """
    if urgency == "high":
        return ["non_enforcement", "emergency_declaration", "municipal_authorization"]
    elif urgency == "medium":
        return ["municipal_authorization", "emergency_declaration", "legislative_change"]
    else:
        return ["legislative_change", "constitutional_change"]


# ---------------------------------------------------------------------
# FALSIFIABILITY: predicted outcomes
# ---------------------------------------------------------------------

FALSIFIABLE_PREDICTIONS = [
    {
        "claim": "regions that remove regulatory constraints during crisis recover faster than regions that add centralized solutions",
        "test": "compare recovery timelines and cascade-resistance metrics",
        "evidence_required": "matched case pairs with constraint-removal vs constraint-addition responses",
        "falsified_if": "constraint-addition regions show equal or faster recovery on multiple matched pairs",
    },
    {
        "claim": "barter networks scale within weeks-to-months when legal constraint is removed, drawing on pre-existing trust networks",
        "test": "measure adoption rate following Argentina 2001, Greece 2010s, similar events",
        "evidence_required": "participation rates over time post-constraint-removal",
        "falsified_if": "adoption requires years or fails to scale beyond small pilot",
    },
    {
        "claim": "constraint removal preserves local knowledge transmission better than constraint addition",
        "test": "measure intergenerational skill transmission rates in matched regions",
        "evidence_required": "elder-to-youth skill transfer measurements",
        "falsified_if": "knowledge transmission declines equally in both",
    },
]


# ---------------------------------------------------------------------
# MAIN: print framework summary
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("CONSTRAINT REMOVAL SOLUTIONS")
    print("=" * 60)
    print(f"Documented case studies: {len(CASE_STUDIES)}")
    print(f"Removal paths: {len(REMOVAL_PATHS)}")
    print(f"Falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
    print()
    for case in CASE_STUDIES:
        print(f"  {case.location}: {case.crisis_type}")
        print(f"    Response: {case.response_chosen}")
        print(f"    Outcome: {case.outcome[:80]}")
        print()
