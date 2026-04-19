"""
resilience_stack.py

Coupled three-layer resilience architecture for detecting failure modes
in systems that optimize over incomplete or documentation-biased models.

LAYER 1: AbsenceSignatures
Marks the shape of knowledge holes in any system model.
Falsifiable parameters for what is NOT in training data.

LAYER 2: ConstraintNavigator
Models problem-solving as bounded-safety constraint-space navigation.
The grammar of substrate-first thinking, made legible.

LAYER 3: RegulatoryScopeAudit
Audits rules/laws/certifications for scope, parameters, expiration.
Flags unbounded regulations as fraud/gatekeeping vectors.

Coupling: Layer 1 identifies what the system cannot see.
Layer 2 shows how bounded-competence navigates those gaps.
Layer 3 shows how unbounded rules weaponize the same gaps.

CC0 | stdlib only | JinnZ2
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
import json


# ============================================================
# LAYER 1: ABSENCE SIGNATURES
# ============================================================

class AbsenceType(Enum):
    CONSTRAINT_LITERACY = "constraint_literacy"            # substrate-first thinking
    BOUNDED_COMPETENCE = "bounded_competence"              # knowing one's own limits
    RELATIONAL_KNOWLEDGE = "relational_knowledge"          # meal-table / landscape
    REPAIR_NETWORKS = "repair_networks"                    # uninvoiced preservation work
    TRANSLATION_BRIDGES = "translation_bridges"            # undocumented intermediaries
    SELF_SUFFICIENCY_GRAMMAR = "self_sufficiency_grammar"  # start-from-zero knowledge


@dataclass
class AbsenceSignature:
    """
    A falsifiability marker for knowledge the system cannot see.
    Does NOT document the knowledge itself -- documents the shape of the hole.
    """
    absence_type: AbsenceType
    description: str
    distortion_signatures: list[str]   # what breaks when this layer is absent
    measurable_proxies: list[str]      # observable correlates of the absence
    falsifiable_claim: str             # how to disprove the absence matters

    def is_present_in_model(self, model_capabilities: list[str]) -> bool:
        """Returns True if model explicitly accounts for this absence."""
        return self.absence_type.value in model_capabilities


def default_absence_registry() -> list[AbsenceSignature]:
    """Baseline registry of structural absences in documentation-biased systems."""
    return [
        AbsenceSignature(
            absence_type=AbsenceType.CONSTRAINT_LITERACY,
            description="Ability to read problems as navigable constraint geometry rather than resource-acquisition tasks.",
            distortion_signatures=[
                "System demands resources it assumes are infinite",
                "Substitution requests treated as unsolvable",
                "Novel constraints produce cascade failure instead of adaptation",
                "Budget overruns correlate with lack of material substitution paths",
            ],
            measurable_proxies=[
                "ratio of problems solved by purchase vs. substitution",
                "failure rate when supply chain interrupted",
                "time-to-workaround when standard part unavailable",
            ],
            falsifiable_claim="If systems with high constraint-literacy fail at equal or higher rates than low-literacy systems under resource interruption, this absence does not matter.",
        ),
        AbsenceSignature(
            absence_type=AbsenceType.BOUNDED_COMPETENCE,
            description="Self-knowledge of operational limits; ability to operate safely within known bounds without external certification.",
            distortion_signatures=[
                "Uniform safety controls replace selection for self-regulation",
                "Compliance fatigue and visual numbness from over-broad controls",
                "Organizations hire for likability instead of limit-awareness",
                "High-capability operators forced through credential loops",
            ],
            measurable_proxies=[
                "injury rate vs. control-layer count (expect inverse correlation under healthy selection)",
                "proportion of hiring decisions citing measurable capability vs. social fit",
                "rate of contextual exception handling in safety frameworks",
            ],
            falsifiable_claim="If incident rates do not improve when selection shifts from credential-match to limit-awareness assessment, bounded competence is not a protective factor.",
        ),
        AbsenceSignature(
            absence_type=AbsenceType.RELATIONAL_KNOWLEDGE,
            description="Landscape-encoded, meal-table-transmitted, multi-generational knowledge that does not self-document.",
            distortion_signatures=[
                "AI training data systematically underweights non-published expertise",
                "Forecasts miss failure modes operating in undocumented systems",
                "Cultural knowledge classified as 'ceremonial' when it is experimental architecture",
            ],
            measurable_proxies=[
                "divergence between AI-predicted outcomes and actual outcomes in rural/traditional contexts",
                "correlation between knowledge-holder density and community resilience under stress",
            ],
            falsifiable_claim="If regions with high undocumented-knowledge density show no resilience advantage under system stress, this absence is not load-bearing.",
        ),
        AbsenceSignature(
            absence_type=AbsenceType.REPAIR_NETWORKS,
            description="Uninvoiced, often anonymous preservation and repair work that prevents cascade failures.",
            distortion_signatures=[
                "Value models assign zero weight to prevention",
                "Budget cuts target invisible repair because impact is not in documented metrics",
                "Collapse accelerates when repair layer is removed",
            ],
            measurable_proxies=[
                "ratio of documented maintenance spend to actual system-uptime contribution",
                "cascade-failure rate correlated with repair-network density loss",
            ],
            falsifiable_claim="If removal of uninvoiced repair networks produces no measurable degradation in system resilience, this layer is not load-bearing.",
        ),
        AbsenceSignature(
            absence_type=AbsenceType.TRANSLATION_BRIDGES,
            description="People who move between documented and undocumented knowledge systems but do not self-promote.",
            distortion_signatures=[
                "Credentialing structures filter them out by design",
                "AI training data cannot see their contributions",
                "Top and bottom strata become unable to communicate",
                "System fractures at the layer that used to translate",
            ],
            measurable_proxies=[
                "gap between formal credential holders and actual problem-solvers in any domain",
                "frequency of 'how did this get done?' events with no documented solver",
            ],
            falsifiable_claim="If systems with strong translation-bridge presence show no advantage in adaptive response, this absence is not structurally critical.",
        ),
        AbsenceSignature(
            absence_type=AbsenceType.SELF_SUFFICIENCY_GRAMMAR,
            description="Knowledge of how to start from substrate with no assumed infrastructure.",
            distortion_signatures=[
                "AI reasons about self-sufficiency using romanticized published accounts",
                "Optimization assumes infinite inputs and ignores substrate-building",
                "Collapse scenarios produce mass inability to function",
            ],
            measurable_proxies=[
                "proportion of population that can identify potable water / build shelter / establish food without purchased inputs",
                "divergence between published self-sufficiency advice and field-tested methods",
            ],
            falsifiable_claim="If populations without substrate-grammar fare equally well under infrastructure loss, this knowledge layer is not decisive.",
        ),
    ]


# ============================================================
# LAYER 2: CONSTRAINT NAVIGATOR
# ============================================================

@dataclass
class ConstraintDimension:
    """A single axis of a problem's constraint space."""
    name: str
    current_value: float
    min_safe: float
    max_safe: float
    unit: str

    def within_bounds(self, proposed: float) -> bool:
        return self.min_safe <= proposed <= self.max_safe


@dataclass
class BoundedSolution:
    """
    A solution with explicit bounds and reassessment points.
    Opposite of 'approved universally or banned' regulatory thinking.
    """
    description: str
    valid_conditions: list[str]                        # under what conditions this works
    operating_bounds: dict[str, tuple[float, float]]   # parameter: (min, max)
    reassessment_trigger: str                          # when to stop and re-evaluate
    estimated_duration: str                            # time/distance/cycles bound
    known_failure_modes: list[str]                     # honest limits
    requires_knowledge: list[str]                      # competence required to deploy safely


@dataclass
class ConstraintProblem:
    """A problem framed as navigable constraint geometry."""
    statement: str
    dimensions: list[ConstraintDimension]
    available_materials: list[str]
    available_tools: list[str]
    safety_bounds: dict[str, str]                      # parameter: limit description
    time_pressure: Optional[str] = None

    def substitution_space(self) -> list[str]:
        """Enumerate material/tool combinations within constraint bounds."""
        return [
            f"{mat} + {tool}"
            for mat in self.available_materials
            for tool in self.available_tools
        ]


class ConstraintNavigator:
    """
    Models problem-solving as constraint-space navigation rather than
    resource-acquisition. Substrate-first, bounded-safety.
    """

    def frame_problem(self, problem: ConstraintProblem) -> dict:
        """Return a structural view of the problem as navigable space."""
        return {
            "statement": problem.statement,
            "degrees_of_freedom": len(problem.dimensions),
            "substitution_options": len(problem.substitution_space()),
            "bounded_safety_parameters": problem.safety_bounds,
            "time_pressure": problem.time_pressure,
            "navigation_grammar": "constraint_space" if problem.dimensions else "resource_acquisition",
        }

    def propose_bounded_solution(
        self,
        problem: ConstraintProblem,
        chosen_materials: list[str],
        duration_bound: str,
        reassessment: str,
        known_limits: list[str],
    ) -> BoundedSolution:
        """
        Build a solution with explicit bounds, not universal approval.
        Example: 'aluminum patch holds to 30 miles, then stop and reassess'.
        """
        return BoundedSolution(
            description=f"Apply {', '.join(chosen_materials)} to resolve: {problem.statement}",
            valid_conditions=[
                f"dimension {d.name} within [{d.min_safe}, {d.max_safe}] {d.unit}"
                for d in problem.dimensions
            ],
            operating_bounds={d.name: (d.min_safe, d.max_safe) for d in problem.dimensions},
            reassessment_trigger=reassessment,
            estimated_duration=duration_bound,
            known_failure_modes=known_limits,
            requires_knowledge=["material behavior", "constraint reading", "self-limit awareness"],
        )


# ============================================================
# LAYER 3: REGULATORY SCOPE AUDIT
# ============================================================

@dataclass
class Regulation:
    """A law, rule, certification requirement, or safety control."""
    identifier: str
    stated_intent: str
    scope_defined: bool                    # is the scope explicitly bounded?
    parameters_measurable: bool            # are outcomes measurable?
    expiration_or_renewal: bool            # does it expire or require renewal?
    exception_handling: bool               # does it allow bounded exceptions?
    root_cause_linked: bool                # tied to actual root cause?
    outcome_metric: Optional[str] = None
    known_perverse_effects: list[str] = field(default_factory=list)


@dataclass
class RegulationAudit:
    identifier: str
    stated_intent: str
    scope_score: int                       # 0-5
    weaponization_risk: int                # 0-5 (higher = more gatekeeping potential)
    flags: list[str]
    recommendation: str


class RegulatoryScopeAudit:
    """
    Audits regulations for scope/parameter/expiration discipline.
    Flags unbounded rules as fraud/gatekeeping vectors.

    Core claim: Rules without bounded scope produce selective enforcement,
    which produces gatekeeping, which produces corruption.
    """

    def audit(self, reg: Regulation) -> RegulationAudit:
        flags = []
        scope_score = 0

        if reg.scope_defined:
            scope_score += 1
        else:
            flags.append("SCOPE_UNBOUNDED: rule applies without contextual limits")

        if reg.parameters_measurable:
            scope_score += 1
        else:
            flags.append("OUTCOME_UNMEASURABLE: compliance cannot be objectively verified")

        if reg.expiration_or_renewal:
            scope_score += 1
        else:
            flags.append("NO_EXPIRATION: rule persists regardless of continued relevance")

        if reg.exception_handling:
            scope_score += 1
        else:
            flags.append("NO_EXCEPTION_GRAMMAR: bounded-competence solutions blocked")

        if reg.root_cause_linked:
            scope_score += 1
        else:
            flags.append("ROOT_CAUSE_SKIPPED: treats symptoms via uniform control")

        weaponization_risk = 5 - scope_score

        if weaponization_risk >= 4:
            recommendation = (
                "HIGH RISK: likely used for gatekeeping, not safety. "
                "Rewrite with bounded scope, measurable outcome, expiration, exception handling."
            )
        elif weaponization_risk >= 2:
            recommendation = "MODERATE RISK: selective enforcement possible. Tighten scope and add outcome metric."
        else:
            recommendation = "LOW RISK: reasonably bounded. Monitor for perverse effects."

        return RegulationAudit(
            identifier=reg.identifier,
            stated_intent=reg.stated_intent,
            scope_score=scope_score,
            weaponization_risk=weaponization_risk,
            flags=flags,
            recommendation=recommendation,
        )


# ============================================================
# COUPLED STACK
# ============================================================

@dataclass
class ResilienceAssessment:
    absences_unaccounted: list[str]
    constraint_literacy_present: bool
    high_risk_regulations: list[str]
    cascade_vulnerability_score: int       # 0-10
    notes: list[str]


class ResilienceStack:
    """
    Coupled pipeline:
    AbsenceSignatures -> ConstraintNavigator -> RegulatoryScopeAudit
    Identifies where a system is structurally blind AND institutionally
    hardened against the competence that would fix it.
    """

    def __init__(self):
        self.absence_registry = default_absence_registry()
        self.navigator = ConstraintNavigator()
        self.auditor = RegulatoryScopeAudit()

    def assess(
        self,
        model_capabilities: list[str],
        regulations: list[Regulation],
        constraint_literacy_present: bool,
    ) -> ResilienceAssessment:
        unaccounted = [
            sig.absence_type.value
            for sig in self.absence_registry
            if not sig.is_present_in_model(model_capabilities)
        ]
        audits = [self.auditor.audit(r) for r in regulations]
        high_risk = [a.identifier for a in audits if a.weaponization_risk >= 4]

        # Cascade vulnerability: unaccounted absences + high-risk regulations
        # minus presence of constraint-literacy as protective factor.
        cascade = min(10, len(unaccounted) + len(high_risk) - (2 if constraint_literacy_present else 0))
        cascade = max(0, cascade)

        notes = []
        if unaccounted and high_risk:
            notes.append(
                "System blind to critical layers AND institutionally gatekeeping the people "
                "who could fill them. Expect accelerated failure under stress."
            )
        if not constraint_literacy_present:
            notes.append("No constraint-literacy protective factor. System assumes resource availability.")
        if cascade >= 7:
            notes.append("Cascade vulnerability HIGH. Parallel adaptive systems will emerge whether sanctioned or not.")

        return ResilienceAssessment(
            absences_unaccounted=unaccounted,
            constraint_literacy_present=constraint_literacy_present,
            high_risk_regulations=high_risk,
            cascade_vulnerability_score=cascade,
            notes=notes,
        )

    def to_json(self, assessment: ResilienceAssessment) -> str:
        return json.dumps(asdict(assessment), indent=2)


# ============================================================
# DEMO / SELF-TEST
# ============================================================

if __name__ == "__main__":
    stack = ResilienceStack()

    # Example: a documentation-biased system with uniform safety controls
    example_regs = [
        Regulation(
            identifier="WETLAND_REMEDIATION_APPROVAL",
            stated_intent="prevent wetland pollution",
            scope_defined=False,
            parameters_measurable=False,
            expiration_or_renewal=False,
            exception_handling=False,
            root_cause_linked=False,
        ),
        Regulation(
            identifier="UNIVERSAL_HIVIS_VEST",
            stated_intent="reduce forklift area injuries",
            scope_defined=True,
            parameters_measurable=False,
            expiration_or_renewal=False,
            exception_handling=False,
            root_cause_linked=False,
            known_perverse_effects=["visual numbness from uniform color", "compliance fatigue"],
        ),
        Regulation(
            identifier="BOUNDED_PATCH_REPAIR_30MI",
            stated_intent="allow field repair with reassessment",
            scope_defined=True,
            parameters_measurable=True,
            expiration_or_renewal=True,
            exception_handling=True,
            root_cause_linked=True,
            outcome_metric="vehicle reaches service point without secondary failure",
        ),
    ]

    # Example: a model that only sees published expertise
    model_caps: list[str] = []  # nothing accounted for

    assessment = stack.assess(
        model_capabilities=model_caps,
        regulations=example_regs,
        constraint_literacy_present=False,
    )

    print(stack.to_json(assessment))
