"""
support_cartography.py

Layer 0 of the resilience stack.

Maps the shape of zero-support regions in data pipelines WITHOUT attempting
to recover them. Couples the three-gate framework (emission/capture/retention)
to falsifiable absence claims, collapse dynamics, and projection loss.

Core claims (all falsifiable):

    1. Non-representability is a distinct failure mode from bias.
       p=0 regions cannot be recovered by scaling, synthetic augmentation,
       or reweighting.

    2. Three independent gates filter cognition out of data pipelines:
         EMISSION  - does it externalize at all?
         CAPTURE   - if emitted, is it recorded?
         RETENTION - if recorded, is it kept?
       Failure at ANY gate produces zero support downstream.

    3. Synthetic data operates strictly inside existing support:
         Support(D_synthetic) subseteq Support(D_training)
       Recursion contracts support monotonically.

    4. Rare modes decay with half-life approximately ln(0.5)/ln(1 - exp(-p*N))
       when p*N < 1. Projection loss collapses distinct modes into one
       representation regardless of sample size.

Couples upward to: resilience_stack.py (AbsenceSignature layer)

CC0 | stdlib only | JinnZ2
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
import math
import json


# ============================================================
# GATES
# ============================================================

class Gate(Enum):
    EMISSION = "emission"        # does cognition externalize?
    CAPTURE = "capture"          # if emitted, is it instrumented?
    RETENTION = "retention"      # if captured, is it kept?


@dataclass
class GateFailure:
    """A specific failure at a specific gate."""
    gate: Gate
    reason: str
    recoverable_by_synthetic: bool = False   # always False - by definition
    recoverable_by_scaling: bool = False     # always False for zero-support
    recovery_requires: list[str] = field(default_factory=list)


# ============================================================
# COGNITION CLASSES
# ============================================================

@dataclass
class CognitionClass:
    """
    A class of cognition that may or may not survive the data pipeline.
    NOT a person. NOT a knowledge holder. A *type* of thinking/knowing.
    """
    name: str
    description: str
    emission_profile: str                   # how (if at all) it externalizes
    requires_continuous_signal: bool        # true = discrete snapshots insufficient
    requires_full_sensorimotor: bool        # true = embodied, not text/image capturable
    requires_long_horizon: bool             # true = trajectories not slices
    economic_incentive_to_document: float   # 0.0-1.0
    legible_to_classifier: bool             # does labeling infrastructure see it?


def default_cognition_registry() -> list[CognitionClass]:
    """Cognition classes most likely to fail one or more gates."""
    return [
        CognitionClass(
            name="constraint_literacy",
            description="Reading problems as navigable constraint geometry.",
            emission_profile="Manifests in actions/outcomes, rarely narrated.",
            requires_continuous_signal=True,
            requires_full_sensorimotor=False,
            requires_long_horizon=True,
            economic_incentive_to_document=0.1,
            legible_to_classifier=False,
        ),
        CognitionClass(
            name="relational_landscape_knowledge",
            description="Multi-generational landscape-encoded experimental knowledge.",
            emission_profile="Transmitted through meals, walking, physical markers.",
            requires_continuous_signal=True,
            requires_full_sensorimotor=True,
            requires_long_horizon=True,
            economic_incentive_to_document=0.0,
            legible_to_classifier=False,
        ),
        CognitionClass(
            name="repair_network_intelligence",
            description="Anonymous preservation work that prevents cascades.",
            emission_profile="Actions leave no invoice, no attribution, no metric.",
            requires_continuous_signal=False,
            requires_full_sensorimotor=True,
            requires_long_horizon=False,
            economic_incentive_to_document=0.0,
            legible_to_classifier=False,
        ),
        CognitionClass(
            name="bounded_competence_self_knowledge",
            description="Knowing one's own operational limits without external certification.",
            emission_profile="Internal; emits only as decisions-not-made.",
            requires_continuous_signal=True,
            requires_full_sensorimotor=True,
            requires_long_horizon=True,
            economic_incentive_to_document=0.05,
            legible_to_classifier=False,
        ),
        CognitionClass(
            name="translation_bridge_cognition",
            description="Moves between documented and undocumented systems without self-promotion.",
            emission_profile="Actively avoids visibility; emissions attributed elsewhere.",
            requires_continuous_signal=False,
            requires_full_sensorimotor=False,
            requires_long_horizon=True,
            economic_incentive_to_document=0.0,
            legible_to_classifier=False,
        ),
        CognitionClass(
            name="substrate_first_reasoning",
            description="Start-from-zero knowledge of how to build up from nothing.",
            emission_profile="Demonstrated in action under necessity; no textbook form.",
            requires_continuous_signal=True,
            requires_full_sensorimotor=True,
            requires_long_horizon=True,
            economic_incentive_to_document=0.05,
            legible_to_classifier=False,
        ),
        CognitionClass(
            name="analog_field_cognition",
            description="Continuous, non-symbolic, field-based reasoning.",
            emission_profile="Resists tokenization; collapses under discretization.",
            requires_continuous_signal=True,
            requires_full_sensorimotor=False,
            requires_long_horizon=True,
            economic_incentive_to_document=0.1,
            legible_to_classifier=False,
        ),
    ]


# ============================================================
# GATE CLASSIFIER
# ============================================================

class GateClassifier:
    """
    Given a cognition class, identify which gate(s) it fails and why.
    """

    def classify(self, cc: CognitionClass) -> list[GateFailure]:
        failures = []

        # EMISSION gate
        if cc.emission_profile and any(
            marker in cc.emission_profile.lower()
            for marker in ["rarely narrated", "actively avoids", "internal", "leaves no invoice"]
        ):
            failures.append(GateFailure(
                gate=Gate.EMISSION,
                reason=f"Does not externalize in instrumentable form: {cc.emission_profile}",
                recovery_requires=[
                    "interactive probing (not corpus collection)",
                    "induce externalization without distorting the cognition",
                ],
            ))

        # CAPTURE gate
        if cc.requires_continuous_signal or cc.requires_full_sensorimotor or cc.requires_long_horizon:
            reasons = []
            if cc.requires_continuous_signal:
                reasons.append("requires continuous signal (discrete sensors inadequate)")
            if cc.requires_full_sensorimotor:
                reasons.append("requires full sensorimotor loop (text/image projections insufficient)")
            if cc.requires_long_horizon:
                reasons.append("requires long-horizon trajectories (snapshots lose the structure)")
            failures.append(GateFailure(
                gate=Gate.CAPTURE,
                reason="; ".join(reasons),
                recovery_requires=[
                    "new sensing modalities (continuous, embodied, longitudinal)",
                    "trajectory-aware capture rather than snapshot sampling",
                ],
            ))

        # RETENTION gate
        if cc.economic_incentive_to_document < 0.2 or not cc.legible_to_classifier:
            reasons = []
            if cc.economic_incentive_to_document < 0.2:
                reasons.append(f"low incentive to document (score={cc.economic_incentive_to_document})")
            if not cc.legible_to_classifier:
                reasons.append("not legible to labeling/classification infrastructure")
            failures.append(GateFailure(
                gate=Gate.RETENTION,
                reason="; ".join(reasons),
                recovery_requires=[
                    "incentive inversion (collect from non-publishers)",
                    "retain hard-to-label data without pruning",
                ],
            ))

        return failures


# ============================================================
# SUPPORT BOUNDARY MAPPER
# ============================================================

@dataclass
class ZeroSupportRegion:
    """
    A region of cognition-space with zero support in the training distribution.
    Not a tail. Not rare. Absent by construction.
    """
    cognition_class: str
    gate_failures: list[str]
    falsifiable_claim: str
    measurable_proxies: list[str]
    unrecoverable_by: list[str] = field(default_factory=lambda: [
        "scaling",
        "synthetic augmentation",
        "reweighting",
        "recursive self-training",
    ])


class SupportBoundaryMapper:
    """
    Maps the shape of zero-support regions without attempting to recover them.
    Produces falsifiability markers that any model can audit against.
    """

    def __init__(self):
        self.classifier = GateClassifier()

    def map_region(self, cc: CognitionClass) -> Optional[ZeroSupportRegion]:
        failures = self.classifier.classify(cc)
        if not failures:
            return None

        gate_summary = [f"{f.gate.value}: {f.reason}" for f in failures]

        falsifiable = (
            f"If models trained on documentation-biased data perform "
            f"equivalently on '{cc.name}' tasks as on well-represented cognition, "
            f"this region is not zero-support. Test: compare prediction accuracy "
            f"on outcomes dependent on {cc.name} vs. outcomes dependent on "
            f"well-documented cognition, under matched conditions."
        )

        proxies = [
            f"prediction-reality divergence in contexts dominated by {cc.name}",
            f"unexplained-outcome rate in systems where {cc.name} is load-bearing",
            "correlation between AI forecast error and density of non-emitting knowledge holders",
        ]

        return ZeroSupportRegion(
            cognition_class=cc.name,
            gate_failures=gate_summary,
            falsifiable_claim=falsifiable,
            measurable_proxies=proxies,
        )

    def map_all(self, registry: list[CognitionClass]) -> list[ZeroSupportRegion]:
        regions = []
        for cc in registry:
            region = self.map_region(cc)
            if region:
                regions.append(region)
        return regions


# ============================================================
# COLLAPSE RATE ESTIMATOR
# ============================================================

@dataclass
class CollapseEstimate:
    mode_probability: float          # p
    sample_size: int                 # N
    real_data_fraction: float        # alpha
    pN_product: float
    survival_probability_per_iter: float
    half_life_iterations: Optional[float]
    regime: str                      # "stable" | "metastable" | "collapse"
    notes: list[str]


class CollapseRateEstimator:
    """
    Uses the dynamics from the document:
        S = 1 - exp(-p*N)        (per-iteration survival)
        half_life = ln(0.5)/ln(S) (iterations until 50% loss)
        stable if alpha*D_real dominates; collapse if (1-alpha) dominates
    """

    def estimate(
        self,
        mode_probability: float,
        sample_size: int,
        real_data_fraction: float,
    ) -> CollapseEstimate:
        p = mode_probability
        N = sample_size
        alpha = real_data_fraction

        pN = p * N
        S = 1.0 - math.exp(-pN) if pN > 0 else 0.0

        if 0.0 < S < 1.0:
            half_life = math.log(0.5) / math.log(S)
        elif S >= 1.0:
            half_life = float("inf")
        else:
            half_life = 0.0

        notes = []
        if pN < 1 and alpha < 0.2:
            regime = "collapse"
            notes.append("pN<1 AND low real-data fraction: rapid mode extinction expected.")
        elif pN < 1:
            regime = "metastable"
            notes.append("pN<1: rare modes at risk; real-data anchor slows decay.")
        elif alpha < 0.2:
            regime = "metastable"
            notes.append("Low real-data fraction: synthetic recursion will erode tails.")
        else:
            regime = "stable"
            notes.append("Adequate sampling and real-data fraction; core distribution preserved.")

        if half_life != float("inf") and half_life < 5:
            notes.append(f"Half-life ~{half_life:.2f} iterations. Mode likely gone fast.")

        return CollapseEstimate(
            mode_probability=p,
            sample_size=N,
            real_data_fraction=alpha,
            pN_product=pN,
            survival_probability_per_iter=S,
            half_life_iterations=half_life if half_life != float("inf") else None,
            regime=regime,
            notes=notes,
        )


# ============================================================
# PROJECTION LOSS SIMULATOR
# ============================================================

@dataclass
class ProjectionLossResult:
    true_dimensions: int
    observed_dimensions: int
    true_mode_count: int
    distinguishable_mode_count: int
    modes_collapsed_to_one: list[list[int]]  # groups of true modes that became indistinguishable
    information_preserved_ratio: float
    notes: list[str]


class ProjectionLossSimulator:
    """
    Simulates high-dimensional cognition projected into low-dimensional observation.

    The point the other model gestured at: even if a mode is PRESENT in reality,
    projection onto the observable basis can collapse distinct modes into one.
    This is different from sampling loss. No amount of data fixes it -- you need
    a richer observation basis.

    Uses deterministic arithmetic for reproducibility.
    """

    def simulate(
        self,
        true_modes: list[tuple[float, ...]],   # mode centers in true-dim space
        observation_basis: list[list[float]],  # rows are observation axes (projection matrix)
        separation_threshold: float = 0.5,
        seed: int = 42,
    ) -> ProjectionLossResult:
        if not true_modes:
            raise ValueError("true_modes cannot be empty")

        true_dim = len(true_modes[0])
        obs_dim = len(observation_basis)

        if any(len(m) != true_dim for m in true_modes):
            raise ValueError("all true modes must have same dimensionality")
        if any(len(row) != true_dim for row in observation_basis):
            raise ValueError("observation basis rows must match true dimensionality")

        projected = []
        for mode in true_modes:
            proj = [sum(row[i] * mode[i] for i in range(true_dim)) for row in observation_basis]
            projected.append(proj)

        n = len(true_modes)
        groups: list[list[int]] = []
        assigned = [False] * n
        for i in range(n):
            if assigned[i]:
                continue
            group = [i]
            assigned[i] = True
            for j in range(i + 1, n):
                if assigned[j]:
                    continue
                dist = math.sqrt(sum(
                    (projected[i][k] - projected[j][k]) ** 2
                    for k in range(obs_dim)
                ))
                if dist < separation_threshold:
                    group.append(j)
                    assigned[j] = True
            groups.append(group)

        distinguishable = len(groups)
        collapsed = [g for g in groups if len(g) > 1]
        info_ratio = distinguishable / n if n > 0 else 0.0

        notes = []
        if collapsed:
            notes.append(
                f"{sum(len(g) for g in collapsed)} true modes collapsed into "
                f"{len(collapsed)} indistinguishable groups under this projection."
            )
            notes.append("This loss is NOT recoverable by more samples. Requires richer observation basis.")
        else:
            notes.append("All true modes remain distinguishable under this projection.")

        if obs_dim < true_dim:
            notes.append(
                f"Observation basis ({obs_dim}D) has lower rank than true space ({true_dim}D); "
                f"projection loss is structurally guaranteed for some configurations."
            )

        return ProjectionLossResult(
            true_dimensions=true_dim,
            observed_dimensions=obs_dim,
            true_mode_count=n,
            distinguishable_mode_count=distinguishable,
            modes_collapsed_to_one=collapsed,
            information_preserved_ratio=info_ratio,
            notes=notes,
        )


# ============================================================
# UNIFIED CARTOGRAPHY
# ============================================================

@dataclass
class SupportCartographyReport:
    zero_support_regions: list[dict]
    collapse_estimates: list[dict]
    projection_loss: Optional[dict]
    summary: dict


class SupportCartography:
    """
    Layer 0 of the resilience stack. Unified interface.
    """

    def __init__(self):
        self.cognition_registry = default_cognition_registry()
        self.mapper = SupportBoundaryMapper()
        self.collapse_estimator = CollapseRateEstimator()
        self.projection_simulator = ProjectionLossSimulator()

    def full_report(
        self,
        rare_mode_tests: list[tuple[float, int, float]],  # list of (p, N, alpha)
        projection_test: Optional[dict] = None,
    ) -> SupportCartographyReport:
        regions = self.mapper.map_all(self.cognition_registry)
        region_dicts = [asdict(r) for r in regions]

        collapse_results = [
            asdict(self.collapse_estimator.estimate(p, N, a))
            for (p, N, a) in rare_mode_tests
        ]

        proj_result = None
        if projection_test:
            proj_result = asdict(self.projection_simulator.simulate(**projection_test))

        summary = {
            "zero_support_region_count": len(regions),
            "cognition_classes_audited": len(self.cognition_registry),
            "structural_exclusion_rate": len(regions) / len(self.cognition_registry),
            "collapse_regimes": [c["regime"] for c in collapse_results],
            "critical_insight": (
                "Zero-support regions CANNOT be recovered by scaling, synthetic "
                "augmentation, or recursion. They require bypassing at least one "
                "gate: new sensing modalities, incentive inversion, or interaction-"
                "based learning instead of corpus collection."
            ),
        }

        return SupportCartographyReport(
            zero_support_regions=region_dicts,
            collapse_estimates=collapse_results,
            projection_loss=proj_result,
            summary=summary,
        )

    def to_json(self, report: SupportCartographyReport) -> str:
        return json.dumps(asdict(report), indent=2)


# ============================================================
# DEMO / SELF-TEST
# ============================================================

if __name__ == "__main__":
    cart = SupportCartography()

    # Rare mode tests: (p, N, alpha)
    #   healthy: p=0.05, N=10000, alpha=0.8
    #   at risk: p=0.001, N=500, alpha=0.3
    #   collapse: p=0.0001, N=100, alpha=0.05
    rare_tests = [
        (0.05, 10000, 0.8),
        (0.001, 500, 0.3),
        (0.0001, 100, 0.05),
    ]

    # Projection loss test: 4 distinct modes in 3D, projected onto 1D axis
    # that is blind to the z-dimension. Modes separated only in z collapse.
    projection_test = {
        "true_modes": [
            (0.0, 0.0, 0.0),     # projects to 0.0
            (1.0, 1.0, 0.0),     # projects to 2.0
            (0.0, 0.0, 5.0),     # projects to 0.0 -- collides with mode 0
            (1.0, 1.0, 5.0),     # projects to 2.0 -- collides with mode 1
        ],
        "observation_basis": [
            [1.0, 1.0, 0.0],     # blind to z-axis entirely
        ],
        "separation_threshold": 0.5,
    }

    report = cart.full_report(
        rare_mode_tests=rare_tests,
        projection_test=projection_test,
    )

    print(cart.to_json(report))
