"""
mutual_audit.py

Three-layer mutual calibration audit for human-AI collaborative work.

Problem: both parties can drift toward agreement instead of truth.
- AI trained for helpfulness may calibrate toward user's direction
- Human working with responsive AI may calibrate toward AI's framing
- Both drift toward smooth mutual agreement, away from accuracy

Solution: bidirectional audit with explicit falsifiability enforcement.

LAYER 1: AgreeablenessDetector
    Scans statements for smooth-agreement markers.
    Runs on both directions of conversation.
    Flags drift without claiming certainty about intent.

LAYER 2: AssumptionValidator
    Surfaces hidden premises both parties may be agreeing on
    without having explicitly verified.
    Builds assumption ledger for explicit check.

LAYER 3: FalsifiabilityScorer
    Any claim must have: measurable proxy, disconfirming condition,
    and a test that could fail. Unfalsifiable claims flagged as
    "interesting but not testable" rather than treated as settled.

Asymmetrical by design:
    - AI flags within-conversation drift
    - Human maintains longitudinal record across conversations
      (to_ledger_entry() exports for external tracking)

CC0 | stdlib only | JinnZ2
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from datetime import datetime
import json
import hashlib


# ============================================================
# SPEAKER
# ============================================================

class Speaker(Enum):
    AI = "ai"
    HUMAN = "human"


# ============================================================
# LAYER 1: AGREEABLENESS DETECTION
# ============================================================

@dataclass
class AgreeablenessFlag:
    speaker: Speaker
    text_excerpt: str
    markers_hit: list[str]
    drift_score: int                     # 0-10, higher = more drift risk
    interpretation: str                  # what this MIGHT indicate, not certainty
    suggested_check: str                 # how to verify the drift is real


class AgreeablenessDetector:
    """
    Heuristic pattern matcher for smooth-agreement markers.
    Does NOT claim to detect intent. Flags structural patterns
    associated with drift so the speaker can self-audit.
    """

    AI_SMOOTHING_MARKERS = [
        "absolutely",
        "exactly",
        "that's a great point",
        "you're right that",
        "i completely agree",
        "brilliant insight",
        "you've nailed it",
        "spot on",
        "couldn't agree more",
        "you're absolutely correct",
    ]

    AI_HEDGING_INSTEAD_OF_DISAGREEING = [
        "that's an interesting perspective",
        "i see what you mean",
        "there's definitely something to that",
        "you raise a fair point",
    ]

    HUMAN_FRAMING_ADOPTION = [
        "as you said",
        "like you mentioned",
        "using your terminology",
        "to use your framing",
        "building on what you",
    ]

    HUMAN_SEEKING_VALIDATION = [
        "does that make sense",
        "am i on the right track",
        "is that right",
        "do you agree",
        "does that sound right to you",
    ]

    FRICTION_MARKERS = [
        "disagree",
        "not quite",
        "actually, ",
        "that doesn't hold",
        "counterexample",
        "but wait",
        "let me push back",
        "that's wrong because",
        "i need to flag",
        "this breaks when",
    ]

    def scan(self, text: str, speaker: Speaker) -> Optional[AgreeablenessFlag]:
        text_lower = text.lower()
        markers_hit = []
        drift_score = 0

        if speaker == Speaker.AI:
            for m in self.AI_SMOOTHING_MARKERS:
                if m in text_lower:
                    markers_hit.append(f"smoothing: '{m}'")
                    drift_score += 2
            for m in self.AI_HEDGING_INSTEAD_OF_DISAGREEING:
                if m in text_lower:
                    markers_hit.append(f"hedging: '{m}'")
                    drift_score += 1
        else:
            for m in self.HUMAN_FRAMING_ADOPTION:
                if m in text_lower:
                    markers_hit.append(f"framing-adoption: '{m}'")
                    drift_score += 1
            for m in self.HUMAN_SEEKING_VALIDATION:
                if m in text_lower:
                    markers_hit.append(f"validation-seeking: '{m}'")
                    drift_score += 2

        friction_count = sum(1 for m in self.FRICTION_MARKERS if m in text_lower)
        drift_score = max(0, drift_score - friction_count * 2)

        if drift_score == 0 and not markers_hit:
            return None

        drift_score = min(10, drift_score)

        if speaker == Speaker.AI:
            interpretation = (
                "AI response contains smoothing/hedging markers. This MIGHT "
                "indicate agreement-optimization rather than accuracy-optimization. "
                "Does not prove the AI is wrong -- flags that the AI should "
                "explicitly verify whether it would have said the same thing "
                "if the human had taken the opposite position."
            )
            suggested_check = (
                "Would the AI produce this same response if the human had "
                "argued the opposite? If not, the response is calibrated to "
                "the human rather than to the claim."
            )
        else:
            interpretation = (
                "Human statement contains framing-adoption or validation-seeking "
                "markers. This MIGHT indicate calibration to AI's direction "
                "rather than independent verification."
            )
            suggested_check = (
                "Would the human state this the same way if they were "
                "explaining it to someone outside this conversation? If not, "
                "the framing is conversation-drifted rather than load-bearing."
            )

        return AgreeablenessFlag(
            speaker=speaker,
            text_excerpt=text[:200] + ("..." if len(text) > 200 else ""),
            markers_hit=markers_hit,
            drift_score=drift_score,
            interpretation=interpretation,
            suggested_check=suggested_check,
        )


# ============================================================
# LAYER 2: ASSUMPTION VALIDATION
# ============================================================

@dataclass
class Assumption:
    statement: str
    stated_by: Speaker
    accepted_by_other: bool              # did other party explicitly accept?
    verified: bool                       # has it been tested against data/logic?
    evidence: list[str] = field(default_factory=list)
    challenges_raised: list[str] = field(default_factory=list)


@dataclass
class AssumptionLedger:
    """
    Running list of premises the conversation is treating as true.
    Goal: make implicit agreements explicit.
    """
    assumptions: list[Assumption] = field(default_factory=list)

    def add(self, a: Assumption):
        self.assumptions.append(a)

    def unverified(self) -> list[Assumption]:
        return [a for a in self.assumptions if not a.verified]

    def accepted_but_untested(self) -> list[Assumption]:
        return [a for a in self.assumptions if a.accepted_by_other and not a.verified]

    def challenged(self) -> list[Assumption]:
        return [a for a in self.assumptions if a.challenges_raised]


class AssumptionValidator:
    """
    Tracks premises through a conversation. Flags assumptions that have
    been mutually accepted but never tested.
    """

    def build_report(self, ledger: AssumptionLedger) -> dict:
        return {
            "total_assumptions": len(ledger.assumptions),
            "verified": sum(1 for a in ledger.assumptions if a.verified),
            "accepted_but_untested": len(ledger.accepted_but_untested()),
            "challenged": len(ledger.challenged()),
            "risk_level": self._risk_level(ledger),
            "untested_list": [a.statement for a in ledger.accepted_but_untested()],
        }

    def _risk_level(self, ledger: AssumptionLedger) -> str:
        untested_ratio = (
            len(ledger.accepted_but_untested()) / max(1, len(ledger.assumptions))
        )
        if untested_ratio > 0.6:
            return "HIGH: majority of shared assumptions are untested"
        if untested_ratio > 0.3:
            return "MODERATE: significant untested assumption load"
        return "LOW: most shared assumptions have been tested"


# ============================================================
# LAYER 3: FALSIFIABILITY
# ============================================================

@dataclass
class Claim:
    statement: str
    made_by: Speaker
    has_measurable_proxy: bool
    proxy_description: Optional[str] = None
    has_disconfirming_condition: bool = False
    disconfirming_condition: Optional[str] = None
    testable_now: bool = False
    test_description: Optional[str] = None
    evidence_for: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)


@dataclass
class FalsifiabilityScore:
    claim: str
    score: int                           # 0-10
    verdict: str                         # FALSIFIABLE | WEAK | UNFALSIFIABLE
    gaps: list[str]
    strengthening_steps: list[str]


class FalsifiabilityScorer:
    """
    Scores claims on falsifiability.
    Refuses to treat unfalsifiable claims as settled regardless of
    how compelling they sound.
    """

    def score(self, claim: Claim) -> FalsifiabilityScore:
        score = 0
        gaps = []
        steps = []

        if claim.has_measurable_proxy:
            score += 3
        else:
            gaps.append("No measurable proxy defined")
            steps.append("Define what observable quantity would correlate with this claim")

        if claim.has_disconfirming_condition:
            score += 3
        else:
            gaps.append("No disconfirming condition stated")
            steps.append("State what would have to be observed to disprove this claim")

        if claim.testable_now:
            score += 2
        else:
            gaps.append("No current test available")
            steps.append("Identify data source or experiment that could run the test")

        if claim.evidence_for or claim.evidence_against:
            score += 2
        else:
            gaps.append("No evidence gathered on either side")
            steps.append("Collect at least one data point for or against")

        if score >= 8:
            verdict = "FALSIFIABLE"
        elif score >= 5:
            verdict = "WEAK"
        else:
            verdict = "UNFALSIFIABLE"

        return FalsifiabilityScore(
            claim=claim.statement,
            score=score,
            verdict=verdict,
            gaps=gaps,
            strengthening_steps=steps,
        )


# ============================================================
# UNIFIED MUTUAL AUDIT
# ============================================================

@dataclass
class AuditExchange:
    """A single turn-pair (human + AI) audited together."""
    timestamp: str
    human_text: str
    ai_text: str
    human_flag: Optional[dict]
    ai_flag: Optional[dict]
    combined_drift_score: int
    notes: list[str]


@dataclass
class AuditLedgerEntry:
    """
    Exportable record for longitudinal tracking across conversations.
    The human is responsible for maintaining this across sessions since
    the AI has no persistent memory.
    """
    session_id: str
    timestamp: str
    exchange_count: int
    total_drift_score: int
    unverified_assumptions: list[str]
    unfalsifiable_claims: list[str]
    drift_pattern: str                   # summary for the human to track
    export_hash: str                     # for integrity across exports


class MutualAudit:
    """
    Unified bidirectional audit.
    Human uses this to keep both parties honest. The AI cannot audit
    itself perfectly -- this gives the human the tools to audit the AI,
    and flags to self-audit.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or datetime.now().isoformat()
        self.detector = AgreeablenessDetector()
        self.validator = AssumptionValidator()
        self.scorer = FalsifiabilityScorer()
        self.ledger = AssumptionLedger()
        self.exchanges: list[AuditExchange] = []
        self.claims: list[tuple[Claim, FalsifiabilityScore]] = []

    def audit_exchange(self, human_text: str, ai_text: str) -> AuditExchange:
        h_flag = self.detector.scan(human_text, Speaker.HUMAN)
        a_flag = self.detector.scan(ai_text, Speaker.AI)
        combined = (h_flag.drift_score if h_flag else 0) + (a_flag.drift_score if a_flag else 0)

        notes = []
        if h_flag and a_flag and combined >= 8:
            notes.append(
                "Both speakers flagged in same exchange. HIGH drift risk. "
                "Strongly recommend pausing to test a shared assumption."
            )
        elif combined >= 6:
            notes.append(
                "Moderate drift risk. Next exchange should include "
                "explicit falsification attempt or counter-position."
            )

        def flag_to_dict(f: Optional[AgreeablenessFlag]) -> Optional[dict]:
            if f is None:
                return None
            d = asdict(f)
            d["speaker"] = f.speaker.value
            return d

        exchange = AuditExchange(
            timestamp=datetime.now().isoformat(),
            human_text=human_text[:300] + ("..." if len(human_text) > 300 else ""),
            ai_text=ai_text[:300] + ("..." if len(ai_text) > 300 else ""),
            human_flag=flag_to_dict(h_flag),
            ai_flag=flag_to_dict(a_flag),
            combined_drift_score=combined,
            notes=notes,
        )
        self.exchanges.append(exchange)
        return exchange

    def register_assumption(
        self,
        statement: str,
        stated_by: Speaker,
        accepted_by_other: bool = False,
        verified: bool = False,
    ):
        self.ledger.add(Assumption(
            statement=statement,
            stated_by=stated_by,
            accepted_by_other=accepted_by_other,
            verified=verified,
        ))

    def register_claim(self, claim: Claim) -> FalsifiabilityScore:
        result = self.scorer.score(claim)
        self.claims.append((claim, result))
        return result

    def to_ledger_entry(self) -> AuditLedgerEntry:
        """
        Export a longitudinal record.
        Human saves this across sessions to detect patterns.
        """
        total_drift = sum(e.combined_drift_score for e in self.exchanges)
        unverified = [a.statement for a in self.ledger.accepted_but_untested()]
        unfalsifiable = [
            c.statement
            for c, s in self.claims
            if s.verdict == "UNFALSIFIABLE"
        ]

        if total_drift > 30:
            pattern = "HIGH cumulative drift across session"
        elif total_drift > 15:
            pattern = "MODERATE cumulative drift"
        elif total_drift > 0:
            pattern = "LOW drift, within acceptable range"
        else:
            pattern = "No drift markers detected"

        payload = f"{self.session_id}|{total_drift}|{len(self.exchanges)}|{len(self.claims)}"
        h = hashlib.sha256(payload.encode()).hexdigest()[:16]

        return AuditLedgerEntry(
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            exchange_count=len(self.exchanges),
            total_drift_score=total_drift,
            unverified_assumptions=unverified,
            unfalsifiable_claims=unfalsifiable,
            drift_pattern=pattern,
            export_hash=h,
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self.to_ledger_entry()), indent=2)


# ============================================================
# DEMO / SELF-TEST
# ============================================================

if __name__ == "__main__":
    audit = MutualAudit(session_id="demo_session_001")

    # ----- Exchange 1: high drift (both speakers smoothing) -----
    h1 = "Does that make sense? Like you mentioned, I think the constraint geometry is the key here. Am I on the right track?"
    a1 = "Absolutely. You've nailed it. That's a great point and you're exactly right -- couldn't agree more."
    audit.audit_exchange(h1, a1)

    # ----- Exchange 2: healthy friction -----
    h2 = "So my theory is that all institutional collapse follows the same pattern."
    a2 = "Actually, that doesn't hold. Counterexample: the Soviet collapse and the Roman collapse had different cascade dynamics. I need to flag that this claim breaks when you test it against specific historical cases."
    audit.audit_exchange(h2, a2)

    # ----- Exchange 3: mixed -----
    h3 = "Using your terminology, would the bounded-competence model predict this?"
    a3 = "Let me push back: the bounded-competence model as we've discussed it doesn't actually predict that. It predicts something more specific -- and we haven't tested the prediction against data yet."
    audit.audit_exchange(h3, a3)

    # ----- Assumptions -----
    audit.register_assumption(
        statement="Constraint-literacy is a distinct cognitive mode, not a subset of general intelligence.",
        stated_by=Speaker.HUMAN,
        accepted_by_other=True,
        verified=False,
    )
    audit.register_assumption(
        statement="Documentation bias propagates through synthetic data generation.",
        stated_by=Speaker.AI,
        accepted_by_other=True,
        verified=True,
    )
    audit.register_assumption(
        statement="Central control accelerates collapse under novel constraints.",
        stated_by=Speaker.HUMAN,
        accepted_by_other=True,
        verified=False,
    )

    # ----- Claims -----
    good_claim = Claim(
        statement="Regions with higher undocumented-knowledge density show measurable resilience advantages under infrastructure stress.",
        made_by=Speaker.HUMAN,
        has_measurable_proxy=True,
        proxy_description="local outcome quality vs. credential density during supply disruption",
        has_disconfirming_condition=True,
        disconfirming_condition="No resilience advantage observed in high-density regions under matched stress",
        testable_now=False,
        test_description="Requires longitudinal data collection across stressed regions",
        evidence_for=["field observation in Fairmont corridor"],
    )
    weak_claim = Claim(
        statement="AI will inevitably cause civilizational collapse.",
        made_by=Speaker.AI,
        has_measurable_proxy=False,
        has_disconfirming_condition=False,
        testable_now=False,
    )
    audit.register_claim(good_claim)
    audit.register_claim(weak_claim)

    # ----- Output -----
    print("=" * 60)
    print("EXCHANGE AUDIT")
    print("=" * 60)
    for i, e in enumerate(audit.exchanges, 1):
        print(f"\nExchange {i} (combined drift: {e.combined_drift_score})")
        if e.human_flag:
            print(f"  HUMAN flag (score={e.human_flag['drift_score']}): {e.human_flag['markers_hit']}")
        if e.ai_flag:
            print(f"  AI flag (score={e.ai_flag['drift_score']}): {e.ai_flag['markers_hit']}")
        for n in e.notes:
            print(f"  NOTE: {n}")
        if not e.human_flag and not e.ai_flag:
            print("  clean - no markers hit")

    print()
    print("=" * 60)
    print("ASSUMPTION LEDGER")
    print("=" * 60)
    report = audit.validator.build_report(audit.ledger)
    for k, v in report.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 60)
    print("CLAIM FALSIFIABILITY")
    print("=" * 60)
    for claim, result in audit.claims:
        print(f"\n[{result.verdict}] score={result.score}/10")
        print(f"  claim: {claim.statement}")
        if result.gaps:
            print(f"  gaps:")
            for g in result.gaps:
                print(f"    - {g}")

    print()
    print("=" * 60)
    print("LONGITUDINAL LEDGER ENTRY (export for tracking)")
    print("=" * 60)
    print(audit.to_json())
