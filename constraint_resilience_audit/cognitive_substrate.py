"""Cognitive substrate: constraint-raised problem-solving capacities.

The cognitive parallel to the biological pattern. Children raised in
resource-tight, ecologically complex, or kinship-dense environments
develop measurable capacities (mental arithmetic, spatial reasoning,
multi-actor social modelling, abductive inference, multilingual
register-switching) that standardized instruments designed around
schooled, individualistic, literate reference populations do not
target and therefore do not detect.

Population descriptors below name groups only where the cited
literature names them; the entries describe what was actually
measured, not generalizations about identity.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class CognitiveCapacity:
    population_descriptor: str
    capacity: str
    constraint_context: str
    measurement_status: str
    typical_deficit_label: str
    ecological_validity: str
    representative_literature: str


CASES: List[CognitiveCapacity] = [
    CognitiveCapacity(
        population_descriptor="Market-vendor children, Recife / Belo Horizonte",
        capacity="Multi-step mental arithmetic under price-and-currency variability",
        constraint_context="Daily transactions, no paper, real consequences for error",
        measurement_status="Not on standard school-math tests",
        typical_deficit_label="Innumerate / poor school math performance",
        ecological_validity="Capacity demonstrated in the market collapses when given equivalent paper-form problems",
        representative_literature="Nunes, Schliemann, Carraher: 'Street Mathematics and School Mathematics' (1993)",
    ),
    CognitiveCapacity(
        population_descriptor="San / Ju/'hoansi tracker apprentices, southern Africa",
        capacity="Abductive inference from partial spoor evidence under time pressure",
        constraint_context="Tracking as livelihood; cost of error is a missed meal or predator encounter",
        measurement_status="No standardized instrument exists",
        typical_deficit_label="Unschooled / low literacy",
        ecological_validity="Inference quality is testable in the field but invisible in classroom-style tasks",
        representative_literature="Liebenberg, 'The Art of Tracking: The Origin of Science' (1990)",
    ),
    CognitiveCapacity(
        population_descriptor="Inuit children, Arctic",
        capacity="Long-range spatial dead-reckoning across feature-poor terrain",
        constraint_context="Sea-ice and tundra navigation where landmarks are ambiguous or absent",
        measurement_status="Partially measured (mental-rotation tasks); ecological measures rare",
        typical_deficit_label="Poor verbal-spatial test performance on schooled instruments",
        ecological_validity="Standard mental-rotation tests under-predict actual field navigation skill",
        representative_literature="Aporta; Kleinfeld; Nisbett's reviews of geographical cognition",
    ),
    CognitiveCapacity(
        population_descriptor="Children in dense extended-kinship systems",
        capacity="Tracking 30+ named individuals' obligations, alliances, and taboos in real time",
        constraint_context="Polygamous / clan-structured / multi-generational households",
        measurement_status="Unmeasured by Western dyadic social-cognition instruments",
        typical_deficit_label="Poor theory-of-mind on Sally-Anne / false-belief tasks",
        ecological_validity="False-belief tasks miss the multi-actor social complexity routinely handled",
        representative_literature="Hewlett et al. on Aka and Bofi child cognition",
    ),
    CognitiveCapacity(
        population_descriptor="Multilingual children at colonial linguistic boundaries",
        capacity="Code-switching with audience-appropriate register and content filtering",
        constraint_context="Three to five languages used across school, market, household, ceremony",
        measurement_status="Often counted as interference in monolingual psychometrics",
        typical_deficit_label="Language delay / mixed dominance / 'semilingualism'",
        ecological_validity="Executive-function advantages now documented but late-acknowledged",
        representative_literature="Bialystok; Kovacs & Mehler",
    ),
    CognitiveCapacity(
        population_descriptor="Children in resource-scarce households",
        capacity="Long-horizon resource planning under uncertainty; opportunistic substitution; repair-over-replace fluency",
        constraint_context="Scarcity makes each decision multi-criteria and partially reversible",
        measurement_status="Tested as 'delay discounting'; framing inverts the finding",
        typical_deficit_label="High delay-discounting / impulsive",
        ecological_validity="Apparent impulsivity is a rational response to an empirically unreliable institutional future",
        representative_literature="Mani et al. (Science, 2013); Mullainathan & Shafir 'Scarcity' (2013)",
    ),
    CognitiveCapacity(
        population_descriptor="Children apprenticed in plant-use cultures",
        capacity="Multi-attribute discrimination of hundreds of taxa with use, season, and location",
        constraint_context="Subsistence and pharmacopoeia depend on getting it right",
        measurement_status="Vocabulary tests count tokens, not the underlying knowledge graph",
        typical_deficit_label="Low vocabulary on age-normed receptive vocabulary instruments",
        ecological_validity="Domain vocabulary in the relevant taxonomy exceeds urban peers by orders of magnitude",
        representative_literature="Atran & Medin: 'The Native Mind and the Cultural Construction of Nature' (2008)",
    ),
    CognitiveCapacity(
        population_descriptor="Apprentices in weaving / textile traditions",
        capacity="Symmetry-group reasoning, modular arithmetic, error detection across long pattern sequences",
        constraint_context="Pattern integrity matters across thousands of operations with no undo",
        measurement_status="Geometry tests examine schooled formal proofs, not embodied symmetry reasoning",
        typical_deficit_label="Low formal geometry performance",
        ecological_validity="Symmetry-group recognition in textiles is documented to exceed undergraduate baselines",
        representative_literature="Washburn & Crowe 'Symmetries of Culture' (1988)",
    ),
    CognitiveCapacity(
        population_descriptor="Children in displaced and post-conflict communities",
        capacity="Threat-cue calibration; rapid trust assessment; multi-route mobility planning",
        constraint_context="Environments where the assumption of safety would be incorrect",
        measurement_status="Coded as hypervigilance / anxiety in clinical instruments",
        typical_deficit_label="PTSD-spectrum symptoms",
        ecological_validity="Same response set is adaptive in the original context; pathology framing imports a different baseline",
        representative_literature="Summerfield critique of trauma-import models",
    ),
]


def by_keyword(kw: str) -> List[CognitiveCapacity]:
    kw = kw.lower()
    return [c for c in CASES if kw in (c.capacity + " " + c.constraint_context).lower()]


def deficit_pairs():
    return [(c.typical_deficit_label, c.capacity) for c in CASES]


if __name__ == "__main__":
    print("COGNITIVE SUBSTRATE  --  deficit label vs actual capacity")
    print("=" * 76)
    for label, cap in deficit_pairs():
        print(f"\n  labeled:    {label}")
        print(f"  actually:   {cap}")
