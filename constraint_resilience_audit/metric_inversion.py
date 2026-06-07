"""Metric inversion: from a 'deficit' claim to its counter-capacity.

Operational function. Given a deficit-framed claim about a population,
produce the most likely capacity that the framing failed to detect,
the context in which it would be visible, and a method that could
actually measure it. Inversion is not 'flipping the sign' -- it asks
what the population was actually doing, with what skill, on what
evidence, under what constraint.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Inversion:
    deficit_claim: str
    likely_constraint_context: str
    counter_capacity: str
    where_to_measure_it: str
    suggested_method: str


INVERSIONS: List[Inversion] = [
    Inversion(
        deficit_claim="Low vocabulary (age-normed receptive vocabulary test)",
        likely_constraint_context="Lexical effort is invested in a non-test domain (plants, kin, places, seasons, weather, animal behaviour)",
        counter_capacity="High specificity and depth of domain vocabulary; richer underlying knowledge graph",
        where_to_measure_it="Free-listing and pile-sorting in the relevant ecological / kin / spiritual domain",
        suggested_method="Folk-taxonomy elicitation; expert-novice comparison on tasks in the active domain",
    ),
    Inversion(
        deficit_claim="Low literacy on standardized reading tests",
        likely_constraint_context="Oral tradition carries the knowledge load; literacy is not the primary memory infrastructure",
        counter_capacity="Long-form recall, narrative threading, multi-generational accuracy of oral records, song-line cartography",
        where_to_measure_it="In-situ recitation, kinship-history reconstruction, navigation by recited landscape",
        suggested_method="Recall fidelity across days/weeks; cross-narrator agreement on landscape coordinates and event sequence",
    ),
    Inversion(
        deficit_claim="Poor performance on Stroop / dyadic-attention tasks",
        likely_constraint_context="Attention is policy-allocated across many simultaneous social and ecological signals",
        counter_capacity="Multi-channel ambient monitoring; rapid context-switching among non-task channels",
        where_to_measure_it="Multi-actor settings: marketplace, household with infants, hunting/foraging party",
        suggested_method="Behavioural observation of attention shifts; ambient-event detection with multiple concurrent streams",
    ),
    Inversion(
        deficit_claim="High delay-discounting / impulsivity",
        likely_constraint_context="The institutional future is empirically unreliable (promises broken, resources confiscated, returns expropriated)",
        counter_capacity="Calibrated discounting; rational response to a measured-unreliable institutional environment",
        where_to_measure_it="Decisions in domains where the future actually delivers (kin networks, subsistence cycles, ceremony)",
        suggested_method="Within-subject comparison of discounting across delivered vs undelivered domains",
    ),
    Inversion(
        deficit_claim="Low STEM test scores",
        likely_constraint_context="Schooling is decontextualized; the population's mathematics is embedded in trade, navigation, weaving, ecology, music",
        counter_capacity="Applied geometry (weaving, basketry), ratio reasoning (trade, dilution), proportional volume estimation, seasonal arithmetic, symmetry groups",
        where_to_measure_it="Workshops, marketplaces, fields, looms, kitchens",
        suggested_method="Task-based mathematical-cognition probes administered in the working context",
    ),
    Inversion(
        deficit_claim="Diet 'deficient' in micronutrient X",
        likely_constraint_context="Survey samples a narrow nutrient panel; traditional preparation alters bioavailability; seasonal cycling not captured",
        counter_capacity="Bioavailability optimization, seasonal nutrient cycling, phytochemical diversity, fermentation-derived nutrients",
        where_to_measure_it="Full annual diet sampling with preparation-state tracking",
        suggested_method="Longitudinal diet diaries; gut-microbiome panels; serum micronutrient biomarkers across seasons",
    ),
    Inversion(
        deficit_claim="Living 'below the poverty line'",
        likely_constraint_context="Wellbeing flows through non-monetary channels invisible to cash-income surveys",
        counter_capacity="Food sovereignty, reciprocity networks, low-cash high-asset (land / livestock / skill) resilience, time wealth",
        where_to_measure_it="Subsistence calorie audit; reciprocity-flow mapping; skill inventory; land/water access mapping",
        suggested_method="Multi-modal livelihood assessment; non-cash wealth accounting; commons-access census",
    ),
    Inversion(
        deficit_claim="Housing 'substandard'",
        likely_constraint_context="Infrastructure baseline assumes grid-tied permanence; mobile and seasonal architectures are coded as lacking",
        counter_capacity="Climate-appropriate design, low-input thermal regulation, mobility-by-design, low-impact siting, repair fluency",
        where_to_measure_it="Comfort under stress (heat, cold, storms), embodied energy, repair frequency, occupant control",
        suggested_method="Thermal performance audit, lifecycle energy accounting, mobility-cost accounting",
    ),
    Inversion(
        deficit_claim="PTSD-spectrum symptoms / hypervigilance",
        likely_constraint_context="The environment in which the response set was acquired is one where the assumption of safety would have been an error",
        counter_capacity="Threat-cue calibration, rapid trust assessment, multi-route mobility planning, alarm-network maintenance",
        where_to_measure_it="Environments matched to the original threat context, not the testing clinic",
        suggested_method="Context-matched threat-detection tasks; trust calibration over realistic time horizons",
    ),
    Inversion(
        deficit_claim="Low labor-force participation",
        likely_constraint_context="Work is being done but not in the wage-employment frame the survey counts",
        counter_capacity="Subsistence agriculture, kin care, ceremonial labor, repair and maintenance, knowledge transmission",
        where_to_measure_it="Full time-use diaries; non-cash production accounting",
        suggested_method="24-hour time-use sampling; output-based rather than employment-based accounting",
    ),
    Inversion(
        deficit_claim="Population is 'data-poor'",
        likely_constraint_context="The data system was not built to register what this population tracks",
        counter_capacity="Place-specific monitoring, multi-generational baseline, qualitative pattern-recognition that catches what aggregate metrics miss",
        where_to_measure_it="Local observation logs, ceremonial calendars, oral baselines, multi-generation comparison",
        suggested_method="Co-produced indicator design; baseline elicitation from elders; participatory monitoring",
    ),
]


def _normalize(s: str) -> str:
    return s.lower().replace("'", "").replace('"', "").replace("-", " ")


def invert(deficit_claim_substring: str) -> List[Inversion]:
    kw = _normalize(deficit_claim_substring)
    return [i for i in INVERSIONS if kw in _normalize(i.deficit_claim)]


def audit_report(claims: List[str]):
    out = []
    for claim in claims:
        matches = invert(claim)
        if matches:
            m = matches[0]
            out.append({
                "claim": claim,
                "counter_capacity": m.counter_capacity,
                "measure_where": m.where_to_measure_it,
                "method": m.suggested_method,
            })
        else:
            out.append({
                "claim": claim,
                "counter_capacity": None,
                "measure_where": None,
                "method": None,
            })
    return out


if __name__ == "__main__":
    print("METRIC INVERSION  --  deficit claim -> counter-capacity")
    print("=" * 76)
    sample_claims = [
        "Low vocabulary",
        "Poor performance on Stroop",
        "High delay-discounting",
        "Living below the poverty line",
        "Housing substandard",
        "Low labor-force participation",
        "Population is data-poor",
    ]
    for r in audit_report(sample_claims):
        print(f"\n  CLAIM:     {r['claim']}")
        if r["counter_capacity"]:
            print(f"  COUNTER:   {r['counter_capacity']}")
            print(f"  MEASURE:   {r['measure_where']}")
            print(f"  METHOD:    {r['method']}")
        else:
            print(f"  (no inversion in catalogue -- add one)")
