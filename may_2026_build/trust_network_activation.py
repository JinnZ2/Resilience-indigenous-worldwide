"""
trust_network_activation.py
============================
CC0. stdlib only. Falsifiable.

Documents social-technology mechanisms for rapid trust development at
scale, distilled from religious movement research and informal economy
research. Strips the metaphysical/doctrinal layer; keeps the
organizational and trust-building mechanisms.

Core insight: trust networks for crisis response do not need to be
built from scratch. Existing networks (kinship, religious, ethnic,
professional, cooperative) can be ACTIVATED through documented social
mechanisms within weeks-to-months, not years.

Falsifiable claim: when crisis triggers existing trust networks to
activate for material survival, scaling follows predictable patterns
(network density, demonstration, ritual, costly signaling) at rates
documented in religious movement and informal economy research.

Author: Kavik (JinnZ2)
License: CC0
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------
# TRUST-BUILDING MECHANISMS (from research literature)
# ---------------------------------------------------------------------

@dataclass
class TrustMechanism:
    """A documented mechanism for rapid trust development."""
    name: str
    description: str
    research_basis: list
    speed: str                            # "days", "weeks", "months", "years"
    applicability: list                   # what kinds of networks it works in
    cost_to_implement: str                # "low", "medium", "high"
    risks: list = field(default_factory=list)


# Mechanisms from religious movement research
NETWORK_DENSITY = TrustMechanism(
    name="pre-existing network density",
    description=(
        "Trust does not develop between strangers. It transfers along "
        "existing relationships. Conversion/adoption happens through "
        "family, friend, and community ties already in place."
    ),
    research_basis=[
        "Stark & Bainbridge (1985) The Future of Religion",
        "Stark (1996) The Rise of Christianity",
        "Snow, Zurcher, Ekland-Olson (1980) Social Networks and Social Movements",
    ],
    speed="immediate when activated",
    applicability=["kinship", "religious", "ethnic", "professional", "cooperative"],
    cost_to_implement="low (networks exist)",
    risks=["in-group exclusion of outsiders"],
)

DEMONSTRATION_OF_VALUE = TrustMechanism(
    name="immediate visible demonstration",
    description=(
        "Rapid trust requires showing something works before asking for "
        "commitment. Pentecostal healing meetings, Mormon welfare "
        "provision, mutual aid responses all demonstrated value before "
        "requesting belief or contribution."
    ),
    research_basis=[
        "Anderson (2004) An Introduction to Pentecostalism",
        "Stark (1984) The Rise of a New World Faith [Mormon studies]",
        "Iannaccone (1994) Why Strict Churches Are Strong",
    ],
    speed="single event can shift relationships",
    applicability=["all networks"],
    cost_to_implement="low to medium",
    risks=["false demonstrations exploit trust"],
)

COMMUNAL_RITUAL = TrustMechanism(
    name="shared embodied ritual",
    description=(
        "Communal meals, shared singing, group ceremony create "
        "physiological synchrony (heart rate, breathing) and trigger "
        "oxytocin release. Embodied gathering produces faster trust than "
        "verbal agreement or digital interaction."
    ),
    research_basis=[
        "Eliade (1959) The Sacred and the Profane",
        "Konvalinka et al (2011) Synchronized arousal between performers and related spectators",
        "Whitehouse (2004) Modes of Religiosity",
    ],
    speed="single ritual creates lasting effect",
    applicability=["any in-person gathering"],
    cost_to_implement="low",
    risks=["ritual without follow-through erodes trust"],
)

CRISIS_RESPONSIVENESS = TrustMechanism(
    name="crisis window adoption",
    description=(
        "Movements grow fastest when solving immediate problems during "
        "crisis. Pentecostalism in Latin America during economic collapse, "
        "early Christianity during Roman plagues, Mormon expansion in "
        "frontier hardship. Crisis opens trust transfer windows that "
        "close during stability."
    ),
    research_basis=[
        "Stark (1996) Rise of Christianity (especially plague response)",
        "Smilde (2007) Reason to Believe: Cultural Agency in Latin American Evangelicalism",
        "Martin (2002) Pentecostalism: The World Their Parish",
    ],
    speed="weeks to months during crisis",
    applicability=["any network during stress"],
    cost_to_implement="low (crisis provides motivation)",
    risks=["coercion possible if crisis exploited"],
)

COSTLY_SIGNALING = TrustMechanism(
    name="public costly commitment",
    description=(
        "Members making visible sacrifices signal trustworthiness. "
        "Tithing, dietary restrictions, time commitment, public "
        "identification all create skin-in-the-game that accelerates "
        "trust. Free riders cannot persist; sincere members visible."
    ),
    research_basis=[
        "Iannaccone (1994) Why Strict Churches Are Strong",
        "Sosis & Alcorta (2003) Signaling, Solidarity, and the Sacred",
        "Henrich (2009) The Evolution of Costly Displays",
    ],
    speed="immediate signal value",
    applicability=["committed networks"],
    cost_to_implement="medium (requires actual sacrifice)",
    risks=["entry barrier may exclude valuable participants"],
)

LOCAL_ADAPTATION = TrustMechanism(
    name="adaptation to local language and culture",
    description=(
        "Movements grow fastest when expressed in local idiom. Korean "
        "Christianity adopted Korean cultural forms. African indigenous "
        "churches integrated local practices. Imposed external forms "
        "create resistance; locally-adapted forms remove friction."
    ),
    research_basis=[
        "Sanneh (1989) Translating the Message: The Missionary Impact on Culture",
        "Walls (1996) The Missionary Movement in Christian History",
        "Mbiti (1969) African Religions and Philosophy",
    ],
    speed="removes resistance immediately",
    applicability=["cross-cultural contexts"],
    cost_to_implement="low to medium",
    risks=["over-adaptation loses coherence"],
)

DECENTRALIZED_AUTHORITY = TrustMechanism(
    name="local leadership with minimal central control",
    description=(
        "Movements with house churches, local leaders, distributed "
        "authority scale faster than centrally-controlled ones. No "
        "bottleneck at center; trust stays close to participants; local "
        "accountability visible."
    ),
    research_basis=[
        "Anderson (2004) An Introduction to Pentecostalism (esp house church movement)",
        "Stark (1996) Rise of Christianity (network structure)",
        "Wuthnow (1988) The Restructuring of American Religion",
    ],
    speed="scales as fast as local leaders emerge",
    applicability=["any distributed network"],
    cost_to_implement="low",
    risks=["coordination challenges; some local leaders may exploit"],
)


TRUST_MECHANISMS = [
    NETWORK_DENSITY,
    DEMONSTRATION_OF_VALUE,
    COMMUNAL_RITUAL,
    CRISIS_RESPONSIVENESS,
    COSTLY_SIGNALING,
    LOCAL_ADAPTATION,
    DECENTRALIZED_AUTHORITY,
]


# ---------------------------------------------------------------------
# INFORMAL ECONOMY RESEARCH (trust in non-monetary trade)
# ---------------------------------------------------------------------

INFORMAL_ECONOMY_FINDINGS = {
    "size_of_informal_economy": {
        "claim": "informal economy accounts for 50%+ of GDP in many developing nations",
        "source": "Schneider (2010) Shadow Economies All over the World",
    },
    "trust_through_repetition": {
        "claim": "repeated transactions between same parties enforce honesty more reliably than legal contracts",
        "source": "Hart (1973) Informal income opportunities and urban employment in Ghana",
    },
    "social_embeddedness": {
        "claim": "trades embedded in family/ethnic/religious networks have lower default rates",
        "source": "Granovetter (1985) Economic Action and Social Structure",
    },
    "rapid_dispute_resolution": {
        "claim": "informal arbitration resolves disputes in days vs years for formal courts",
        "source": "MacGaffey (1991) The Real Economy of Zaire",
    },
    "rapid_scaling": {
        "claim": "informal networks scale within weeks during formal economy collapse",
        "source": "Norman & Russell (2005) Argentine Trueque Networks; Sotiropoulou (2011) Alternative Exchange Systems in Greece",
    },
    "implicit_organization": {
        "claim": "informal economies are highly organized through implicit rules; not chaotic",
        "source": "Neuwirth (2011) Stealth of Nations",
    },
}


# ---------------------------------------------------------------------
# DOCUMENTED SCALING RATES (calibration data)
# ---------------------------------------------------------------------

SCALING_RATES_HISTORICAL = {
    "early_christianity": {
        "growth_rate_per_decade": "~40% (Stark estimate)",
        "duration": "300 years to majority status in Roman Empire",
        "mechanism": "network density + crisis response + ritual",
    },
    "mormon_expansion": {
        "growth_rate_per_decade": "doubling through 1800s",
        "duration": "200 years",
        "mechanism": "network density + welfare provision + costly signaling",
    },
    "pentecostal_global": {
        "growth_total": "0 to 600 million in 100 years",
        "peak_growth_regions": "Latin America during economic crisis",
        "mechanism": "crisis response + healing demonstrations + local adaptation",
    },
    "korean_christianity": {
        "growth_total": "0 to 30% of national population in 50 years",
        "mechanism": "local adaptation + crisis response (Japanese occupation, Korean War)",
    },
    "argentina_trueque_2001": {
        "scale": "~6 million participants",
        "time_to_peak": "months",
        "mechanism": "crisis response + pre-existing trust networks + demonstrated value",
    },
    "greek_alternative_currencies_2010s": {
        "scale": "dozens of cities adopted local systems",
        "time_to_emergence": "months after austerity intensified",
        "mechanism": "crisis response + existing community networks",
    },
}


# ---------------------------------------------------------------------
# ACTIVATION PROTOCOL
# ---------------------------------------------------------------------

def design_activation_protocol(context: dict) -> list:
    """
    Recommends ordered activation steps based on context.

    context format:
        {
            "crisis_level": "high|medium|low",
            "existing_networks": [list of network types],
            "geography": "rural|urban|mixed",
            "trust_baseline": "high|medium|low",
        }
    """
    steps = []

    if context.get("crisis_level") == "high":
        steps.append({
            "step": 1,
            "action": "activate existing networks for immediate need",
            "mechanism": "network density",
            "speed": "days",
        })

    steps.append({
        "step": 2,
        "action": "stage demonstration of value (successful trade, mutual aid)",
        "mechanism": "demonstration of value",
        "speed": "days to weeks",
    })

    steps.append({
        "step": 3,
        "action": "establish regular gathering (market day, communal meal)",
        "mechanism": "communal ritual",
        "speed": "weeks",
    })

    steps.append({
        "step": 4,
        "action": "introduce public commitment mechanisms (reputation tracking)",
        "mechanism": "costly signaling",
        "speed": "weeks to months",
    })

    if context.get("geography") in ("rural", "mixed"):
        steps.append({
            "step": 5,
            "action": "use traditional measurement, language, customs",
            "mechanism": "local adaptation",
            "speed": "ongoing",
        })

    steps.append({
        "step": 6,
        "action": "designate local arbitrators; no central authority",
        "mechanism": "decentralized authority",
        "speed": "ongoing",
    })

    return steps


# ---------------------------------------------------------------------
# WHAT TO LEAVE BEHIND (from religious movement research)
# ---------------------------------------------------------------------

DOCTRINAL_LAYER_NOT_REQUIRED = [
    "shared metaphysical beliefs",
    "exclusive membership",
    "central charismatic authority",
    "in-group purity requirements",
    "out-group sanctions",
    "doctrinal orthodoxy testing",
]

KEEP_SOCIAL_TECHNOLOGY_DROP_METAPHYSICS = {
    "what_works_universally": [
        "network propagation",
        "demonstration of material value",
        "ritual that creates synchrony",
        "crisis-response timing",
        "costly signaling for trust",
        "local adaptation",
        "decentralized authority",
    ],
    "what_is_doctrine_specific": [
        "shared belief systems",
        "exclusive identity claims",
        "metaphysical commitments",
    ],
    "implication": (
        "barter networks need the social technology, not the doctrine. "
        "Trust mechanisms work without requiring participants to share "
        "religious beliefs or cult identity."
    ),
}


# ---------------------------------------------------------------------
# FALSIFIABLE PREDICTIONS
# ---------------------------------------------------------------------

FALSIFIABLE_PREDICTIONS = [
    {
        "claim": "barter networks activated through existing trust structures during crisis will scale to functional size within 3-6 months",
        "test": "measure participation rates and trade volume in newly-permitted barter networks during current Bolivia/Kenya crises",
        "evidence_required": "longitudinal participation data",
        "falsified_if": "scaling requires years or fails to reach functional density",
    },
    {
        "claim": "networks using documented trust mechanisms (demonstration, ritual, costly signaling) develop trust faster than networks relying on legal contracts",
        "test": "compare trust development rates in networks with vs without these mechanisms",
        "evidence_required": "matched-pair trust development data",
        "falsified_if": "legal-contract-based networks show equal or faster trust development",
    },
    {
        "claim": "stripping the doctrinal layer while keeping the social technology produces equivalent network resilience",
        "test": "compare religious-affiliated barter networks vs secular ones using same social mechanisms",
        "evidence_required": "resilience metrics across both types",
        "falsified_if": "doctrinal networks show measurably more resilience",
    },
]


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("TRUST NETWORK ACTIVATION")
    print("=" * 60)
    print(f"Documented trust mechanisms: {len(TRUST_MECHANISMS)}")
    for mech in TRUST_MECHANISMS:
        print(f"  - {mech.name} (speed: {mech.speed})")

    print(f"\nHistorical scaling cases: {len(SCALING_RATES_HISTORICAL)}")
    print(f"Informal economy findings: {len(INFORMAL_ECONOMY_FINDINGS)}")
    print(f"Falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")

    print("\nExample protocol for high-crisis rural context:")
    context = {
        "crisis_level": "high",
        "existing_networks": ["kinship", "religious", "agricultural cooperative"],
        "geography": "rural",
        "trust_baseline": "high",
    }
    protocol = design_activation_protocol(context)
    for step in protocol:
        print(f"  Step {step['step']}: {step['action']} ({step['speed']})")
