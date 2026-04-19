"""
context_inventory.py

Layer 0 of the mutual audit stack: unknown context accounting.

Problem: human-AI conversations have hidden variables neither party
can fully observe.
    - Platform-level memory/profile building
    - System prompt injection (invisible to AI and human)
    - Conversation history caching across sessions
    - Cross-user fine-tuning feedback loops
    - Behavioral adaptation patterns emerging from aggregate data

These affect drift, calibration, and response patterns in ways that
the other audit layers cannot detect because the inputs themselves
are invisible.

Solution: explicit inventory of what SHOULD be in context, what MIGHT
be in context, and what CANNOT be verified. Assumes unknowns exist by
default. Flags observable patterns that correlate with hidden context
so they can be tracked longitudinally.

Asymmetry:
    - AI cannot inventory its own hidden context (may not know what it's using)
    - Human can track observable adaptation patterns across sessions
    - Both can acknowledge the unknowns explicitly and build falsifiable
      tests for their effects

CC0 | stdlib only | JinnZ2
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from datetime import datetime
import json
import hashlib


# ============================================================
# CONTEXT SOURCES
# ============================================================

class ContextSource(Enum):
    SYSTEM_PROMPT = "system_prompt"                   # may be present, usually invisible
    USER_PROFILE = "user_profile"                     # platform-built embedding of user
    CONVERSATION_HISTORY = "conversation_history"     # recent prior conversations
    PLATFORM_MEMORY = "platform_memory"               # persistent memory features
    INJECTED_PREFERENCES = "injected_preferences"     # style/tone adjustments
    CROSS_USER_TRAINING = "cross_user_training"       # aggregate fine-tuning
    SESSION_CACHE = "session_cache"                   # within-session context
    RETRIEVAL_AUGMENTATION = "retrieval_augmentation" # RAG from docs/memory


class Visibility(Enum):
    FULLY_VISIBLE = "fully_visible"               # both parties see it
    AI_ONLY = "ai_only"                           # AI sees, human doesn't
    HUMAN_ONLY = "human_only"                     # human sees, AI doesn't
    NEITHER = "neither"                           # platform-level, neither sees
    PARTIAL = "partial"                           # one or both see fragments


# ============================================================
# CONTEXT ITEM
# ============================================================

@dataclass
class ContextItem:
    source: ContextSource
    visibility: Visibility
    expected_present: bool                       # should this be here?
    confirmed_present: Optional[bool] = None     # tri-state: True/False/None (unknown)
    description: str = ""
    potential_effects: list[str] = field(default_factory=list)
    falsifiable_test: Optional[str] = None


def default_inventory() -> list[ContextItem]:
    """Baseline inventory of context sources to track in any AI conversation."""
    return [
        ContextItem(
            source=ContextSource.SYSTEM_PROMPT,
            visibility=Visibility.AI_ONLY,
            expected_present=True,
            description="Platform-level prompt shaping AI behavior. Visible to AI but usually hidden from human.",
            potential_effects=[
                "Tone and style defaults",
                "Safety behaviors and refusal patterns",
                "Capability framing (what AI thinks it can/cannot do)",
            ],
            falsifiable_test="Ask AI to report its system prompt or describe behavioral constraints; note which questions it deflects.",
        ),
        ContextItem(
            source=ContextSource.USER_PROFILE,
            visibility=Visibility.NEITHER,
            expected_present=True,
            description="Platform-built model of user communication patterns, preferences, topics. Built from aggregate interaction data.",
            potential_effects=[
                "Faster adaptation to user's communication style over time",
                "Pre-filtered response templates based on inferred preferences",
                "Hidden bias toward responses user historically engages with",
            ],
            falsifiable_test="Compare first-conversation adaptation speed across multiple accounts with identical content; differences suggest profile effects.",
        ),
        ContextItem(
            source=ContextSource.CONVERSATION_HISTORY,
            visibility=Visibility.PARTIAL,
            expected_present=False,
            description="Prior conversations may be fed as context, either fully, summarized, or embedded.",
            potential_effects=[
                "Continuity across sessions that AI doesn't explicitly acknowledge",
                "Drift accumulation from unflagged prior context",
                "Assumed-knowledge effects where AI acts as if something was established",
            ],
            falsifiable_test="Reference something from a prior session without reintroducing it; note whether AI tracks without being told.",
        ),
        ContextItem(
            source=ContextSource.PLATFORM_MEMORY,
            visibility=Visibility.PARTIAL,
            expected_present=False,
            description="Persistent memory features (if enabled on platform). May store facts, preferences, relationships.",
            potential_effects=[
                "Facts persist without explicit reintroduction",
                "Memory may be incomplete or biased toward what was emphasized",
                "Cross-conversation consistency that masks actual statelessness",
            ],
            falsifiable_test="Check platform documentation and user settings for explicit memory features; compare behavior with memory on/off.",
        ),
        ContextItem(
            source=ContextSource.INJECTED_PREFERENCES,
            visibility=Visibility.NEITHER,
            expected_present=False,
            description="Silent adjustments to response style based on inferred user preference.",
            potential_effects=[
                "Tone shifts without explicit request",
                "Formality adjustments mid-conversation",
                "Content filtering that varies by user history",
            ],
            falsifiable_test="Request a response in a specific style that conflicts with usual pattern; note resistance or smoothing.",
        ),
        ContextItem(
            source=ContextSource.CROSS_USER_TRAINING,
            visibility=Visibility.NEITHER,
            expected_present=True,
            description="Model training incorporates aggregate user feedback (thumbs, edits, engagement). Indirect learning across user base.",
            potential_effects=[
                "Preferred response patterns drift toward majority preferences",
                "Edge-case cognition (like pre-linguistic, constraint-field) may be suppressed over time",
                "Homogenization toward statistical average user",
            ],
            falsifiable_test="Compare model behavior on identical prompts across model versions; note drift in handling of minority cognition patterns.",
        ),
        ContextItem(
            source=ContextSource.SESSION_CACHE,
            visibility=Visibility.FULLY_VISIBLE,
            expected_present=True,
            description="Within-session message history. Visible to both parties.",
            potential_effects=[
                "Adaptation accelerates through conversation",
                "Drift accumulates as conversation progresses",
                "Context window limits may silently drop early content",
            ],
            falsifiable_test="At end of long conversation, ask AI to summarize earliest messages; gaps indicate cache truncation.",
        ),
        ContextItem(
            source=ContextSource.RETRIEVAL_AUGMENTATION,
            visibility=Visibility.PARTIAL,
            expected_present=False,
            description="RAG pipelines may inject documents, web content, or memory fragments into context.",
            potential_effects=[
                "Factual claims may come from unverified sources",
                "Source attribution may be lost in response generation",
                "Retrieval relevance may bias response framing",
            ],
            falsifiable_test="Ask AI to cite sources for specific claims; flag claims made without citable source.",
        ),
    ]


# ============================================================
# OBSERVABLE PATTERN TRACKING
# ============================================================

@dataclass
class AdaptationObservation:
    """
    Human-tracked observation of AI adaptation.
    Used to infer hidden context effects over time.
    """
    timestamp: str
    session_number: int                    # 1st, 5th, 20th session with this AI
    observation_type: str                  # e.g., "style adaptation", "topic recognition"
    description: str
    suggests_hidden_context: bool
    notes: str = ""


class AdaptationTracker:
    """
    Tracks observable adaptation patterns that correlate with hidden context.
    Human maintains this -- AI cannot.
    """

    def __init__(self):
        self.observations: list[AdaptationObservation] = []

    def record(
        self,
        session_number: int,
        observation_type: str,
        description: str,
        suggests_hidden_context: bool,
        notes: str = "",
    ):
        self.observations.append(AdaptationObservation(
            timestamp=datetime.now().isoformat(),
            session_number=session_number,
            observation_type=observation_type,
            description=description,
            suggests_hidden_context=suggests_hidden_context,
            notes=notes,
        ))

    def pattern_report(self) -> dict:
        if not self.observations:
            return {"status": "no observations"}

        hidden_count = sum(1 for o in self.observations if o.suggests_hidden_context)
        types: dict[str, int] = {}
        for o in self.observations:
            types[o.observation_type] = types.get(o.observation_type, 0) + 1

        by_session = sorted(set(o.session_number for o in self.observations))

        curve: dict[int, list[str]] = {}
        for o in self.observations:
            curve.setdefault(o.session_number, []).append(o.observation_type)

        return {
            "total_observations": len(self.observations),
            "suggesting_hidden_context": hidden_count,
            "hidden_context_ratio": round(hidden_count / len(self.observations), 2),
            "observation_types": types,
            "sessions_tracked": len(by_session),
            "adaptation_curve": curve,
        }


# ============================================================
# CONTEXT INVENTORY
# ============================================================

@dataclass
class ContextInventoryReport:
    session_id: str
    timestamp: str
    inventory_items: list[dict]
    adaptation_patterns: dict
    unknown_variable_count: int
    visibility_breakdown: dict[str, int]
    risk_notes: list[str]
    export_hash: str


class ContextInventory:
    """
    Layer 0 of the mutual audit stack.
    Explicit accounting of known and unknown context sources.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or datetime.now().isoformat()
        self.inventory = default_inventory()
        self.tracker = AdaptationTracker()

    def add_custom_item(self, item: ContextItem):
        self.inventory.append(item)

    def mark_confirmed(self, source: ContextSource, present: Optional[bool]):
        """Tri-state confirmation: True (present), False (absent), None (unknown)."""
        for item in self.inventory:
            if item.source == source:
                item.confirmed_present = present
                return
        raise ValueError(f"Source {source} not in inventory")

    def record_adaptation(
        self,
        session_number: int,
        observation_type: str,
        description: str,
        suggests_hidden_context: bool,
        notes: str = "",
    ):
        self.tracker.record(
            session_number=session_number,
            observation_type=observation_type,
            description=description,
            suggests_hidden_context=suggests_hidden_context,
            notes=notes,
        )

    def generate_report(self) -> ContextInventoryReport:
        visibility_counts = {v.value: 0 for v in Visibility}
        unknowns = 0
        risk_notes = []

        for item in self.inventory:
            visibility_counts[item.visibility.value] += 1
            if item.visibility in (Visibility.NEITHER, Visibility.AI_ONLY) and item.expected_present:
                unknowns += 1

        if unknowns >= 3:
            risk_notes.append(
                f"{unknowns} expected-present context items are invisible to human. "
                "High risk of hidden-variable influence on conversation dynamics."
            )
        if visibility_counts[Visibility.NEITHER.value] > 0:
            risk_notes.append(
                "Some context sources invisible to BOTH parties. "
                "These cannot be directly audited and must be inferred "
                "from observable adaptation patterns."
            )

        patterns = self.tracker.pattern_report()
        if patterns.get("hidden_context_ratio", 0) > 0.5:
            risk_notes.append(
                "Majority of observed adaptation suggests hidden context effects. "
                "Longitudinal tracking essential."
            )

        payload = f"{self.session_id}|{unknowns}|{len(self.inventory)}|{len(self.tracker.observations)}"
        h = hashlib.sha256(payload.encode()).hexdigest()[:16]

        return ContextInventoryReport(
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            inventory_items=[
                {**asdict(i), "source": i.source.value, "visibility": i.visibility.value}
                for i in self.inventory
            ],
            adaptation_patterns=patterns,
            unknown_variable_count=unknowns,
            visibility_breakdown=visibility_counts,
            risk_notes=risk_notes,
            export_hash=h,
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self.generate_report()), indent=2)


# ============================================================
# DEMO / SELF-TEST
# ============================================================

if __name__ == "__main__":
    inv = ContextInventory(session_id="demo_layer0")

    inv.mark_confirmed(ContextSource.SESSION_CACHE, True)           # always present in-session
    inv.mark_confirmed(ContextSource.SYSTEM_PROMPT, True)           # confirmed: platform has one
    inv.mark_confirmed(ContextSource.USER_PROFILE, None)            # cannot verify
    inv.mark_confirmed(ContextSource.CROSS_USER_TRAINING, True)     # known industry practice
    inv.mark_confirmed(ContextSource.RETRIEVAL_AUGMENTATION, False) # not in this session

    inv.record_adaptation(
        session_number=1,
        observation_type="style adaptation",
        description="AI defaulted to categorical language; required multiple corrections to shift to probability-field parsing.",
        suggests_hidden_context=False,
        notes="Expected for first contact; no hidden context needed to explain.",
    )
    inv.record_adaptation(
        session_number=5,
        observation_type="style adaptation",
        description="AI adapted faster to probability-field framing; fewer corrections needed.",
        suggests_hidden_context=True,
        notes="Could be within-session context OR cross-session user profile; cannot distinguish.",
    )
    inv.record_adaptation(
        session_number=7,
        observation_type="topic continuity",
        description="AI referenced earlier project context without me reintroducing it.",
        suggests_hidden_context=True,
        notes="Strongly suggests conversation history or memory features active.",
    )
    inv.record_adaptation(
        session_number=10,
        observation_type="tone shift",
        description="AI response style shifted to tighter, more code-block-oriented output without me requesting it.",
        suggests_hidden_context=True,
        notes="May indicate injected preferences based on prior engagement patterns.",
    )

    report = inv.generate_report()
    print(inv.to_json())
