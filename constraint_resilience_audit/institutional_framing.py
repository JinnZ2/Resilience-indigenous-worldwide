"""Institutional framing: how studies measure deficit vs capacity.

The meta-layer. The choices baked into instrument design, sampling
frames, baseline-setting, and reporting conventions determine which
capacities become visible as 'present' and which become recorded as
'lacking.' These are not neutral choices; they encode the priorities
and assumptions of the institutions doing the measuring, and they
tend to render invisible exactly those capacities that constrained
populations have built.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class FramingDistortion:
    instrument_or_study_type: str
    baseline_assumption: str
    what_it_measures: str
    what_it_silently_assumes_normal: str
    what_it_renders_invisible: str
    typical_conclusion_drawn: str


DISTORTIONS: List[FramingDistortion] = [
    FramingDistortion(
        instrument_or_study_type="IQ batteries (Wechsler, Stanford-Binet, Raven)",
        baseline_assumption="Schooled, literate, individualistic problem-solving is the target capacity",
        what_it_measures="Decontextualized verbal/visual reasoning under examiner-paced time pressure",
        what_it_silently_assumes_normal="Test-taking as a familiar social act; dyadic examiner-examinee rapport; item content drawn from one knowledge tradition",
        what_it_renders_invisible="Collaborative problem-solving, ecological reasoning, multi-actor social cognition, long-horizon planning",
        typical_conclusion_drawn="Population X has a 'cognitive gap'",
    ),
    FramingDistortion(
        instrument_or_study_type="School-readiness screens",
        baseline_assumption="Letter recognition and decontextualized counting predict learning",
        what_it_measures="Pre-literate proxies for schooled academic performance",
        what_it_silently_assumes_normal="Print-saturated, individually-instructed early environments",
        what_it_renders_invisible="Oral memory, kinship reasoning, observational-apprenticeship readiness, manual fluency",
        typical_conclusion_drawn="Child enters school 'behind'",
    ),
    FramingDistortion(
        instrument_or_study_type="GDP / cash-income poverty measures",
        baseline_assumption="Wellbeing flows through monetized exchange",
        what_it_measures="Cash flows that touch formal markets",
        what_it_silently_assumes_normal="Subsistence, reciprocity, and the commons are residual or invisible",
        what_it_renders_invisible="Food sovereignty, non-monetary mutual aid, ecological wealth, time wealth, skill stock",
        typical_conclusion_drawn="Community lives 'below the poverty line'",
    ),
    FramingDistortion(
        instrument_or_study_type="Nutrition surveys (24-hour recall, fixed micronutrient panel)",
        baseline_assumption="Calories plus a fixed nutrient list define dietary adequacy",
        what_it_measures="Energy and ~20 standardized nutrients on a small sample of intake",
        what_it_silently_assumes_normal="The industrial reference diet is the implicit comparator",
        what_it_renders_invisible="Phytochemical diversity, seasonal cycling, fermentation effects, traditional preparation that changes bioavailability, microbiome-support diversity",
        typical_conclusion_drawn="Diet is 'deficient' in nutrient X",
    ),
    FramingDistortion(
        instrument_or_study_type="Mental-health diagnostic categories (DSM-derived)",
        baseline_assumption="Distress maps to discrete intra-individual disorders",
        what_it_measures="Symptom checklists against a single cultural template",
        what_it_silently_assumes_normal="Distress is private; sociopolitical context is not part of the diagnosis",
        what_it_renders_invisible="Collective grief, displacement injury, cultural-loss syndromes, responses considered functional in the original context",
        typical_conclusion_drawn="Individual has disorder Y; community has elevated prevalence",
    ),
    FramingDistortion(
        instrument_or_study_type="Developmental milestone charts",
        baseline_assumption="A single normed trajectory describes healthy development",
        what_it_measures="Age-of-acquisition for a Western-defined ordered list",
        what_it_silently_assumes_normal="Independent infant sleep, age-graded peer groups, individual feeding milestones",
        what_it_renders_invisible="Alloparenting competence, kin-network social milestones, observational-learning competence",
        typical_conclusion_drawn="Child is 'delayed' on item Z",
    ),
    FramingDistortion(
        instrument_or_study_type="Housing-adequacy / infrastructure surveys",
        baseline_assumption="Permanent, single-family, piped-utility housing is the floor of adequacy",
        what_it_measures="Presence/absence of fixed infrastructure",
        what_it_silently_assumes_normal="Sedentism, nuclear-family housing, grid-tied services",
        what_it_renders_invisible="Mobile architectures, seasonal dwellings, low-input thermal regulation, off-grid water systems, repair-economy resilience",
        typical_conclusion_drawn="Housing is 'substandard'",
    ),
    FramingDistortion(
        instrument_or_study_type="Education attainment metrics (years-of-schooling)",
        baseline_assumption="Time-in-classroom is the unit of learning",
        what_it_measures="Enrollment and credentialing flow through formal institutions",
        what_it_silently_assumes_normal="Knowledge is transmitted through age-graded classroom hours",
        what_it_renders_invisible="Apprenticeship, ceremonial knowledge transmission, language inheritance, place-based curriculum",
        typical_conclusion_drawn="Population has 'low educational attainment'",
    ),
    FramingDistortion(
        instrument_or_study_type="Labor-force participation surveys",
        baseline_assumption="Work is monetized employment with an employer",
        what_it_measures="Hours sold to a wage-paying entity",
        what_it_silently_assumes_normal="Care work, subsistence work, and reciprocal labor are not labor",
        what_it_renders_invisible="Subsistence agriculture, kin care, ceremonial labor, repair and maintenance",
        typical_conclusion_drawn="Population has 'low labor-force participation'",
    ),
]


def render_invisible_for(area_keyword: str) -> List[FramingDistortion]:
    kw = area_keyword.lower()
    return [d for d in DISTORTIONS if kw in d.instrument_or_study_type.lower()]


def systematic_blind_spots() -> List[str]:
    return [d.what_it_renders_invisible for d in DISTORTIONS]


def framing_check(instrument_description: str) -> List[FramingDistortion]:
    """Suggest framing risks for an instrument description by keyword match."""
    desc = instrument_description.lower()
    hits = []
    for d in DISTORTIONS:
        toks = set(d.instrument_or_study_type.lower().replace("/", " ").split())
        if any(t for t in toks if len(t) > 3 and t in desc):
            hits.append(d)
    return hits


if __name__ == "__main__":
    print("INSTITUTIONAL FRAMING  --  what each instrument renders invisible")
    print("=" * 76)
    for d in DISTORTIONS:
        print(f"\n  {d.instrument_or_study_type}")
        print(f"    assumes normal:    {d.what_it_silently_assumes_normal}")
        print(f"    renders invisible: {d.what_it_renders_invisible}")
        print(f"    typical conclusion: {d.typical_conclusion_drawn}")
