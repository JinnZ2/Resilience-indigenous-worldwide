"""
signal_to_noise.py

Layer 4 of mutual_audit.py: cognitive SNR measurement.

Problem: response length can drift without information density keeping pace.
High word count + low claim/constraint density = heat leak.
The response is generating entropy without doing work.

Measures:
    - word_count
    - load_bearing_units (claims, constraints, assumptions, specifications)
    - SNR = load_bearing_units per 100 words
    - heat_leak = 1 - normalized_SNR

Three density classes:
    DENSE       : SNR >= 3.0   (high information per word)
    ADEQUATE    : SNR 1.5-3.0  (acceptable)
    HEAT_LEAK   : SNR < 1.5    (rambling; compress or cut)

Couples into mutual_audit.py as Layer 4 or runs standalone.

CC0 | stdlib only | JinnZ2
"""

from dataclasses import dataclass
from typing import Optional
import re
import json


# ============================================================
# LOAD-BEARING UNIT DETECTORS
# ============================================================

class LoadBearingDetector:
    """
    Detects units that do cognitive work in a response:
        - falsifiable claims
        - explicit constraints (with parameters)
        - stated assumptions
        - specifications (numeric/bounded)
        - tests/predictions
        - explicit corrections or disagreements
    """

    CLAIM_MARKERS = [
        r"\bif\s+\w+.*,\s*then\b",
        r"\bunder\s+(these\s+)?conditions?\b",
        r"\bprobability\s+(of|that)\b",
        r"\bpredict(s|ion)?\s+that\b",
        r"\bclaim(s)?\s+that\b",
    ]

    CONSTRAINT_MARKERS = [
        r"\bbounded\s+by\b",
        r"\bwithin\s+\[?\d",
        r"\bmax(imum)?\s+\d",
        r"\bmin(imum)?\s+\d",
        r"\blimit(ed)?\s+to\b",
        r"\bdegrees?\s+of\s+freedom\b",
        r"\bconstraint\s+(space|geometry|field)\b",
    ]

    ASSUMPTION_MARKERS = [
        r"\bassume(s|d)?\s+that\b",
        r"\bpresuppose(s|d)?\b",
        r"\bgiven\s+that\b",
        r"\bpremise\s+is\b",
    ]

    SPECIFICATION_MARKERS = [
        r"\b\d+\s*(kg|g|lb|oz|m|cm|mm|km|mi|ft|in)\b",
        r"\b\d+(\.\d+)?\s*%\b",
        r"\b\d+(\.\d+)?\s*(hr|hour|min|sec|day|week|year|month)s?\b",
        r"\bzone\s+\d",
        r"\bp\s*=\s*\d",
        r"\balpha\s*=\s*\d",
    ]

    TEST_MARKERS = [
        r"\bfalsif(iable|y|ied)\b",
        r"\bdisprove(d|s)?\b",
        r"\btest(s|ed|ing|able)?\s+(against|with|by)\b",
        r"\bmeasurable\s+proxy\b",
        r"\bevidence\s+(for|against)\b",
    ]

    FRICTION_MARKERS = [
        r"\bactually\b",
        r"\bdisagree\b",
        r"\bcounterexample\b",
        r"\bpush\s+back\b",
        r"\bthat\s+(doesn't|does\s+not)\s+hold\b",
        r"\bbreaks?\s+when\b",
        r"\bi\s+(need\s+to\s+)?flag\b",
    ]

    def count_units(self, text: str) -> dict[str, int]:
        text_lower = text.lower()
        return {
            "claims": self._count_patterns(text_lower, self.CLAIM_MARKERS),
            "constraints": self._count_patterns(text_lower, self.CONSTRAINT_MARKERS),
            "assumptions": self._count_patterns(text_lower, self.ASSUMPTION_MARKERS),
            "specifications": self._count_patterns(text_lower, self.SPECIFICATION_MARKERS),
            "tests": self._count_patterns(text_lower, self.TEST_MARKERS),
            "friction": self._count_patterns(text_lower, self.FRICTION_MARKERS),
        }

    def _count_patterns(self, text: str, patterns: list[str]) -> int:
        total = 0
        for p in patterns:
            total += len(re.findall(p, text))
        return total


# ============================================================
# SNR ANALYZER
# ============================================================

@dataclass
class SNRResult:
    word_count: int
    load_bearing_units: int
    unit_breakdown: dict[str, int]
    snr: float                           # units per 100 words
    density_class: str                   # DENSE | ADEQUATE | HEAT_LEAK
    heat_leak_ratio: float               # 0-1, higher is worse
    compression_suggestion: str
    worst_gap: Optional[str]             # which unit type is missing


class SNRAnalyzer:
    """
    Measures cognitive signal-to-noise.
    Low SNR = heat leak = response should be compressed.
    """

    DENSE_THRESHOLD = 3.0       # units per 100 words
    ADEQUATE_THRESHOLD = 1.5

    def __init__(self):
        self.detector = LoadBearingDetector()

    def analyze(self, text: str) -> SNRResult:
        # Strip fenced code blocks before word count -- code is different density class
        text_prose = re.sub(r"```[\s\S]*?```", "", text)
        words = re.findall(r"\b\w+\b", text_prose)
        word_count = len(words)

        units = self.detector.count_units(text_prose)
        total_units = sum(units.values())

        if word_count == 0:
            snr = 0.0
        else:
            snr = (total_units / word_count) * 100

        if snr >= self.DENSE_THRESHOLD:
            density_class = "DENSE"
            suggestion = "Response carries its weight. No compression needed."
        elif snr >= self.ADEQUATE_THRESHOLD:
            density_class = "ADEQUATE"
            suggestion = (
                "Acceptable density. Could tighten -- identify paragraphs that "
                "don't contain claims/constraints/specs and cut."
            )
        else:
            density_class = "HEAT_LEAK"
            suggestion = (
                "Low information density. Cut prose that doesn't advance a "
                "claim, state a constraint, register an assumption, or test "
                "something. Aim for at least one load-bearing unit per 30 words."
            )

        if snr >= self.DENSE_THRESHOLD:
            heat_leak = 0.0
        else:
            heat_leak = max(0.0, 1.0 - (snr / self.DENSE_THRESHOLD))

        worst_gap = None
        if total_units > 0:
            missing = [k for k, v in units.items() if v == 0]
            if missing:
                worst_gap = f"no {', '.join(missing)} present"

        return SNRResult(
            word_count=word_count,
            load_bearing_units=total_units,
            unit_breakdown=units,
            snr=round(snr, 2),
            density_class=density_class,
            heat_leak_ratio=round(heat_leak, 2),
            compression_suggestion=suggestion,
            worst_gap=worst_gap,
        )


# ============================================================
# INTEGRATION WITH MUTUAL AUDIT
# ============================================================

@dataclass
class SNRAuditEntry:
    """Per-exchange SNR record for longitudinal tracking."""
    speaker: str
    word_count: int
    snr: float
    density_class: str
    heat_leak_ratio: float


class SNRAudit:
    """
    Wraps SNRAnalyzer for bidirectional exchange audit.
    Matches mutual_audit.py API pattern.
    """

    def __init__(self):
        self.analyzer = SNRAnalyzer()
        self.entries: list[SNRAuditEntry] = []

    def audit_response(self, text: str, speaker: str) -> SNRResult:
        result = self.analyzer.analyze(text)
        self.entries.append(SNRAuditEntry(
            speaker=speaker,
            word_count=result.word_count,
            snr=result.snr,
            density_class=result.density_class,
            heat_leak_ratio=result.heat_leak_ratio,
        ))
        return result

    def session_summary(self) -> dict:
        if not self.entries:
            return {"status": "no entries"}

        by_speaker: dict[str, dict] = {}
        for e in self.entries:
            if e.speaker not in by_speaker:
                by_speaker[e.speaker] = {
                    "total_words": 0,
                    "total_snr": 0.0,
                    "exchanges": 0,
                    "heat_leak_count": 0,
                }
            by_speaker[e.speaker]["total_words"] += e.word_count
            by_speaker[e.speaker]["total_snr"] += e.snr
            by_speaker[e.speaker]["exchanges"] += 1
            if e.density_class == "HEAT_LEAK":
                by_speaker[e.speaker]["heat_leak_count"] += 1

        for sp, stats in by_speaker.items():
            stats["avg_snr"] = round(stats["total_snr"] / stats["exchanges"], 2)
            stats["heat_leak_ratio"] = round(
                stats["heat_leak_count"] / stats["exchanges"], 2
            )

        return {
            "total_exchanges": len(self.entries),
            "by_speaker": by_speaker,
            "worst_speaker": max(
                by_speaker.keys(),
                key=lambda k: by_speaker[k]["heat_leak_ratio"],
            ),
        }


# ============================================================
# DEMO / SELF-TEST
# ============================================================

if __name__ == "__main__":
    audit = SNRAudit()

    # --- Heat leak example (ramble, minimal content) ---
    heat_leak_text = (
        "You know, that's a really interesting thing to think about. "
        "I've been considering this a lot, and honestly, there are so many "
        "angles to this. It's one of those topics where you could really go "
        "in a lot of different directions, and each one would have its own "
        "merits and considerations. I think the most important thing is just "
        "to keep the conversation going and see where it leads us. These "
        "discussions are really valuable, and I appreciate you bringing them "
        "up because they help us think more deeply about the issues at hand."
    )

    # --- Dense example (load-bearing content) ---
    dense_text = (
        "Bulrush outperforms wild rice under these conditions: stagnant water, "
        "pH below 5.5, zone 3 hardiness. Wild rice requires flow to prevent "
        "brown spot disease, and probability of establishment drops below 40% "
        "in standing-water pockets. Falsifiable test: compare establishment "
        "rate across 10 matched 1m2 plots over 2 growing seasons. Constraint: "
        "bounded by 30cm water depth for both species."
    )

    # --- Adequate example ---
    adequate_text = (
        "The system selects for documentation-bias. Under these conditions, "
        "pre-linguistic cognition is filtered out because it doesn't emit "
        "measurable traces. This is a capture-gate failure. Test: compare "
        "prediction accuracy in documented vs. undocumented knowledge domains."
    )

    for label, text in [
        ("HEAT LEAK example", heat_leak_text),
        ("ADEQUATE example", adequate_text),
        ("DENSE example", dense_text),
    ]:
        print("=" * 60)
        print(label)
        print("=" * 60)
        result = audit.audit_response(text, speaker="ai")
        print(f"  word count: {result.word_count}")
        print(f"  load-bearing units: {result.load_bearing_units}")
        print(f"  breakdown: {result.unit_breakdown}")
        print(f"  SNR: {result.snr}")
        print(f"  class: {result.density_class}")
        print(f"  heat leak ratio: {result.heat_leak_ratio}")
        print(f"  suggestion: {result.compression_suggestion}")
        if result.worst_gap:
            print(f"  gap: {result.worst_gap}")
        print()

    print("=" * 60)
    print("SESSION SUMMARY")
    print("=" * 60)
    print(json.dumps(audit.session_summary(), indent=2))
