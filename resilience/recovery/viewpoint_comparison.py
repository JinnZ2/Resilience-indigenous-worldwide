#!/usr/bin/env python3
"""
viewpoint_comparison.py — Ontological Viewpoint Comparison Framework

Purpose
-------
Maps and compares ontological viewpoints on any domain by analyzing what each
viewpoint sees, asks, assumes, and misses.  Computes pairwise gap analyses
including blind spots, unique observations, question gaps, and assumption
conflicts.  Useful for surfacing structural blind spots that arise when a
single epistemological lens is applied to a complex system.

Methodology
-----------
Each viewpoint is modelled as four sets: {sees}, {asks}, {assumes}, {misses}.
Gap analysis between two viewpoints A and B computes:

    blind_spots_A  =  A.misses  ∩  B.sees
    blind_spots_B  =  B.misses  ∩  A.sees
    shared_sees    =  A.sees    ∩  B.sees
    unique_to_X    =  X.sees    -  Y.sees
    question_gap   =  symmetric difference of asks

A multi-viewpoint matrix enumerates all unique pairs.

References
----------
- Kuhn, T. S. (1962). The Structure of Scientific Revolutions.
- Midgley, G. (2000). Systemic Intervention: Philosophy, Methodology, and
  Practice. Kluwer Academic.
- Checkland, P. (1981). Systems Thinking, Systems Practice. Wiley.

Usage
-----
    python3 scripts/viewpoint_comparison.py --demo
    python3 scripts/viewpoint_comparison.py --demo --json
    python3 scripts/viewpoint_comparison.py --help
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Viewpoint:
    """An ontological viewpoint -- what it sees, asks, assumes, and misses."""

    name: str
    sees: List[str]
    asks: List[str]
    assumes: List[str]
    misses: List[str]


def gap_analysis(a: Viewpoint, b: Viewpoint) -> Dict[str, Any]:
    """
    Compute the ontological gap between two viewpoints.

    Returns
    -------
    dict with:
        blind_spots_a : what A misses that B sees
        blind_spots_b : what B misses that A sees
        shared_sees   : intersection of what both see
        assumption_conflict : assumptions that contradict
        question_gap  : questions one asks that the other doesn't
    """
    set_a_sees = set(a.sees)
    set_b_sees = set(b.sees)
    set_a_misses = set(a.misses)
    set_b_misses = set(b.misses)
    set_a_asks = set(a.asks)
    set_b_asks = set(b.asks)

    return {
        "viewpoint_a": a.name,
        "viewpoint_b": b.name,
        "blind_spots_a": sorted(set_a_misses & set_b_sees),
        "blind_spots_b": sorted(set_b_misses & set_a_sees),
        "shared_sees": sorted(set_a_sees & set_b_sees),
        "unique_to_a": sorted(set_a_sees - set_b_sees),
        "unique_to_b": sorted(set_b_sees - set_a_sees),
        "questions_only_a_asks": sorted(set_a_asks - set_b_asks),
        "questions_only_b_asks": sorted(set_b_asks - set_a_asks),
        "a_misses_count": len(a.misses),
        "b_misses_count": len(b.misses),
        "gap_ratio": len(a.misses) / max(1, len(b.misses)),
    }


def multi_viewpoint_matrix(
    viewpoints: List[Viewpoint],
) -> Dict[str, Dict[str, Any]]:
    """
    Compare all pairs of viewpoints.

    Returns
    -------
    dict keyed by "A_vs_B" -> gap_analysis result
    """
    results = {}
    for i, a in enumerate(viewpoints):
        for b in viewpoints[i + 1 :]:
            key = f"{a.name}_vs_{b.name}"
            results[key] = gap_analysis(a, b)
    return results


def build_demo_viewpoints() -> List[Viewpoint]:
    """Build a set of demo viewpoints illustrating institutional inversion."""
    physics = Viewpoint(
        name="Physics/Thermodynamics",
        sees=[
            "energy flow constraints",
            "entropy production",
            "dissipative structures",
            "feedback loops",
            "conservation laws",
        ],
        asks=[
            "Does energy flow freely?",
            "Are feedback loops intact?",
            "Is entropy being exported or accumulated?",
        ],
        assumes=[
            "systems obey conservation laws",
            "closed systems tend toward equilibrium",
        ],
        misses=[
            "subjective experience",
            "cultural meaning",
            "political power dynamics",
        ],
    )

    institutional = Viewpoint(
        name="Institutional/Bureaucratic",
        sees=[
            "compliance metrics",
            "hierarchical authority",
            "policy adherence",
            "political power dynamics",
        ],
        asks=[
            "Is the process being followed?",
            "Who has authority?",
            "Are metrics being met?",
        ],
        assumes=[
            "hierarchy ensures order",
            "metrics reflect reality",
            "compliance equals safety",
        ],
        misses=[
            "energy flow constraints",
            "entropy production",
            "feedback loops",
            "emergent behaviour",
            "lived experience of participants",
        ],
    )

    biological = Viewpoint(
        name="Biology/Evolution",
        sees=[
            "adaptive capacity",
            "feedback loops",
            "emergent behaviour",
            "survival mechanisms",
            "symbiosis",
        ],
        asks=[
            "Does this support survival?",
            "Are adaptive mechanisms intact?",
            "What are the selection pressures?",
        ],
        assumes=[
            "organisms evolve under selection pressure",
            "diversity increases resilience",
        ],
        misses=[
            "institutional incentive structures",
            "political power dynamics",
            "cultural meaning",
        ],
    )

    return [physics, institutional, biological]


def format_gap_human(key: str, gap: Dict[str, Any]) -> str:
    """Format a single gap analysis result for human-readable output."""
    lines = []
    lines.append(f"=== {gap['viewpoint_a']}  vs  {gap['viewpoint_b']} ===")
    lines.append("")

    lines.append(f"  Blind spots of {gap['viewpoint_a']}  (misses what B sees):")
    if gap["blind_spots_a"]:
        for item in gap["blind_spots_a"]:
            lines.append(f"    - {item}")
    else:
        lines.append("    (none)")

    lines.append(f"  Blind spots of {gap['viewpoint_b']}  (misses what A sees):")
    if gap["blind_spots_b"]:
        for item in gap["blind_spots_b"]:
            lines.append(f"    - {item}")
    else:
        lines.append("    (none)")

    lines.append(f"  Shared observations:")
    if gap["shared_sees"]:
        for item in gap["shared_sees"]:
            lines.append(f"    - {item}")
    else:
        lines.append("    (none)")

    lines.append(f"  Unique to {gap['viewpoint_a']}:")
    for item in gap.get("unique_to_a", []):
        lines.append(f"    - {item}")

    lines.append(f"  Unique to {gap['viewpoint_b']}:")
    for item in gap.get("unique_to_b", []):
        lines.append(f"    - {item}")

    lines.append(f"  Questions only {gap['viewpoint_a']} asks:")
    for item in gap.get("questions_only_a_asks", []):
        lines.append(f"    - {item}")

    lines.append(f"  Questions only {gap['viewpoint_b']} asks:")
    for item in gap.get("questions_only_b_asks", []):
        lines.append(f"    - {item}")

    lines.append(
        f"  Gap ratio (A misses / B misses): {gap['gap_ratio']:.2f}  "
        f"({gap['a_misses_count']} / {gap['b_misses_count']})"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Ontological Viewpoint Comparison Framework — map and compare "
            "what different viewpoints see, ask, assume, and miss."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a demonstration comparing Physics, Institutional, and Biology viewpoints",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON instead of human-readable text",
    )
    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        print(
            "\nUse --demo to run a built-in demonstration of viewpoint comparison.",
            file=sys.stderr,
        )
        sys.exit(0)

    viewpoints = build_demo_viewpoints()
    matrix = multi_viewpoint_matrix(viewpoints)

    if args.json_output:
        print(json.dumps(matrix, indent=2))
    else:
        print("Ontological Viewpoint Comparison — Demo")
        print("=" * 42)
        print()
        for key, gap in matrix.items():
            print(format_gap_human(key, gap))


if __name__ == "__main__":
    main()
