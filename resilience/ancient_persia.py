#!/usr/bin/env python3
"""
ancient_persia.py -- Consolidated resilience toolkit.

Combined modules from Inversion/scripts for indigenous resilience analysis:
  - Contamination detection (quantitative text analysis)
  - Resource flow dynamics (accumulation vs. circulation modeling)
  - Operational risk monitoring (weighted scoring, redline detection)
  - Dependency audit (hidden subsidies, vulnerability, sovereignty)
  - Validation framework (multi-epistemological claim validation)
  - Zero-infrastructure alerts (environmental signal networks)
  - Salvage reclamation (material recovery and reinventory)
  - Desert sand energy coupling (multi-physics energy harvesting)
  - Geometric desalination (vector-space water infrastructure)
  - Mineral mulch (stone-mulch microclimate simulation)
  - Organizational topology (hierarchy vs. distributed vs. embedded-rule)

Source: https://github.com/JinnZ2/Inversion/tree/main/scripts
"""


# ===========================================================================
# MODULE: Contamination Detector
# Source: scripts/contamination_detector.py
# ===========================================================================
"""
Contamination Detector -- Quantitative Text Analysis

Analyzes text for structural properties that correlate with institutional
capture and epistemic degradation. Uses five quantitative metrics rather
than keyword matching:

  1. Lexical Diversity (MATTR)  -- Moving-Average Type-Token Ratio
  2. Epistemic Hedging Ratio    -- hedge words vs. assertive words
  3. Source Diversity            -- citation count and entropy
  4. Argument Density            -- premise-conclusion pair ratio
  5. Circular Reasoning Score   -- Jaccard similarity between premises & conclusions

Each metric is individually reported with its value and interpretation.
The composite score combines all five on a [0, 1] scale.

References:
  - Covington & McFall (2010): MATTR for lexical diversity
  - Hyland (1998): hedging in academic discourse
  - Jaccard (1912): similarity coefficient
  - Shannon (1948): entropy for source concentration
"""

from __future__ import annotations

import argparse
import json
import math
import re
import string
import sys
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Tokenization
# ---------------------------------------------------------------------------

_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    return [w for w in text.lower().translate(_PUNCT_TABLE).split() if w]


def sentencize(text: str) -> list[str]:
    """Split text into sentences (simple heuristic)."""
    # Split on period/question/exclamation followed by space+capital or end
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in parts if s.strip()]


# ---------------------------------------------------------------------------
# Stopwords (minimal set for content-word extraction)
# ---------------------------------------------------------------------------

STOPWORDS = frozenset(
    "a an the and or but if in on at to for of is are was were be been being "
    "have has had do does did will would shall should can could may might must "
    "this that these those it its he she they we you i my your his her their "
    "our with from by as not no nor so yet also very too than then there here "
    "what which who whom whose when where how all each every some any many much "
    "more most other another such only just about above below between into "
    "through during before after".split()
)


def content_words(text: str) -> set[str]:
    """Extract content words (non-stopwords, length > 3)."""
    return {w for w in tokenize(text) if w not in STOPWORDS and len(w) > 3}


# ---------------------------------------------------------------------------
# Metric 1: Lexical Diversity -- MATTR
# ---------------------------------------------------------------------------

def compute_mattr(tokens: list[str], window: int = 50) -> float:
    """
    Moving-Average Type-Token Ratio (Covington & McFall, 2010).

    Computes TTR over a sliding window and averages. This corrects for
    the text-length bias of raw TTR.

    Returns value in [0, 1]. Higher = more lexically diverse.
    """
    if len(tokens) < window:
        if not tokens:
            return 0.0
        return len(set(tokens)) / len(tokens)

    ttrs: list[float] = []
    for i in range(len(tokens) - window + 1):
        w = tokens[i : i + window]
        ttrs.append(len(set(w)) / window)
    return sum(ttrs) / len(ttrs)


# ---------------------------------------------------------------------------
# Metric 2: Epistemic Hedging Ratio
# ---------------------------------------------------------------------------

HEDGE_WORDS = [
    "might", "could", "possibly", "suggests", "appears", "seems",
    "arguably", "perhaps", "may", "likely", "unlikely", "approximately",
    "roughly", "tends", "sometimes", "often", "generally", "typically",
    "probably", "plausibly", "potentially", "conceivably",
]

ASSERTIVE_WORDS = [
    "clearly", "obviously", "undeniably", "certainly", "always", "never",
    "proven", "definitively", "unquestionably", "absolutely", "must",
    "guaranteed", "indisputable", "undoubtedly", "irrefutable",
    "incontrovertible", "without question", "beyond doubt",
]


def compute_hedging_ratio(tokens: list[str]) -> tuple[float, int, int]:
    """
    Ratio of hedging language to total epistemic markers.

    Healthy scientific text: 0.3-0.6 (Hyland 1998).
    Below 0.15: low epistemic humility -- high assertiveness.
    Above 0.8: excessive hedging -- may lack substance.

    Returns (ratio, hedge_count, assert_count).
    """
    text_joined = " ".join(tokens)
    hedge_count = sum(text_joined.count(h) for h in HEDGE_WORDS)
    assert_count = sum(text_joined.count(a) for a in ASSERTIVE_WORDS)
    total = hedge_count + assert_count
    if total == 0:
        return 0.5, 0, 0  # neutral if no epistemic markers
    return hedge_count / total, hedge_count, assert_count


# ---------------------------------------------------------------------------
# Metric 3: Source Diversity
# ---------------------------------------------------------------------------

CITATION_PATTERNS = [
    re.compile(r"\(([A-Z][a-z]+(?:\s+(?:et\s+al|&\s+[A-Z][a-z]+))?\.?,?\s*\d{4})\)"),  # (Author 2024)
    re.compile(r"\[(\d+)\]"),                          # [1]
    re.compile(r"https?://\S+"),                       # URLs
    re.compile(r"[Aa]ccording\s+to\s+([A-Z][^\.,]+)"),  # According to X
]


def compute_source_diversity(text: str) -> tuple[float, int, float]:
    """
    Analyze citation patterns in text.

    Returns:
      - source_density: unique_sources / paragraph_count
      - unique_source_count
      - source_entropy: Shannon entropy over source frequencies (bits)
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    n_paragraphs = max(len(paragraphs), 1)

    sources: list[str] = []
    for pattern in CITATION_PATTERNS:
        for match in pattern.finditer(text):
            sources.append(match.group(0).lower().strip())

    unique = set(sources)
    n_unique = len(unique)
    source_density = n_unique / n_paragraphs

    # Shannon entropy over source frequencies
    if not sources:
        return source_density, 0, 0.0
    from collections import Counter
    counts = Counter(sources)
    total = len(sources)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())

    return source_density, n_unique, entropy


# ---------------------------------------------------------------------------
# Metric 4: Argument Density
# ---------------------------------------------------------------------------

PREMISE_INDICATORS = [
    "because", "since", "given that", "as evidenced by",
    "the reason is", "due to", "on the grounds that",
    "supported by", "as shown by", "the evidence shows",
]

CONCLUSION_INDICATORS = [
    "therefore", "thus", "hence", "consequently",
    "it follows that", "this means", "we can conclude",
    "this shows", "this demonstrates", "this implies",
    "as a result", "accordingly",
]


def compute_argument_density(sentences: list[str]) -> tuple[float, int]:
    """
    Ratio of premise-conclusion pairs to total sentences.

    Measures how much of the text is structured argumentation vs.
    bare assertion. Scientific text typically > 0.1.

    Returns (density, pair_count).
    """
    if not sentences:
        return 0.0, 0

    premise_indices: list[int] = []
    conclusion_indices: list[int] = []

    for i, sent in enumerate(sentences):
        lower = sent.lower()
        if any(ind in lower for ind in PREMISE_INDICATORS):
            premise_indices.append(i)
        if any(ind in lower for ind in CONCLUSION_INDICATORS):
            conclusion_indices.append(i)

    # Count valid premise-conclusion pairs (premise before conclusion, within 5 sentences)
    pairs = 0
    for ci in conclusion_indices:
        for pi in premise_indices:
            if 0 < ci - pi <= 5:
                pairs += 1
                break  # one match per conclusion

    return pairs / len(sentences), pairs


# ---------------------------------------------------------------------------
# Metric 5: Circular Reasoning Detection
# ---------------------------------------------------------------------------

def compute_circular_reasoning(sentences: list[str]) -> tuple[float, list[tuple[int, int, float]]]:
    """
    Detect circular reasoning via Jaccard similarity between premise
    and conclusion content words.

    For each conclusion sentence, find the nearest preceding premise.
    If the Jaccard similarity of their content words exceeds 0.5,
    flag as potential circular reasoning.

    Returns (score, list of (premise_idx, conclusion_idx, jaccard)).
    """
    if not sentences:
        return 0.0, []

    premise_map: dict[int, set[str]] = {}
    conclusion_map: dict[int, set[str]] = {}

    for i, sent in enumerate(sentences):
        lower = sent.lower()
        if any(ind in lower for ind in PREMISE_INDICATORS):
            premise_map[i] = content_words(sent)
        if any(ind in lower for ind in CONCLUSION_INDICATORS):
            conclusion_map[i] = content_words(sent)

    circular_pairs: list[tuple[int, int, float]] = []

    for ci, c_words in conclusion_map.items():
        if not c_words:
            continue
        # Find nearest preceding premise
        best_pi = -1
        best_jaccard = 0.0
        for pi, p_words in premise_map.items():
            if pi >= ci or not p_words:
                continue
            intersection = len(c_words & p_words)
            union = len(c_words | p_words)
            jaccard = intersection / union if union > 0 else 0.0
            if jaccard > best_jaccard:
                best_jaccard = jaccard
                best_pi = pi

        if best_pi >= 0 and best_jaccard > 0.5:
            circular_pairs.append((best_pi, ci, best_jaccard))

    n_conclusions = max(len(conclusion_map), 1)
    score = len(circular_pairs) / n_conclusions
    return score, circular_pairs


# ---------------------------------------------------------------------------
# Composite Report
# ---------------------------------------------------------------------------

@dataclass
class MetricResult:
    """Result of a single metric computation."""
    name: str
    value: float
    interpretation: str
    details: dict = field(default_factory=dict)


@dataclass
class Report:
    """Full analysis report."""
    source: str
    total_lines: int
    total_tokens: int
    total_sentences: int
    metrics: list[MetricResult] = field(default_factory=list)
    composite_score: float = 0.0
    risk_level: str = "CLEAN"


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def interpret_mattr(v: float) -> str:
    if v >= 0.70:
        return "HIGH lexical diversity -- varied vocabulary"
    elif v >= 0.50:
        return "MODERATE lexical diversity -- typical range"
    else:
        return "LOW lexical diversity -- repetitive, formulaic language"


def interpret_hedging(v: float) -> str:
    if v < 0.15:
        return "VERY LOW epistemic humility -- almost exclusively absolute claims"
    elif v < 0.30:
        return "LOW hedging -- more assertive than typical scientific discourse"
    elif v <= 0.60:
        return "NORMAL hedging ratio -- consistent with scientific discourse (Hyland 1998)"
    else:
        return "HIGH hedging -- excessive qualification, may lack substance"


def interpret_argument_density(v: float) -> str:
    if v >= 0.10:
        return "ADEQUATE argument structure -- claims supported by reasoning"
    elif v >= 0.05:
        return "LOW argument density -- many unsupported assertions"
    else:
        return "VERY LOW -- almost no structured argumentation detected"


def analyze(text: str, source: str = "<stdin>", sensor_import: object = None) -> Report:
    """Run all metrics and produce a composite report.

    If sensor_import (from fieldlink.parse_sensor_import) is provided,
    a sixth metric -- Sensor Coherence -- is added, measuring alignment
    between the text's epistemic signals and the somatic sensor atlas.
    """
    tokens = tokenize(text)
    sentences = sentencize(text)

    report = Report(
        source=source,
        total_lines=text.count("\n") + 1,
        total_tokens=len(tokens),
        total_sentences=len(sentences),
    )

    # 1. MATTR
    mattr = compute_mattr(tokens, window=50)
    report.metrics.append(MetricResult(
        name="Lexical Diversity (MATTR-50)",
        value=round(mattr, 4),
        interpretation=interpret_mattr(mattr),
        details={"window": 50, "total_tokens": len(tokens)},
    ))

    # 2. Hedging ratio
    hedging, n_hedge, n_assert = compute_hedging_ratio(tokens)
    report.metrics.append(MetricResult(
        name="Epistemic Hedging Ratio",
        value=round(hedging, 4),
        interpretation=interpret_hedging(hedging),
        details={"hedge_count": n_hedge, "assertive_count": n_assert},
    ))

    # 3. Source diversity
    src_density, n_sources, src_entropy = compute_source_diversity(text)
    report.metrics.append(MetricResult(
        name="Source Diversity",
        value=round(src_density, 4),
        interpretation=(
            f"{n_sources} unique source(s), density={src_density:.2f}/paragraph, "
            f"entropy={src_entropy:.2f} bits"
        ),
        details={
            "unique_sources": n_sources,
            "density": round(src_density, 4),
            "entropy_bits": round(src_entropy, 4),
        },
    ))

    # 4. Argument density
    arg_density, n_pairs = compute_argument_density(sentences)
    report.metrics.append(MetricResult(
        name="Argument Density",
        value=round(arg_density, 4),
        interpretation=interpret_argument_density(arg_density),
        details={"premise_conclusion_pairs": n_pairs, "total_sentences": len(sentences)},
    ))

    # 5. Circular reasoning
    circ_score, circ_pairs = compute_circular_reasoning(sentences)
    report.metrics.append(MetricResult(
        name="Circular Reasoning Score",
        value=round(circ_score, 4),
        interpretation=(
            f"{len(circ_pairs)} circular pair(s) detected"
            + (f" (max Jaccard={max(j for _, _, j in circ_pairs):.2f})" if circ_pairs else "")
        ),
        details={
            "circular_pairs": [
                {"premise_sentence": p, "conclusion_sentence": c, "jaccard": round(j, 4)}
                for p, c, j in circ_pairs
            ],
        },
    ))

    # 6. Sensor coherence (optional -- requires fieldlink sensor import)
    sensor_concern = 0.0
    has_sensor = False
    if sensor_import is not None:
        try:
            from scripts.fieldlink import compute_sensor_coherence
            coherence = compute_sensor_coherence(text, sensor_import)
            sensor_score = coherence["coherence_score"]
            report.metrics.append(MetricResult(
                name="Sensor Coherence (fieldlink)",
                value=round(sensor_score, 4),
                interpretation=(
                    f"Coherence with somatic sensor atlas: {sensor_score:.2f} "
                    f"({coherence['n_sensors_matched']} sensors matched, "
                    f"{coherence['n_corruption_matches']} corruption flags)"
                ),
                details=coherence,
            ))
            sensor_concern = 1.0 - clamp(sensor_score)  # low coherence is concerning
            has_sensor = True
        except ImportError:
            pass  # fieldlink not available, skip gracefully

    # Composite score: higher = more contamination signals
    # Each component maps a metric to a [0,1] "concern" value
    mattr_concern = 1.0 - clamp(mattr / 0.70)           # low diversity is concerning
    hedging_concern = 1.0 - clamp(hedging / 0.50)        # low hedging is concerning
    arg_concern = 1.0 - clamp(arg_density / 0.10)        # low argument density is concerning
    src_concern = 1.0 - clamp(src_density / 0.50)        # low source density is concerning
    circ_concern = clamp(circ_score)                      # circular reasoning is concerning

    if has_sensor:
        # With sensor data: redistribute weights to include sensor coherence
        report.composite_score = round(
            0.20 * hedging_concern
            + 0.17 * mattr_concern
            + 0.17 * arg_concern
            + 0.17 * circ_concern
            + 0.12 * src_concern
            + 0.17 * sensor_concern,
            4,
        )
    else:
        report.composite_score = round(
            0.25 * hedging_concern
            + 0.20 * mattr_concern
            + 0.20 * arg_concern
            + 0.20 * circ_concern
            + 0.15 * src_concern,
            4,
        )

    if report.composite_score < 0.20:
        report.risk_level = "LOW"
    elif report.composite_score < 0.45:
        report.risk_level = "MODERATE"
    elif report.composite_score < 0.70:
        report.risk_level = "HIGH"
    else:
        report.risk_level = "CRITICAL"

    return report


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(report: Report) -> None:
    print("=" * 80)
    print("  QUANTITATIVE TEXT ANALYSIS REPORT")
    print(f"  Source: {report.source}")
    print(f"  Tokens: {report.total_tokens}  |  Sentences: {report.total_sentences}  |  Lines: {report.total_lines}")
    print("=" * 80)

    for m in report.metrics:
        print(f"\n  [{m.name}]")
        print(f"    Value: {m.value}")
        print(f"    {m.interpretation}")

    print(f"\n{'=' * 80}")
    print(f"  COMPOSITE SCORE: {report.composite_score:.4f}  [{report.risk_level}]")
    print(f"{'=' * 80}")
    print()
    print("  Score components (0 = no concern, 1 = high concern):")
    print(f"    Hedging deficit    (25%): {1.0 - clamp(report.metrics[1].value / 0.50):.3f}")
    print(f"    Lexical poverty    (20%): {1.0 - clamp(report.metrics[0].value / 0.70):.3f}")
    print(f"    Argument deficit   (20%): {1.0 - clamp(report.metrics[3].value / 0.10):.3f}")
    print(f"    Circular reasoning (20%): {clamp(report.metrics[4].value):.3f}")
    print(f"    Source deficit     (15%): {1.0 - clamp(report.metrics[2].details['density'] / 0.50):.3f}")
    print()


def print_json_report(report: Report) -> None:
    data = {
        "source": report.source,
        "total_tokens": report.total_tokens,
        "total_sentences": report.total_sentences,
        "composite_score": report.composite_score,
        "risk_level": report.risk_level,
        "metrics": [
            {
                "name": m.name,
                "value": m.value,
                "interpretation": m.interpretation,
                **m.details,
            }
            for m in report.metrics
        ],
    }
    print(json.dumps(data, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quantitative text analysis for epistemic quality"
    )
    parser.add_argument("file", nargs="?", help="File to analyze (default: stdin)")
    parser.add_argument("--text", "-t", help="Inline text to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--sensors", metavar="PATH",
        help="Path to Emotions-as-Sensors JSON export for sensor-augmented analysis",
    )
    args = parser.parse_args()

    if args.text:
        text = args.text
        source = "<inline>"
    elif args.file:
        with open(args.file) as f:
            text = f.read()
        source = args.file
    else:
        text = sys.stdin.read()
        source = "<stdin>"

    # Load sensor import if provided
    sensor_import = None
    if args.sensors:
        try:
            from scripts.fieldlink import parse_sensor_import
            with open(args.sensors) as sf:
                sensor_import = parse_sensor_import(json.load(sf))
        except (ImportError, FileNotFoundError) as e:
            print(f"Warning: Could not load sensor data: {e}", file=sys.stderr)

    report = analyze(text, source, sensor_import=sensor_import)

    if args.json:
        print_json_report(report)
    else:
        print_report(report)

    if report.risk_level in ("HIGH", "CRITICAL"):
        sys.exit(2)
    elif report.risk_level == "MODERATE":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Resource Flow Dynamics
# Source: scripts/resource_flow_dynamics.py
# ===========================================================================
"""
resource_flow_dynamics.py — Coupled resource flow dynamics simulation.

Models accumulation vs. circulation vs. coupling in single-pool and
multi-agent networked systems.  Tracks circulating resource (C),
hoarded/stored resource (H), and responsiveness (R, a coupling
efficiency between 0 and 1).

Single-pool model
    Minimal three-variable ODE: extraction drains C into H, release
    returns H to C, productivity amplifies C proportional to R, and
    dissipation removes C.  Responsiveness degrades under load and
    recovers toward 1.

Multi-agent networked model
    N agents each carry their own (C, H, R) and are linked by a
    row-stochastic adjacency matrix.  Diffusive flow moves C from
    high- to low-concentration agents.  Designated "hoarder" agents
    can have elevated extraction and suppressed release.

Analysis utilities compute peak throughput, collapse detection
(throughput < 20 % of peak), and Gini coefficients for terminal
distributions.

References
----------
* Lotka–Volterra resource competition — Volterra (1926), Gause (1934).
* Gini coefficient — Gini, C. (1912).  "Variabilità e mutabilità."
* Diffusion on networks — Masuda, Porter & Lambiotte (2017), "Random
  walks and diffusion on networks", Physics Reports 716–717.

Usage
-----
    python3 scripts/resource_flow_dynamics.py --mode single --steps 2000
    python3 scripts/resource_flow_dynamics.py --mode network --steps 800 --agents 30
    python3 scripts/resource_flow_dynamics.py --mode network --json
    python3 scripts/resource_flow_dynamics.py --help
"""

import argparse
import json
import math
import random
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple


# -----------------------------------------------------------------------
#  Numeric helpers (stdlib replacements for numpy operations)
# -----------------------------------------------------------------------

def _clip(value, lo, hi):
    """Clamp a scalar to [lo, hi]."""
    if lo is not None and value < lo:
        return lo
    if hi is not None and value > hi:
        return hi
    return value


def _vec_clip(vec, lo, hi):
    """Element-wise clamp a list of floats."""
    return [_clip(v, lo, hi) for v in vec]


def _vec_add(a, b):
    return [x + y for x, y in zip(a, b)]


def _vec_sub(a, b):
    return [x - y for x, y in zip(a, b)]


def _vec_mul(a, b):
    """Element-wise multiplication of two lists."""
    return [x * y for x, y in zip(a, b)]


def _vec_scale(a, s):
    return [x * s for x in a]


def _vec_div_scalar(a, s):
    return [x / s for x in a]


def _vec_full(n, val):
    return [val] * n


def _vec_sum(a):
    return sum(a)


def _vec_mean(a):
    return sum(a) / len(a) if a else 0.0


def _vec_min(a):
    return min(a)


def _vec_max(a):
    return max(a)


def _vec_argmax(a):
    return max(range(len(a)), key=lambda i: a[i])


def _vec_copy(a):
    return list(a)


def _vec_abs(a):
    return [abs(x) for x in a]


def _vec_sorted(a):
    return sorted(a)


def _make_row_stochastic(matrix, n):
    """Normalise each row to sum to 1 and zero the diagonal."""
    for i in range(n):
        s = sum(matrix[i])
        if s > 0:
            matrix[i] = [v / s for v in matrix[i]]
        matrix[i][i] = 0.0
    return matrix


def _random_adjacency(n, rng):
    """Create a random row-stochastic adjacency matrix (list of lists)."""
    mat = [[rng.random() for _ in range(n)] for _ in range(n)]
    return _make_row_stochastic(mat, n)


# -----------------------------------------------------------------------
#  Single-Pool Model
# -----------------------------------------------------------------------

@dataclass
class FlowParams:
    """Parameters for single-pool H/C/R dynamics."""
    alpha: float = 0.08    # extraction rate (C -> H)
    beta: float = 0.02     # release rate (H -> C)
    delta: float = 0.04    # productivity (C generates more C)
    gamma: float = 0.02    # dissipation (entropy loss from C)
    k1: float = 0.005      # responsiveness degradation rate
    k2: float = 0.010      # responsiveness recovery rate
    C_ref: float = 100.0   # reference C level for signal normalization
    dt: float = 0.1        # time step


@dataclass
class FlowState:
    """State of a single-pool system."""
    C: float = 100.0       # circulating resource
    H: float = 10.0        # hoarded/stored resource
    R: float = 1.0         # responsiveness (coupling efficiency, 0-1)


def step_single(state: FlowState, params: FlowParams) -> FlowState:
    """Advance single-pool system by one time step."""
    C, H, R = state.C, state.H, state.R
    dt = params.dt

    extraction = params.alpha * C
    release = params.beta * H
    productivity = params.delta * C * R
    dissipation = params.gamma * C
    signal = C / params.C_ref  # normalized coupling load (0-1 scale)

    dC = -extraction + release + productivity - dissipation
    dH = extraction - release
    dR = -params.k1 * signal + params.k2 * (1.0 - R)

    return FlowState(
        C=max(0, C + dC * dt),
        H=max(0, H + dH * dt),
        R=_clip(R + dR * dt, 0, 1),
    )


def run_single(
    params: FlowParams,
    initial: Optional[FlowState] = None,
    steps: int = 2000,
) -> Dict[str, Any]:
    """
    Run single-pool simulation.

    Returns
    -------
    dict with time series for C, H, R, throughput, and total resource.
    """
    state = initial or FlowState()
    history: Dict[str, list] = {
        "C": [], "H": [], "R": [], "throughput": [], "total": [],
    }

    for _ in range(steps):
        throughput = params.delta * state.C * state.R
        history["C"].append(state.C)
        history["H"].append(state.H)
        history["R"].append(state.R)
        history["throughput"].append(throughput)
        history["total"].append(state.C + state.H)
        state = step_single(state, params)

    return history


# -----------------------------------------------------------------------
#  Multi-Agent Networked Model
# -----------------------------------------------------------------------

@dataclass
class NetworkParams:
    """Parameters for multi-agent networked dynamics."""
    n_agents: int = 30
    kappa: float = 0.15          # network flow strength
    alpha: Optional[list] = None       # per-agent extraction rates
    beta: Optional[list] = None        # per-agent release rates
    delta: Optional[list] = None       # per-agent productivity
    gamma: Optional[list] = None       # per-agent dissipation
    k1: float = 0.004            # responsiveness degradation
    k2: float = 0.008            # responsiveness recovery
    C_ref: float = 50.0          # reference C level for signal normalization
    dt: float = 0.05
    adjacency: Optional[list] = None   # row-stochastic adjacency matrix

    def __post_init__(self):
        n = self.n_agents
        if self.alpha is None:
            self.alpha = _vec_full(n, 0.06)
        if self.beta is None:
            self.beta = _vec_full(n, 0.02)
        if self.delta is None:
            self.delta = _vec_full(n, 0.04)
        if self.gamma is None:
            self.gamma = _vec_full(n, 0.02)
        if self.adjacency is None:
            rng = random.Random(42)
            self.adjacency = _random_adjacency(n, rng)


@dataclass
class NetworkState:
    """State of a multi-agent network."""
    C: list   # circulating per agent
    H: list   # stored per agent
    R: list   # responsiveness per agent

    @classmethod
    def default(cls, n: int, seed: int = 42) -> "NetworkState":
        rng = random.Random(seed)
        C = [_clip(50 + 10 * rng.gauss(0, 1), 10, None) for _ in range(n)]
        H = _vec_full(n, 10.0)
        R = _vec_full(n, 1.0)
        return cls(C=C, H=H, R=R)


def network_flow(C: list, A: list, kappa: float) -> list:
    """Compute net flow for each agent from diffusion on adjacency."""
    n = len(C)
    result = [0.0] * n
    for i in range(n):
        for j in range(n):
            # F_ij = kappa * A_ij * (C_i - C_j)
            f = kappa * A[i][j] * (C[i] - C[j])
            # inflow from j's perspective, outflow from i's perspective
            result[j] += f
            result[i] -= f
    return result


def step_network(state: NetworkState, params: NetworkParams) -> NetworkState:
    """Advance network by one time step."""
    C, H, R = state.C, state.H, state.R
    dt = params.dt

    extraction = _vec_mul(params.alpha, C)
    release = _vec_mul(params.beta, H)
    productivity = _vec_mul(_vec_mul(params.delta, C), R)
    dissipation = _vec_mul(params.gamma, C)
    net_flow = network_flow(C, params.adjacency, params.kappa)
    signal = _vec_div_scalar(C, params.C_ref)

    # dC = -extraction + release + productivity - dissipation + net_flow
    dC = _vec_add(
        _vec_add(_vec_sub(_vec_sub([0.0] * len(C), extraction), dissipation),
                 release),
        _vec_add(productivity, net_flow),
    )
    dH = _vec_sub(extraction, release)
    # dR = -k1 * signal + k2 * (1 - R)
    dR = _vec_add(
        _vec_scale(signal, -params.k1),
        _vec_scale(_vec_sub(_vec_full(len(R), 1.0), R), params.k2),
    )

    return NetworkState(
        C=_vec_clip(_vec_add(C, _vec_scale(dC, dt)), 0, None),
        H=_vec_clip(_vec_add(H, _vec_scale(dH, dt)), 0, None),
        R=_vec_clip(_vec_add(R, _vec_scale(dR, dt)), 0, 1),
    )


def run_network(
    params: NetworkParams,
    initial: Optional[NetworkState] = None,
    steps: int = 800,
    hoarder_indices: Optional[List[int]] = None,
    hoarder_alpha: float = 0.10,
    hoarder_beta: float = 0.005,
    perturbation_step: Optional[int] = None,
    perturbation_fraction: float = 0.3,
    perturbation_sigma: float = 2.0,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Run multi-agent network simulation.

    Parameters
    ----------
    hoarder_indices : list[int], optional
        Agents with elevated extraction and reduced release.
    perturbation_step : int, optional
        Step at which to inject random perturbation.

    Returns
    -------
    dict with aggregate time series and per-agent final state.
    """
    rng = random.Random(seed)

    # Apply hoarder parameters
    if hoarder_indices:
        for i in hoarder_indices:
            params.alpha[i] = hoarder_alpha
            params.beta[i] = hoarder_beta

    state = initial or NetworkState.default(params.n_agents, seed)

    agg: Dict[str, list] = {
        "total_C": [], "total_H": [], "total_throughput": [],
        "mean_R": [], "min_R": [],
    }

    for t in range(steps):
        # Perturbation
        if perturbation_step is not None and t == perturbation_step:
            count = max(1, int(params.n_agents * perturbation_fraction))
            indices = rng.sample(range(params.n_agents), count)
            for idx in indices:
                state.C[idx] += rng.gauss(0, perturbation_sigma)
            state.C = _vec_clip(state.C, 0, None)

        throughput = _vec_mul(_vec_mul(params.delta, state.C), state.R)

        agg["total_C"].append(_vec_sum(state.C))
        agg["total_H"].append(_vec_sum(state.H))
        agg["total_throughput"].append(_vec_sum(throughput))
        agg["mean_R"].append(_vec_mean(state.R))
        agg["min_R"].append(_vec_min(state.R))

        state = step_network(state, params)

    return {
        "aggregates": agg,
        "final_state": {
            "C": _vec_copy(state.C),
            "H": _vec_copy(state.H),
            "R": _vec_copy(state.R),
        },
        "params": {
            "n_agents": params.n_agents,
            "kappa": params.kappa,
            "k1": params.k1,
            "k2": params.k2,
            "hoarder_indices": hoarder_indices or [],
        },
    }


# -----------------------------------------------------------------------
#  Analysis Utilities
# -----------------------------------------------------------------------

def diagnose_single(history: Dict[str, list]) -> Dict[str, Any]:
    """Diagnose single-pool run."""
    C, H, R = history["C"], history["H"], history["R"]
    tp = history["throughput"]

    peak_throughput_t = _vec_argmax(tp)
    final_R = float(R[-1])
    total_accumulated = float(H[-1])
    total_circulating = float(C[-1])

    # Detect collapse: throughput drops below 20% of peak
    peak_tp = _vec_max(tp)
    collapse_t = None
    for t in range(peak_throughput_t, len(tp)):
        if tp[t] < 0.2 * peak_tp:
            collapse_t = t
            break

    return {
        "peak_throughput": float(peak_tp),
        "peak_throughput_time": peak_throughput_t,
        "final_responsiveness": final_R,
        "final_stored": total_accumulated,
        "final_circulating": total_circulating,
        "collapse_time": collapse_t,
        "regime": (
            "collapsed" if collapse_t is not None
            else "degraded" if final_R < 0.3
            else "stable"
        ),
    }


def diagnose_network(result: Dict[str, Any]) -> Dict[str, Any]:
    """Diagnose network run."""
    agg = result["aggregates"]
    tp = agg["total_throughput"]
    mean_R = agg["mean_R"]

    peak_tp = float(_vec_max(tp))
    peak_t = _vec_argmax(tp)
    final_tp = float(tp[-1])

    collapse_t = None
    for t in range(peak_t, len(tp)):
        if tp[t] < 0.2 * peak_tp:
            collapse_t = t
            break

    final = result["final_state"]
    gini_C = _gini(final["C"])
    gini_H = _gini(final["H"])

    return {
        "peak_throughput": peak_tp,
        "final_throughput": final_tp,
        "throughput_retention": final_tp / peak_tp if peak_tp > 0 else 0,
        "final_mean_R": float(mean_R[-1]),
        "collapse_time": collapse_t,
        "gini_C": gini_C,
        "gini_H": gini_H,
        "regime": (
            "collapsed" if collapse_t is not None
            else "degraded" if mean_R[-1] < 0.3
            else "stable"
        ),
    }


def _gini(arr: list) -> float:
    """Gini coefficient (0 = equal, 1 = one agent has everything)."""
    arr = [abs(x) for x in arr]
    total = sum(arr)
    if total == 0:
        return 0.0
    sorted_arr = sorted(arr)
    n = len(sorted_arr)
    weighted_sum = sum((i + 1) * v for i, v in enumerate(sorted_arr))
    return float((2 * weighted_sum / (n * total)) - (n + 1) / n)


# -----------------------------------------------------------------------
#  CLI
# -----------------------------------------------------------------------

def _format_diagnosis(diag: Dict[str, Any], label: str) -> str:
    """Format a diagnosis dict as human-readable text."""
    lines = [f"--- {label} ---"]
    for k, v in diag.items():
        if isinstance(v, float):
            lines.append(f"  {k}: {v:.6f}")
        else:
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Coupled resource flow dynamics: accumulation vs "
                    "circulation vs coupling.  Single-pool and multi-agent "
                    "networked models with diagnosis utilities.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  %(prog)s --mode single --steps 2000\n"
            "  %(prog)s --mode network --agents 30 --steps 800\n"
            "  %(prog)s --mode network --hoarders 0,1,2 --json\n"
        ),
    )
    parser.add_argument(
        "--mode", choices=["single", "network"], default="single",
        help="simulation mode (default: single)",
    )
    parser.add_argument(
        "--steps", type=int, default=None,
        help="number of time steps (default: 2000 single, 800 network)",
    )
    parser.add_argument(
        "--agents", type=int, default=30,
        help="number of agents for network mode (default: 30)",
    )
    parser.add_argument(
        "--hoarders", type=str, default=None,
        help="comma-separated agent indices to designate as hoarders",
    )
    parser.add_argument(
        "--hoarder-alpha", type=float, default=0.10,
        help="extraction rate for hoarder agents (default: 0.10)",
    )
    parser.add_argument(
        "--hoarder-beta", type=float, default=0.005,
        help="release rate for hoarder agents (default: 0.005)",
    )
    parser.add_argument(
        "--perturbation-step", type=int, default=None,
        help="step at which to inject random perturbation (network mode)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="random seed (default: 42)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="output full results as JSON",
    )

    args = parser.parse_args()

    if args.mode == "single":
        steps = args.steps or 2000
        params = FlowParams()
        history = run_single(params, steps=steps)
        diag = diagnose_single(history)

        if args.json:
            json.dump({
                "mode": "single",
                "steps": steps,
                "diagnosis": diag,
                "history": {k: [round(x, 8) for x in v] for k, v in history.items()},
            }, sys.stdout, indent=2)
            print()
        else:
            print(_format_diagnosis(diag, "Single-Pool Diagnosis"))

    elif args.mode == "network":
        steps = args.steps or 800
        hoarder_indices = None
        if args.hoarders:
            hoarder_indices = [int(x.strip()) for x in args.hoarders.split(",")]

        params = NetworkParams(n_agents=args.agents)
        result = run_network(
            params,
            steps=steps,
            hoarder_indices=hoarder_indices,
            hoarder_alpha=args.hoarder_alpha,
            hoarder_beta=args.hoarder_beta,
            perturbation_step=args.perturbation_step,
            seed=args.seed,
        )
        diag = diagnose_network(result)

        if args.json:
            output = {
                "mode": "network",
                "steps": steps,
                "diagnosis": diag,
                "aggregates": {
                    k: [round(x, 8) for x in v]
                    for k, v in result["aggregates"].items()
                },
                "final_state": {
                    k: [round(x, 8) for x in v]
                    for k, v in result["final_state"].items()
                },
                "params": result["params"],
            }
            json.dump(output, sys.stdout, indent=2)
            print()
        else:
            print(_format_diagnosis(diag, "Network Diagnosis"))
            print(f"\n  agents: {args.agents}")
            if hoarder_indices:
                print(f"  hoarders: {hoarder_indices}")


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Operational Risk
# Source: scripts/operational_risk.py
# ===========================================================================
"""
operational_risk.py — Operational Risk Monitor

Weighted risk scoring, price divergence detection, field observation
analysis, redline threshold checking, and batch auditing.

This is a generic framework: configure weights and thresholds for any
domain.  All metrics are expected on a 0-1 normalized scale unless
otherwise noted.

Methodology
-----------
- **Weighted risk scoring**: composite score as a convex combination of
  normalised indicator values, following standard multi-criteria
  decision analysis (MCDA) weighted-sum approaches (Keeney & Raiffa,
  1976).
- **Price divergence**: ratio-based anomaly detection against a
  reference price, flagging potential input substitution when actual
  cost falls well below expected cost.
- **Redline detection**: rule-based threshold monitoring inspired by
  control-chart logic (Shewhart, 1931) — each rule specifies
  "above"/"below" bounds and triggers when all conditions are met
  simultaneously.

References
----------
Keeney, R. L. & Raiffa, H. (1976). Decisions with Multiple
    Objectives. Wiley.
Shewhart, W. A. (1931). Economic Control of Quality of Manufactured
    Product. Van Nostrand.

Usage
-----
    python3 scripts/operational_risk.py --help
    python3 scripts/operational_risk.py --demo
    python3 scripts/operational_risk.py --demo --json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


# ------------------
# Weighted Risk Scorer
# ------------------

@dataclass
class RiskProfile:
    """Configurable weighted risk scorer."""
    weights: Dict[str, float]
    # metric_name -> weight (should sum to ~1.0)

    def score(self, metrics: Dict[str, float]) -> float:
        """
        Weighted sum of normalized metrics (each 0-1).
        Returns 0-1 composite risk score.
        """
        total = sum(
            metrics.get(k, 0) * w
            for k, w in self.weights.items()
        )
        return round(min(1.0, max(0, total)), 3)

    def classify(
        self,
        metrics: Dict[str, float],
        thresholds: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Score and classify into risk bands.

        Parameters
        ----------
        thresholds : dict, optional
            {"critical": 0.7, "warning": 0.4}
        """
        if thresholds is None:
            thresholds = {"critical": 0.7, "warning": 0.4}

        s = self.score(metrics)
        if s >= thresholds.get("critical", 0.7):
            level = "critical"
        elif s >= thresholds.get("warning", 0.4):
            level = "warning"
        else:
            level = "nominal"

        return {"score": s, "level": level, "metrics": metrics}


# ------------------
# Price Divergence Detector
# ------------------

def price_divergence(
    reference_price: float,
    actual_price: float,
    critical_threshold: float = 0.30,
) -> Dict[str, Any]:
    """
    Detect when actual price diverges significantly from reference.
    Large negative divergence (actual << reference) may indicate
    substitution with lower-quality inputs.

    Returns
    -------
    dict with divergence ratio and classification
    """
    if reference_price <= 0:
        return {"divergence": 0, "level": "invalid", "note": "reference_price <= 0"}

    divergence = (reference_price - actual_price) / reference_price

    if divergence > critical_threshold:
        level = "critical"
    elif divergence > critical_threshold * 0.5:
        level = "warning"
    else:
        level = "nominal"

    return {
        "reference_price": reference_price,
        "actual_price": actual_price,
        "divergence": round(divergence, 3),
        "level": level,
    }


# ------------------
# Field Observation Scorer
# ------------------

@dataclass
class FieldObservation:
    """
    Weighted field observation risk assessment.
    Each observation is 0-1 (0 = no concern, 1 = maximum concern).
    """
    weights: Dict[str, float]
    # observation_name -> weight

    def assess(
        self,
        observations: Dict[str, float],
        thresholds: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Score field observations and classify.
        """
        if thresholds is None:
            thresholds = {"critical": 0.7, "warning": 0.4}

        total = sum(
            observations.get(k, 0) * w
            for k, w in self.weights.items()
        )
        total = round(min(1.0, max(0, total)), 3)

        if total >= thresholds.get("critical", 0.7):
            level = "critical"
        elif total >= thresholds.get("warning", 0.4):
            level = "warning"
        else:
            level = "nominal"

        return {"score": total, "level": level, "observations": observations}


# ------------------
# Redline Detector
# ------------------

def redline_check(
    metrics: Dict[str, float],
    redline_rules: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Check if a system has crossed critical thresholds.

    Parameters
    ----------
    metrics : dict
        metric_name -> value (0-1 scale, direction depends on metric)
    redline_rules : list of dicts, optional
        Each rule: {"name": str, "conditions": dict, "level": str}
        conditions: metric_name -> {"above": float} or {"below": float}

    Returns
    -------
    dict with triggered rules and overall status
    """
    if redline_rules is None:
        # Default: infrastructure below 0.4 AND error above 0.6
        redline_rules = [
            {
                "name": "systemic_failure",
                "conditions": {
                    "infrastructure_integrity": {"below": 0.4},
                    "error_rate": {"above": 0.6},
                },
                "level": "critical",
            },
            {
                "name": "infrastructure_decay",
                "conditions": {
                    "infrastructure_integrity": {"below": 0.5},
                },
                "level": "warning",
            },
            {
                "name": "high_error",
                "conditions": {
                    "error_rate": {"above": 0.5},
                },
                "level": "warning",
            },
        ]

    triggered = []
    for rule in redline_rules:
        all_met = True
        for metric_name, condition in rule["conditions"].items():
            value = metrics.get(metric_name, 0)
            if "above" in condition and value <= condition["above"]:
                all_met = False
            if "below" in condition and value >= condition["below"]:
                all_met = False
        if all_met:
            triggered.append({"rule": rule["name"], "level": rule["level"]})

    # Overall status: worst triggered level
    if any(t["level"] == "critical" for t in triggered):
        overall = "critical"
    elif any(t["level"] == "warning" for t in triggered):
        overall = "warning"
    else:
        overall = "nominal"

    return {"overall": overall, "triggered": triggered, "metrics": metrics}


# ------------------
# Batch Audit
# ------------------

def audit_batch(
    entities: Dict[str, Dict[str, float]],
    risk_profile: RiskProfile,
    thresholds: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """
    Run risk scoring across multiple entities.

    Parameters
    ----------
    entities : dict
        entity_name -> {metric_name: value}
    risk_profile : RiskProfile

    Returns
    -------
    list of results sorted by score descending
    """
    results = []
    for name, metrics in entities.items():
        r = risk_profile.classify(metrics, thresholds)
        r["entity"] = name
        results.append(r)

    results.sort(key=lambda x: -x["score"])
    return results


# ------------------
# Demo / CLI
# ------------------

def run_demo() -> Dict[str, Any]:
    """Run a demonstration with sample data and return all results."""
    output: Dict[str, Any] = {}

    # 1. Weighted risk scoring
    profile = RiskProfile(weights={
        "cost_deviation": 0.3,
        "error_rate": 0.3,
        "infrastructure_integrity": 0.2,
        "compliance_gap": 0.2,
    })
    sample_metrics = {
        "cost_deviation": 0.8,
        "error_rate": 0.6,
        "infrastructure_integrity": 0.35,
        "compliance_gap": 0.5,
    }
    output["risk_classification"] = profile.classify(sample_metrics)

    # 2. Price divergence
    output["price_divergence"] = price_divergence(
        reference_price=100.0, actual_price=55.0
    )

    # 3. Field observations
    field_obs = FieldObservation(weights={
        "visible_deterioration": 0.4,
        "documentation_gaps": 0.3,
        "stakeholder_complaints": 0.3,
    })
    sample_obs = {
        "visible_deterioration": 0.9,
        "documentation_gaps": 0.7,
        "stakeholder_complaints": 0.6,
    }
    output["field_observation"] = field_obs.assess(sample_obs)

    # 4. Redline check
    output["redline_check"] = redline_check(sample_metrics)

    # 5. Batch audit
    entities = {
        "unit_alpha": {
            "cost_deviation": 0.2,
            "error_rate": 0.1,
            "infrastructure_integrity": 0.9,
            "compliance_gap": 0.1,
        },
        "unit_beta": {
            "cost_deviation": 0.8,
            "error_rate": 0.7,
            "infrastructure_integrity": 0.3,
            "compliance_gap": 0.6,
        },
        "unit_gamma": {
            "cost_deviation": 0.5,
            "error_rate": 0.4,
            "infrastructure_integrity": 0.6,
            "compliance_gap": 0.3,
        },
    }
    output["batch_audit"] = audit_batch(entities, profile)

    return output


def print_human(results: Dict[str, Any]) -> None:
    """Pretty-print demo results for human consumption."""
    print("=" * 60)
    print("  Operational Risk Monitor — Demo")
    print("=" * 60)

    rc = results["risk_classification"]
    print(f"\n--- Risk Classification ---")
    print(f"  Score : {rc['score']}")
    print(f"  Level : {rc['level']}")
    print(f"  Metrics:")
    for k, v in rc["metrics"].items():
        print(f"    {k}: {v}")

    pd = results["price_divergence"]
    print(f"\n--- Price Divergence ---")
    print(f"  Reference : {pd['reference_price']}")
    print(f"  Actual    : {pd['actual_price']}")
    print(f"  Divergence: {pd['divergence']}")
    print(f"  Level     : {pd['level']}")

    fo = results["field_observation"]
    print(f"\n--- Field Observation ---")
    print(f"  Score : {fo['score']}")
    print(f"  Level : {fo['level']}")
    print(f"  Observations:")
    for k, v in fo["observations"].items():
        print(f"    {k}: {v}")

    rl = results["redline_check"]
    print(f"\n--- Redline Check ---")
    print(f"  Overall : {rl['overall']}")
    if rl["triggered"]:
        print(f"  Triggered rules:")
        for t in rl["triggered"]:
            print(f"    [{t['level']}] {t['rule']}")
    else:
        print(f"  No rules triggered.")

    ba = results["batch_audit"]
    print(f"\n--- Batch Audit (sorted by score desc) ---")
    for entry in ba:
        print(f"  {entry['entity']}: score={entry['score']}  level={entry['level']}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Operational Risk Monitor — weighted risk scoring, price "
            "divergence detection, field observation analysis, redline "
            "threshold checking, and batch auditing."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a demonstration with sample data.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON instead of human-readable text.",
    )
    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        sys.exit(0)

    results = run_demo()

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print_human(results)


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Dependency Audit
# Source: scripts/dependency_audit.py
# ===========================================================================
"""
Dependency Audit Framework
==========================

Maps structural vulnerabilities, hidden subsidies, and systemic risks
within dependency networks.  Models each dependency as an auditable entry
with current cost, hidden subsidy, true cost, degradation rate, and
substitution feasibility.  Produces a structured report with vulnerability
index, sovereignty score, and actionable recommendations.

Metrics
-------
- **Externalization ratio** -- hidden subsidy / true cost across all
  dependencies.  Indicates what fraction of real cost is invisible to
  the operating entity.
- **Vulnerability index** (0-1) -- weighted sum of risk levels scaled
  by substitution difficulty (1 - feasibility).  Higher values indicate
  greater systemic fragility.
- **Sovereignty score** (0-1) -- weighted by dependency source type
  (commons > social capital > natural capital > public infra > private
  monopoly) and degradation rate.  Higher values indicate more
  autonomous control over critical inputs.

References
----------
- Meadows, D. (2008). *Thinking in Systems*.
- Ostrom, E. (1990). *Governing the Commons*.
- Raworth, K. (2017). *Doughnut Economics* -- hidden subsidies and
  externalized costs.
- Shannon, C. E. (1948). A Mathematical Theory of Communication --
  entropy as uncertainty measure applied to risk weighting.

Usage
-----
    python3 scripts/dependency_audit.py --demo
    python3 scripts/dependency_audit.py --demo --json
    python3 scripts/dependency_audit.py --demo --compare
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import argparse
import json
import math


# ------------------
# Audit Core Structures
# ------------------

class DependencyRisk(Enum):
    """Risk levels for dependencies."""
    CRITICAL = "critical"       # < 10 years remaining
    HIGH = "high"               # 10-20 years remaining
    MODERATE = "moderate"       # 20-50 years remaining
    LOW = "low"                 # > 50 years remaining
    IMPROVING = "improving"     # Negative degradation (building)


class DependencySource(Enum):
    """Where the dependency comes from."""
    PUBLIC_INFRASTRUCTURE = "public_infrastructure"
    PRIVATE_MONOPOLY = "private_monopoly"
    COMMONS = "commons"
    NATURAL_CAPITAL = "natural_capital"
    SOCIAL_CAPITAL = "social_capital"


@dataclass
class DependencyAuditEntry:
    """Complete audit record for a single dependency."""
    name: str
    source: DependencySource
    current_cost: float
    hidden_subsidy: float
    true_cost: float
    degradation_rate: float
    years_remaining: float
    risk_level: DependencyRisk
    alternative_available: bool
    alternative_cost: float
    substitution_feasibility: float   # 0-1
    measurement_method: str
    data_quality: float               # 0-1
    last_measured: datetime
    trend_history: List[float] = field(default_factory=list)

    def update_risk_level(self):
        """Update risk level based on years remaining."""
        if self.degradation_rate <= 0:
            self.risk_level = DependencyRisk.IMPROVING
        elif self.years_remaining < 10:
            self.risk_level = DependencyRisk.CRITICAL
        elif self.years_remaining < 20:
            self.risk_level = DependencyRisk.HIGH
        elif self.years_remaining < 50:
            self.risk_level = DependencyRisk.MODERATE
        else:
            self.risk_level = DependencyRisk.LOW


@dataclass
class SystemDependencyAudit:
    """Complete audit of all system dependencies."""
    system_name: str
    audit_date: datetime
    dependencies: Dict[str, DependencyAuditEntry]

    def total_hidden_subsidy(self) -> float:
        return sum(d.hidden_subsidy for d in self.dependencies.values())

    def total_true_cost(self) -> float:
        return sum(d.true_cost for d in self.dependencies.values())

    def externalization_ratio(self) -> float:
        total = self.total_true_cost()
        return self.total_hidden_subsidy() / total if total > 0 else 0

    def critical_dependencies(self) -> List[DependencyAuditEntry]:
        return [d for d in self.dependencies.values()
                if d.risk_level == DependencyRisk.CRITICAL]

    def vulnerability_index(self) -> float:
        """
        System vulnerability (0-1).
        Weighted by risk level and substitution difficulty.
        """
        weights = {
            DependencyRisk.CRITICAL: 1.0,
            DependencyRisk.HIGH: 0.7,
            DependencyRisk.MODERATE: 0.4,
            DependencyRisk.LOW: 0.1,
            DependencyRisk.IMPROVING: 0.0
        }
        total_risk = sum(
            weights[d.risk_level] * (1 - d.substitution_feasibility)
            for d in self.dependencies.values()
        )
        max_risk = len(self.dependencies) * 1.0
        return min(1.0, total_risk / max_risk) if max_risk > 0 else 0

    def sovereignty_score(self) -> float:
        """
        System sovereignty (0-1).
        Higher = more control over own dependencies.
        """
        source_weights = {
            DependencySource.COMMONS: 1.0,
            DependencySource.SOCIAL_CAPITAL: 0.9,
            DependencySource.NATURAL_CAPITAL: 0.7,
            DependencySource.PUBLIC_INFRASTRUCTURE: 0.4,
            DependencySource.PRIVATE_MONOPOLY: 0.1
        }
        total_score = sum(
            source_weights[d.source] * (1 - d.degradation_rate if d.degradation_rate > 0 else 1)
            for d in self.dependencies.values()
        )
        max_score = len(self.dependencies) * 1.0
        return total_score / max_score if max_score > 0 else 0

    def generate_report(self) -> Dict[str, Any]:
        """Generate structured audit report."""
        return {
            "system_name": self.system_name,
            "audit_date": self.audit_date.isoformat(),
            "summary": {
                "total_dependencies": len(self.dependencies),
                "total_hidden_subsidy": self.total_hidden_subsidy(),
                "total_true_cost": self.total_true_cost(),
                "externalization_ratio": self.externalization_ratio(),
                "critical_dependencies": len(self.critical_dependencies()),
                "vulnerability_index": self.vulnerability_index(),
                "sovereignty_score": self.sovereignty_score()
            },
            "dependencies": {
                name: {
                    "source": d.source.value,
                    "current_cost": d.current_cost,
                    "hidden_subsidy": d.hidden_subsidy,
                    "true_cost": d.true_cost,
                    "degradation_rate": d.degradation_rate,
                    "years_remaining": d.years_remaining,
                    "risk_level": d.risk_level.value,
                    "alternative_available": d.alternative_available,
                    "substitution_feasibility": d.substitution_feasibility,
                    "data_quality": d.data_quality
                }
                for name, d in self.dependencies.items()
            },
            "vulnerabilities": [
                {
                    "dependency": name,
                    "risk": d.risk_level.value,
                    "years": d.years_remaining,
                    "substitution": d.substitution_feasibility
                }
                for name, d in self.dependencies.items()
                if d.risk_level in [DependencyRisk.CRITICAL, DependencyRisk.HIGH]
            ],
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate audit recommendations from data."""
        recommendations = []

        for dep in self.critical_dependencies():
            recommendations.append(
                f"CRITICAL: {dep.name} -- {dep.years_remaining:.0f} years remaining. "
                f"Alternative at {dep.alternative_cost:.0f} available."
            )

        if self.externalization_ratio() > 0.5:
            recommendations.append(
                f"Externalization ratio at {self.externalization_ratio():.0%}. "
                f"Internalization required for true cost visibility."
            )

        if self.sovereignty_score() < 0.3:
            recommendations.append(
                "Low sovereignty score -- high private monopoly control. "
                "Transition to commons-based alternatives recommended."
            )

        for name, dep in self.dependencies.items():
            if dep.data_quality < 0.5:
                recommendations.append(
                    f"Low data quality for {name} ({dep.data_quality:.0%}). "
                    f"Measurement improvement needed."
                )

        return recommendations


# ------------------
# Audit Factory
# ------------------

def create_audit(
    system_name: str,
    entries: List[DependencyAuditEntry],
    audit_date: Optional[datetime] = None
) -> SystemDependencyAudit:
    """
    Build an audit from a list of entries.

    Parameters
    ----------
    system_name : str
    entries : list[DependencyAuditEntry]
    audit_date : datetime, optional (defaults to now)

    Returns
    -------
    SystemDependencyAudit
    """
    if audit_date is None:
        audit_date = datetime.now()

    dependencies = {}
    for entry in entries:
        entry.update_risk_level()
        dependencies[entry.name] = entry

    return SystemDependencyAudit(
        system_name=system_name,
        audit_date=audit_date,
        dependencies=dependencies
    )


def compare_audits(
    audits: Dict[str, SystemDependencyAudit]
) -> Dict[str, Dict[str, Any]]:
    """
    Compare N audits side by side.

    Returns
    -------
    dict keyed by audit name -> summary metrics
    """
    results = {}
    for name, audit in audits.items():
        report = audit.generate_report()
        results[name] = report["summary"]
    return results


# ------------------
# Demo Data
# ------------------

def _build_demo_entries() -> List[DependencyAuditEntry]:
    """Return a set of illustrative dependency audit entries."""
    now = datetime.now()
    return [
        DependencyAuditEntry(
            name="Groundwater",
            source=DependencySource.NATURAL_CAPITAL,
            current_cost=50.0,
            hidden_subsidy=200.0,
            true_cost=250.0,
            degradation_rate=0.03,
            years_remaining=15.0,
            risk_level=DependencyRisk.HIGH,
            alternative_available=True,
            alternative_cost=400.0,
            substitution_feasibility=0.4,
            measurement_method="USGS well-level monitoring",
            data_quality=0.8,
            last_measured=now,
        ),
        DependencyAuditEntry(
            name="Grid Electricity",
            source=DependencySource.PRIVATE_MONOPOLY,
            current_cost=120.0,
            hidden_subsidy=80.0,
            true_cost=200.0,
            degradation_rate=0.01,
            years_remaining=40.0,
            risk_level=DependencyRisk.MODERATE,
            alternative_available=True,
            alternative_cost=180.0,
            substitution_feasibility=0.7,
            measurement_method="EIA capacity factor data",
            data_quality=0.9,
            last_measured=now,
        ),
        DependencyAuditEntry(
            name="Topsoil",
            source=DependencySource.NATURAL_CAPITAL,
            current_cost=0.0,
            hidden_subsidy=500.0,
            true_cost=500.0,
            degradation_rate=0.05,
            years_remaining=8.0,
            risk_level=DependencyRisk.CRITICAL,
            alternative_available=False,
            alternative_cost=1200.0,
            substitution_feasibility=0.1,
            measurement_method="NRCS soil survey",
            data_quality=0.6,
            last_measured=now,
        ),
        DependencyAuditEntry(
            name="Community Knowledge",
            source=DependencySource.SOCIAL_CAPITAL,
            current_cost=0.0,
            hidden_subsidy=150.0,
            true_cost=150.0,
            degradation_rate=-0.02,
            years_remaining=100.0,
            risk_level=DependencyRisk.IMPROVING,
            alternative_available=False,
            alternative_cost=0.0,
            substitution_feasibility=0.0,
            measurement_method="Participatory assessment",
            data_quality=0.4,
            last_measured=now,
        ),
        DependencyAuditEntry(
            name="Municipal Water Treatment",
            source=DependencySource.PUBLIC_INFRASTRUCTURE,
            current_cost=30.0,
            hidden_subsidy=70.0,
            true_cost=100.0,
            degradation_rate=0.02,
            years_remaining=25.0,
            risk_level=DependencyRisk.MODERATE,
            alternative_available=True,
            alternative_cost=90.0,
            substitution_feasibility=0.5,
            measurement_method="EPA compliance reports",
            data_quality=0.85,
            last_measured=now,
        ),
    ]


def _build_demo_comparison() -> Dict[str, SystemDependencyAudit]:
    """Build three scenario audits for side-by-side comparison."""
    now = datetime.now()
    base_entries = _build_demo_entries()

    baseline = create_audit("Baseline", base_entries, audit_date=now)

    # Degraded scenario: double degradation rates, halve years remaining
    degraded_entries = []
    for e in _build_demo_entries():
        e.degradation_rate = abs(e.degradation_rate) * 2
        e.years_remaining = max(1.0, e.years_remaining / 2)
        degraded_entries.append(e)
    degraded = create_audit("Degraded", degraded_entries, audit_date=now)

    # Resilient scenario: negative or zero degradation, high substitution
    resilient_entries = []
    for e in _build_demo_entries():
        e.degradation_rate = min(0, e.degradation_rate)
        e.substitution_feasibility = min(1.0, e.substitution_feasibility + 0.3)
        e.years_remaining = e.years_remaining * 2
        resilient_entries.append(e)
    resilient = create_audit("Resilient", resilient_entries, audit_date=now)

    return {"Baseline": baseline, "Degraded": degraded, "Resilient": resilient}


# ------------------
# CLI Presentation
# ------------------

def _print_report(report: Dict[str, Any]) -> None:
    """Pretty-print a single audit report to stdout."""
    s = report["summary"]
    print(f"=== Dependency Audit: {report['system_name']} ===")
    print(f"Date: {report['audit_date']}")
    print()
    print("Summary")
    print("-" * 40)
    print(f"  Total dependencies:      {s['total_dependencies']}")
    print(f"  Total hidden subsidy:    {s['total_hidden_subsidy']:.2f}")
    print(f"  Total true cost:         {s['total_true_cost']:.2f}")
    print(f"  Externalization ratio:   {s['externalization_ratio']:.2%}")
    print(f"  Critical dependencies:   {s['critical_dependencies']}")
    print(f"  Vulnerability index:     {s['vulnerability_index']:.4f}")
    print(f"  Sovereignty score:       {s['sovereignty_score']:.4f}")
    print()

    print("Dependencies")
    print("-" * 40)
    for name, d in report["dependencies"].items():
        print(f"  {name}")
        print(f"    Source:          {d['source']}")
        print(f"    Current cost:    {d['current_cost']:.2f}")
        print(f"    Hidden subsidy:  {d['hidden_subsidy']:.2f}")
        print(f"    True cost:       {d['true_cost']:.2f}")
        print(f"    Degradation:     {d['degradation_rate']:.4f}")
        print(f"    Years remaining: {d['years_remaining']:.1f}")
        print(f"    Risk level:      {d['risk_level']}")
        print(f"    Substitution:    {d['substitution_feasibility']:.2f}")
        print(f"    Data quality:    {d['data_quality']:.2f}")
        print()

    if report["vulnerabilities"]:
        print("Vulnerabilities")
        print("-" * 40)
        for v in report["vulnerabilities"]:
            print(f"  {v['dependency']:30s}  risk={v['risk']:10s}  "
                  f"years={v['years']:.0f}  substitution={v['substitution']:.2f}")
        print()

    if report["recommendations"]:
        print("Recommendations")
        print("-" * 40)
        for rec in report["recommendations"]:
            print(f"  - {rec}")
        print()


def _print_comparison(comparison: Dict[str, Dict[str, Any]]) -> None:
    """Pretty-print a side-by-side comparison table."""
    print("=== Audit Comparison ===")
    print()
    headers = list(comparison.keys())
    col_w = max(len(h) for h in headers) + 2
    metric_w = 28

    # Header row
    print(f"{'Metric':<{metric_w}}", end="")
    for h in headers:
        print(f"{h:>{col_w}}", end="")
    print()
    print("-" * (metric_w + col_w * len(headers)))

    # Metric rows
    sample = next(iter(comparison.values()))
    for key in sample:
        print(f"{key:<{metric_w}}", end="")
        for h in headers:
            val = comparison[h][key]
            if isinstance(val, float):
                print(f"{val:>{col_w}.4f}", end="")
            else:
                print(f"{val:>{col_w}}", end="")
        print()
    print()


# ------------------
# Main / CLI
# ------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Dependency Audit Framework -- maps structural vulnerabilities, "
            "hidden subsidies, and systemic risks within dependency networks."
        )
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a demo audit with illustrative dependency data."
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run three scenario comparison (baseline / degraded / resilient)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit output as JSON instead of human-readable text."
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.demo and not args.compare:
        parser.print_help()
        return

    if args.compare:
        audits = _build_demo_comparison()
        if args.json_output:
            comparison = compare_audits(audits)
            print(json.dumps(comparison, indent=2))
        else:
            comparison = compare_audits(audits)
            _print_comparison(comparison)
            # Also print full reports
            for audit in audits.values():
                report = audit.generate_report()
                _print_report(report)
    elif args.demo:
        entries = _build_demo_entries()
        audit = create_audit("Demo System", entries)
        report = audit.generate_report()
        if args.json_output:
            print(json.dumps(report, indent=2))
        else:
            _print_report(report)


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Validation Framework
# Source: scripts/validation_framework.py
# ===========================================================================
"""
Multi-Epistemological Validation Framework -- Quantitative Edition

Validates claims using information-theoretic and structural metrics
rather than keyword matching:

  1. Information Entropy     -- character & word-level Shannon entropy, compressibility
  2. Falsifiability Score    -- quantifier specificity, temporal grounding, measurability
  3. Internal Consistency    -- relation extraction and sign-consistency checking
  4. Citation Analysis       -- source concentration, age distribution, authority entropy
  5. Cross-Domain Score      -- probabilistic aggregation across all domains

References:
  - Shannon (1948): information entropy
  - Popper (1959): falsifiability as demarcation criterion
  - Normalized Compression Distance: Cilibrasi & Vitanyi (2005)
  - Kolmogorov complexity approximation via zlib: Li et al. (2004)
"""

from __future__ import annotations

import argparse
import json
import math
import re
import string
import sys
import zlib
from collections import Counter
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Tokenization helpers
# ---------------------------------------------------------------------------

_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def tokenize(text: str) -> list[str]:
    return [w for w in text.lower().translate(_PUNCT_TABLE).split() if w]


def sentencize(text: str) -> list[str]:
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in parts if s.strip()]


# ---------------------------------------------------------------------------
# Metric 1: Information Entropy & Compressibility
# ---------------------------------------------------------------------------

def char_entropy(text: str) -> float:
    """Shannon entropy over character distribution (bits)."""
    if not text:
        return 0.0
    counts = Counter(text.lower())
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def word_entropy(tokens: list[str]) -> float:
    """Shannon entropy over word distribution (bits)."""
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    total = len(tokens)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def compressibility(text: str) -> float:
    """
    Compression ratio as a proxy for Kolmogorov complexity.
    Uses zlib (stdlib). Higher = more compressible = more redundant.

    Based on Normalized Compression Distance literature
    (Cilibrasi & Vitanyi 2005).
    """
    if not text:
        return 0.0
    original = text.encode("utf-8")
    compressed = zlib.compress(original, 9)
    return 1.0 - len(compressed) / len(original)


@dataclass
class EntropyResult:
    char_entropy_bits: float       # typical English: 4.0-4.5
    word_entropy_bits: float
    compressibility_ratio: float   # 0 = incompressible, 1 = fully redundant
    interpretation: str


def analyze_entropy(text: str, tokens: list[str]) -> EntropyResult:
    h_char = char_entropy(text)
    h_word = word_entropy(tokens)
    comp = compressibility(text)

    issues = []
    if h_char < 3.0:
        issues.append("very low character entropy (highly repetitive)")
    if h_char > 4.8:
        issues.append("unusually high character entropy (possibly random/encoded)")
    if comp > 0.7:
        issues.append(f"high compressibility ({comp:.0%}) -- low information density")

    return EntropyResult(
        char_entropy_bits=round(h_char, 4),
        word_entropy_bits=round(h_word, 4),
        compressibility_ratio=round(comp, 4),
        interpretation="; ".join(issues) if issues else "entropy within normal range",
    )


# ---------------------------------------------------------------------------
# Metric 2: Falsifiability Score
# ---------------------------------------------------------------------------

SPECIFIC_QUANTIFIERS = re.compile(
    r"\b\d+\.?\d*\s*%|\b\d+\.?\d*\b(?:\s*(?:times|fold|percent|kg|km|m|cm|mm|"
    r"hours?|days?|years?|months?|seconds?|million|billion|thousand))\b|"
    r"\bbetween\s+\d+\s+and\s+\d+\b|\bby\s+\d{4}\b|\bin\s+\d{4}\b",
    re.IGNORECASE,
)

VAGUE_QUANTIFIERS = re.compile(
    r"\b(many|most|some|various|significant|numerous|several|"
    r"few|substantial|considerable|a lot|a number of)\b",
    re.IGNORECASE,
)

TEMPORAL_SPECIFIC = re.compile(
    r"\b(in\s+\d{4}|by\s+\d{4}|within\s+\d+\s+\w+|"
    r"\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}|"
    r"between\s+\d{4}\s+and\s+\d{4}|from\s+\d{4}\s+to\s+\d{4}|"
    r"since\s+\d{4}|after\s+\d{4}|before\s+\d{4}|"
    r"next\s+\d+\s+\w+|over\s+\d+\s+\w+)\b",
    re.IGNORECASE,
)

TEMPORAL_VAGUE = re.compile(
    r"\b(always|never|inherently|by nature|eternally|"
    r"fundamentally|inevitably|permanently)\b",
    re.IGNORECASE,
)

MEASURABILITY_WORDS = re.compile(
    r"\b(measured|observed|counted|rate of|percentage|"
    r"correlation|statistically|empirically|quantified|"
    r"data shows|experiment|sample size|p-value|confidence interval)\b",
    re.IGNORECASE,
)

UNFALSIFIABLE_FRAMING = re.compile(
    r"\b(essentially|in principle|fundamentally|by definition|"
    r"it is known that|self-evidently|axiomatically|"
    r"it goes without saying|needless to say)\b",
    re.IGNORECASE,
)


@dataclass
class FalsifiabilityResult:
    score: float                  # [0, 1], higher = more falsifiable
    quantifier_specificity: float
    temporal_specificity: float
    measurability: float
    interpretation: str
    details: dict = field(default_factory=dict)


def analyze_falsifiability(text: str) -> FalsifiabilityResult:
    """
    Score how falsifiable a claim is based on structural properties.

    Based on Popper's demarcation criterion: a claim is scientific
    if it makes specific, testable, potentially refutable predictions.
    """
    n_specific_q = len(SPECIFIC_QUANTIFIERS.findall(text))
    n_vague_q = len(VAGUE_QUANTIFIERS.findall(text))
    quantifier_spec = n_specific_q / (n_specific_q + n_vague_q + 1)

    n_temporal_spec = len(TEMPORAL_SPECIFIC.findall(text))
    n_temporal_vague = len(TEMPORAL_VAGUE.findall(text))
    temporal_spec = n_temporal_spec / (n_temporal_spec + n_temporal_vague + 1)

    n_measurable = len(MEASURABILITY_WORDS.findall(text))
    n_unfalsifiable = len(UNFALSIFIABLE_FRAMING.findall(text))
    measurability = n_measurable / (n_measurable + n_unfalsifiable + 1)

    score = (
        0.40 * quantifier_spec
        + 0.30 * measurability
        + 0.30 * temporal_spec
    )

    if score >= 0.40:
        interp = "FALSIFIABLE -- contains specific, testable elements"
    elif score >= 0.20:
        interp = "PARTIALLY FALSIFIABLE -- some specificity, could be more testable"
    else:
        interp = "LOW FALSIFIABILITY -- vague, hard to test or refute"

    return FalsifiabilityResult(
        score=round(score, 4),
        quantifier_specificity=round(quantifier_spec, 4),
        temporal_specificity=round(temporal_spec, 4),
        measurability=round(measurability, 4),
        interpretation=interp,
        details={
            "specific_quantifiers": n_specific_q,
            "vague_quantifiers": n_vague_q,
            "temporal_specific": n_temporal_spec,
            "temporal_vague": n_temporal_vague,
            "measurability_markers": n_measurable,
            "unfalsifiable_markers": n_unfalsifiable,
        },
    )


# ---------------------------------------------------------------------------
# Metric 3: Internal Consistency
# ---------------------------------------------------------------------------

POSITIVE_PREDICATES = re.compile(
    r"\b(increases?|causes?|leads?\s+to|improves?|promotes?|"
    r"enables?|produces?|creates?|enhances?|strengthens?)\b",
    re.IGNORECASE,
)

NEGATIVE_PREDICATES = re.compile(
    r"\b(decreases?|reduces?|prevents?|harms?|inhibits?|"
    r"destroys?|weakens?|eliminates?|undermines?|blocks?)\b",
    re.IGNORECASE,
)


@dataclass
class Relation:
    subject: str
    direction: int  # +1 or -1
    obj: str
    sentence_idx: int


@dataclass
class ConsistencyResult:
    score: float              # [0, 1], higher = more consistent
    relations_found: int
    contradictions: list[tuple[str, str]]  # pairs of contradictory sentences
    interpretation: str


def extract_relations(sentences: list[str]) -> list[Relation]:
    """
    Extract subject-predicate-object relations from simple sentence structures.
    Looks for patterns like "X increases Y" or "X leads to Y".
    """
    relations: list[Relation] = []
    for idx, sent in enumerate(sentences):
        # Try positive predicates
        for m in POSITIVE_PREDICATES.finditer(sent):
            before = sent[:m.start()].strip().split()[-3:]  # last 3 words as subject
            after = sent[m.end():].strip().split()[:3]       # first 3 words as object
            if before and after:
                relations.append(Relation(
                    subject=" ".join(before).lower().strip(string.punctuation),
                    direction=1,
                    obj=" ".join(after).lower().strip(string.punctuation),
                    sentence_idx=idx,
                ))
        # Try negative predicates
        for m in NEGATIVE_PREDICATES.finditer(sent):
            before = sent[:m.start()].strip().split()[-3:]
            after = sent[m.end():].strip().split()[:3]
            if before and after:
                relations.append(Relation(
                    subject=" ".join(before).lower().strip(string.punctuation),
                    direction=-1,
                    obj=" ".join(after).lower().strip(string.punctuation),
                    sentence_idx=idx,
                ))
    return relations


def check_consistency(sentences: list[str]) -> ConsistencyResult:
    """
    Check for direct contradictions: same subject-object pair with
    opposite direction predicates.
    """
    relations = extract_relations(sentences)
    if not relations:
        return ConsistencyResult(
            score=1.0, relations_found=0, contradictions=[],
            interpretation="No extractable relations -- cannot assess consistency",
        )

    # Group by (subject, object) pair
    pairs: dict[tuple[str, str], list[Relation]] = {}
    for r in relations:
        key = (r.subject, r.obj)
        pairs.setdefault(key, []).append(r)

    contradictions: list[tuple[str, str]] = []
    for (subj, obj), rels in pairs.items():
        directions = {r.direction for r in rels}
        if len(directions) > 1:  # both +1 and -1
            s1 = sentences[rels[0].sentence_idx][:80]
            s2 = next(sentences[r.sentence_idx][:80] for r in rels if r.direction != rels[0].direction)
            contradictions.append((s1, s2))

    n_pairs = len(pairs)
    n_contradictions = len(contradictions)
    score = 1.0 - (n_contradictions / max(n_pairs, 1))

    if n_contradictions == 0:
        interp = "CONSISTENT -- no direct contradictions detected"
    elif n_contradictions <= 2:
        interp = f"MINOR INCONSISTENCY -- {n_contradictions} contradiction(s)"
    else:
        interp = f"INCONSISTENT -- {n_contradictions} contradictions in {n_pairs} relation pairs"

    return ConsistencyResult(
        score=round(max(0.0, score), 4),
        relations_found=len(relations),
        contradictions=contradictions,
        interpretation=interp,
    )


# ---------------------------------------------------------------------------
# Metric 4: Citation Analysis
# ---------------------------------------------------------------------------

CITATION_AUTHOR = re.compile(r"\(([A-Z][a-z]+(?:\s+(?:et\s+al|&\s+[A-Z][a-z]+))?)[.,]?\s*(\d{4})\)")
CITATION_YEAR = re.compile(r"\b((?:19|20)\d{2})\b")


@dataclass
class CitationResult:
    citation_count: int
    unique_authors: int
    author_entropy: float          # Shannon entropy over cited authors (bits)
    mean_citation_age: float       # years from current year
    citation_to_sentence_ratio: float
    interpretation: str


def analyze_citations(text: str, sentences: list[str], current_year: int = 2026) -> CitationResult:
    """Analyze citation patterns for authority concentration and currency."""
    author_matches = CITATION_AUTHOR.findall(text)
    authors = [a[0].lower() for a in author_matches]
    years = [int(a[1]) for a in author_matches]

    # Also count bare [N] style citations
    bracket_cites = re.findall(r"\[\d+\]", text)

    total_cites = len(authors) + len(bracket_cites)
    unique_auth = len(set(authors))

    # Author entropy
    if authors:
        counts = Counter(authors)
        total_a = len(authors)
        author_entropy = -sum((c / total_a) * math.log2(c / total_a) for c in counts.values())
    else:
        author_entropy = 0.0

    # Mean citation age
    if years:
        mean_age = sum(current_year - y for y in years) / len(years)
    else:
        mean_age = 0.0

    ratio = total_cites / max(len(sentences), 1)

    issues = []
    if total_cites == 0:
        issues.append("no citations found")
    elif unique_auth > 0 and author_entropy < 1.0:
        issues.append("low author diversity -- possible authority concentration")
    if mean_age > 20:
        issues.append(f"mean citation age is {mean_age:.0f} years -- evidence may be outdated")
    if ratio < 0.05 and len(sentences) > 5:
        issues.append("very low citation-to-sentence ratio for empirical claims")

    return CitationResult(
        citation_count=total_cites,
        unique_authors=unique_auth,
        author_entropy=round(author_entropy, 4),
        mean_citation_age=round(mean_age, 1),
        citation_to_sentence_ratio=round(ratio, 4),
        interpretation="; ".join(issues) if issues else "citation profile within normal range",
    )


# ---------------------------------------------------------------------------
# Cross-Domain Aggregation
# ---------------------------------------------------------------------------

@dataclass
class DomainScore:
    name: str
    score: float          # [0, 1], higher = more concern
    interpretation: str


@dataclass
class ValidationReport:
    claim: str
    entropy: EntropyResult
    falsifiability: FalsifiabilityResult
    consistency: ConsistencyResult
    citations: CitationResult
    domain_scores: list[DomainScore]
    overall_concern: float    # [0, 1]
    interpretation: str


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def validate_claim(text: str, sensor_import: object = None) -> ValidationReport:
    """Run all analyses and produce a cross-domain validation report.

    If sensor_import (from fieldlink.parse_sensor_import) is provided,
    a fifth domain -- Somatic Alignment -- is added to the cross-domain
    scoring, measuring consistency with the body's evolved sensing
    apparatus as mapped by the Emotions-as-Sensors sensor atlas.
    """
    tokens = tokenize(text)
    sentences = sentencize(text)

    entropy = analyze_entropy(text, tokens)
    falsifiability = analyze_falsifiability(text)
    consistency = check_consistency(sentences)
    citations = analyze_citations(text, sentences)

    # Map metrics to domain concern scores [0, 1]
    domains = []

    # Physics/Thermodynamics: concerned about unfalsifiable claims with high compressibility
    phys_concern = (
        0.5 * (1.0 - clamp(falsifiability.score / 0.4))
        + 0.5 * clamp(entropy.compressibility_ratio / 0.6)
    )
    domains.append(DomainScore(
        "Physics / Thermodynamics", round(phys_concern, 4),
        "Assesses whether claims are thermodynamically plausible and testable",
    ))

    # Biology/Evolution: concerned about low falsifiability + no temporal grounding
    bio_concern = (
        0.6 * (1.0 - clamp(falsifiability.score / 0.4))
        + 0.4 * (1.0 - clamp(falsifiability.temporal_specificity / 0.3))
    )
    domains.append(DomainScore(
        "Biology / Evolution", round(bio_concern, 4),
        "Assesses whether claims about living systems are grounded and testable",
    ))

    # Systems Dynamics: concerned about inconsistency + low information content
    sys_concern = (
        0.5 * (1.0 - clamp(consistency.score))
        + 0.5 * clamp(entropy.compressibility_ratio / 0.5)
    )
    domains.append(DomainScore(
        "Systems Dynamics", round(sys_concern, 4),
        "Assesses internal consistency and information density of systems claims",
    ))

    # Empirical Observation: concerned about citation gaps + unfalsifiability
    emp_concern = (
        0.4 * (1.0 - clamp(citations.citation_to_sentence_ratio / 0.1))
        + 0.3 * (1.0 - clamp(falsifiability.measurability / 0.3))
        + 0.3 * (1.0 - clamp(citations.author_entropy / 2.0))
    )
    domains.append(DomainScore(
        "Empirical Observation", round(emp_concern, 4),
        "Assesses evidence base, citation quality, and measurability",
    ))

    # 5. Somatic Alignment (optional -- requires fieldlink sensor import)
    if sensor_import is not None:
        try:
            from scripts.fieldlink import compute_somatic_alignment
            somatic = compute_somatic_alignment(text, sensor_import)
            domains.append(DomainScore(
                "Somatic Alignment", round(somatic["concern"], 4),
                somatic["interpretation"],
            ))
        except ImportError:
            pass  # fieldlink not available, skip gracefully

    # Aggregate: weighted mean of domain scores, with a boost if multiple domains flag
    mean_score = sum(d.score for d in domains) / len(domains)
    n_flagged = sum(1 for d in domains if d.score > 0.5)
    # Multi-domain boost: if 3+ domains flag, escalate
    multi_boost = 0.1 * max(0, n_flagged - 2)
    overall = round(clamp(mean_score + multi_boost), 4)

    if overall < 0.25:
        interp = "LOW CONCERN -- claim structure appears epistemically sound"
    elif overall < 0.50:
        interp = "MODERATE CONCERN -- some structural weaknesses in claim"
    elif overall < 0.70:
        interp = "HIGH CONCERN -- multiple epistemic red flags"
    else:
        interp = "VERY HIGH CONCERN -- claim fails multiple validation dimensions"

    return ValidationReport(
        claim=text,
        entropy=entropy,
        falsifiability=falsifiability,
        consistency=consistency,
        citations=citations,
        domain_scores=domains,
        overall_concern=overall,
        interpretation=interp,
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(report: ValidationReport) -> None:
    print("=" * 80)
    print("  MULTI-EPISTEMOLOGICAL VALIDATION REPORT")
    print("=" * 80)

    claim_display = report.claim[:200] + "..." if len(report.claim) > 200 else report.claim
    print(f"\n  Claim: \"{claim_display}\"\n")

    # Entropy
    e = report.entropy
    print(f"  [1] Information Entropy")
    print(f"      Character entropy:  {e.char_entropy_bits:.4f} bits  (English typical: 4.0-4.5)")
    print(f"      Word entropy:       {e.word_entropy_bits:.4f} bits")
    print(f"      Compressibility:    {e.compressibility_ratio:.4f}  (zlib proxy for Kolmogorov complexity)")
    print(f"      {e.interpretation}")

    # Falsifiability
    f = report.falsifiability
    print(f"\n  [2] Falsifiability (Popper 1959)")
    print(f"      Overall score:      {f.score:.4f}  [0=unfalsifiable, 1=highly testable]")
    print(f"      Quantifier spec:    {f.quantifier_specificity:.4f}  ({f.details['specific_quantifiers']} specific / {f.details['vague_quantifiers']} vague)")
    print(f"      Temporal grounding: {f.temporal_specificity:.4f}  ({f.details['temporal_specific']} specific / {f.details['temporal_vague']} vague)")
    print(f"      Measurability:      {f.measurability:.4f}  ({f.details['measurability_markers']} markers / {f.details['unfalsifiable_markers']} unfalsifiable)")
    print(f"      {f.interpretation}")

    # Consistency
    c = report.consistency
    print(f"\n  [3] Internal Consistency")
    print(f"      Score:              {c.score:.4f}  [0=contradictory, 1=consistent]")
    print(f"      Relations extracted: {c.relations_found}")
    if c.contradictions:
        print(f"      Contradictions ({len(c.contradictions)}):")
        for s1, s2 in c.contradictions[:3]:
            print(f"        \"{s1}...\"")
            print(f"        vs \"{s2}...\"")
    print(f"      {c.interpretation}")

    # Citations
    ci = report.citations
    print(f"\n  [4] Citation Analysis")
    print(f"      Total citations:    {ci.citation_count}")
    print(f"      Unique authors:     {ci.unique_authors}")
    print(f"      Author entropy:     {ci.author_entropy:.4f} bits  (higher = more diverse)")
    print(f"      Mean citation age:  {ci.mean_citation_age:.1f} years")
    print(f"      Cite/sentence ratio: {ci.citation_to_sentence_ratio:.4f}")
    print(f"      {ci.interpretation}")

    # Domain scores
    print(f"\n  [5] Cross-Domain Concern Scores")
    for d in report.domain_scores:
        bar = "#" * int(d.score * 20) + "." * (20 - int(d.score * 20))
        print(f"      [{bar}] {d.score:.4f}  {d.name}")

    print(f"\n{'=' * 80}")
    print(f"  OVERALL: {report.overall_concern:.4f}  --  {report.interpretation}")
    print(f"  Aggregation: mean(domain_scores) + multi-domain boost")
    print(f"{'=' * 80}\n")


def print_json_report(report: ValidationReport) -> None:
    data = {
        "claim": report.claim[:500],
        "overall_concern": report.overall_concern,
        "interpretation": report.interpretation,
        "entropy": {
            "char_bits": report.entropy.char_entropy_bits,
            "word_bits": report.entropy.word_entropy_bits,
            "compressibility": report.entropy.compressibility_ratio,
        },
        "falsifiability": {
            "score": report.falsifiability.score,
            "quantifier_specificity": report.falsifiability.quantifier_specificity,
            "temporal_specificity": report.falsifiability.temporal_specificity,
            "measurability": report.falsifiability.measurability,
            **report.falsifiability.details,
        },
        "consistency": {
            "score": report.consistency.score,
            "relations_found": report.consistency.relations_found,
            "contradictions": len(report.consistency.contradictions),
        },
        "citations": {
            "count": report.citations.citation_count,
            "unique_authors": report.citations.unique_authors,
            "author_entropy": report.citations.author_entropy,
            "mean_age": report.citations.mean_citation_age,
            "cite_sentence_ratio": report.citations.citation_to_sentence_ratio,
        },
        "domain_scores": {d.name: d.score for d in report.domain_scores},
    }
    print(json.dumps(data, indent=2))


def interactive_mode() -> None:
    print("=" * 80)
    print("  MULTI-EPISTEMOLOGICAL VALIDATION FRAMEWORK (Quantitative)")
    print("  Enter claims to validate (Ctrl+D or 'quit' to exit)")
    print("=" * 80)

    while True:
        try:
            claim = input("\n  Enter claim: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not claim or claim.lower() in ("quit", "exit", "q"):
            break
        report = validate_claim(claim)
        print()
        print_report(report)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quantitative multi-epistemological claim validation"
    )
    parser.add_argument("--claim", "-c", help="Single claim to validate")
    parser.add_argument("--file", "-f", help="File to validate (full text)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--sensors", metavar="PATH",
        help="Path to Emotions-as-Sensors JSON export for somatic alignment scoring",
    )
    args = parser.parse_args()

    # Load sensor import if provided
    sensor_import = None
    if args.sensors:
        try:
            from scripts.fieldlink import parse_sensor_import
            with open(args.sensors) as sf:
                sensor_import = parse_sensor_import(json.load(sf))
        except (ImportError, FileNotFoundError) as e:
            print(f"Warning: Could not load sensor data: {e}", file=sys.stderr)

    if args.claim:
        report = validate_claim(args.claim, sensor_import=sensor_import)
        (print_json_report if args.json else print_report)(report)
    elif args.file:
        with open(args.file) as f:
            text = f.read()
        report = validate_claim(text, sensor_import=sensor_import)
        (print_json_report if args.json else print_report)(report)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Zero Infrastructure Alerts
# Source: scripts/zero_infrastructure_alerts.py
# ===========================================================================
"""
Zero-Infrastructure Alert Systems
==================================

Build alert networks from environmental signals that require no
infrastructure (electricity, internet, supply chains). Registers
detectable signals, assembles them into alert systems, and weaves
systems into a coupled geometric network.

Framework
---------
1. **EnvironmentalSignal** — a single observable (e.g. bird alarm calls,
   wind-carried scent change) with range, reliability, and power requirement.
2. **AlertSystem** — a composite detector assembled from one or more signals,
   with materials list, setup time, and reliability.
3. **AlertCouplingRule** — a synergy rule that fires when two or more alert
   systems are co-present, increasing network integrity.
4. **AlertNetworkWeaver** — selects feasible systems given available materials,
   identifies active couplings, and computes geometric metrics (coupling
   density, average strength, integrity score).

The geometric metrics are inspired by graph-density measures from
algebraic graph theory (Fiedler, 1973) and network resilience analysis
(Albert & Barabasi, 2002).

References
----------
- Fiedler, M. (1973). Algebraic connectivity of graphs.
  *Czechoslovak Mathematical Journal*, 23(2), 298-305.
- Albert, R., & Barabasi, A.-L. (2002). Statistical mechanics of
  complex networks. *Reviews of Modern Physics*, 74(1), 47-97.
- Prigogine, I., & Stengers, I. (1984). *Order Out of Chaos*.

Usage
-----
    python3 scripts/zero_infrastructure_alerts.py --help
    python3 scripts/zero_infrastructure_alerts.py --demo
    python3 scripts/zero_infrastructure_alerts.py --demo --json
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
import argparse
import itertools
import json
import sys

# ------------------------------------------------------------------
# Environmental Signal
# ------------------------------------------------------------------


@dataclass
class EnvironmentalSignal:
    """A signal detectable without infrastructure."""
    name: str
    source: str
    detection_method: str
    what_it_indicates: List[str]
    range_meters: float
    reliability: float           # 0-1
    requires_power: bool
    tags: Dict[str, str] = field(default_factory=dict)


# ------------------------------------------------------------------
# Alert System
# ------------------------------------------------------------------


@dataclass
class AlertSystem:
    """An alert system assembled from environmental signals."""
    name: str
    signals: List[str]           # signal names used
    detection_method: str
    what_it_detects: List[str]
    range_meters: float
    setup_time_minutes: float
    materials_needed: List[str]
    reliability: float


# ------------------------------------------------------------------
# Coupling Rule
# ------------------------------------------------------------------


@dataclass
class AlertCouplingRule:
    """Detects synergy between two alert systems."""
    name: str
    requires: List[str]          # alert system names
    description: str
    strength: float = 0.7


# ------------------------------------------------------------------
# Signal Library
# ------------------------------------------------------------------


class SignalLibrary:
    """Registry of environmental signals. Populate via register()."""

    def __init__(self):
        self.signals: Dict[str, EnvironmentalSignal] = {}

    def register(self, signal: EnvironmentalSignal):
        self.signals[signal.name] = signal

    def passive(self) -> List[EnvironmentalSignal]:
        return [s for s in self.signals.values() if not s.requires_power]

    def by_range(self, minimum: float) -> List[EnvironmentalSignal]:
        return [s for s in self.signals.values() if s.range_meters >= minimum]


# ------------------------------------------------------------------
# Alert System Library
# ------------------------------------------------------------------


class AlertSystemLibrary:
    """Registry of alert systems. Populate via register()."""

    def __init__(self):
        self.systems: Dict[str, AlertSystem] = {}

    def register(self, system: AlertSystem):
        self.systems[system.name] = system

    def by_reliability(self, minimum: float) -> List[AlertSystem]:
        return [s for s in self.systems.values() if s.reliability >= minimum]

    def by_materials(self, available: List[str]) -> List[AlertSystem]:
        """Systems whose materials are all in the available list."""
        result = []
        for sys in self.systems.values():
            if all(
                any(m in available for m in [mat, mat.split()[0]])
                for mat in sys.materials_needed
            ) or not sys.materials_needed:
                result.append(sys)
        return result

    def all(self) -> List[AlertSystem]:
        return list(self.systems.values())


# ------------------------------------------------------------------
# Alert Network Weaver
# ------------------------------------------------------------------


class AlertNetworkWeaver:
    """Weave alert systems into a geometric network."""

    def __init__(
        self,
        alert_library: AlertSystemLibrary,
        coupling_rules: Optional[List[AlertCouplingRule]] = None,
        max_systems: int = 8,
    ):
        self.library = alert_library
        self.coupling_rules = coupling_rules or []
        self.max_systems = max_systems

    def select(
        self,
        available_materials: List[str],
        sort_key: Optional[Callable[[AlertSystem], float]] = None,
    ) -> List[str]:
        """
        Select feasible alert systems ranked by sort_key.
        Default sort: reliability desc, range desc.
        """
        feasible = self.library.by_materials(available_materials)
        if sort_key is None:
            sort_key = lambda s: (-s.reliability, -s.range_meters)
        feasible.sort(key=sort_key)
        return [s.name for s in feasible[: self.max_systems]]

    def identify_couplings(self, selected: List[str]) -> List[Dict[str, Any]]:
        active = []
        for rule in self.coupling_rules:
            if all(r in selected for r in rule.requires):
                active.append({
                    "components": rule.requires,
                    "description": rule.description,
                    "strength": rule.strength,
                })
        return active

    def geometric_metrics(
        self, selected: List[str], couplings: List[Dict]
    ) -> Dict[str, float]:
        n = len(selected)
        nc = len(couplings)
        max_c = n * (n - 1) / 2 if n > 1 else 1
        density = nc / max_c if max_c > 0 else 0
        avg_str = sum(c.get("strength", 0) for c in couplings) / nc if nc else 0
        area = n * density * avg_str
        return {
            "vectors": n,
            "couplings": nc,
            "coupling_density": density,
            "avg_coupling_strength": avg_str,
            "geometric_area": area,
            "integrity": min(1.0, area / 10),
        }

    def create_network(
        self, available_materials: List[str], name: str = "Alert Network"
    ) -> Dict[str, Any]:
        selected = self.select(available_materials)
        couplings = self.identify_couplings(selected)
        metrics = self.geometric_metrics(selected, couplings)

        # Coverage summary
        all_detects: set = set()
        for sn in selected:
            sys = self.library.systems.get(sn)
            if sys:
                all_detects.update(sys.what_it_detects)

        return {
            "name": name,
            "available_materials": available_materials,
            "selected_systems": selected,
            "couplings": couplings,
            "geometric_metrics": metrics,
            "coverage": sorted(all_detects),
        }


# ------------------------------------------------------------------
# Demo data
# ------------------------------------------------------------------


def _build_demo() -> Dict[str, Any]:
    """Build a demo signal library, alert systems, coupling rules,
    and return the resulting network dict."""

    # --- signals ---
    sig_lib = SignalLibrary()
    sig_lib.register(EnvironmentalSignal(
        name="bird_alarm",
        source="songbirds",
        detection_method="listen for alarm calls",
        what_it_indicates=["predator approach", "human movement"],
        range_meters=200,
        reliability=0.75,
        requires_power=False,
    ))
    sig_lib.register(EnvironmentalSignal(
        name="wind_shift",
        source="atmosphere",
        detection_method="feel wind direction change",
        what_it_indicates=["weather change", "fire approach"],
        range_meters=500,
        reliability=0.6,
        requires_power=False,
    ))
    sig_lib.register(EnvironmentalSignal(
        name="ground_vibration",
        source="ground",
        detection_method="feel or listen for vibrations",
        what_it_indicates=["vehicle approach", "large animal movement"],
        range_meters=300,
        reliability=0.65,
        requires_power=False,
    ))
    sig_lib.register(EnvironmentalSignal(
        name="water_clarity",
        source="stream / pond",
        detection_method="observe turbidity change",
        what_it_indicates=["upstream disturbance", "runoff event"],
        range_meters=1000,
        reliability=0.55,
        requires_power=False,
    ))

    # --- alert systems ---
    alert_lib = AlertSystemLibrary()
    alert_lib.register(AlertSystem(
        name="perimeter_bird_watch",
        signals=["bird_alarm"],
        detection_method="station observers at bird-rich edges",
        what_it_detects=["human approach", "predator"],
        range_meters=200,
        setup_time_minutes=5,
        materials_needed=[],
        reliability=0.75,
    ))
    alert_lib.register(AlertSystem(
        name="vibration_line",
        signals=["ground_vibration"],
        detection_method="place containers of water on ground, watch ripples",
        what_it_detects=["vehicle approach", "heavy foot traffic"],
        range_meters=300,
        setup_time_minutes=10,
        materials_needed=["container", "water"],
        reliability=0.65,
    ))
    alert_lib.register(AlertSystem(
        name="wind_scent_net",
        signals=["wind_shift"],
        detection_method="hang light cloth strips to visualise airflow",
        what_it_detects=["fire approach", "chemical release"],
        range_meters=500,
        setup_time_minutes=15,
        materials_needed=["cloth", "string"],
        reliability=0.6,
    ))
    alert_lib.register(AlertSystem(
        name="water_turbidity_watch",
        signals=["water_clarity"],
        detection_method="check upstream water clarity at intervals",
        what_it_detects=["upstream disturbance", "contamination"],
        range_meters=1000,
        setup_time_minutes=5,
        materials_needed=["container", "water"],
        reliability=0.55,
    ))

    # --- coupling rules ---
    rules = [
        AlertCouplingRule(
            name="bird+vibration",
            requires=["perimeter_bird_watch", "vibration_line"],
            description="birds confirm vibration source is animate",
            strength=0.8,
        ),
        AlertCouplingRule(
            name="wind+water",
            requires=["wind_scent_net", "water_turbidity_watch"],
            description="wind direction + water change triangulates source",
            strength=0.7,
        ),
    ]

    # --- weave ---
    weaver = AlertNetworkWeaver(alert_lib, coupling_rules=rules)
    materials = ["container", "water", "cloth", "string"]
    network = weaver.create_network(materials, name="Demo Alert Network")
    return network


# ------------------------------------------------------------------
# Human-readable output
# ------------------------------------------------------------------


def _print_network(network: Dict[str, Any]) -> None:
    """Pretty-print a network dictionary."""
    print(f"=== {network['name']} ===\n")

    print("Available materials:", ", ".join(network["available_materials"]))
    print()

    print("Selected systems:")
    for s in network["selected_systems"]:
        print(f"  - {s}")
    print()

    print("Couplings:")
    if network["couplings"]:
        for c in network["couplings"]:
            comps = " + ".join(c["components"])
            print(f"  - {comps}  (strength {c['strength']:.2f})")
            print(f"    {c['description']}")
    else:
        print("  (none)")
    print()

    gm = network["geometric_metrics"]
    print("Geometric metrics:")
    print(f"  vectors              : {gm['vectors']}")
    print(f"  couplings            : {gm['couplings']}")
    print(f"  coupling density     : {gm['coupling_density']:.4f}")
    print(f"  avg coupling strength: {gm['avg_coupling_strength']:.4f}")
    print(f"  geometric area       : {gm['geometric_area']:.4f}")
    print(f"  integrity            : {gm['integrity']:.4f}")
    print()

    print("Coverage:")
    for item in network["coverage"]:
        print(f"  - {item}")


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Zero-infrastructure alert systems — build alert networks "
            "from environmental signals that require no electricity, "
            "internet, or supply chains."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a built-in demo with sample signals, systems, and coupling rules.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="use_json",
        help="Output results as JSON instead of human-readable text.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        print("\n(Use --demo to run a sample alert network.)")
        sys.exit(0)

    network = _build_demo()

    if args.use_json:
        print(json.dumps(network, indent=2))
    else:
        _print_network(network)


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Salvage Reclamation
# Source: scripts/salvage_reclamation.py
# ===========================================================================
"""
salvage_reclamation.py -- Material reclamation and salvage potential accounting.

Purpose
-------
Models the failure-to-reinventory loop for system components.  Failed
components are decomposed into a material inventory (recoverable metals,
reusable subassemblies, capturable waste heat) that feeds the next design
iteration.  Integrates with system_weaver.py's SystemComponent model.

Core loop:
    Failed components -> material inventory -> next-iteration inputs

Key metrics:
    - effective_salvage: salvage potential gated by available tooling (0-1)
    - innovation_potential: recoverable value / reprocessing cost ratio
    - sovereignty_score: workshop self-sufficiency (tool coverage, material
      diversity, total mass)

References
----------
- Graedel, T. E. & Allenby, B. R. (2003). Industrial Ecology, 2nd ed.
  Prentice Hall.  (material flow analysis, design-for-recycling)
- Stahel, W. R. (2016). "The Circular Economy." Nature 531, 435-438.
  (closed-loop material reclamation)
- Prigogine, I. & Stengers, I. (1984). Order Out of Chaos. Bantam.
  (entropy production in open systems -- entropy_leak_w metric)

Usage
-----
    python3 scripts/salvage_reclamation.py --demo
    python3 scripts/salvage_reclamation.py --demo --json
    python3 scripts/salvage_reclamation.py --help
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set


# ------------------
# Salvage Profile
# ------------------

@dataclass
class SalvageProfile:
    """
    Salvage characteristics of a system component.
    Attach to any component to track what it yields on failure.
    """
    salvage_potential: float              # 0-1, 1.0 = fully rebuildable from scrap
    recoverable_materials: Dict[str, float]  # material_name -> mass_kg
    reusable_subassemblies: List[str]     # parts usable without reprocessing
    tooling_required: List[str]           # tools needed to reclaim (e.g. "lathe", "smelter")
    entropy_leak_w: float = 0.0          # waste heat (W) that could be captured
    modular_fraction: float = 1.0        # fraction operable if subassembly fails (0-1)

    def effective_salvage(self, available_tools: Set[str]) -> float:
        """
        Salvage potential gated by available tooling.
        Returns 0-1: what fraction of materials can actually be recovered.
        """
        if not self.tooling_required:
            return self.salvage_potential
        tool_coverage = len(available_tools & set(self.tooling_required))
        tool_ratio = tool_coverage / len(self.tooling_required)
        return self.salvage_potential * tool_ratio

    def total_recoverable_mass(self) -> float:
        return sum(self.recoverable_materials.values())


# ------------------
# Reclamation Node
# ------------------

@dataclass
class ReclamationNode:
    """
    A failed component re-indexed as material input.
    Bridges the gap between 'failure' and 'next iteration'.
    """
    component_name: str
    failure_mode: str                     # e.g. "thermal_limit", "wear", "corrosion"
    salvage_profile: SalvageProfile
    retooling_energy_kwh: float           # energy to process salvage
    available_tools: Set[str] = field(default_factory=set)

    def innovation_potential(self) -> float:
        """
        Ratio of recoverable value to reprocessing cost.
        Higher = more worth reclaiming vs discarding.
        """
        effective = self.salvage_profile.effective_salvage(self.available_tools)
        mass = self.salvage_profile.total_recoverable_mass()
        if self.retooling_energy_kwh <= 0:
            return float('inf') if mass > 0 else 0
        return (effective * mass) / self.retooling_energy_kwh

    def harvest(self) -> Dict[str, Any]:
        """
        Execute reclamation: return inventory of recovered materials and parts.
        """
        effective = self.salvage_profile.effective_salvage(self.available_tools)
        return {
            "component": self.component_name,
            "failure_mode": self.failure_mode,
            "raw_materials": {
                mat: mass * effective
                for mat, mass in self.salvage_profile.recoverable_materials.items()
            },
            "reusable_parts": (
                self.salvage_profile.reusable_subassemblies
                if effective > 0.5 else []
            ),
            "capturable_heat_w": self.salvage_profile.entropy_leak_w,
            "effective_salvage": effective,
            "innovation_potential": self.innovation_potential(),
        }


# ------------------
# Workshop Inventory
# ------------------

@dataclass
class WorkshopInventory:
    """
    Tracks available tools, recovered materials, and parts.
    Feeds back into system design: what can be built from what's on hand.
    """
    tools: Set[str] = field(default_factory=set)
    materials: Dict[str, float] = field(default_factory=dict)  # name -> kg
    parts: List[str] = field(default_factory=list)

    def add_tools(self, tools: List[str]):
        self.tools.update(tools)

    def ingest_harvest(self, harvest: Dict[str, Any]):
        """Add reclaimed materials and parts to inventory."""
        for mat, mass in harvest.get("raw_materials", {}).items():
            self.materials[mat] = self.materials.get(mat, 0) + mass
        self.parts.extend(harvest.get("reusable_parts", []))

    def can_build(self, required_materials: Dict[str, float]) -> bool:
        """Check if inventory has enough materials for a build."""
        return all(
            self.materials.get(mat, 0) >= amount
            for mat, amount in required_materials.items()
        )

    def consume(self, required_materials: Dict[str, float]) -> bool:
        """Consume materials for a build. Returns False if insufficient."""
        if not self.can_build(required_materials):
            return False
        for mat, amount in required_materials.items():
            self.materials[mat] -= amount
        return True

    def summary(self) -> Dict[str, Any]:
        return {
            "tools": sorted(self.tools),
            "materials": dict(self.materials),
            "parts": list(self.parts),
            "material_types": len(self.materials),
            "total_mass_kg": sum(self.materials.values()),
        }


# ------------------
# Material Reclamation System
# ------------------

class MaterialReclamationSystem:
    """
    Manages the failure -> harvest -> reinventory loop.
    Components fail; materials are recovered; new builds draw from inventory.
    """

    def __init__(self, inventory: Optional[WorkshopInventory] = None):
        self.inventory = inventory or WorkshopInventory()
        self.reclamation_log: List[Dict[str, Any]] = []

    def register_failure(
        self,
        component_name: str,
        failure_mode: str,
        salvage_profile: SalvageProfile,
        retooling_energy_kwh: float,
    ) -> Dict[str, Any]:
        """
        Process a component failure: harvest and add to inventory.

        Returns harvest report.
        """
        node = ReclamationNode(
            component_name=component_name,
            failure_mode=failure_mode,
            salvage_profile=salvage_profile,
            retooling_energy_kwh=retooling_energy_kwh,
            available_tools=self.inventory.tools,
        )
        harvest = node.harvest()
        self.inventory.ingest_harvest(harvest)
        self.reclamation_log.append(harvest)
        return harvest

    def sovereignty_score(self) -> float:
        """
        How self-sufficient is the workshop?
        Based on tool coverage and material diversity.
        """
        tool_score = min(1.0, len(self.inventory.tools) / 10)
        material_score = min(1.0, len(self.inventory.materials) / 15)
        mass_score = min(1.0, sum(self.inventory.materials.values()) / 500)
        return (tool_score + material_score + mass_score) / 3

    def can_rebuild(
        self, salvage_profile: SalvageProfile
    ) -> Dict[str, Any]:
        """
        Check if a component could be rebuilt from current inventory.
        """
        effective = salvage_profile.effective_salvage(self.inventory.tools)
        buildable = self.inventory.can_build(salvage_profile.recoverable_materials)
        return {
            "effective_salvage": effective,
            "materials_available": buildable,
            "missing_materials": {
                mat: max(0, amount - self.inventory.materials.get(mat, 0))
                for mat, amount in salvage_profile.recoverable_materials.items()
                if self.inventory.materials.get(mat, 0) < amount
            },
            "missing_tools": sorted(
                set(salvage_profile.tooling_required) - self.inventory.tools
            ),
        }

    def summary(self) -> Dict[str, Any]:
        return {
            "reclamations": len(self.reclamation_log),
            "sovereignty_score": self.sovereignty_score(),
            "inventory": self.inventory.summary(),
        }


# ------------------
# Demo / CLI
# ------------------

def run_demo() -> Dict[str, Any]:
    """
    Run a demonstration scenario: a workshop processes two component
    failures and checks whether a third component can be rebuilt.
    """
    # Set up a workshop with basic tools
    workshop = WorkshopInventory()
    workshop.add_tools(["lathe", "smelter", "welder", "drill_press"])

    system = MaterialReclamationSystem(inventory=workshop)

    # First failure: a heat exchanger with corrosion damage
    heat_exchanger_profile = SalvageProfile(
        salvage_potential=0.75,
        recoverable_materials={"copper": 12.5, "steel": 30.0, "aluminum": 5.0},
        reusable_subassemblies=["pressure_gauge", "flow_valve"],
        tooling_required=["smelter", "lathe"],
        entropy_leak_w=450.0,
        modular_fraction=0.6,
    )
    harvest1 = system.register_failure(
        component_name="heat_exchanger_A",
        failure_mode="corrosion",
        salvage_profile=heat_exchanger_profile,
        retooling_energy_kwh=8.0,
    )

    # Second failure: a drive motor with thermal damage
    motor_profile = SalvageProfile(
        salvage_potential=0.55,
        recoverable_materials={"copper": 6.0, "steel": 18.0, "rare_earth": 0.3},
        reusable_subassemblies=["bearing_assembly", "encoder"],
        tooling_required=["lathe", "welder", "magnetizer"],
        entropy_leak_w=200.0,
        modular_fraction=0.4,
    )
    harvest2 = system.register_failure(
        component_name="drive_motor_B",
        failure_mode="thermal_limit",
        salvage_profile=motor_profile,
        retooling_energy_kwh=12.0,
    )

    # Check if we could rebuild the heat exchanger from inventory
    rebuild_check = system.can_rebuild(heat_exchanger_profile)

    return {
        "harvest_1": harvest1,
        "harvest_2": harvest2,
        "rebuild_check_heat_exchanger": rebuild_check,
        "system_summary": system.summary(),
    }


def print_human_readable(results: Dict[str, Any]) -> None:
    """Pretty-print demo results for human consumption."""
    print("=" * 60)
    print("  MATERIAL RECLAMATION SYSTEM -- DEMO")
    print("=" * 60)

    for i, key in enumerate(["harvest_1", "harvest_2"], 1):
        h = results[key]
        print(f"\n--- Harvest {i}: {h['component']} ({h['failure_mode']}) ---")
        print(f"  Effective salvage:      {h['effective_salvage']:.2f}")
        print(f"  Innovation potential:    {h['innovation_potential']:.3f}")
        print(f"  Capturable heat:        {h['capturable_heat_w']:.1f} W")
        print(f"  Recovered materials:")
        for mat, mass in h["raw_materials"].items():
            print(f"    {mat:20s}  {mass:8.2f} kg")
        print(f"  Reusable parts:         {', '.join(h['reusable_parts']) or '(none)'}")

    rc = results["rebuild_check_heat_exchanger"]
    print("\n--- Rebuild Check: heat_exchanger ---")
    print(f"  Materials available:    {rc['materials_available']}")
    print(f"  Effective salvage:      {rc['effective_salvage']:.2f}")
    if rc["missing_materials"]:
        print(f"  Missing materials:")
        for mat, amount in rc["missing_materials"].items():
            print(f"    {mat:20s}  {amount:8.2f} kg needed")
    if rc["missing_tools"]:
        print(f"  Missing tools:          {', '.join(rc['missing_tools'])}")

    s = results["system_summary"]
    print("\n--- System Summary ---")
    print(f"  Total reclamations:     {s['reclamations']}")
    print(f"  Sovereignty score:      {s['sovereignty_score']:.3f}")
    inv = s["inventory"]
    print(f"  Material types:         {inv['material_types']}")
    print(f"  Total mass on hand:     {inv['total_mass_kg']:.2f} kg")
    print(f"  Tools:                  {', '.join(inv['tools'])}")
    print(f"  Parts:                  {', '.join(inv['parts']) or '(none)'}")
    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Material reclamation and salvage potential accounting. "
            "Models the failure-to-reinventory loop: failed components are "
            "decomposed into recoverable materials and reusable subassemblies "
            "that feed the next design iteration."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a demonstration scenario with sample component failures.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable text.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        sys.exit(0)

    results = run_demo()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_human_readable(results)


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Desert Sand Energy Coupling
# Source: scripts/desert_sand_energy_coupling.py
# ===========================================================================
"""
desert_sand_energy_coupling.py

Physics framework for multi-domain energy coupling from substrate materials.

Models how energy can be extracted from environmental substrates (e.g., desert
sand) by coupling multiple physics domains -- mechanical, thermal, electromagnetic,
piezoelectric, triboelectric, etc. Provides a generic registry of coupling
techniques, a synergy detection engine, and a weaving system that combines
couplings into integrated energy harvesting architectures.

Key concepts:
    - EnergyCoupling: a single technique with efficiency, power density,
      scalability, environment suitability, and resonance characteristics.
    - CouplingLibrary: registry populated via register(); queryable by
      physics domain, environment tag, scalability, resonance, or material.
    - SynergyEngine: pluggable rule engine that detects beneficial
      interactions between pairs of couplings.
    - CouplingWeaver: composes couplings into integrated systems, computing
      aggregate power density, efficiency, environment fit, and novel
      multi-physics or multi-resonant characteristics.

References:
    - Priya, S. & Inman, D.J. (2009). Energy Harvesting Technologies.
      Springer.
    - Beeby, S.P., Tudor, M.J. & White, N.M. (2006). "Energy harvesting
      vibration sources for microsystems applications." Measurement Science
      and Technology, 17(12), R175.
    - Fan, F.R., Tian, Z.Q. & Wang, Z.L. (2012). "Flexible triboelectric
      generator." Nano Energy, 1(2), 328-334.
    - Prigogine, I. & Nicolis, G. (1977). Self-Organization in
      Non-Equilibrium Systems. Wiley.

Usage:
    python3 scripts/desert_sand_energy_coupling.py --demo
    python3 scripts/desert_sand_energy_coupling.py --demo --json
    python3 scripts/desert_sand_energy_coupling.py --help
"""

import math
import json
import sys
import argparse
import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum
from collections import defaultdict

# ------------------
# Physics Domains
# ------------------


class PhysicsDomain(Enum):
    """Physics domains available for coupling."""
    MECHANICAL = "mechanical"
    THERMAL = "thermal"
    ELECTROMAGNETIC = "electromagnetic"
    QUANTUM = "quantum"
    ACOUSTIC = "acoustic"
    OPTICAL = "optical"
    CHEMICAL = "chemical"
    GRAVITATIONAL = "gravitational"
    FLUID_DYNAMIC = "fluid_dynamic"
    THERMOELECTRIC = "thermoelectric"
    PIEZOELECTRIC = "piezoelectric"
    PYROELECTRIC = "pyroelectric"
    TRIBOELECTRIC = "triboelectric"
    MAGNETIC = "magnetic"
    RADIO_FREQUENCY = "radio_frequency"


@dataclass
class EnergyCoupling:
    """A coupling technique to extract energy from a substrate."""
    name: str
    physics: List[PhysicsDomain]
    mechanism: str
    efficiency: float               # 0-1
    power_density: Optional[float]  # W/m² or W/kg (None if enhancement-only)
    scalability: float              # 0-1
    environment_fit: Dict[str, float] = field(default_factory=dict)
    # environment tag -> 0-1 suitability
    resonance_frequency: Optional[float] = None  # Hz, if resonant
    materials_needed: List[str] = field(default_factory=list)
    status: str = ""


# ------------------
# Coupling Library
# ------------------


class CouplingLibrary:
    """Registry of energy coupling techniques. Populate via register()."""

    def __init__(self):
        self.couplings: Dict[str, EnergyCoupling] = {}

    def register(self, coupling: EnergyCoupling):
        self.couplings[coupling.name] = coupling

    def all(self) -> List[EnergyCoupling]:
        return list(self.couplings.values())

    def by_physics(self, domain: PhysicsDomain) -> List[EnergyCoupling]:
        return [c for c in self.couplings.values() if domain in c.physics]

    def by_environment(self, tag: str, threshold: float = 0.5) -> List[EnergyCoupling]:
        return [
            c for c in self.couplings.values()
            if c.environment_fit.get(tag, 0) >= threshold
        ]

    def by_scalability(self, minimum: float) -> List[EnergyCoupling]:
        return [c for c in self.couplings.values() if c.scalability >= minimum]

    def resonant(self) -> List[EnergyCoupling]:
        return [c for c in self.couplings.values() if c.resonance_frequency is not None]

    def by_material(self, material: str) -> List[EnergyCoupling]:
        return [c for c in self.couplings.values() if material in c.materials_needed]


# ------------------
# Synergy Rule Engine
# ------------------


@dataclass
class SynergyRule:
    """Pluggable rule for detecting synergy between two couplings."""
    name: str
    match_a: Callable[[EnergyCoupling], bool]
    match_b: Callable[[EnergyCoupling], bool]
    description: str
    bonus: float = 0.1  # additive power-density or EROI bonus factor


class SynergyEngine:
    """Detects synergies via pluggable rules."""

    def __init__(self):
        self.rules: List[SynergyRule] = []

    def add_rule(self, rule: SynergyRule):
        self.rules.append(rule)

    def detect(self, couplings: List[EnergyCoupling]) -> List[Dict[str, Any]]:
        found = []
        for c1, c2 in itertools.combinations(couplings, 2):
            for rule in self.rules:
                if (rule.match_a(c1) and rule.match_b(c2)) or \
                   (rule.match_a(c2) and rule.match_b(c1)):
                    found.append({
                        "rule": rule.name,
                        "couplings": [c1.name, c2.name],
                        "description": rule.description,
                        "bonus": rule.bonus,
                    })
        return found


# ------------------
# Coupling Weaver
# ------------------


class CouplingWeaver:
    """Weaves coupling techniques into integrated energy systems."""

    def __init__(
        self,
        library: CouplingLibrary,
        synergy_engine: Optional[SynergyEngine] = None,
    ):
        self.library = library
        self.synergy_engine = synergy_engine or SynergyEngine()
        self.weavings: List[Dict[str, Any]] = []

    def weave(
        self, couplings: List[EnergyCoupling], name: str
    ) -> Dict[str, Any]:
        """Weave couplings into an integrated system."""

        all_physics: set = set()
        all_materials: set = set()
        power_sources: List[float] = []

        for c in couplings:
            all_physics.update(c.physics)
            all_materials.update(c.materials_needed)
            if c.power_density is not None:
                power_sources.append(c.power_density)

        synergies = self.synergy_engine.detect(couplings)
        synergy_bonus = sum(s["bonus"] for s in synergies)

        total_power = sum(power_sources)
        avg_efficiency = (
            sum(c.efficiency for c in couplings) / len(couplings)
            if couplings else 0
        )
        avg_scalability = (
            sum(c.scalability for c in couplings) / len(couplings)
            if couplings else 0
        )

        # Environment fit intersection
        env_tags: set = set()
        for c in couplings:
            env_tags.update(c.environment_fit.keys())
        env_scores = {}
        for tag in env_tags:
            scores = [c.environment_fit.get(tag, 0) for c in couplings]
            env_scores[tag] = sum(scores) / len(scores)

        # Resonance spectrum
        resonant = [c for c in couplings if c.resonance_frequency is not None]
        freq_bands = sorted(set(c.resonance_frequency for c in resonant))

        # Novel coupling detection
        novel: List[str] = []
        if len(all_physics) >= 5:
            novel.append(
                f"Multi-physics harvesting: {len(all_physics)} domains coupled"
            )
        if len(freq_bands) >= 2:
            novel.append(
                f"Multi-resonant system: {len(freq_bands)} frequency bands"
            )

        weaving = {
            "name": name,
            "couplings": [c.name for c in couplings],
            "physics_domains": sorted(p.value for p in all_physics),
            "materials": sorted(all_materials),
            "synergies": synergies,
            "novel_couplings": novel,
            "total_power_density": total_power,
            "average_efficiency": avg_efficiency,
            "average_scalability": avg_scalability,
            "environment_fit": env_scores,
            "frequency_bands": freq_bands,
        }

        self.weavings.append(weaving)
        return weaving

    def weave_by_environment(
        self, tag: str, name: str, threshold: float = 0.5
    ) -> Dict[str, Any]:
        suited = self.library.by_environment(tag, threshold)
        if not suited:
            return {"name": name, "error": f"No couplings for '{tag}' >= {threshold}"}
        return self.weave(suited, name)

    def weave_by_physics(
        self, domain: PhysicsDomain, name: str
    ) -> Dict[str, Any]:
        matching = self.library.by_physics(domain)
        if not matching:
            return {"name": name, "error": f"No couplings for '{domain.value}'"}
        return self.weave(matching, name)

    def weave_resonant(self, name: str = "Resonant System") -> Dict[str, Any]:
        resonant = self.library.resonant()
        if not resonant:
            return {"name": name, "error": "No resonant couplings registered"}
        return self.weave(resonant, name)

    def compare_weavings(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": w["name"],
                "power": w.get("total_power_density", 0),
                "efficiency": w.get("average_efficiency", 0),
                "scalability": w.get("average_scalability", 0),
                "physics_count": len(w.get("physics_domains", [])),
                "synergy_count": len(w.get("synergies", [])),
            }
            for w in self.weavings
        ]


# ------------------
# Demo / CLI
# ------------------


def _build_demo_library() -> CouplingLibrary:
    """Build a demonstration library with sample desert-sand couplings."""
    lib = CouplingLibrary()

    lib.register(EnergyCoupling(
        name="Piezoelectric Sand Compression",
        physics=[PhysicsDomain.PIEZOELECTRIC, PhysicsDomain.MECHANICAL],
        mechanism="Quartz-bearing sand grains under cyclic mechanical stress "
                  "generate charge via direct piezoelectric effect.",
        efficiency=0.15,
        power_density=0.5,
        scalability=0.7,
        environment_fit={"desert": 0.9, "coastal": 0.6},
        resonance_frequency=40.0,
        materials_needed=["quartz sand", "electrode array"],
        status="theoretical",
    ))

    lib.register(EnergyCoupling(
        name="Triboelectric Wind-Sand",
        physics=[PhysicsDomain.TRIBOELECTRIC, PhysicsDomain.MECHANICAL],
        mechanism="Wind-driven sand particle collisions generate charge "
                  "separation via triboelectric effect.",
        efficiency=0.08,
        power_density=0.2,
        scalability=0.8,
        environment_fit={"desert": 0.95, "coastal": 0.5},
        materials_needed=["collection electrodes"],
        status="experimental",
    ))

    lib.register(EnergyCoupling(
        name="Thermal Gradient Harvesting",
        physics=[PhysicsDomain.THERMOELECTRIC, PhysicsDomain.THERMAL],
        mechanism="Exploit day-night temperature differential in sand "
                  "layers via Seebeck effect thermoelectric generators.",
        efficiency=0.10,
        power_density=1.5,
        scalability=0.6,
        environment_fit={"desert": 0.95, "arid": 0.8},
        materials_needed=["thermoelectric modules", "heat sinks"],
        status="proven",
    ))

    lib.register(EnergyCoupling(
        name="Pyroelectric Thermal Cycling",
        physics=[PhysicsDomain.PYROELECTRIC, PhysicsDomain.THERMAL],
        mechanism="Rapid temperature fluctuations in surface sand induce "
                  "pyroelectric charge generation in crystalline grains.",
        efficiency=0.05,
        power_density=0.1,
        scalability=0.5,
        environment_fit={"desert": 0.7},
        resonance_frequency=0.001,
        materials_needed=["pyroelectric crystals"],
        status="theoretical",
    ))

    lib.register(EnergyCoupling(
        name="Acoustic Resonance Harvesting",
        physics=[PhysicsDomain.ACOUSTIC, PhysicsDomain.MECHANICAL],
        mechanism="Desert 'singing sand' dune resonance captured via "
                  "tuned acoustic-to-electric transducers.",
        efficiency=0.03,
        power_density=0.05,
        scalability=0.4,
        environment_fit={"desert": 0.6},
        resonance_frequency=90.0,
        materials_needed=["acoustic transducers"],
        status="conceptual",
    ))

    return lib


def _build_demo_synergy_engine() -> SynergyEngine:
    """Build a synergy engine with sample rules."""
    engine = SynergyEngine()

    engine.add_rule(SynergyRule(
        name="Thermo-Piezo Cascade",
        match_a=lambda c: PhysicsDomain.THERMAL in c.physics,
        match_b=lambda c: PhysicsDomain.PIEZOELECTRIC in c.physics,
        description="Thermal expansion drives mechanical stress in "
                    "piezoelectric substrates, cascading energy conversion.",
        bonus=0.12,
    ))

    engine.add_rule(SynergyRule(
        name="Tribo-Acoustic Feedback",
        match_a=lambda c: PhysicsDomain.TRIBOELECTRIC in c.physics,
        match_b=lambda c: PhysicsDomain.ACOUSTIC in c.physics,
        description="Triboelectric particle collisions excite acoustic "
                    "modes; acoustic resonance enhances particle agitation.",
        bonus=0.08,
    ))

    return engine


def _format_weaving(w: Dict[str, Any], indent: int = 0) -> str:
    """Format a weaving result for human-readable output."""
    pad = " " * indent
    lines = []
    lines.append(f"{pad}=== {w['name']} ===")

    if "error" in w:
        lines.append(f"{pad}  Error: {w['error']}")
        return "\n".join(lines)

    lines.append(f"{pad}  Couplings: {', '.join(w.get('couplings', []))}")
    lines.append(f"{pad}  Physics domains: {', '.join(w.get('physics_domains', []))}")
    lines.append(f"{pad}  Materials: {', '.join(w.get('materials', []))}")
    lines.append(f"{pad}  Total power density: {w.get('total_power_density', 0):.3f} W/m2")
    lines.append(f"{pad}  Average efficiency: {w.get('average_efficiency', 0):.3f}")
    lines.append(f"{pad}  Average scalability: {w.get('average_scalability', 0):.3f}")

    env = w.get("environment_fit", {})
    if env:
        env_str = ", ".join(f"{k}: {v:.2f}" for k, v in sorted(env.items()))
        lines.append(f"{pad}  Environment fit: {env_str}")

    freq = w.get("frequency_bands", [])
    if freq:
        lines.append(f"{pad}  Frequency bands: {freq}")

    synergies = w.get("synergies", [])
    if synergies:
        lines.append(f"{pad}  Synergies detected: {len(synergies)}")
        for s in synergies:
            lines.append(f"{pad}    - {s['rule']}: {s['description']} (bonus: +{s['bonus']:.2f})")

    novel = w.get("novel_couplings", [])
    if novel:
        lines.append(f"{pad}  Novel couplings:")
        for n in novel:
            lines.append(f"{pad}    - {n}")

    return "\n".join(lines)


def run_demo(use_json: bool = False):
    """Run a demonstration of the coupling framework."""
    lib = _build_demo_library()
    engine = _build_demo_synergy_engine()
    weaver = CouplingWeaver(lib, engine)

    # Weave all desert-suited couplings
    desert_system = weaver.weave_by_environment("desert", "Desert Sand Energy System")

    # Weave by thermal physics domain
    thermal_system = weaver.weave_by_physics(
        PhysicsDomain.THERMAL, "Thermal Harvesting Subsystem"
    )

    # Weave resonant couplings
    resonant_system = weaver.weave_resonant("Resonant Harvesting Subsystem")

    comparison = weaver.compare_weavings()

    if use_json:
        output = {
            "weavings": weaver.weavings,
            "comparison": comparison,
            "library_size": len(lib.all()),
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print("Desert Sand Energy Coupling Framework -- Demo")
        print("=" * 55)
        print()
        print(f"Registered couplings: {len(lib.all())}")
        print()

        for w in weaver.weavings:
            print(_format_weaving(w))
            print()

        print("-" * 55)
        print("Comparison of weavings:")
        print(f"  {'Name':<35} {'Power':>8} {'Eff':>6} {'Scale':>6} {'Phys':>5} {'Syn':>4}")
        for c in comparison:
            print(
                f"  {c['name']:<35} "
                f"{c['power']:>8.3f} "
                f"{c['efficiency']:>6.3f} "
                f"{c['scalability']:>6.3f} "
                f"{c['physics_count']:>5d} "
                f"{c['synergy_count']:>4d}"
            )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Physics framework for multi-domain energy coupling from "
            "substrate materials. Models how energy can be extracted from "
            "environmental substrates by coupling multiple physics domains."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a demonstration with sample desert-sand couplings and synergy rules.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable text.",
    )

    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        sys.exit(0)

    run_demo(use_json=args.json)


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Geometric Desalination
# Source: scripts/geometric_desalination.py
# ===========================================================================
"""
Geometric Desalination — desalination as a geometric system of coupled vectors.

Models desalination infrastructure as a multi-dimensional vector space where each
vector represents a functional dimension (energy input, water output, brine
management, ecological restoration, etc.). System quality is measured by geometric
properties: the "area" (integration proxy) and "integrity" (balance × coupling)
of the resulting polytope.

A pluggable CouplingEngine detects synergies between practices, and the
GeometricDesalinationWeaver composes practices into integrated systems scored
by vector count, coupling density, and geometric potential.

The framework is generic: populate the WisdomLibrary and CouplingEngine via
constructors / register() for any real-world or hypothetical practice set.

References
----------
- Elimelech, M. & Phillip, W. A. (2011). The future of seawater desalination:
  energy, technology, and the environment. *Science*, 333(6043), 712-717.
- Prigogine, I. (1980). *From Being to Becoming*. W. H. Freeman.
- Jones, E. et al. (2019). The state of desalination and brine production:
  a global outlook. *Science of the Total Environment*, 657, 1343-1356.

Usage
-----
    python3 scripts/geometric_desalination.py --demo
    python3 scripts/geometric_desalination.py --demo --json
    python3 scripts/geometric_desalination.py --help
"""

import math
import itertools
import json
import argparse
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum

# ------------------
# Desalination Vectors
# ------------------


class DesalinationVector(Enum):
    """Possible vectors in a geometric desalination system."""
    ENERGY_INPUT = "energy_input"
    WATER_OUTPUT = "water_output"
    BRINE_MANAGEMENT = "brine_management"
    MINERAL_EXTRACTION = "mineral_extraction"
    MARINE_ECOLOGY = "marine_ecology"
    WASTE_HEAT = "waste_heat"
    RENEWABLE_COUPLING = "renewable_coupling"
    ATMOSPHERIC_HARVEST = "atmospheric_harvest"
    ECOLOGICAL_RESTORATION = "ecological_restoration"
    COMMUNITY_OWNERSHIP = "community_ownership"
    PASSIVE_THERMAL = "passive_thermal"
    WAVE_ENERGY = "wave_energy"
    SOLAR_STILL = "solar_still"
    BIOSALINE_AGRICULTURE = "biosaline_agriculture"


# ------------------
# Desalination System
# ------------------


@dataclass
class DesalinationSystem:
    """Desalination as a geometric system of coupled vectors."""
    name: str
    vectors: Dict[DesalinationVector, float]
    couplings: Dict[Tuple[DesalinationVector, DesalinationVector], float]

    def active_vectors(self) -> List[DesalinationVector]:
        return [v for v, mag in self.vectors.items() if mag > 0]

    def area(self) -> float:
        """
        Geometric proxy for system integration.
        Larger -> more coupled, more resilient.
        """
        active = self.active_vectors()
        if len(active) < 3:
            return 0
        avg_mag = sum(
            self.vectors[v] for v in active
        ) / len(active)
        coupling_factor = (
            sum(self.couplings.values()) / len(self.couplings)
            if self.couplings else 0
        )
        return avg_mag * coupling_factor * len(active) / 8

    def integrity(self) -> float:
        """
        Geometric integrity (0-1).
        Balance of magnitudes x average coupling strength.
        """
        active = [self.vectors[v] for v in self.active_vectors()]
        if not active:
            return 0
        avg = sum(active) / len(active)
        balance = (
            1 - (sum(abs(m - avg) for m in active) / (len(active) * avg))
            if avg > 0 else 0
        )
        coupling_avg = (
            sum(self.couplings.values()) / len(self.couplings)
            if self.couplings else 0
        )
        return balance * 0.5 + coupling_avg * 0.5

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "active_vectors": len(self.active_vectors()),
            "total_vectors": len(self.vectors),
            "area": self.area(),
            "integrity": self.integrity(),
        }


# ------------------
# Desalination Wisdom
# ------------------


@dataclass
class DesalinationWisdom:
    """A desalination practice with its vector coverage and coupling potential."""
    name: str
    mechanism: str
    vectors: List[DesalinationVector]
    efficiency: float
    coupling_potential: List[str]
    tags: Dict[str, str] = field(default_factory=dict)
    # arbitrary metadata: origin, status, etc.


class DesalinationWisdomLibrary:
    """Registry of desalination practices. Populate via register()."""

    def __init__(self):
        self.practices: Dict[str, DesalinationWisdom] = {}

    def register(self, practice: DesalinationWisdom):
        self.practices[practice.name] = practice

    def by_vector(self, vector: DesalinationVector) -> List[DesalinationWisdom]:
        return [
            p for p in self.practices.values() if vector in p.vectors
        ]

    def all(self) -> List[DesalinationWisdom]:
        return list(self.practices.values())


# ------------------
# Coupling Rule Engine
# ------------------


@dataclass
class CouplingRule:
    """Pluggable rule detecting coupling between two practices."""
    name: str
    match_a: Callable[[DesalinationWisdom], bool]
    match_b: Callable[[DesalinationWisdom], bool]
    description: str


class CouplingEngine:
    def __init__(self):
        self.rules: List[CouplingRule] = []

    def add_rule(self, rule: CouplingRule):
        self.rules.append(rule)

    def detect(
        self, practices: List[DesalinationWisdom]
    ) -> List[Dict[str, Any]]:
        found = []
        for p1, p2 in itertools.combinations(practices, 2):
            for rule in self.rules:
                if (rule.match_a(p1) and rule.match_b(p2)) or \
                   (rule.match_a(p2) and rule.match_b(p1)):
                    found.append({
                        "rule": rule.name,
                        "practices": [p1.name, p2.name],
                        "description": rule.description,
                    })
        return found


# ------------------
# Geometric Desalination Weaver
# ------------------


class GeometricDesalinationWeaver:
    """Weaves desalination practices into geometric systems."""

    def __init__(
        self,
        library: DesalinationWisdomLibrary,
        coupling_engine: Optional[CouplingEngine] = None,
    ):
        self.library = library
        self.coupling_engine = coupling_engine or CouplingEngine()
        self.weavings: List[Dict[str, Any]] = []

    def weave(
        self, practice_names: List[str], name: str
    ) -> Dict[str, Any]:
        """Weave named practices into an integrated system."""
        practices = [
            self.library.practices[p]
            for p in practice_names
            if p in self.library.practices
        ]

        all_vectors: set = set()
        for p in practices:
            all_vectors.update(p.vectors)

        couplings = self.coupling_engine.detect(practices)

        vector_count = len(all_vectors)
        coupling_count = len(couplings)
        possible = vector_count * (vector_count - 1) / 2 if vector_count > 1 else 1
        coupling_density = coupling_count / possible

        weaving = {
            "name": name,
            "practices": practice_names,
            "vectors": sorted(v.value for v in all_vectors),
            "couplings": couplings,
            "vector_count": vector_count,
            "coupling_count": coupling_count,
            "coupling_density": coupling_density,
            "geometric_potential": vector_count * coupling_density,
        }

        self.weavings.append(weaving)
        return weaving

    def weave_all(self, name: str = "Complete System") -> Dict[str, Any]:
        return self.weave(list(self.library.practices.keys()), name)

    def compare_weavings(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": w["name"],
                "vectors": w["vector_count"],
                "couplings": w["coupling_count"],
                "density": w["coupling_density"],
                "potential": w["geometric_potential"],
            }
            for w in self.weavings
        ]


# ------------------
# Demo / CLI
# ------------------


def build_demo_library() -> DesalinationWisdomLibrary:
    """Build a small demonstration library of desalination practices."""
    lib = DesalinationWisdomLibrary()

    lib.register(DesalinationWisdom(
        name="Solar Still Array",
        mechanism="Passive solar evaporation with condensation recovery",
        vectors=[
            DesalinationVector.SOLAR_STILL,
            DesalinationVector.PASSIVE_THERMAL,
            DesalinationVector.WATER_OUTPUT,
        ],
        efficiency=0.35,
        coupling_potential=["waste_heat_recovery", "biosaline_irrigation"],
        tags={"origin": "traditional", "status": "proven"},
    ))

    lib.register(DesalinationWisdom(
        name="Wave-Powered RO",
        mechanism="Direct wave-energy pressurisation for reverse osmosis",
        vectors=[
            DesalinationVector.WAVE_ENERGY,
            DesalinationVector.RENEWABLE_COUPLING,
            DesalinationVector.WATER_OUTPUT,
            DesalinationVector.ENERGY_INPUT,
        ],
        efficiency=0.55,
        coupling_potential=["marine_ecology_monitoring", "brine_dispersal"],
        tags={"origin": "engineering", "status": "prototype"},
    ))

    lib.register(DesalinationWisdom(
        name="Brine-to-Mineral Recovery",
        mechanism="Selective crystallisation extracting Li, Mg, Na salts from RO brine",
        vectors=[
            DesalinationVector.BRINE_MANAGEMENT,
            DesalinationVector.MINERAL_EXTRACTION,
        ],
        efficiency=0.40,
        coupling_potential=["waste_heat_input", "biosaline_agriculture"],
        tags={"origin": "chemistry", "status": "pilot"},
    ))

    lib.register(DesalinationWisdom(
        name="Biosaline Agroforestry",
        mechanism="Salt-tolerant crops irrigated with diluted brine",
        vectors=[
            DesalinationVector.BIOSALINE_AGRICULTURE,
            DesalinationVector.ECOLOGICAL_RESTORATION,
            DesalinationVector.BRINE_MANAGEMENT,
        ],
        efficiency=0.30,
        coupling_potential=["community_ownership", "marine_ecology"],
        tags={"origin": "agroecology", "status": "established"},
    ))

    lib.register(DesalinationWisdom(
        name="Community Fog Harvesting",
        mechanism="Mesh-net atmospheric water capture with community governance",
        vectors=[
            DesalinationVector.ATMOSPHERIC_HARVEST,
            DesalinationVector.COMMUNITY_OWNERSHIP,
            DesalinationVector.WATER_OUTPUT,
        ],
        efficiency=0.20,
        coupling_potential=["ecological_restoration", "solar_still"],
        tags={"origin": "indigenous", "status": "proven"},
    ))

    return lib


def build_demo_coupling_engine() -> CouplingEngine:
    """Build a coupling engine with example rules for the demo library."""
    engine = CouplingEngine()

    engine.add_rule(CouplingRule(
        name="brine_loop",
        match_a=lambda p: DesalinationVector.BRINE_MANAGEMENT in p.vectors,
        match_b=lambda p: DesalinationVector.MINERAL_EXTRACTION in p.vectors
            or DesalinationVector.BIOSALINE_AGRICULTURE in p.vectors,
        description="Brine output of one practice feeds mineral or agricultural input of another",
    ))

    engine.add_rule(CouplingRule(
        name="renewable_energy_share",
        match_a=lambda p: DesalinationVector.RENEWABLE_COUPLING in p.vectors
            or DesalinationVector.WAVE_ENERGY in p.vectors,
        match_b=lambda p: DesalinationVector.ENERGY_INPUT in p.vectors
            or DesalinationVector.PASSIVE_THERMAL in p.vectors,
        description="Renewable energy generated by one practice powers another",
    ))

    engine.add_rule(CouplingRule(
        name="community_governance",
        match_a=lambda p: DesalinationVector.COMMUNITY_OWNERSHIP in p.vectors,
        match_b=lambda p: DesalinationVector.ECOLOGICAL_RESTORATION in p.vectors,
        description="Community governance couples with ecological restoration feedback",
    ))

    return engine


def run_demo(as_json: bool = False):
    """Run the demonstration: build library, weave systems, print results."""
    lib = build_demo_library()
    engine = build_demo_coupling_engine()
    weaver = GeometricDesalinationWeaver(lib, engine)

    # Weave a partial system
    partial = weaver.weave(
        ["Solar Still Array", "Brine-to-Mineral Recovery"],
        name="Partial: Solar + Mineral",
    )

    # Weave a broader system
    broad = weaver.weave(
        ["Wave-Powered RO", "Brine-to-Mineral Recovery",
         "Biosaline Agroforestry"],
        name="Broad: Wave + Mineral + Agro",
    )

    # Weave the complete system
    complete = weaver.weave_all(name="Complete Demo System")

    comparison = weaver.compare_weavings()

    if as_json:
        output = {
            "weavings": weaver.weavings,
            "comparison": comparison,
        }
        print(json.dumps(output, indent=2))
        return

    # Human-readable output
    print("=" * 60)
    print("GEOMETRIC DESALINATION — Demo Weavings")
    print("=" * 60)

    for w in weaver.weavings:
        print()
        print(f"--- {w['name']} ---")
        print(f"  Practices:          {', '.join(w['practices'])}")
        print(f"  Vectors ({w['vector_count']:>2}):       {', '.join(w['vectors'])}")
        print(f"  Couplings found:    {w['coupling_count']}")
        print(f"  Coupling density:   {w['coupling_density']:.3f}")
        print(f"  Geometric potential: {w['geometric_potential']:.3f}")
        if w["couplings"]:
            print("  Coupling details:")
            for c in w["couplings"]:
                print(f"    [{c['rule']}] {c['practices'][0]} <-> {c['practices'][1]}")
                print(f"      {c['description']}")

    print()
    print("=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"  {'Name':<35} {'Vec':>4} {'Coup':>5} {'Dens':>7} {'Potntl':>7}")
    print(f"  {'-'*35} {'-'*4} {'-'*5} {'-'*7} {'-'*7}")
    for row in comparison:
        print(
            f"  {row['name']:<35} {row['vectors']:>4} "
            f"{row['couplings']:>5} {row['density']:>7.3f} "
            f"{row['potential']:>7.3f}"
        )
    print()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Geometric Desalination — model desalination infrastructure as "
            "a geometric system of coupled vectors. Practices are composed "
            "into integrated systems scored by vector count, coupling density, "
            "and geometric potential."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a built-in demonstration with sample practices and couplings",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output results as JSON instead of human-readable text",
    )

    args = parser.parse_args()

    if args.demo:
        run_demo(as_json=args.as_json)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Mineral Mulch
# Source: scripts/mineral_mulch.py
# ===========================================================================
"""
mineral_mulch.py — Stone-mulch microclimate simulation for root-zone protection.

Purpose:
    Simulate the effects of stone mulch layers on root-zone microclimates,
    including thermal condensation, pH buffering via mineral dissolution,
    biological activity gating, multi-layer mineral decay over years,
    thermal shock propagation, cumulative stress/recovery cycles, and
    lateral frost protection scaling.

    All parameters are configurable — no hardcoded location constants.

Methodology:
    - Thermal cycle: sinusoidal daily temperature model with albedo-dependent
      stone surface cooling and dew-point condensation estimates.
    - pH buffering: dissolution rate proportional to acid deficit (pH < 7).
    - Biological activity: microbe efficiency as a function of pH proximity
      to optimum; insect density gated by temperature and moisture windows.
    - Mineral decay: two-layer model (reactive buffer + protective armor)
      with weathering and dissolution over multi-year timescales.
    - Thermal shock: exponential heat-loss model through insulative layers
      with lethal-threshold detection.
    - Cumulative stress: entropy-load accumulation from shock events with
      seasonal recovery and health tracking.
    - Frost protection: radial heat-diffusion scaling — time to frost
      penetration proportional to (effective radius)^2 / severity.

References:
    - Jury, W.A. & Horton, R. (2004). Soil Physics, 6th ed. Wiley.
    - Hillel, D. (2003). Introduction to Environmental Soil Physics. Academic Press.
    - Poesen, J. & Lavee, H. (1994). Rock fragments in top soils: significance
      and processes. Catena, 23(1-2), 1-28.
    - Kemper, W.D. et al. (1994). Stone cover and mulch effects on soil loss.
      Soil Technology, 7(2), 97-108.
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

# ------------------
# Site and Material Parameters
# ------------------


@dataclass
class SiteParams:
    """Environmental baseline for the site."""
    soil_ph: float = 4.5
    soil_moisture: float = 0.15         # fraction (0-1)
    mean_temp_c: float = 11.0           # daily mean
    temp_amplitude_c: float = 13.0      # half-range of daily swing
    temp_peak_hour: int = 14            # hour of day peak
    root_temp_initial_c: float = 2.0    # stable root-zone temperature
    root_death_temp_c: float = -15.0    # lethal root threshold


@dataclass
class StoneLayer:
    """Properties of a single stone layer."""
    name: str
    albedo: float               # 0-1, reflectivity
    dissolution_rate: float     # pH units buffered per time step per pH deficit
    porosity: float             # 0-1
    weathering_rate: float      # fraction lost per year per unit weather severity
    insulation_factor: float    # 0-1, thermal resistance contribution


# ------------------
# Daily Thermal Cycle
# ------------------


def hourly_temperature(hour: int, mean: float, amplitude: float, peak_hour: int = 14) -> float:
    """Sinusoidal temperature model."""
    return mean + amplitude * math.sin((hour - peak_hour + 6) * math.pi / 12)


def thermal_condensation(
    air_temp: float,
    albedo: float,
) -> tuple:
    """
    Stone surface temperature and condensation estimate.

    Returns (stone_temp, condensation_mm)
    """
    stone_temp = air_temp * (1 - albedo)
    condensation = max(0, (air_temp - stone_temp) * 0.01)
    return stone_temp, condensation


def simulate_daily_cycle(
    site: SiteParams,
    layer: StoneLayer,
    hours: int = 24,
    report_interval: int = 4,
) -> Dict[str, Any]:
    """
    Run one 24-hour cycle tracking temperature, condensation, pH, moisture.

    Returns dict with hourly arrays and final state.
    """
    ph = site.soil_ph
    moisture = site.soil_moisture
    log = []

    for hour in range(hours):
        air_temp = hourly_temperature(hour, site.mean_temp_c, site.temp_amplitude_c, site.temp_peak_hour)
        stone_temp, dew = thermal_condensation(air_temp, layer.albedo)
        moisture += dew

        # pH buffering: dissolution proportional to acid deficit
        if ph < 7.0:
            ph += layer.dissolution_rate / (ph + 0.1)

        log.append({
            "hour": hour,
            "air_temp": round(air_temp, 2),
            "stone_temp": round(stone_temp, 2),
            "condensation": round(dew, 5),
            "ph": round(ph, 3),
            "moisture": round(moisture, 5),
        })

    return {
        "log": log,
        "final_ph": ph,
        "final_moisture": moisture,
        "total_condensation": sum(e["condensation"] for e in log),
    }


# ------------------
# Biological Activity Gate
# ------------------


@dataclass
class BioState:
    """Biological activity state."""
    microbe_efficiency: float = 0.0   # 0-1
    insect_density: float = 0.0       # relative


def update_biology(
    state: BioState,
    ph: float,
    moisture: float,
    temp: float,
    ph_optimum: float = 7.0,
    ph_range: float = 3.0,
    moisture_threshold: float = 0.18,
    temp_low: float = 10.0,
    temp_high: float = 22.0,
    growth_rate: float = 0.05,
    decline_rate: float = 0.02,
) -> BioState:
    """
    Update biological activity based on current conditions.
    Microbe efficiency peaks when pH approaches optimum.
    Insect density grows when temperature and moisture are favorable.
    """
    efficiency = max(0, 1 - abs(ph_optimum - ph) / ph_range)

    if temp_low < temp < temp_high and moisture > moisture_threshold:
        density = state.insect_density + growth_rate * efficiency
    else:
        density = state.insect_density - decline_rate

    return BioState(
        microbe_efficiency=round(efficiency, 4),
        insect_density=round(max(0, density), 4),
    )


# ------------------
# Multi-Layer Mineral Decay (Long-Term)
# ------------------


@dataclass
class MineralState:
    """State of multi-layer mineral reserves."""
    buffer_reserve: float = 100.0    # reactive layer (e.g., limestone) %
    armor_integrity: float = 100.0   # protective cap (e.g., granite) %
    soil_ph: float = 4.5
    biotic_capital: float = 0.0      # accumulated biological capacity


def step_mineral_year(
    state: MineralState,
    weather_severity: float = 1.0,
    buffer_layer: Optional[StoneLayer] = None,
    armor_layer: Optional[StoneLayer] = None,
) -> MineralState:
    """
    Advance mineral state by one year.

    buffer_layer dissolves to raise pH.
    armor_layer weathers slowly, protecting buffer.
    """
    bl = buffer_layer or StoneLayer("buffer", 0.4, 0.005, 0.2, 0.001, 0.4)
    al = armor_layer or StoneLayer("armor", 0.5, 0.0001, 0.05, 0.001, 0.5)

    # Armor weathering
    armor = max(0, state.armor_integrity - al.weathering_rate * weather_severity * 100)

    # Buffer dissolution (proportional to pH deficit)
    ph_deficit = max(0, 7.0 - state.soil_ph)
    dissolution = 0.05 * ph_deficit
    buffer = max(0, state.buffer_reserve - dissolution)

    # pH change
    if state.buffer_reserve > 0:
        ph = state.soil_ph + dissolution * 0.8
    else:
        ph = state.soil_ph - 0.02  # slow re-acidification

    # Biotic capital accumulates as pH improves
    bio = state.biotic_capital + 0.1 * (ph / 5.0)

    return MineralState(
        buffer_reserve=round(buffer, 2),
        armor_integrity=round(armor, 2),
        soil_ph=round(min(7.0, ph), 3),
        biotic_capital=round(bio, 3),
    )


def simulate_years(
    initial: Optional[MineralState] = None,
    years: int = 15,
    weather_severity: float = 1.0,
    buffer_layer: Optional[StoneLayer] = None,
    armor_layer: Optional[StoneLayer] = None,
) -> List[Dict[str, Any]]:
    """Run multi-year mineral decay simulation."""
    state = initial or MineralState()
    log = []
    for y in range(1, years + 1):
        state = step_mineral_year(state, weather_severity, buffer_layer, armor_layer)
        log.append({
            "year": y,
            "buffer_reserve": state.buffer_reserve,
            "armor_integrity": state.armor_integrity,
            "soil_ph": state.soil_ph,
            "biotic_capital": state.biotic_capital,
        })
    return log


# ------------------
# Thermal Shock
# ------------------


def thermal_shock(
    root_temp: float,
    ambient_temp: float,
    duration_hours: int,
    insulation_factor: float = 0.85,
    death_threshold: float = -15.0,
) -> Dict[str, Any]:
    """
    Simulate thermal shock propagation through insulation.

    Returns final root temp, survival status, and hourly trace.
    """
    trace = []
    alive = True
    t = root_temp

    for hour in range(duration_hours):
        heat_loss = (t - ambient_temp) * (1 - insulation_factor) * 0.05
        t -= heat_loss
        trace.append(round(t, 3))
        if t <= death_threshold:
            alive = False
            break

    return {
        "initial_root_temp": root_temp,
        "ambient_temp": ambient_temp,
        "duration_hours": duration_hours,
        "final_root_temp": round(t, 3),
        "alive": alive,
        "hours_survived": len(trace),
        "trace": trace,
    }


# ------------------
# Cumulative Stress / Recovery
# ------------------


@dataclass
class StressState:
    """Cumulative stress and health state."""
    health: float = 100.0
    entropy_load: float = 0.0


def step_stress_year(
    state: StressState,
    shock_events: int,
    insulation_factor: float = 0.85,
    temp_delta: float = 42.0,
    damage_threshold: float = 20.0,
    damage_rate: float = 0.5,
    summer_recovery: float = 15.0,
    health_regen: float = 3.0,
) -> StressState:
    """
    Apply shock events and summer recovery for one year.
    """
    entropy = state.entropy_load
    health = state.health

    for _ in range(shock_events):
        stress = temp_delta * (1 - insulation_factor)
        entropy += stress
        if entropy > damage_threshold:
            health -= (entropy - damage_threshold) * damage_rate

    # Summer recovery
    entropy = max(0, entropy - summer_recovery)
    health = min(100, health + health_regen)

    return StressState(
        health=round(max(0, health), 2),
        entropy_load=round(entropy, 2),
    )


def simulate_stress_years(
    years: int = 15,
    initial: Optional[StressState] = None,
    event_schedule: Optional[List[int]] = None,
    insulation_factor: float = 0.85,
) -> List[Dict[str, Any]]:
    """
    Multi-year cumulative stress simulation.

    event_schedule: shock events per year (default: increasing).
    """
    state = initial or StressState()
    if event_schedule is None:
        event_schedule = [1 + (y // 4) for y in range(years)]

    log = []
    for y in range(years):
        events = event_schedule[y] if y < len(event_schedule) else event_schedule[-1]
        state = step_stress_year(state, events, insulation_factor)
        log.append({
            "year": y + 1,
            "events": events,
            "health": state.health,
            "entropy_load": state.entropy_load,
            "status": "alive" if state.health > 0 else "dead",
        })
        if state.health <= 0:
            break
    return log


# ------------------
# Lateral Frost Protection
# ------------------


def frost_protection_hours(
    spread_diameter_ft: float,
    external_temp_c: float = -45.0,
    insulation_bonus: float = 0.4,
    reference_temp_c: float = -10.0,
) -> float:
    """
    Estimate hours until frost penetrates to root center.
    Time scales with (effective_radius)^2 / temperature severity.
    """
    radius_cm = (spread_diameter_ft / 2) * 30.48
    effective_resistance = radius_cm * (1 + insulation_bonus)
    severity = abs(external_temp_c / reference_temp_c)
    return (effective_resistance ** 2) / (100 * severity)


def compare_spreads(
    diameters_ft: List[float],
    external_temp_c: float = -45.0,
    insulation_bonus: float = 0.4,
) -> List[Dict[str, float]]:
    """Compare frost protection across different spread diameters."""
    return [
        {
            "diameter_ft": d,
            "safe_hours": round(frost_protection_hours(d, external_temp_c, insulation_bonus), 1),
        }
        for d in diameters_ft
    ]


# ------------------
# CLI
# ------------------


def _print_table(rows: List[Dict[str, Any]], keys: Optional[List[str]] = None) -> None:
    """Print a list of dicts as a simple aligned table."""
    if not rows:
        return
    keys = keys or list(rows[0].keys())
    widths = {k: max(len(str(k)), *(len(str(r.get(k, ""))) for r in rows)) for k in keys}
    header = "  ".join(str(k).rjust(widths[k]) for k in keys)
    print(header)
    print("  ".join("-" * widths[k] for k in keys))
    for r in rows:
        print("  ".join(str(r.get(k, "")).rjust(widths[k]) for k in keys))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stone-mulch microclimate simulation for root-zone protection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s daily                           Run a 24-hour thermal/pH cycle
  %(prog)s mineral --years 20              Multi-year mineral decay
  %(prog)s stress --years 20               Cumulative stress simulation
  %(prog)s shock --ambient -40 --hours 72  Thermal shock event
  %(prog)s frost --diameters 4 8 12 16     Compare frost protection by spread
  %(prog)s all --json                      Run all simulations, output JSON
""",
    )
    sub = parser.add_subparsers(dest="command", help="Simulation to run")

    # -- daily --
    p_daily = sub.add_parser("daily", help="24-hour thermal/condensation/pH cycle")
    p_daily.add_argument("--mean-temp", type=float, default=11.0, help="Daily mean temp C (default: 11)")
    p_daily.add_argument("--amplitude", type=float, default=13.0, help="Temp half-range C (default: 13)")
    p_daily.add_argument("--soil-ph", type=float, default=4.5, help="Initial soil pH (default: 4.5)")
    p_daily.add_argument("--albedo", type=float, default=0.4, help="Stone albedo (default: 0.4)")
    p_daily.add_argument("--json", action="store_true", help="Output as JSON")

    # -- mineral --
    p_min = sub.add_parser("mineral", help="Multi-year mineral decay simulation")
    p_min.add_argument("--years", type=int, default=15, help="Simulation years (default: 15)")
    p_min.add_argument("--weather-severity", type=float, default=1.0, help="Weather severity multiplier (default: 1.0)")
    p_min.add_argument("--json", action="store_true", help="Output as JSON")

    # -- stress --
    p_stress = sub.add_parser("stress", help="Cumulative stress/recovery simulation")
    p_stress.add_argument("--years", type=int, default=15, help="Simulation years (default: 15)")
    p_stress.add_argument("--insulation", type=float, default=0.85, help="Insulation factor (default: 0.85)")
    p_stress.add_argument("--json", action="store_true", help="Output as JSON")

    # -- shock --
    p_shock = sub.add_parser("shock", help="Thermal shock propagation")
    p_shock.add_argument("--root-temp", type=float, default=2.0, help="Initial root temp C (default: 2)")
    p_shock.add_argument("--ambient", type=float, default=-30.0, help="Ambient temp C (default: -30)")
    p_shock.add_argument("--hours", type=int, default=48, help="Duration hours (default: 48)")
    p_shock.add_argument("--insulation", type=float, default=0.85, help="Insulation factor (default: 0.85)")
    p_shock.add_argument("--json", action="store_true", help="Output as JSON")

    # -- frost --
    p_frost = sub.add_parser("frost", help="Lateral frost protection comparison")
    p_frost.add_argument("--diameters", type=float, nargs="+", default=[4, 8, 12, 16],
                         help="Spread diameters in feet (default: 4 8 12 16)")
    p_frost.add_argument("--external-temp", type=float, default=-45.0, help="External temp C (default: -45)")
    p_frost.add_argument("--insulation-bonus", type=float, default=0.4, help="Insulation bonus (default: 0.4)")
    p_frost.add_argument("--json", action="store_true", help="Output as JSON")

    # -- all --
    p_all = sub.add_parser("all", help="Run all simulations with defaults")
    p_all.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    use_json = getattr(args, "json", False)

    if args.command == "daily":
        site = SiteParams(
            soil_ph=args.soil_ph,
            mean_temp_c=args.mean_temp,
            temp_amplitude_c=args.amplitude,
        )
        layer = StoneLayer("mulch", args.albedo, 0.005, 0.2, 0.001, 0.4)
        result = simulate_daily_cycle(site, layer)
        if use_json:
            print(json.dumps(result, indent=2))
        else:
            print("=== Daily Thermal/pH Cycle ===\n")
            _print_table(result["log"])
            print(f"\nFinal pH: {result['final_ph']:.3f}")
            print(f"Final moisture: {result['final_moisture']:.5f}")
            print(f"Total condensation: {result['total_condensation']:.5f} mm")

    elif args.command == "mineral":
        log = simulate_years(years=args.years, weather_severity=args.weather_severity)
        if use_json:
            print(json.dumps(log, indent=2))
        else:
            print("=== Multi-Year Mineral Decay ===\n")
            _print_table(log)

    elif args.command == "stress":
        log = simulate_stress_years(years=args.years, insulation_factor=args.insulation)
        if use_json:
            print(json.dumps(log, indent=2))
        else:
            print("=== Cumulative Stress / Recovery ===\n")
            _print_table(log)

    elif args.command == "shock":
        result = thermal_shock(
            root_temp=args.root_temp,
            ambient_temp=args.ambient,
            duration_hours=args.hours,
            insulation_factor=args.insulation,
        )
        if use_json:
            print(json.dumps(result, indent=2))
        else:
            print("=== Thermal Shock ===\n")
            print(f"Initial root temp: {result['initial_root_temp']} C")
            print(f"Ambient temp:      {result['ambient_temp']} C")
            print(f"Duration:          {result['duration_hours']} hours")
            print(f"Final root temp:   {result['final_root_temp']} C")
            print(f"Survived:          {'YES' if result['alive'] else 'NO'}")
            print(f"Hours survived:    {result['hours_survived']}")

    elif args.command == "frost":
        result = compare_spreads(args.diameters, args.external_temp, args.insulation_bonus)
        if use_json:
            print(json.dumps(result, indent=2))
        else:
            print("=== Lateral Frost Protection ===\n")
            _print_table(result)

    elif args.command == "all":
        site = SiteParams()
        layer = StoneLayer("mulch", 0.4, 0.005, 0.2, 0.001, 0.4)
        all_results = {
            "daily_cycle": simulate_daily_cycle(site, layer),
            "mineral_decay": simulate_years(),
            "stress": simulate_stress_years(),
            "shock": thermal_shock(site.root_temp_initial_c, -30.0, 48),
            "frost_comparison": compare_spreads([4, 8, 12, 16]),
        }
        if use_json:
            print(json.dumps(all_results, indent=2))
        else:
            print("=== Daily Cycle ===\n")
            _print_table(all_results["daily_cycle"]["log"])
            dc = all_results["daily_cycle"]
            print(f"\nFinal pH: {dc['final_ph']:.3f}  |  "
                  f"Moisture: {dc['final_moisture']:.5f}  |  "
                  f"Condensation: {dc['total_condensation']:.5f} mm\n")

            print("=== Mineral Decay ===\n")
            _print_table(all_results["mineral_decay"])
            print()

            print("=== Cumulative Stress ===\n")
            _print_table(all_results["stress"])
            print()

            shock = all_results["shock"]
            print("=== Thermal Shock ===\n")
            print(f"Root {shock['initial_root_temp']}C -> {shock['final_root_temp']}C "
                  f"at ambient {shock['ambient_temp']}C over {shock['hours_survived']}h  "
                  f"Survived: {'YES' if shock['alive'] else 'NO'}\n")

            print("=== Frost Protection ===\n")
            _print_table(all_results["frost_comparison"])


if __name__ == "__main__":
    main()


# ===========================================================================
# MODULE: Organizational Topology
# Source: scripts/organizational_topology.py
# ===========================================================================
"""
Organizational Topology Simulator
==================================

Compare organizational topologies under explicit constraint sets:
Hierarchy vs Distributed vs Embedded-Rule (bee-like).

No narrative -- just mechanics.

Models three canonical organizational topologies and measures convergence
speed, energy expenditure, perturbation resilience, and failure tolerance
under identical conditions.

Update rules
------------
- Hierarchy:      x_i(t+1) = x_i + alpha * (u_parent - x_i)
- Distributed:    x_i(t+1) = x_i + beta  * sum_neighbors(x_j - x_i)
- Embedded-rule:  x_i(t+1) = x_i + gamma * grad_F(x_i, target)

References
----------
- Watts, D.J. & Strogatz, S.H. (1998). Collective dynamics of
  'small-world' networks. Nature, 393(6684), 440-444.
- Camazine, S. et al. (2001). Self-Organization in Biological Systems.
  Princeton University Press.
- Prigogine, I. & Stengers, I. (1984). Order Out of Chaos.
  Bantam Books.
- Shannon, C.E. (1948). A Mathematical Theory of Communication.
  Bell System Technical Journal.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import argparse
import json
import math
import random


# ------------------
# Topology Types
# ------------------

class TopologyType(Enum):
    HIERARCHY = "hierarchy"
    DISTRIBUTED = "distributed"
    EMBEDDED_RULE = "embedded_rule"


# ------------------
# System Parameters
# ------------------

@dataclass
class SystemParams:
    """Parameters defining an organizational system."""
    name: str
    topology: TopologyType
    n_agents: int
    update_rate: float              # compliance/coupling rate (alpha, beta, or gamma)
    replacement_elasticity: float   # E_r: 0-1, how easily nodes swap without degradation
    constraint_density: float       # D_c: constraints per node
    externalization_capacity: float # S_e: 0-1, ability to push cost outside boundary
    connectivity: int = 4           # k: neighbors per node (distributed only)


# ------------------
# Simulation State
# ------------------

@dataclass
class SimState:
    """State of a running simulation."""
    positions: List[float]          # agent states x_i
    target: float                   # T
    time: int = 0
    energy_spent: float = 0.0
    history: List[float] = field(default_factory=list)  # E(t) over time


# ------------------
# Topology Simulation Engine
# ------------------

class TopologySimulator:
    """
    Simulate convergence, energy, and failure for different topologies.

    Update rules:
        Hierarchy:      x_i(t+1) = x_i + alpha * (u_parent - x_i)
        Distributed:    x_i(t+1) = x_i + beta  * sum_neighbors(x_j - x_i)
        Embedded-rule:  x_i(t+1) = x_i + gamma * grad_F(x_i, target)
    """

    def __init__(self, params: SystemParams, target: float = 0.0, seed: int = 42):
        self.params = params
        self.rng = random.Random(seed)
        self.state = SimState(
            positions=[self.rng.gauss(0, 1) for _ in range(params.n_agents)],
            target=target,
        )
        self._build_topology()

    def _build_topology(self):
        """Build adjacency structure based on topology type."""
        n = self.params.n_agents
        self.adjacency: Dict[int, List[int]] = {i: [] for i in range(n)}

        if self.params.topology == TopologyType.HIERARCHY:
            # Binary tree
            for i in range(n):
                parent = (i - 1) // 2 if i > 0 else None
                if parent is not None:
                    self.adjacency[i].append(parent)
                    self.adjacency[parent].append(i)

        elif self.params.topology == TopologyType.DISTRIBUTED:
            # Ring + random shortcuts
            k = self.params.connectivity
            for i in range(n):
                for j in range(1, k // 2 + 1):
                    neighbor = (i + j) % n
                    if neighbor not in self.adjacency[i]:
                        self.adjacency[i].append(neighbor)
                        self.adjacency[neighbor].append(i)

        elif self.params.topology == TopologyType.EMBEDDED_RULE:
            # No explicit adjacency -- each node uses local gradient
            pass

    def error(self) -> float:
        """Total squared error E(t) = sum(x_i - T)^2."""
        return sum((x - self.state.target) ** 2 for x in self.state.positions)

    def step(self):
        """One simulation step."""
        n = self.params.n_agents
        α = self.params.update_rate
        new_positions = list(self.state.positions)
        step_energy = 0.0

        if self.params.topology == TopologyType.HIERARCHY:
            # Top-down: node 0 is root, knows target
            # Information compresses at each level
            for i in range(n):
                if i == 0:
                    command = self.state.target
                else:
                    parent = (i - 1) // 2
                    # Parent's signal, with compression noise
                    depth = int(math.log2(i + 1))
                    noise = self.rng.gauss(0, 0.05 * depth)
                    command = self.state.positions[parent] + noise

                delta = α * (command - self.state.positions[i])
                new_positions[i] = self.state.positions[i] + delta
                step_energy += abs(delta)

        elif self.params.topology == TopologyType.DISTRIBUTED:
            for i in range(n):
                neighbors = self.adjacency[i]
                if not neighbors:
                    continue
                avg_neighbor = sum(self.state.positions[j] for j in neighbors) / len(neighbors)
                delta = α * (avg_neighbor - self.state.positions[i])
                new_positions[i] = self.state.positions[i] + delta
                step_energy += abs(delta)

        elif self.params.topology == TopologyType.EMBEDDED_RULE:
            # Each node independently moves toward target via local gradient
            for i in range(n):
                gradient = self.state.target - self.state.positions[i]
                delta = α * gradient
                new_positions[i] = self.state.positions[i] + delta
                step_energy += abs(delta)

        # Apply externalization: fraction of energy "exported" (not counted)
        visible_energy = step_energy * (1 - self.params.externalization_capacity)

        self.state.positions = new_positions
        self.state.time += 1
        self.state.energy_spent += visible_energy
        self.state.history.append(self.error())

    def perturb(self, fraction: float = 0.3, sigma: float = 2.0):
        """Randomly displace a fraction of agents."""
        n = self.params.n_agents
        count = max(1, int(n * fraction))
        indices = self.rng.sample(range(n), count)
        for i in indices:
            self.state.positions[i] += self.rng.gauss(0, sigma)

    def remove_nodes(self, fraction: float = 0.05):
        """Remove a fraction of nodes (simulate failure)."""
        n = len(self.state.positions)
        count = max(1, int(n * fraction))
        indices = sorted(self.rng.sample(range(n), count), reverse=True)
        for i in indices:
            self.state.positions.pop(i)
        self.params.n_agents = len(self.state.positions)
        self._build_topology()

    def run(self, steps: int = 100) -> Dict[str, Any]:
        """Run simulation and return results."""
        for _ in range(steps):
            self.step()

        return self.results()

    def results(self) -> Dict[str, Any]:
        """Current simulation results."""
        # Convergence: first time error drops below threshold
        threshold = 0.1 * self.params.n_agents
        convergence_time = None
        for t, e in enumerate(self.state.history):
            if e < threshold:
                convergence_time = t
                break

        return {
            "name": self.params.name,
            "topology": self.params.topology.value,
            "n_agents": self.params.n_agents,
            "final_error": self.error(),
            "convergence_time": convergence_time,
            "total_energy": self.state.energy_spent,
            "externalization": self.params.externalization_capacity,
            "steps_run": self.state.time,
            "error_history": self.state.history,
        }


# ------------------
# Comparative Analysis
# ------------------

def compare_topologies(
    n_agents: int = 64,
    steps: int = 100,
    externalization: float = 0.0,
    perturbation_at: Optional[int] = None,
    failure_at: Optional[int] = None,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """
    Run all three topologies under identical conditions and compare.

    Parameters
    ----------
    n_agents : int
        Number of agents in each topology.
    steps : int
        Number of simulation steps.
    externalization : float
        S_e for all systems (set to 0 for closed-loop comparison).
    perturbation_at : int, optional
        Step at which to inject perturbation.
    failure_at : int, optional
        Step at which to remove 5% of nodes.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    list of result dicts, one per topology
    """
    configs = [
        SystemParams("Hierarchy", TopologyType.HIERARCHY, n_agents, 0.5,
                      replacement_elasticity=0.9, constraint_density=0.6,
                      externalization_capacity=externalization),
        SystemParams("Distributed", TopologyType.DISTRIBUTED, n_agents, 0.3,
                      replacement_elasticity=0.7, constraint_density=0.3,
                      externalization_capacity=externalization, connectivity=4),
        SystemParams("Embedded-Rule", TopologyType.EMBEDDED_RULE, n_agents, 0.4,
                      replacement_elasticity=0.5, constraint_density=0.1,
                      externalization_capacity=externalization),
    ]

    results = []
    for cfg in configs:
        sim = TopologySimulator(cfg, target=0.0, seed=seed)
        for t in range(steps):
            if perturbation_at is not None and t == perturbation_at:
                sim.perturb()
            if failure_at is not None and t == failure_at:
                sim.remove_nodes()
            sim.step()
        results.append(sim.results())

    return results


def format_results_text(results: List[Dict[str, Any]]) -> str:
    """Format comparison results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("ORGANIZATIONAL TOPOLOGY COMPARISON")
    lines.append("=" * 70)

    for r in results:
        lines.append("")
        lines.append(f"--- {r['name']} ({r['topology']}) ---")
        lines.append(f"  Agents:            {r['n_agents']}")
        lines.append(f"  Steps run:         {r['steps_run']}")
        lines.append(f"  Final error:       {r['final_error']:.6f}")
        conv = r['convergence_time']
        lines.append(f"  Convergence time:  {conv if conv is not None else 'did not converge'}")
        lines.append(f"  Total energy:      {r['total_energy']:.4f}")
        lines.append(f"  Externalization:   {r['externalization']:.2f}")

    lines.append("")
    lines.append("=" * 70)

    # Summary comparison
    converged = [r for r in results if r['convergence_time'] is not None]
    if converged:
        fastest = min(converged, key=lambda r: r['convergence_time'])
        lines.append(f"Fastest convergence: {fastest['name']} at step {fastest['convergence_time']}")

    lowest_energy = min(results, key=lambda r: r['total_energy'])
    lines.append(f"Lowest energy:       {lowest_energy['name']} ({lowest_energy['total_energy']:.4f})")

    lowest_error = min(results, key=lambda r: r['final_error'])
    lines.append(f"Lowest final error:  {lowest_error['name']} ({lowest_error['final_error']:.6f})")

    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare organizational topologies (Hierarchy, Distributed, "
                    "Embedded-Rule) under identical constraints. Models convergence, "
                    "energy expenditure, perturbation resilience, and failure tolerance.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  %(prog)s --compare
  %(prog)s --agents 128 --steps 200
  %(prog)s --perturbation-at 50 --failure-at 75
  %(prog)s --externalization 0.3 --json
""",
    )

    parser.add_argument(
        "--compare", action="store_true", default=True,
        help="Run comparative analysis of all three topologies (default behavior)",
    )
    parser.add_argument(
        "--agents", type=int, default=64,
        help="Number of agents per topology (default: 64)",
    )
    parser.add_argument(
        "--steps", type=int, default=100,
        help="Number of simulation steps (default: 100)",
    )
    parser.add_argument(
        "--externalization", type=float, default=0.0,
        help="Externalization capacity S_e for all systems, 0-1 (default: 0.0)",
    )
    parser.add_argument(
        "--perturbation-at", type=int, default=None,
        help="Step at which to inject perturbation (default: none)",
    )
    parser.add_argument(
        "--failure-at", type=int, default=None,
        help="Step at which to remove 5%% of nodes (default: none)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    results = compare_topologies(
        n_agents=args.agents,
        steps=args.steps,
        externalization=args.externalization,
        perturbation_at=args.perturbation_at,
        failure_at=args.failure_at,
        seed=args.seed,
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_results_text(results))


if __name__ == "__main__":
    main()
