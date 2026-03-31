#!/usr/bin/env python3
"""Unified geometric framework for coupled systems analysis.

Models any coupled system (agriculture, energy, water, economics, etc.) as
a collection of vectors in an abstract health-space.  Each vector represents
a measurable dimension of system health; couplings capture interactions
between dimensions.  The polygon formed by active vector endpoints gives a
single geometric proxy for system integrity and resilience.

Key metrics
-----------
- **Coupling density** -- ratio of active couplings to the maximum possible.
- **Vector balance** -- evenness of magnitudes across active vectors.
- **Polygon area** -- shoelace-formula area of the vector-endpoint polygon,
  scaled by coupling synergy.  Larger area ≈ more integrated system.
- **Integrity** -- weighted composite of area ratio, balance, coupling
  density, and average coupling strength (0-1 scale).

References
----------
- Donella Meadows, *Thinking in Systems* (2008) -- leverage points and
  feedback structure in complex systems.
- Robert Ulanowicz, *A Third Window* (2009) -- quantitative ecology of
  network mutualism and ascendency.
- Shoelace formula for polygon area: Meister (1769), Gauss.

Usage
-----
    python3 scripts/unified_geometric_framework.py --demo
    python3 scripts/unified_geometric_framework.py --demo --json
"""

import argparse
import json
import math
import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict


# ------------------
# Core Geometric Structures
# ------------------

@dataclass
class Vector:
    """A dimension of system health."""
    name: str
    magnitude: float    # 0-1, current state
    direction: float    # degrees, angular position in system space
    domain: str = ""    # which system domain
    target: float = 1.0 # desired magnitude

    def component_in(self, other: 'Vector') -> float:
        angle_rad = math.radians(self.direction - other.direction)
        return self.magnitude * math.cos(angle_rad)

    def orthogonal_component(self, other: 'Vector') -> float:
        angle_rad = math.radians(self.direction - other.direction)
        return self.magnitude * math.sin(angle_rad)


@dataclass
class Coupling:
    """An interaction between two vectors."""
    v1: str
    v2: str
    strength: float     # 0-1
    mechanism: str = ""
    synergy: float = 1.0  # multiplicative effect (>1 = positive)


@dataclass
class GeometricSystem:
    """A system as geometry of coupled vectors."""
    name: str
    domain: str
    vectors: Dict[str, Vector]
    couplings: Dict[Tuple[str, str], Coupling]

    def active_vectors(self) -> List[Vector]:
        return [v for v in self.vectors.values() if v.magnitude > 0]

    def active_couplings(self) -> List[Coupling]:
        return [c for c in self.couplings.values() if c.strength > 0]

    def coupling_density(self) -> float:
        """Ratio of actual to possible couplings among active vectors."""
        n = len(self.active_vectors())
        if n < 2:
            return 0
        possible = n * (n - 1) / 2
        return len(self.active_couplings()) / possible

    def vector_balance(self) -> float:
        """How balanced magnitudes are (0-1). 1 = all equal."""
        active = [v.magnitude for v in self.active_vectors()]
        if not active:
            return 0
        avg = sum(active) / len(active)
        if avg == 0:
            return 0
        variance = sum(abs(m - avg) for m in active) / len(active)
        return max(0, 1 - variance / avg)

    def coupling_strength_avg(self) -> float:
        active = self.active_couplings()
        return sum(c.strength for c in active) / len(active) if active else 0

    def coupling_synergy_avg(self) -> float:
        active = self.active_couplings()
        return sum(c.synergy for c in active) / len(active) if active else 1.0

    def polygon_area(self) -> float:
        """
        Area of the polygon formed by vector endpoints.
        Larger → more integrated, more resilient.
        Scaled by coupling synergy.
        """
        active = sorted(self.active_vectors(), key=lambda v: v.direction)
        if len(active) < 3:
            return 0

        area = 0.0
        for i in range(len(active)):
            v1 = active[i]
            v2 = active[(i + 1) % len(active)]
            x1 = v1.magnitude * math.cos(math.radians(v1.direction))
            y1 = v1.magnitude * math.sin(math.radians(v1.direction))
            x2 = v2.magnitude * math.cos(math.radians(v2.direction))
            y2 = v2.magnitude * math.sin(math.radians(v2.direction))
            area += x1 * y2 - x2 * y1

        area = abs(area) / 2
        coupling_factor = 1 + (
            self.coupling_density()
            * self.coupling_strength_avg()
            * (self.coupling_synergy_avg() - 1)
        )
        return area * coupling_factor

    def integrity(self) -> float:
        """
        Geometric integrity (0-1).
        Combines area ratio, balance, and coupling density.
        """
        active = self.active_vectors()
        if not active:
            return 0

        n = len(active)
        max_area = (n * math.sin(2 * math.pi / n)) / 2 if n >= 3 else 1.0
        actual = self.polygon_area()
        area_ratio = min(1.0, actual / max_area) if max_area > 0 else 0

        return min(1.0, (
            area_ratio * 0.4
            + self.vector_balance() * 0.3
            + self.coupling_density() * 0.2
            + self.coupling_strength_avg() * 0.1
        ))

    def emergent_properties(self) -> List[str]:
        """Properties that emerge from the geometry."""
        props = []
        integrity = self.integrity()
        if integrity > 0.7:
            props.append("High resilience: system absorbs shocks")
        elif integrity > 0.4:
            props.append("Moderate resilience")
        else:
            props.append("Fragile: small perturbations may cascade")

        waste = 1 - self.coupling_density()
        if waste > 0.5:
            props.append(f"High uncoupled potential: {waste:.0%} of couplings unused")

        if self.coupling_synergy_avg() > 1.2:
            props.append("Strong synergy across couplings")

        dims = len(self.active_vectors())
        if dims > 6:
            props.append(f"High dimensionality: {dims} active vectors")
        elif dims < 3:
            props.append(f"Low dimensionality: {dims} vectors -- linear behavior")

        return props

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "domain": self.domain,
            "active_vectors": len(self.active_vectors()),
            "active_couplings": len(self.active_couplings()),
            "coupling_density": self.coupling_density(),
            "vector_balance": self.vector_balance(),
            "polygon_area": self.polygon_area(),
            "integrity": self.integrity(),
            "emergent": self.emergent_properties(),
        }


# ------------------
# Geometric Analyzer
# ------------------

class GeometricAnalyzer:
    """Analyze and compare geometric systems."""

    def __init__(self):
        self.systems: List[GeometricSystem] = []

    def add(self, system: GeometricSystem):
        self.systems.append(system)

    def compare(self) -> List[Dict[str, Any]]:
        return [s.summary() for s in self.systems]

    def rank_by(self, metric: str = "integrity") -> List[Dict[str, Any]]:
        summaries = self.compare()
        return sorted(summaries, key=lambda s: -s.get(metric, 0))


# ------------------
# Demo scenarios
# ------------------

def build_demo_systems() -> List[GeometricSystem]:
    """Build three contrasting demo systems for illustration."""

    # --- Scenario 1: Healthy coupled agriculture ---
    ag_vectors = {
        "soil":   Vector("soil",   0.85, 0,   "agriculture"),
        "water":  Vector("water",  0.80, 60,  "agriculture"),
        "bio":    Vector("bio",    0.75, 120, "agriculture"),
        "yield":  Vector("yield",  0.70, 180, "agriculture"),
        "labour": Vector("labour", 0.65, 240, "agriculture"),
        "market": Vector("market", 0.60, 300, "agriculture"),
    }
    ag_couplings = {
        ("soil", "water"):  Coupling("soil", "water",  0.8, "infiltration",   1.3),
        ("soil", "bio"):    Coupling("soil", "bio",    0.7, "microbiome",     1.4),
        ("water", "bio"):   Coupling("water", "bio",   0.6, "habitat",        1.2),
        ("bio", "yield"):   Coupling("bio", "yield",   0.7, "pollination",    1.3),
        ("yield", "market"):Coupling("yield", "market", 0.5, "supply",        1.1),
        ("labour", "yield"):Coupling("labour", "yield", 0.6, "stewardship",   1.2),
    }
    healthy_ag = GeometricSystem("Integrated Farm", "agriculture",
                                 ag_vectors, ag_couplings)

    # --- Scenario 2: Monoculture (decoupled, low diversity) ---
    mono_vectors = {
        "soil":   Vector("soil",   0.30, 0,   "agriculture"),
        "water":  Vector("water",  0.40, 60,  "agriculture"),
        "bio":    Vector("bio",    0.15, 120, "agriculture"),
        "yield":  Vector("yield",  0.90, 180, "agriculture"),
        "labour": Vector("labour", 0.20, 240, "agriculture"),
        "market": Vector("market", 0.85, 300, "agriculture"),
    }
    mono_couplings = {
        ("yield", "market"): Coupling("yield", "market", 0.9, "commodity", 1.0),
    }
    monoculture = GeometricSystem("Industrial Monoculture", "agriculture",
                                  mono_vectors, mono_couplings)

    # --- Scenario 3: Renewable energy micro-grid ---
    energy_vectors = {
        "solar":    Vector("solar",    0.70, 0,   "energy"),
        "wind":     Vector("wind",     0.60, 72,  "energy"),
        "storage":  Vector("storage",  0.50, 144, "energy"),
        "demand":   Vector("demand",   0.80, 216, "energy"),
        "grid":     Vector("grid",     0.65, 288, "energy"),
    }
    energy_couplings = {
        ("solar", "storage"):  Coupling("solar", "storage",  0.7, "charge",    1.2),
        ("wind", "storage"):   Coupling("wind", "storage",   0.6, "charge",    1.2),
        ("storage", "demand"): Coupling("storage", "demand", 0.8, "dispatch",  1.1),
        ("grid", "demand"):    Coupling("grid", "demand",    0.7, "balance",   1.0),
        ("solar", "wind"):     Coupling("solar", "wind",     0.4, "complement",1.3),
    }
    microgrid = GeometricSystem("Community Micro-grid", "energy",
                                energy_vectors, energy_couplings)

    return [healthy_ag, monoculture, microgrid]


def print_human_report(results: List[Dict[str, Any]]) -> None:
    """Pretty-print analysis results to stdout."""
    print("=" * 64)
    print("  UNIFIED GEOMETRIC FRAMEWORK -- System Comparison")
    print("=" * 64)

    for r in results:
        print(f"\n--- {r['name']} ({r['domain']}) ---")
        print(f"  Active vectors   : {r['active_vectors']}")
        print(f"  Active couplings : {r['active_couplings']}")
        print(f"  Coupling density : {r['coupling_density']:.3f}")
        print(f"  Vector balance   : {r['vector_balance']:.3f}")
        print(f"  Polygon area     : {r['polygon_area']:.4f}")
        print(f"  Integrity        : {r['integrity']:.3f}")
        print(f"  Emergent properties:")
        for prop in r["emergent"]:
            print(f"    - {prop}")

    print("\n" + "=" * 64)
    print("  Ranking by integrity (highest first)")
    print("=" * 64)
    ranked = sorted(results, key=lambda s: -s["integrity"])
    for i, r in enumerate(ranked, 1):
        print(f"  {i}. {r['name']:30s}  integrity = {r['integrity']:.3f}")
    print()


# ------------------
# CLI entry point
# ------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Unified geometric framework for coupled-system analysis.  "
            "Models systems as vector polygons with couplings and computes "
            "integrity, resilience, and emergent properties."
        ),
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Run three built-in demo scenarios (agriculture and energy).",
    )
    parser.add_argument(
        "--json", dest="use_json", action="store_true",
        help="Emit results as JSON instead of human-readable text.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.demo:
        # Default to demo when no other mode is available yet.
        args.demo = True

    systems = build_demo_systems()
    analyzer = GeometricAnalyzer()
    for s in systems:
        analyzer.add(s)

    results = analyzer.rank_by("integrity")

    if args.use_json:
        print(json.dumps(results, indent=2))
    else:
        print_human_report(results)


if __name__ == "__main__":
    main()
