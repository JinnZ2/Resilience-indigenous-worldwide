"""
substrate_damage_audit.py

Audit module flagging when behavioral, psychological, and collapse-prediction
models are built on populations exhibiting institutional substrate damage
rather than baseline human capacity.

Core metrology problem:
Most "human nature" and "collapse behavior" models train on populations
several generations into accumulated institutional stress (chronic racism,
patriarchy, socioeconomic hierarchy, ecological disconnection). Measured
fragility is misread as biological universal. Resulting predictions then
justify policies that deepen the damage, closing a self-validating loop.

This module encodes the cascade as falsifiable claims with detection signals,
scoring dimensions, and a scope-audit gate. CC0. Standard library only.

License: CC0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional
from enum import Enum

# -----------------------------------------------------------
# CLAIM REGISTRY
# -----------------------------------------------------------

class Confidence(Enum):
    HIGH = "high"            # multiple independent lines of evidence
    MODERATE = "moderate"    # converging but partial evidence
    LOW = "low"              # plausible mechanism, limited direct data


@dataclass
class Claim:
    id: str
    statement: str
    mechanism: str
    falsifier: str            # what observation would refute
    confirmer: str            # what observation would confirm
    confidence: Confidence
    references: List[str] = field(default_factory=list)


CLAIMS: List[Claim] = [

    Claim(
        id="C1_collapse_models_on_damaged_substrate",
        statement=(
            "Collapse-prediction and crisis-behavior models trained on "
            "Western institutional-stress populations measure damage "
            "pathology, not baseline human capacity."
        ),
        mechanism=(
            "Training populations exhibit chronic stress activation, "
            "kinship-network atrophy, and ecological disconnection. "
            "Observed fragility is an artifact of these conditions, not "
            "a species-level property."
        ),
        falsifier=(
            "Equivalent fragility patterns observed in populations with "
            "intact kinship networks, low chronic institutional stress, "
            "and high ecological embeddedness."
        ),
        confirmer=(
            "Adaptive-capacity differential between high-stress and "
            "low-stress substrates exceeds within-group variance."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="C2_chronic_stress_alters_substrate",
        statement=(
            "Chronic institutional stress (systemic racism, hierarchical "
            "subordination, socioeconomic precarity) produces measurable "
            "epigenetic, endocrine, and immune changes that confound "
            "downstream behavioral and psychological measurement."
        ),
        mechanism=(
            "Sustained HPA-axis activation alters glucocorticoid receptor "
            "expression; inflammatory cytokine baselines shift; placental "
            "function during gestation is sensitized; offspring inherit "
            "altered stress-response architecture."
        ),
        falsifier=(
            "Removal of chronic stressors fails to normalize endocrine "
            "and inflammatory markers within one to two generations."
        ),
        confirmer=(
            "Documented epigenetic recovery in populations transitioning "
            "out of high-stress conditions; observed convergence toward "
            "low-stress-population baselines."
        ),
        confidence=Confidence.HIGH,
        references=[
            "Amedor & Giussani, Trends in Endocrinology & Metabolism, "
            "April 2026: physiological mechanisms mediating "
            "socio-environmental influences on pregnancy outcomes."
        ],
    ),

    Claim(
        id="C3_low_institutional_stress_communities_show_different_patterns",
        statement=(
            "Communities with intact kinship networks, distributed "
            "decision-making, and ecological embeddedness exhibit "
            "adaptive recovery patterns under disaster and crisis that "
            "differ structurally from Western-population responses."
        ),
        mechanism=(
            "Network-distributed load-bearing reduces individual stress "
            "concentration. Pre-tested generational knowledge provides "
            "operational adaptation rather than narrative-only coping. "
            "Substrate fluency in real constraint (weather, terrain, "
            "biology) yields functional response under disruption."
        ),
        falsifier=(
            "Matched-disaster comparison shows equivalent PTSD rates, "
            "recovery timelines, and adaptive behavior between Western "
            "and traditional-network populations."
        ),
        confirmer=(
            "Lower individual-fragility metrics and faster functional "
            "recovery in network-embedded populations, persisting after "
            "controlling for disaster severity."
        ),
        confidence=Confidence.MODERATE,
    ),

    Claim(
        id="C4_escape_narratives_as_symptom",
        statement=(
            "Escape narratives (transhumanism, AI-replacement, "
            "body-rejection, off-world migration) correlate with "
            "high-institutional-stress populations and should be read "
            "as substrate-damage symptom, not as evidence of human "
            "biological inadequacy."
        ),
        mechanism=(
            "Sustained institutional damage with no clear external "
            "attribution channel produces displaced rejection of the "
            "self or species. Frame shifts from 'system harmed me' to "
            "'humanity is limited.' Escape impulse becomes culturally "
            "amplified by the same institutions causing the damage."
        ),
        falsifier=(
            "Populations in low-institutional-stress conditions generate "
            "escape narratives at equivalent rates and intensities."
        ),
        confirmer=(
            "Escape-narrative incidence and intensity scale with "
            "institutional-stress markers; declines observed where "
            "stress is reduced and community fluency restored."
        ),
        confidence=Confidence.MODERATE,
    ),

    Claim(
        id="C5_disaster_research_methodologically_biased",
        statement=(
            "Disaster and collapse research generalizes from "
            "non-equivalent populations. Comparing damaged-substrate "
            "samples to less-damaged samples without flagging substrate "
            "state as a primary variable invalidates universal claims "
            "about 'human behavior under stress.'"
        ),
        mechanism=(
            "Methodological bias treats Western individual-psychology "
            "frameworks as universal. Traditional-network resilience "
            "data, where present, is reframed as 'cultural coping' "
            "rather than evidence of substrate baseline. The damaged "
            "sample is implicitly treated as control."
        ),
        falsifier=(
            "Re-analysis of disaster literature shows substrate-state "
            "variables fully accounted for and traditional-network "
            "populations treated as comparison baseline rather than "
            "cultural outlier."
        ),
        confirmer=(
            "Systematic review reveals substrate-state confound left "
            "uncorrected across the majority of cited collapse-behavior "
            "literature."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="C6_multigenerational_compounding",
        statement=(
            "Epigenetic and developmental damage from chronic "
            "institutional stress compounds across generations. Current "
            "'baseline' human-capacity measurements are taken several "
            "generations into accumulated harm and cannot represent "
            "unstressed substrate."
        ),
        mechanism=(
            "Maternal stress during gestation alters fetal HPA-axis "
            "calibration; resulting offspring enter adulthood "
            "pre-sensitized; their own gestational environments transmit "
            "further calibration shifts. No living Western-industrial "
            "cohort exists without inherited accumulation."
        ),
        falsifier=(
            "Cross-generational stress-marker data show stability "
            "rather than compounding."
        ),
        confirmer=(
            "Stress-marker baselines drift across generations in "
            "directions consistent with sustained institutional load."
        ),
        confidence=Confidence.MODERATE,
    ),

    Claim(
        id="C7_hierarchy_as_substrate_degradation",
        statement=(
            "Patriarchy, racial hierarchy, and rigid socioeconomic "
            "stratification are not only ethical problems but measurable "
            "substrate degradation affecting reproductive biology and "
            "population-level resilience."
        ),
        mechanism=(
            "Hierarchical stress is biologically transmitted through "
            "gestational physiology. Suppressed genetic and phenotypic "
            "diversity reduces population adaptive capacity. Damage "
            "extends to populations in dominant tiers via different "
            "pathways (isolation, constraint-blindness, dependency on "
            "artificial supports)."
        ),
        falsifier=(
            "Populations under rigid hierarchy show equivalent "
            "resilience metrics to populations with distributed "
            "decision-making and reciprocal stewardship."
        ),
        confirmer=(
            "Hierarchical-stress populations exhibit reduced adaptive "
            "capacity across multiple substrate measures, independent "
            "of position in hierarchy."
        ),
        confidence=Confidence.HIGH,
        references=[
            "Cambridge / Amedor & Giussani 2026: Black women nearly "
            "three times more likely to die in pregnancy, with "
            "physiological mediation by chronic socio-environmental "
            "stress."
        ],
    ),
]


# -----------------------------------------------------------
# SCORING DIMENSIONS
# -----------------------------------------------------------

DIMENSIONS: Dict[str, str] = {
    "substrate_state_flagged": (
        "Does the model explicitly treat institutional-stress substrate "
        "state as a primary variable rather than implicit constant?"
    ),
    "comparison_population_balanced": (
        "Are low-institutional-stress populations included as comparison, "
        "or is a damaged sample treated as control?"
    ),
    "generational_accumulation_acknowledged": (
        "Does the model account for multi-generational epigenetic "
        "compounding, or treat current cohorts as unstressed baseline?"
    ),
    "fragility_attribution": (
        "Is observed fragility attributed to biology / species nature, "
        "or to institutional substrate damage?"
    ),
    "kinship_network_treatment": (
        "Are kinship and ecological-network variables coded as "
        "load-bearing infrastructure or as optional cultural variables?"
    ),
    "escape_narrative_handling": (
        "Are escape impulses (transhumanism, body-rejection, off-world) "
        "treated as evidence about humanity, or as substrate-damage "
        "symptom in the measured population?"
    ),
    "feedback_loop_disclosed": (
        "Does the model disclose that its predictions inform policies "
        "that further alter the substrate it is measuring?"
    ),
    "falsifiability": (
        "Are the model's claims about human capacity falsifiable through "
        "low-stress-population comparison?"
    ),
    "policy_recommendation_direction": (
        "Do recommendations reduce institutional stress, or tighten "
        "control 'in preparation' for the fragility being measured?"
    ),
    "metrology_audit": (
        "Are measurement instruments themselves validated outside the "
        "damaged population, or are they self-referential to it?"
    ),
}


# -----------------------------------------------------------
# SCOPE-AUDIT GATE
# -----------------------------------------------------------

@dataclass
class ModelDescriptor:
    """
    Light-weight descriptor of a behavioral / collapse / capacity model
    being audited. Fields are flags (0 or 1) or short strings; the audit
    function flags where the model fails substrate-aware scope.
    """
    name: str
    substrate_state_flagged: int = 0
    comparison_population_balanced: int = 0
    generational_accumulation_acknowledged: int = 0
    fragility_attributed_to_biology: int = 1  # default-failure direction
    kinship_network_as_load_bearing: int = 0
    escape_narratives_as_symptom: int = 0
    feedback_loop_disclosed: int = 0
    falsifiable_by_low_stress_comparison: int = 0
    recommends_stress_reduction: int = 0
    metrology_validated_outside_sample: int = 0


def audit(model: ModelDescriptor) -> Dict[str, object]:
    """
    Run the scope-audit gate. Returns a dict with score, flagged
    dimensions, and a verdict on whether the model's conclusions
    about 'human nature' are admissible.
    """
    checks = {
        "substrate_state_flagged":
            model.substrate_state_flagged,
        "comparison_population_balanced":
            model.comparison_population_balanced,
        "generational_accumulation_acknowledged":
            model.generational_accumulation_acknowledged,
        "fragility_attribution":
            1 - model.fragility_attributed_to_biology,
        "kinship_network_treatment":
            model.kinship_network_as_load_bearing,
        "escape_narrative_handling":
            model.escape_narratives_as_symptom,
        "feedback_loop_disclosed":
            model.feedback_loop_disclosed,
        "falsifiability":
            model.falsifiable_by_low_stress_comparison,
        "policy_recommendation_direction":
            model.recommends_stress_reduction,
        "metrology_audit":
            model.metrology_validated_outside_sample,
    }

    score = sum(checks.values())
    max_score = len(checks)
    flagged = [k for k, v in checks.items() if v == 0]

    if score >= 8:
        verdict = "ADMISSIBLE: substrate-aware scope"
    elif score >= 5:
        verdict = "PARTIAL: substrate-aware but with gaps"
    elif score >= 2:
        verdict = "CONTAMINATED: claims about 'human nature' not admissible"
    else:
        verdict = "FULLY CAPTURED: measuring institutional damage as nature"

    return {
        "model": model.name,
        "score": f"{score}/{max_score}",
        "verdict": verdict,
        "passed": [k for k, v in checks.items() if v == 1],
        "flagged": flagged,
    }


# -----------------------------------------------------------
# RESEARCH AGENDA (open questions worth funding / running)
# -----------------------------------------------------------

RESEARCH_QUESTIONS: List[str] = [
    "Disaster-recovery comparison: matched events across "
    "kinship-networked traditional communities and Western individualist "
    "populations, with substrate-stress markers as primary variable.",

    "Multi-generational stress-marker drift: longitudinal epigenetic "
    "data across three or more generations in (a) populations exiting "
    "high-stress conditions and (b) populations under sustained stress.",

    "Escape-narrative incidence by substrate-stress load: prevalence "
    "of transhumanist / body-rejection / off-world frameworks across "
    "populations stratified by institutional-stress markers.",

    "Hierarchy-tier resilience differential: adaptive-capacity metrics "
    "across positions in hierarchical systems, including dominant tiers, "
    "controlling for substrate-stress exposure pathway.",

    "Recovery latency: how rapidly do endocrine, immune, and "
    "behavioral markers normalize after removal of chronic institutional "
    "stressors, at individual and generational scales?",

    "Methodological audit of collapse-modeling literature: systematic "
    "review of substrate-state treatment in cited human-behavior-under-"
    "stress studies.",

    "Adaptive-capacity ceiling: in populations with low chronic stress, "
    "intact kinship networks, and ecological embeddedness, what is the "
    "upper bound on human problem-solving, recovery, and innovation? "
    "Current baselines almost certainly underestimate this."
]


# -----------------------------------------------------------
# DEMO / SELF-TEST
# -----------------------------------------------------------

if __name__ == "__main__":

    print("=" * 64)
    print("SUBSTRATE DAMAGE AUDIT")
    print("=" * 64)
    print(f"\n{len(CLAIMS)} falsifiable claims registered.")
    print(f"{len(DIMENSIONS)} scoring dimensions defined.")
    print(f"{len(RESEARCH_QUESTIONS)} open research questions queued.\n")

    # Example: typical Western collapse-behavior model
    typical_model = ModelDescriptor(
        name="Typical Western Collapse-Behavior Model",
        substrate_state_flagged=0,
        comparison_population_balanced=0,
        generational_accumulation_acknowledged=0,
        fragility_attributed_to_biology=1,
        kinship_network_as_load_bearing=0,
        escape_narratives_as_symptom=0,
        feedback_loop_disclosed=0,
        falsifiable_by_low_stress_comparison=0,
        recommends_stress_reduction=0,
        metrology_validated_outside_sample=0,
    )

    # Example: substrate-aware alternative
    aware_model = ModelDescriptor(
        name="Substrate-Aware Human-Capacity Model",
        substrate_state_flagged=1,
        comparison_population_balanced=1,
        generational_accumulation_acknowledged=1,
        fragility_attributed_to_biology=0,
        kinship_network_as_load_bearing=1,
        escape_narratives_as_symptom=1,
        feedback_loop_disclosed=1,
        falsifiable_by_low_stress_comparison=1,
        recommends_stress_reduction=1,
        metrology_validated_outside_sample=1,
    )

    for m in (typical_model, aware_model):
        result = audit(m)
        print("-" * 64)
        print(f"MODEL:     {result['model']}")
        print(f"SCORE:     {result['score']}")
        print(f"VERDICT:   {result['verdict']}")
        if result["flagged"]:
            print(f"FLAGGED:   {', '.join(result['flagged'])}")
        print()
