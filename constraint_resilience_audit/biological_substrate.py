"""Biological substrate: stress-recovery and constraint-induced capacity.

Documents the well-attested biological pattern that organisms exposed
to bounded stressors develop capacity along the stressor axis, while
unstressed controls show structural atrophy along the same axis. The
pattern crosses kingdom boundaries (plants, animals, microbes) and
spans timescales from minutes (immune memory consolidation) to
generations (transgenerational epigenetic inheritance).
"""

from dataclasses import dataclass
from typing import List


@dataclass
class StressResponse:
    organism: str
    stressor: str
    duration: str
    deficit_framing: str
    developed_capacity: str
    mechanism: str
    reference_pattern: str


CASES: List[StressResponse] = [
    StressResponse(
        organism="Trees in wind-exposed sites",
        stressor="Mechanical loading by wind",
        duration="years",
        deficit_framing="Stunted height relative to sheltered conspecifics",
        developed_capacity="Greater stem diameter, deeper root anchoring, denser cell walls",
        mechanism="Thigmomorphogenesis (mechano-transduction via touch-response genes)",
        reference_pattern="Wolff's-law analogue",
    ),
    StressResponse(
        organism="Drought-cycled wheat lines",
        stressor="Intermittent water restriction at seedling phase",
        duration="weeks per cycle, multi-generation",
        deficit_framing="Lower biomass at maturity in good years",
        developed_capacity="Deeper root systems, faster stomatal closure, transgenerational drought tolerance",
        mechanism="Epigenetic priming (DNA methylation of stress-response loci)",
        reference_pattern="Stress memory / hormesis",
    ),
    StressResponse(
        organism="Human skeleton",
        stressor="Mechanical impact loading",
        duration="years of activity",
        deficit_framing="Joint wear, microfractures",
        developed_capacity="Bone density, trabecular alignment, tendon strength",
        mechanism="Osteoblast/osteoclast remodeling driven by strain gradient",
        reference_pattern="Wolff's law",
    ),
    StressResponse(
        organism="Human skeletal muscle",
        stressor="Eccentric loading near failure",
        duration="weeks",
        deficit_framing="Acute soreness, transient strength loss",
        developed_capacity="Hypertrophy, mitochondrial density, neuromuscular efficiency",
        mechanism="Satellite cell activation, mTOR signaling, IGF-1 axis",
        reference_pattern="Supercompensation",
    ),
    StressResponse(
        organism="Mammalian immune system",
        stressor="Antigen exposure",
        duration="days to lifetime",
        deficit_framing="Acute illness, inflammation, fever",
        developed_capacity="Adaptive immunity, memory T/B cells, broader receptor repertoire",
        mechanism="Clonal selection, somatic hypermutation, immunological memory",
        reference_pattern="Hormesis (immunological)",
    ),
    StressResponse(
        organism="Mycorrhizal-fungus-tree symbiosis",
        stressor="Nutrient-poor or patchy soil",
        duration="growing seasons",
        deficit_framing="Slow growth on poor soil",
        developed_capacity="Denser symbiotic network, broader nutrient exchange, drought buffering",
        mechanism="Carbon-for-nutrient trade incentivized by scarcity",
        reference_pattern="Resource-scarcity-driven mutualism",
    ),
    StressResponse(
        organism="Yeast under caloric restriction",
        stressor="Reduced glucose availability",
        duration="chronological lifespan",
        deficit_framing="Slower division rate",
        developed_capacity="Extended chronological lifespan, increased autophagy",
        mechanism="SIRT / TOR downregulation",
        reference_pattern="Caloric-restriction hormesis",
    ),
    StressResponse(
        organism="High-altitude human populations",
        stressor="Chronic hypoxia",
        duration="generations",
        deficit_framing="Reduced arterial O2 saturation by sea-level norms",
        developed_capacity="Higher hemoglobin or nitric-oxide-mediated vasodilation; population-specific solutions",
        mechanism="EPAS1 (Tibetan), Andean polycythemia, Ethiopian alternative pathway",
        reference_pattern="Adaptive selection under sustained stress",
    ),
    StressResponse(
        organism="Coppiced hardwoods",
        stressor="Cyclic stem removal",
        duration="decades",
        deficit_framing="Loss of canopy form",
        developed_capacity="Sustained high productivity, root reserves, multi-stem regeneration",
        mechanism="Apical-dominance release, root-stored carbohydrate mobilization",
        reference_pattern="Disturbance-fed productivity",
    ),
]


def by_pattern(pattern_substring: str) -> List[StressResponse]:
    s = pattern_substring.lower()
    return [c for c in CASES if s in c.reference_pattern.lower()]


def capacity_inventory() -> dict:
    return {c.developed_capacity: (c.organism, c.stressor) for c in CASES}


def deficit_vs_capacity_table():
    return [
        {"organism": c.organism,
         "if you measure for": c.deficit_framing,
         "you miss": c.developed_capacity}
        for c in CASES
    ]


if __name__ == "__main__":
    print("BIOLOGICAL SUBSTRATE  --  deficit framing vs developed capacity")
    print("=" * 76)
    for row in deficit_vs_capacity_table():
        print(f"\n  {row['organism']}")
        print(f"    if you measure: {row['if you measure for']}")
        print(f"    you miss:       {row['you miss']}")
