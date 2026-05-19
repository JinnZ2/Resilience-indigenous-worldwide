"""
dual_layer_economic_system.py
==============================
CC0. stdlib only. Falsifiable.

Models parallel currency + barter system as a transition architecture
for regions in crisis. The currency layer remains intact to satisfy
external systems (IMF, debt servicing, formal economy, identity needs
for participants who depend on monetary measurement). The barter
layer is unblocked at the local level to enable direct exchange,
restoring local survival capacity without confronting the formal
economy.

Key insight: this is NOT abolishing currency, NOT building new
infrastructure, NOT requiring permission from international actors.
It is REMOVING a regulatory constraint on a parallel layer that
allows existing networks to function.

Falsifiable claim: regions implementing dual-layer systems show
better crisis-period outcomes (food security, energy access, social
stability) than regions maintaining single-layer formal economy.

Author: Kavik (JinnZ2)
License: CC0
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------
# LAYER STRUCTURES
# ---------------------------------------------------------------------

@dataclass
class CurrencyLayer:
    """The formal monetary economy layer."""
    name: str
    function: str
    serves: list                          # who and what it satisfies
    external_obligations: list            # IMF, debt, etc.
    domestic_obligations: list            # taxes, formal trade, civil servants
    failure_modes: list                   # what happens when this layer fails
    leave_intact: bool = True             # this layer keeps running


@dataclass
class BarterLayer:
    """The parallel direct-exchange layer."""
    name: str
    function: str
    activates_through: list               # mechanisms for activation
    handles: list                         # what kinds of exchange happen here
    requires_no_permission: bool = True   # operates without central authorization
    dispute_resolution: str = "local community arbitration"
    measurement: str = "direct, contextual, relational"


@dataclass
class DualLayerSystem:
    """Both layers operating simultaneously."""
    name: str
    currency_layer: CurrencyLayer
    barter_layer: BarterLayer
    interface_rules: dict                 # how the layers interact
    activation_speed: str
    stability_features: list = field(default_factory=list)


# ---------------------------------------------------------------------
# STANDARD DUAL-LAYER DESIGN
# ---------------------------------------------------------------------

STANDARD_CURRENCY_LAYER = CurrencyLayer(
    name="formal currency economy",
    function="external compliance and identity-protection for money-oriented participants",
    serves=[
        "IMF debt servicing",
        "international trade",
        "formal sector employment",
        "tax collection",
        "people whose identity is tied to monetary measurement",
        "international observers and regulators",
    ],
    external_obligations=[
        "debt service to international lenders",
        "currency stability requirements",
        "trade balance reporting",
    ],
    domestic_obligations=[
        "civil servant payment",
        "infrastructure financing",
        "central government operations",
        "formal financial sector",
    ],
    failure_modes=[
        "hyperinflation",
        "currency devaluation",
        "loss of import capacity",
        "bank collapse",
        "trade isolation",
    ],
)

STANDARD_BARTER_LAYER = BarterLayer(
    name="regional barter economy",
    function="direct exchange of goods, services, knowledge between people and regions",
    activates_through=[
        "non-enforcement of barter restrictions",
        "municipal designation of trade fair days",
        "existing kinship/religious/cooperative networks",
        "emergency declarations",
        "informal market revival",
    ],
    handles=[
        "food (local production direct to local consumption)",
        "labor (work exchanged for goods or other work)",
        "knowledge and skills (teaching, mentorship, apprenticeship)",
        "tools and equipment",
        "energy (direct trades of fuel, electricity, batteries)",
        "transport (rides for goods, trips for services)",
        "healthcare (herbalists, midwives, healers)",
        "construction (collective building projects)",
    ],
    requires_no_permission=True,
    dispute_resolution="elder council, community witnesses, repeated-game enforcement",
    measurement="direct quality assessment, customary exchange ratios, relationship value",
)

INTERFACE_RULES_DEFAULT = {
    "no_required_currency_conversion": (
        "barter transactions do not require expressing value in currency terms"
    ),
    "voluntary_layer_choice": (
        "participants choose which layer to use for any given transaction"
    ),
    "no_central_record_required": (
        "barter trades do not require government registration or reporting"
    ),
    "tax_treatment_minimal": (
        "barter trades treated as personal exchange; not subject to commercial tax"
    ),
    "currency_layer_remains_legal_tender": (
        "currency continues to function for those who choose it"
    ),
    "no_competing_authority_required": (
        "no need for the barter layer to claim authority equal to currency"
    ),
}

BOLIVIA_DUAL_LAYER = DualLayerSystem(
    name="Bolivia Dual-Layer Proposal",
    currency_layer=STANDARD_CURRENCY_LAYER,
    barter_layer=STANDARD_BARTER_LAYER,
    interface_rules=INTERFACE_RULES_DEFAULT,
    activation_speed="weeks to months",
    stability_features=[
        "currency layer continues servicing external debt",
        "IMF receives expected payments via currency layer",
        "barter layer provides food and energy security to population",
        "external observers see currency economy continuing",
        "internal observers see actual survival happening",
        "no political confrontation required",
    ],
)


# ---------------------------------------------------------------------
# CRISIS RESPONSE TIMING
# ---------------------------------------------------------------------

CRISIS_RESPONSE_TIMELINE = {
    "day_0_to_day_7": {
        "phase": "non-enforcement initiation",
        "action": "government stops enforcing barter restrictions",
        "cost": "zero",
        "visibility": "minimal; people just trade directly",
        "expected_outcome": "immediate relief in worst-hit areas",
    },
    "week_1_to_week_4": {
        "phase": "municipal activation",
        "action": "cities designate weekly market days; explicit permission for trade fairs",
        "cost": "low; administrative coordination",
        "visibility": "moderate; visible markets emerge",
        "expected_outcome": "trade networks scale within trusted relationships",
    },
    "month_1_to_month_3": {
        "phase": "emergency formalization",
        "action": "executive declaration formalizes temporary framework",
        "cost": "low; political",
        "visibility": "high; explicit dual-layer policy",
        "expected_outcome": "broader participation; investment in market infrastructure",
    },
    "month_3_to_year_1": {
        "phase": "permanent integration",
        "action": "legislative framework establishes dual-layer as permanent option",
        "cost": "moderate; legislative process",
        "visibility": "high; international attention",
        "expected_outcome": "stable two-layer system; both layers operating normally",
    },
}


# ---------------------------------------------------------------------
# COMPARISON: SINGLE LAYER vs DUAL LAYER
# ---------------------------------------------------------------------

def compare_single_vs_dual(crisis_severity: str = "high") -> dict:
    """
    Compares projected outcomes for single-layer vs dual-layer crisis response.
    """
    if crisis_severity == "high":
        return {
            "single_layer_response": {
                "food_security": "deteriorating rapidly",
                "energy_access": "constrained by foreign currency availability",
                "social_stability": "deteriorating; protests escalating",
                "trust_in_institutions": "collapsing",
                "external_debt_service": "increasingly difficult",
                "political_legitimacy": "eroding",
            },
            "dual_layer_response": {
                "food_security": "regional production trades meet local needs",
                "energy_access": "local generation + barter for fuel",
                "social_stability": "people focused on participation, not protest",
                "trust_in_institutions": "rebuilding through local success",
                "external_debt_service": "continues via currency layer",
                "political_legitimacy": "preserved by visible relief",
            },
            "key_difference": (
                "dual layer preserves both external compliance AND internal survival; "
                "single layer forces choice between them"
            ),
        }
    elif crisis_severity == "medium":
        return {
            "single_layer_response": "manageable; some hardship; cascade not yet triggered",
            "dual_layer_response": "preventive resilience; cascade unlikely to develop",
            "key_difference": "dual layer builds resilience before crisis acute",
        }
    else:
        return {
            "single_layer_response": "stable",
            "dual_layer_response": "available as backup; no immediate activation needed",
            "key_difference": "dual layer optionality has low cost when not active",
        }


# ---------------------------------------------------------------------
# OBJECTIONS AND RESPONSES
# ---------------------------------------------------------------------

OBJECTIONS_AND_RESPONSES = {
    "this_will_undermine_currency": {
        "objection": "permitting barter will reduce currency demand and weaken the formal economy",
        "response": (
            "barter handles transactions that the currency layer is failing to "
            "serve anyway. People are not going to barter for things the formal "
            "economy still provides reliably. Barter activates exactly where "
            "currency fails. The currency layer is not undermined; it is "
            "relieved of demand it cannot meet."
        ),
        "evidence": "Argentina trueque clubs declined as formal economy recovered",
    },
    "barter_is_inefficient": {
        "objection": "barter requires double-coincidence-of-wants; cannot scale",
        "response": (
            "research on informal economies shows barter networks handle "
            "60-80% of GDP in many developing nations. The 'inefficiency' "
            "argument is from textbook economics; the empirical evidence "
            "shows barter scales fine at regional level through repeated "
            "relationships and credit networks."
        ),
        "evidence": "Schneider (2010); Hart (1973); Neuwirth (2011)",
    },
    "this_invites_black_market": {
        "objection": "removing barter restrictions opens door to illegal trade",
        "response": (
            "the black market already exists. The networks already operate. "
            "Legitimizing food, labor, and material exchange does not "
            "affect drug, weapons, or human trafficking, which remain "
            "regulated separately. In fact, formalizing legitimate barter "
            "draws activity OUT of fully-underground networks."
        ),
        "evidence": "Norman & Russell on Argentine trueque demographic shift",
    },
    "this_will_cause_inflation": {
        "objection": "barter creates parallel money supply",
        "response": (
            "barter does not create money. Direct exchange does not increase "
            "any monetary aggregate. If anything, removing demand from the "
            "currency layer relieves currency pressure."
        ),
        "evidence": "monetary theory; barter does not enter M0/M1/M2",
    },
    "IMF_will_object": {
        "objection": "international lenders will require single-layer compliance",
        "response": (
            "the currency layer continues all formal obligations. IMF receives "
            "scheduled payments. International trade continues. Barter operates "
            "below the threshold of international monetary measurement. "
            "Compliance is unchanged."
        ),
        "evidence": "Greek alternative currencies during austerity did not trigger IMF response",
    },
}


# ---------------------------------------------------------------------
# IMPLEMENTATION CHECKLIST
# ---------------------------------------------------------------------

IMPLEMENTATION_CHECKLIST = [
    "identify regulations currently prohibiting direct barter",
    "issue executive directive of non-enforcement on identified regulations",
    "designate physical spaces for weekly markets (use existing market days where possible)",
    "publicize that barter is permitted; remove ambiguity",
    "support elder councils as dispute resolution venues",
    "encourage radio and community SMS announcements of trade opportunities",
    "do NOT impose new measurement systems; let local custom determine ratios",
    "do NOT require registration of trades",
    "do NOT impose new authorities; let existing community networks lead",
    "monitor for fraud through community reporting, not central oversight",
    "maintain currency layer functioning without modification",
    "report to international bodies on currency layer; barter layer is internal",
]


# ---------------------------------------------------------------------
# FALSIFIABLE PREDICTIONS
# ---------------------------------------------------------------------

FALSIFIABLE_PREDICTIONS = [
    {
        "claim": "regions implementing dual-layer systems during currency crisis show better food and energy security outcomes than regions maintaining single-layer formal economy",
        "test": "compare matched crisis periods across regions with different responses",
        "evidence_required": "food security and energy access metrics during 2025-2027 in Bolivia/Kenya/Sri Lanka/Lebanon",
        "falsified_if": "single-layer regions show equal or better outcomes",
    },
    {
        "claim": "dual-layer activation does not significantly disrupt formal currency operations or external debt servicing",
        "test": "compare currency stability and debt service in dual-layer vs single-layer crisis regions",
        "evidence_required": "currency metrics and IMF/lender reports",
        "falsified_if": "dual-layer regions show worse currency or debt outcomes",
    },
    {
        "claim": "dual-layer systems remain stable; do not require constant central intervention to maintain",
        "test": "measure required policy interventions over time in dual-layer regions",
        "evidence_required": "policy intervention frequency data",
        "falsified_if": "dual-layer systems require continuous central management",
    },
]


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("DUAL-LAYER ECONOMIC SYSTEM")
    print("=" * 60)
    print(f"\nLayers: {BOLIVIA_DUAL_LAYER.currency_layer.name} + {BOLIVIA_DUAL_LAYER.barter_layer.name}")
    print(f"Activation speed: {BOLIVIA_DUAL_LAYER.activation_speed}")
    print(f"\nCrisis response phases: {len(CRISIS_RESPONSE_TIMELINE)}")
    for phase_key, phase in CRISIS_RESPONSE_TIMELINE.items():
        print(f"  {phase_key}: {phase['phase']}")
    print(f"\nObjections addressed: {len(OBJECTIONS_AND_RESPONSES)}")
    print(f"Implementation steps: {len(IMPLEMENTATION_CHECKLIST)}")
    print(f"Falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
