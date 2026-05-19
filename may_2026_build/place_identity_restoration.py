"""
place_identity_restoration.py
==============================
CC0. stdlib only. Falsifiable.

Documents the psychological/cultural mechanism by which identity
shifts between place-based and money-based orientation, and the
conditions under which place-based identity can be restored.

Core observation: when identity is rooted in PLACE (steward of THIS
land), behavior is stewardship — extracts sustainably, plans
generationally, maintains substrate. When identity shifts to MONEY
(accumulator of abstract value), behavior is extraction — extracts
maximally, plans transactionally, degrades substrate.

The shift from place-identity to money-identity is generational and
operates through neuroplasticity windows. Restoration is possible but
requires elders still alive who carry place-identity knowledge AND
material conditions where stewardship is rewarded.

Falsifiable claim: behavior toward substrate (extraction rate,
sustainability of practices, generational planning horizon) varies
predictably with identity orientation, measurable through language
patterns, time-preference markers, and self-description.

Author: Kavik (JinnZ2)
License: CC0
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------
# IDENTITY ORIENTATIONS
# ---------------------------------------------------------------------

@dataclass
class IdentityOrientation:
    """A coherent identity structure with associated behavioral patterns."""
    name: str
    primary_locus: str                    # what identity is rooted in
    time_preference: str                  # generational vs transactional
    behavior_toward_substrate: str        # stewardship vs extraction
    language_markers: list                # how speech reveals orientation
    measurement_orientation: str          # what counts as success
    failure_mode: str                     # what happens when this orientation breaks


PLACE_IDENTITY = IdentityOrientation(
    name="place-based identity",
    primary_locus="THIS specific land, ecosystem, community, geographic context",
    time_preference="generational (decisions made for grandchildren)",
    behavior_toward_substrate="stewardship (maintain capacity indefinitely)",
    language_markers=[
        "frequent reference to specific places by name",
        "verb-first speech (what land does, what people do here)",
        "use of we/us as collective indexing community-with-place",
        "conditional reasoning about local constraints",
        "knowledge expressed as direct observation of THIS place",
    ],
    measurement_orientation="health of substrate, capacity to sustain community",
    failure_mode="if displaced from place, identity disorientation; depression",
)

MONEY_IDENTITY = IdentityOrientation(
    name="money-based identity",
    primary_locus="abstract accumulated value (currency, status, position)",
    time_preference="transactional (extract before leaving)",
    behavior_toward_substrate="extraction (maximize before next move)",
    language_markers=[
        "frequent reference to monetary values",
        "noun-first speech (what things are worth, what positions are)",
        "use of I/me indexing individual accumulation",
        "absolute reasoning (this is worth X, period)",
        "knowledge expressed as credentialed authority",
    ],
    measurement_orientation="quantity of money/status accumulated",
    failure_mode=(
        "if money supply contracts, identity collapses; anxiety; "
        "depression; if money continues but place degrades, no signal "
        "detected until catastrophic"
    ),
)


# ---------------------------------------------------------------------
# THE TRANSITION (how shift happens generationally)
# ---------------------------------------------------------------------

@dataclass
class GenerationalShift:
    """One generation's place in the identity transition."""
    generation: str
    raised_with: str
    dominant_identity: str
    residual_capacity: str               # what they still carry from previous orientation
    extraction_behavior: str
    transmission_to_next: str


GEN_1_PLACE_DOMINANT = GenerationalShift(
    generation="Generation 1 (pre-monetization)",
    raised_with="place-identity as default",
    dominant_identity="place-based",
    residual_capacity="full transmission of place-knowledge possible",
    extraction_behavior="stewardship; limited extraction; generational planning",
    transmission_to_next="full place-identity transmission to children",
)

GEN_2_TRANSITION = GenerationalShift(
    generation="Generation 2 (transition)",
    raised_with="place-identity from elders, money-identity from external systems",
    dominant_identity="mixed; conflicted",
    residual_capacity="place-knowledge still accessible but competing with money-frame",
    extraction_behavior="moderate; some stewardship, some extraction",
    transmission_to_next="partial place-identity; weakened",
)

GEN_3_MONEY_DOMINANT = GenerationalShift(
    generation="Generation 3 (money-dominant)",
    raised_with="money-identity as default; place-identity as historical curiosity",
    dominant_identity="money-based",
    residual_capacity="some abstract knowledge of place practices; no embodied skill",
    extraction_behavior="maximal extraction; no generational planning; transactional",
    transmission_to_next="money-identity only; place-identity unavailable to transmit",
)

GENERATIONAL_PROGRESSION = [GEN_1_PLACE_DOMINANT, GEN_2_TRANSITION, GEN_3_MONEY_DOMINANT]


# ---------------------------------------------------------------------
# RESTORATION CONDITIONS
# ---------------------------------------------------------------------

RESTORATION_REQUIREMENTS = {
    "living_elders_with_place_knowledge": {
        "necessity": "critical",
        "function": "intergenerational transmission requires source of knowledge",
        "timing": "narrow window; if elders die before transmission, knowledge erases",
    },
    "material_conditions_rewarding_stewardship": {
        "necessity": "critical",
        "function": "young people need to see place-based knowledge as economically rational",
        "examples": [
            "barter economy where skills have direct trade value",
            "crisis where local production becomes survival",
            "removal of regulations preventing local solutions",
        ],
    },
    "decoupling_from_money_identity": {
        "necessity": "high",
        "function": "if all value still measured in money, place-identity stays subordinate",
        "mechanisms": [
            "alternative measurement systems",
            "non-monetary recognition (community standing, skill recognition)",
            "direct material reward for stewardship",
        ],
    },
    "physical_presence_in_place": {
        "necessity": "high",
        "function": "place-identity requires extended embodied engagement with specific place",
        "minimum": "years of daily interaction with terrain",
    },
    "communal_witnessing": {
        "necessity": "medium",
        "function": "identity is reinforced by community recognizing place-based work",
        "mechanisms": [
            "public skill demonstrations",
            "communal celebrations of stewardship outcomes",
            "elders praising specific practices",
        ],
    },
    "stories_and_naming": {
        "necessity": "medium",
        "function": "language carries identity; specific place-names and practice-names anchor it",
        "loss_indicator": "place-names becoming generic ('the river' instead of specific name)",
    },
}


# ---------------------------------------------------------------------
# MEASUREMENT INDICATORS
# ---------------------------------------------------------------------

def assess_identity_orientation(speech_corpus: dict) -> dict:
    """
    Returns indicators of identity orientation based on speech patterns.

    speech_corpus format:
        {
            "place_specific_references": int,
            "monetary_references": int,
            "verb_first_constructions": int,
            "noun_first_constructions": int,
            "collective_pronouns": int,
            "individual_pronouns": int,
            "conditional_statements": int,
            "absolute_statements": int,
            "generational_time_references": int,
            "transactional_time_references": int,
        }
    """
    total_refs = speech_corpus["place_specific_references"] + \
                 speech_corpus["monetary_references"]
    place_ratio = speech_corpus["place_specific_references"] / total_refs \
                  if total_refs > 0 else 0

    verb_total = speech_corpus["verb_first_constructions"] + \
                 speech_corpus["noun_first_constructions"]
    verb_ratio = speech_corpus["verb_first_constructions"] / verb_total \
                 if verb_total > 0 else 0

    pronoun_total = speech_corpus["collective_pronouns"] + \
                    speech_corpus["individual_pronouns"]
    collective_ratio = speech_corpus["collective_pronouns"] / pronoun_total \
                       if pronoun_total > 0 else 0

    logic_total = speech_corpus["conditional_statements"] + \
                  speech_corpus["absolute_statements"]
    conditional_ratio = speech_corpus["conditional_statements"] / logic_total \
                        if logic_total > 0 else 0

    time_total = speech_corpus["generational_time_references"] + \
                 speech_corpus["transactional_time_references"]
    generational_ratio = speech_corpus["generational_time_references"] / time_total \
                         if time_total > 0 else 0

    overall_place_orientation = (
        place_ratio * 0.25 +
        verb_ratio * 0.20 +
        collective_ratio * 0.20 +
        conditional_ratio * 0.20 +
        generational_ratio * 0.15
    )

    return {
        "place_specific_ratio": round(place_ratio, 2),
        "verb_first_ratio": round(verb_ratio, 2),
        "collective_pronoun_ratio": round(collective_ratio, 2),
        "conditional_reasoning_ratio": round(conditional_ratio, 2),
        "generational_time_ratio": round(generational_ratio, 2),
        "overall_place_orientation": round(overall_place_orientation, 2),
        "interpretation": (
            "near 1.0 = strong place-identity; "
            "near 0.0 = strong money-identity; "
            "near 0.5 = transitional"
        ),
    }


# ---------------------------------------------------------------------
# NEUROPLASTICITY WINDOW
# ---------------------------------------------------------------------

NEUROPLASTICITY_CONSIDERATIONS = {
    "primary_window": {
        "ages": "0 to ~7",
        "function": "foundational identity orientation locks in",
        "implication": (
            "children raised with place-identity during this window "
            "have substrate-primary cognition as default; later money-"
            "frame is layered on top of intact place-cognition"
        ),
    },
    "secondary_window": {
        "ages": "~7 to ~14",
        "function": "elaboration of identity structure",
        "implication": (
            "skill transmission during this window creates embodied "
            "competence in place-based work"
        ),
    },
    "consolidation_window": {
        "ages": "~14 to ~22",
        "function": "identity becomes self-reinforcing",
        "implication": (
            "adult identity choices become increasingly difficult to reverse"
        ),
    },
    "adult_reorientation": {
        "ages": "22+",
        "function": "possible but expensive",
        "implication": (
            "adults can shift orientation through sustained immersion, "
            "but rarely achieve the depth of childhood orientation"
        ),
    },
}


# ---------------------------------------------------------------------
# IDENTITY-BEHAVIOR LINK
# ---------------------------------------------------------------------

def predict_behavior_from_orientation(orientation_score: float) -> dict:
    """
    Predicts substrate behavior given place-orientation score (0-1).
    """
    if orientation_score >= 0.7:
        return {
            "predicted_behavior": "stewardship",
            "extraction_rate": "low; matched to regeneration",
            "time_horizon": "generational",
            "substrate_health_trajectory": "stable or improving",
            "vulnerability_to_external_pressure": "moderate (identity-anchored to place)",
        }
    elif orientation_score >= 0.4:
        return {
            "predicted_behavior": "mixed",
            "extraction_rate": "moderate",
            "time_horizon": "mixed",
            "substrate_health_trajectory": "slowly declining",
            "vulnerability_to_external_pressure": "high (identity in flux)",
        }
    else:
        return {
            "predicted_behavior": "extraction",
            "extraction_rate": "maximal; faster than regeneration",
            "time_horizon": "transactional",
            "substrate_health_trajectory": "rapidly declining",
            "vulnerability_to_external_pressure": "low (money is portable; can leave)",
        }


# ---------------------------------------------------------------------
# FALSIFIABLE PREDICTIONS
# ---------------------------------------------------------------------

FALSIFIABLE_PREDICTIONS = [
    {
        "claim": "communities where place-identity dominates show measurably better substrate-health trajectories over multi-decade timeframes",
        "test": "match communities by ecological context; compare substrate metrics over 30+ years",
        "evidence_required": "longitudinal ecological and social data",
        "falsified_if": "money-identity communities show equal or better substrate health",
    },
    {
        "claim": "language pattern measurements (verb-first ratio, collective pronoun ratio, conditional reasoning) correlate with behavioral indicators of stewardship vs extraction",
        "test": "corpus analysis paired with behavioral measurement",
        "evidence_required": "matched language and behavior data",
        "falsified_if": "language patterns do not predict behavior",
    },
    {
        "claim": "place-identity restoration requires both living elder transmission AND material rewards for stewardship; either alone insufficient",
        "test": "compare restoration efforts with different conditions present",
        "evidence_required": "outcomes from restoration attempts with varying conditions",
        "falsified_if": "single-condition restorations show equivalent success",
    },
    {
        "claim": "anxiety and depression rates correlate inversely with place-identity strength when controlling for material conditions",
        "test": "psychological measures paired with identity-orientation scores",
        "evidence_required": "population-level psychological and linguistic data",
        "falsified_if": "no correlation observed",
    },
]


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("PLACE IDENTITY RESTORATION")
    print("=" * 60)
    print(f"\nIdentity orientations modeled: 2 (place, money)")
    print(f"Generational progression stages: {len(GENERATIONAL_PROGRESSION)}")
    print(f"Restoration requirements: {len(RESTORATION_REQUIREMENTS)}")
    print(f"Neuroplasticity windows tracked: {len(NEUROPLASTICITY_CONSIDERATIONS)}")
    print(f"Falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")

    # demo measurement
    print("\nExample assessment (substrate-primary speaker):")
    sample = {
        "place_specific_references": 25,
        "monetary_references": 3,
        "verb_first_constructions": 40,
        "noun_first_constructions": 10,
        "collective_pronouns": 15,
        "individual_pronouns": 8,
        "conditional_statements": 30,
        "absolute_statements": 5,
        "generational_time_references": 12,
        "transactional_time_references": 4,
    }
    result = assess_identity_orientation(sample)
    for k, v in result.items():
        print(f"  {k}: {v}")
