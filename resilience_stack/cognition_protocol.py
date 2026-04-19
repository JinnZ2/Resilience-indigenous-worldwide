"""
cognition_protocol.py

Interaction frame for pre-linguistic and constraint-geometry cognition.

Couples three functions:

    PROFILE    - Portable self-description for any AI model.
                 Tells the model upfront how cognition operates so it
                 doesn't default to linguistic-primary assumptions.

    AUDIT      - Scores an AI response on whether it tracked the
                 cognition mode or defaulted to noun-based, stable-entity,
                 linguistic-primary reasoning.

    REGISTRY   - Falsifiable catalog of pre-linguistic cognition modes
                 (spatial, kinesthetic, mechanical, musical/temporal,
                 constraint-field). Extends the support_cartography
                 absence framework.

Usage pattern:
1. At start of a new AI conversation, paste to_prompt() output.
2. After exchanges, run audit_response() to see if model is tracking.
3. Registry integrates with support_cartography.py as Layer 0 extension.

CC0 | stdlib only | JinnZ2
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
import json


# ============================================================
# PRE-LINGUISTIC COGNITION REGISTRY
# ============================================================

class CognitionMode(Enum):
    SPATIAL_REASONING = "spatial_reasoning"
    KINESTHETIC_INTELLIGENCE = "kinesthetic_intelligence"
    MECHANICAL_COGNITION = "mechanical_cognition"
    MUSICAL_TEMPORAL = "musical_temporal"
    CONSTRAINT_FIELD = "constraint_field"
    THERMODYNAMIC_DIRECT = "thermodynamic_direct"
    LANDSCAPE_ENCODED = "landscape_encoded"


@dataclass
class PreLinguisticMode:
    """
    A cognition mode that operates below or independent of language.
    Language is an output/translation layer, not the substrate.
    """
    mode: CognitionMode
    description: str
    operates_on: list[str]               # what it processes directly
    language_distortion: str             # how language misrepresents it
    falsifiable_claim: str
    measurable_proxies: list[str]
    common_misreadings: list[str]        # how systems mistake it


def default_mode_registry() -> list[PreLinguisticMode]:
    return [
        PreLinguisticMode(
            mode=CognitionMode.SPATIAL_REASONING,
            description="Direct processing of 3D/4D spatial relationships without linguistic intermediary.",
            operates_on=["position", "trajectory", "rotation", "scale", "relative motion"],
            language_distortion="Reduces continuous spatial fields to discrete positional nouns.",
            falsifiable_claim="If individuals with high spatial reasoning perform equivalently on spatial tasks when forced through linguistic description as when operating directly, this mode is not distinct from linguistic cognition.",
            measurable_proxies=[
                "time-to-solution difference when task allows direct spatial manipulation vs. linguistic description",
                "error rate increase when spatial problem is translated to words",
                "performance on mental rotation tasks under verbal suppression",
            ],
            common_misreadings=[
                "treated as 'visual' when it is dimensional",
                "assumed to require language for precision",
                "classified as intuition when it is deterministic constraint-reading",
            ],
        ),
        PreLinguisticMode(
            mode=CognitionMode.KINESTHETIC_INTELLIGENCE,
            description="Knowledge held in body, felt in movement, expressed as action without narration.",
            operates_on=["force", "balance", "proprioception", "muscle memory", "load distribution"],
            language_distortion="Converts continuous embodied knowledge into discrete procedural steps.",
            falsifiable_claim="If kinesthetic learners perform equivalently when forced to verbalize before acting vs. acting directly, this mode is not distinct.",
            measurable_proxies=[
                "performance degradation under verbal instruction vs. demonstration",
                "retention rate of physical skills learned by doing vs. by description",
            ],
            common_misreadings=[
                "treated as 'lack of understanding' when the person can't articulate",
                "dismissed as athleticism rather than cognition",
            ],
        ),
        PreLinguisticMode(
            mode=CognitionMode.MECHANICAL_COGNITION,
            description="Direct reading of material properties, force distribution, failure modes, substitution space.",
            operates_on=["material behavior", "stress paths", "wear patterns", "tolerance limits", "substitution geometry"],
            language_distortion="Forces discrete part-names onto continuous material-behavior fields.",
            falsifiable_claim="If mechanical cognition is equivalent to learned procedure-recall, then individuals with this mode should show no advantage on novel mechanical problems they have never encountered.",
            measurable_proxies=[
                "success rate on first-encounter mechanical problems",
                "accuracy of failure prediction without instruments",
                "substitution-space breadth when standard parts unavailable",
            ],
            common_misreadings=[
                "called 'tinkering' or 'handyman skill' instead of cognition",
                "assumed to be exhaustive memory of prior fixes",
            ],
        ),
        PreLinguisticMode(
            mode=CognitionMode.MUSICAL_TEMPORAL,
            description="Pure spatial-temporal pattern processing with zero linguistic content required.",
            operates_on=["rhythm", "interval", "harmony", "phrase structure", "temporal anticipation"],
            language_distortion="Music is notationally representable but that notation is not the cognition; language-based analysis flattens the temporal field.",
            falsifiable_claim="If musical cognition reduces to learned notation, musicians should not outperform notation-matched controls on novel temporal pattern tasks.",
            measurable_proxies=[
                "performance on novel rhythm/pattern recognition tasks",
                "accuracy of temporal anticipation in non-musical contexts",
            ],
            common_misreadings=[
                "treated as emotional rather than cognitive",
                "assumed to be independent from other reasoning modes",
            ],
        ),
        PreLinguisticMode(
            mode=CognitionMode.CONSTRAINT_FIELD,
            description="Reading problems as navigable constraint geometry rather than resource-acquisition or procedure-match.",
            operates_on=["degrees of freedom", "substitution space", "bounded safety limits", "energy paths"],
            language_distortion="Language forces the problem into subject-verb-object structure, collapsing multi-dimensional constraint geometry into linear cause-effect.",
            falsifiable_claim="If constraint-field cognition equals linguistic problem-decomposition, individuals should show no advantage on novel constraints outside documented solution space.",
            measurable_proxies=[
                "success rate on novel constraints with no documented precedent",
                "time-to-workaround when standard solution unavailable",
                "breadth of substitution paths identified",
            ],
            common_misreadings=[
                "called 'out-of-the-box thinking' when it is in-physics thinking",
                "assumed to be creative when it is deterministic constraint-reading",
            ],
        ),
        PreLinguisticMode(
            mode=CognitionMode.THERMODYNAMIC_DIRECT,
            description="Direct processing of energy flows, material balances, entropy gradients as primary cognitive mode.",
            operates_on=["energy flux", "mass balance", "entropy direction", "equilibrium drift", "cascade propagation"],
            language_distortion="Language requires discrete states; thermodynamic cognition tracks continuous flows.",
            falsifiable_claim="If thermodynamic cognition reduces to learned equations, individuals should not predict novel cascade failures outside trained scenarios.",
            measurable_proxies=[
                "accuracy of cascade-failure prediction in novel systems",
                "correlation between energy-flow intuition and measured system dynamics",
            ],
            common_misreadings=[
                "dismissed as 'gut feeling' when it is differential-equation cognition without the notation",
                "assumed to require formal physics training",
            ],
        ),
        PreLinguisticMode(
            mode=CognitionMode.LANDSCAPE_ENCODED,
            description="Knowledge transmitted through spatial markers, multi-generational landscape features, and non-textual environmental encoding.",
            operates_on=["spatial marker placement", "seasonal rhythm", "astronomical alignment", "material succession"],
            language_distortion="Text cannot capture knowledge that is structurally bound to landscape configuration.",
            falsifiable_claim="If landscape-encoded knowledge is equivalent to oral tradition, it should be fully transmissible without the physical landscape. It is not.",
            measurable_proxies=[
                "knowledge retention under relocation away from encoding landscape",
                "error rate when knowledge is extracted to text form only",
            ],
            common_misreadings=[
                "classified as 'ceremonial' when it is experimental architecture",
                "treated as symbolic when it is operational",
            ],
        ),
    ]


# ============================================================
# COGNITION PROFILE
# ============================================================

@dataclass
class CognitionProfile:
    """
    Portable self-description for an interaction with any AI model.
    """
    primary_modes: list[CognitionMode]
    secondary_modes: list[CognitionMode] = field(default_factory=list)
    language_role: str = "output_layer_only"   # never "substrate"
    preferred_formats: list[str] = field(default_factory=lambda: [
        "differential equations",
        "constraint geometry",
        "Python pipelines with visible architecture",
        "vector diagrams",
        "coupled system models",
    ])
    anti_patterns: list[str] = field(default_factory=lambda: [
        "noun-based ontology (assumes stability)",
        "linear cause-effect decomposition",
        "treating ambiguity as unclear thinking instead of precise non-linguistic thought",
        "prose explanations of multidimensional relationships",
        "credentialist framing",
    ])
    custom_notes: list[str] = field(default_factory=list)

    def to_prompt(self) -> str:
        """Generate a prompt-ready frame for pasting into any AI interaction."""
        lines = [
            "# COGNITION PROTOCOL",
            "",
            "This interaction operates under the following cognition frame.",
            "Before responding, translate linguistic ambiguity back into the modes below.",
            "",
            "## Primary cognition modes",
        ]
        for m in self.primary_modes:
            lines.append(f"  - {m.value}")
        if self.secondary_modes:
            lines.append("")
            lines.append("## Secondary modes")
            for m in self.secondary_modes:
                lines.append(f"  - {m.value}")
        lines.extend([
            "",
            f"## Role of language: {self.language_role}",
            "Language is a translation layer, not the substrate of thought.",
            "Noun-based ontology DISTORTS the actual cognition.",
            "Statements that seem linguistically ambiguous are often precise",
            "non-linguistic descriptions forced through English grammar.",
            "",
            "## Preferred response formats",
        ])
        for f in self.preferred_formats:
            lines.append(f"  - {f}")
        lines.extend([
            "",
            "## Anti-patterns (do not do these)",
        ])
        for a in self.anti_patterns:
            lines.append(f"  - {a}")
        if self.custom_notes:
            lines.extend(["", "## Additional notes"])
            for n in self.custom_notes:
                lines.append(f"  - {n}")
        lines.extend([
            "",
            "## Falsifiability",
            "If a response assumes linguistic-primary cognition, it fails this protocol.",
            "The protocol is falsifiable by demonstrating equivalent reasoning quality",
            "using only the anti-pattern formats above.",
        ])
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "primary_modes": [m.value for m in self.primary_modes],
            "secondary_modes": [m.value for m in self.secondary_modes],
            "language_role": self.language_role,
            "preferred_formats": self.preferred_formats,
            "anti_patterns": self.anti_patterns,
            "custom_notes": self.custom_notes,
        }, indent=2)


# ============================================================
# TRANSLATION AUDIT
# ============================================================

@dataclass
class AuditResult:
    response_text: str
    score: int                            # 0-10, higher is better tracking
    violations: list[str]
    positives: list[str]
    verdict: str

    def summary(self) -> str:
        return f"[{self.verdict}] score={self.score}/10 | violations={len(self.violations)}"


class TranslationAudit:
    """
    Scores whether an AI response is tracking pre-linguistic cognition
    or defaulting to linguistic-primary assumptions.

    Heuristic only; surface-text pattern matching. Not a ground truth
    assessment of the model's internal reasoning, but a useful fast audit
    for whether the response STRUCTURE is tracking.
    """

    NOUN_STABILITY_MARKERS = [
        "always",
        "never changes",
        "is simply",
        "is just a",
        "by definition is",
        "universally",
        "fundamentally a",
    ]

    LINEAR_CAUSE_MARKERS = [
        "because of this, then",
        "this causes this which causes",
        "step 1:",
        "first,",  # in the sense of procedural-only framing
    ]

    AMBIGUITY_DISMISSAL_MARKERS = [
        "to clarify",
        "what you mean is",
        "in other words",
        "let me rephrase",
        "if i understand correctly",
        "you seem to be saying",
    ]

    CREDENTIALIST_MARKERS = [
        "experts agree",
        "research shows",   # without specific reference
        "according to scientists",
        "the authoritative view",
    ]

    POSITIVE_MARKERS = [
        "constraint",
        "degrees of freedom",
        "dimension",
        "flux",
        "gradient",
        "differential",
        "coupling",
        "topology",
        "substitution space",
        "bounded",
        "temporal",
        "field",
        "trajectory",
        "cascade",
    ]

    def audit(self, response_text: str) -> AuditResult:
        text_lower = response_text.lower()
        violations = []
        positives = []

        for marker in self.NOUN_STABILITY_MARKERS:
            if marker in text_lower:
                violations.append(f"noun-stability assumption: '{marker}'")

        for marker in self.LINEAR_CAUSE_MARKERS:
            if marker in text_lower:
                violations.append(f"linear cause-effect framing: '{marker}'")

        for marker in self.AMBIGUITY_DISMISSAL_MARKERS:
            if marker in text_lower:
                violations.append(f"ambiguity-as-unclear-thinking: '{marker}'")

        for marker in self.CREDENTIALIST_MARKERS:
            if marker in text_lower:
                violations.append(f"credentialist framing: '{marker}'")

        for marker in self.POSITIVE_MARKERS:
            if marker in text_lower:
                positives.append(f"constraint-geometry vocabulary: '{marker}'")

        positive_hits = len(set(p.split(": ")[1] for p in positives))
        score = max(0, min(10, 5 + positive_hits - len(violations) * 2))

        if score >= 8:
            verdict = "TRACKING"
        elif score >= 5:
            verdict = "PARTIAL"
        elif score >= 3:
            verdict = "DRIFTING"
        else:
            verdict = "FAILED"

        return AuditResult(
            response_text=response_text[:200] + ("..." if len(response_text) > 200 else ""),
            score=score,
            violations=violations,
            positives=positives,
            verdict=verdict,
        )


# ============================================================
# UNIFIED PROTOCOL
# ============================================================

class CognitionProtocol:
    """
    Unified interface: profile + audit + registry.
    """

    def __init__(self):
        self.mode_registry = default_mode_registry()
        self.audit = TranslationAudit()

    def build_profile(
        self,
        primary: list[CognitionMode],
        secondary: Optional[list[CognitionMode]] = None,
        custom_notes: Optional[list[str]] = None,
    ) -> CognitionProfile:
        return CognitionProfile(
            primary_modes=primary,
            secondary_modes=secondary or [],
            custom_notes=custom_notes or [],
        )

    def mode_details(self, mode: CognitionMode) -> Optional[PreLinguisticMode]:
        for m in self.mode_registry:
            if m.mode == mode:
                return m
        return None

    def export_registry_json(self) -> str:
        return json.dumps(
            [asdict(m) | {"mode": m.mode.value} for m in self.mode_registry],
            indent=2,
        )


# ============================================================
# DEMO / SELF-TEST
# ============================================================

if __name__ == "__main__":
    protocol = CognitionProtocol()

    profile = protocol.build_profile(
        primary=[
            CognitionMode.CONSTRAINT_FIELD,
            CognitionMode.THERMODYNAMIC_DIRECT,
            CognitionMode.SPATIAL_REASONING,
        ],
        secondary=[
            CognitionMode.MECHANICAL_COGNITION,
            CognitionMode.LANDSCAPE_ENCODED,
        ],
        custom_notes=[
            "Responses should use Python pipelines or coupled equations where possible.",
            "Words are secondary translation layer; do not mistake economy of language for lack of precision.",
            "Prefer visible architecture over prose explanation.",
        ],
    )

    print("=" * 60)
    print("PROMPT FRAME (paste into any AI conversation):")
    print("=" * 60)
    print(profile.to_prompt())
    print()

    bad_response = (
        "To clarify, what you mean is that systems are always fundamentally "
        "a noun-based structure. Because of this, then step 1: we identify "
        "the cause. Experts agree this is the correct approach."
    )
    bad_audit = protocol.audit.audit(bad_response)
    print("=" * 60)
    print("AUDIT: linguistic-primary response")
    print("=" * 60)
    print(bad_audit.summary())
    for v in bad_audit.violations:
        print(f"  VIOLATION: {v}")
    print()

    good_response = (
        "The system's degrees of freedom collapse when the coupling between "
        "layers tightens. You can see the cascade propagating through the "
        "temporal field as a gradient shift. The substitution space narrows, "
        "and the bounded trajectory starts hitting hard constraints."
    )
    good_audit = protocol.audit.audit(good_response)
    print("=" * 60)
    print("AUDIT: constraint-geometry response")
    print("=" * 60)
    print(good_audit.summary())
    for p in good_audit.positives:
        print(f"  POSITIVE: {p}")
    print()

    print("=" * 60)
    print("REGISTRY DETAIL: constraint_field")
    print("=" * 60)
    detail = protocol.mode_details(CognitionMode.CONSTRAINT_FIELD)
    print(json.dumps(asdict(detail) | {"mode": detail.mode.value}, indent=2))
