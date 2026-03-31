#!/usr/bin/env python3
"""
energy_wisdom_explorer.py — Curiosity-Driven Energy System Exploration

Weaves heterogeneous energy practices into novel integrated configurations,
detects synergies between practices using pluggable rules, and scores the
resulting systems on EROI, scalability, novelty, and domain coverage.

Concepts & References
---------------------
- Energy Return On Investment (EROI):
    Hall, C.A.S., Lambert, J.G., & Balogh, S.B. (2014).
    "EROI of different fuels and the implications for society."
    Energy Policy, 64, 141-152.
- Synergy detection via combinatorial rule matching follows a simple
  pairwise enumeration (itertools.combinations) with predicate filters.
- Geometric-mean scalability aggregation prevents a single low-scalability
  practice from being masked by arithmetic averaging.
- Novelty is measured as the ratio of distinct energy origins to total
  practice count, rewarding cross-domain integration.

Usage
-----
    python3 scripts/energy_wisdom_explorer.py --demo
    python3 scripts/energy_wisdom_explorer.py --demo --json
    python3 scripts/energy_wisdom_explorer.py --help
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from enum import Enum
from collections import defaultdict
import argparse
import itertools
import json
import math
import sys

# ------------------
# Energy Practice Classification
# ------------------


class EnergyOrigin(Enum):
    """Origin classification for energy practices."""
    PIEZOELECTRIC = "piezoelectric"
    THERMAL_MASS = "thermal_mass"
    CONCENTRATED_SOLAR = "concentrated_solar"
    THERMOELECTRIC = "thermoelectric"
    BIOENERGY = "bioenergy"
    WIND_PASSIVE = "wind_passive"
    MAGNETIC = "magnetic"
    RADIANT = "radiant"
    GEOTHERMAL = "geothermal"
    PHOTOVOLTAIC = "photovoltaic"
    BIOMIMETIC = "biomimetic"
    VERNACULAR = "vernacular"


class EnergyDomain(Enum):
    """Domains of energy application."""
    GENERATION = "generation"
    STORAGE = "storage"
    TRANSMISSION = "transmission"
    EFFICIENCY = "efficiency"
    HEAT_MANAGEMENT = "heat_management"
    MATERIALS = "materials"
    MANUFACTURING = "manufacturing"
    RECLAMATION = "reclamation"


# ------------------
# Energy Practice
# ------------------


@dataclass
class EnergyPractice:
    """An energy practice with measurable parameters."""
    name: str
    origin: EnergyOrigin
    domains: List[EnergyDomain]
    description: str
    mechanism: str
    parameters: Dict[str, float]
    dependencies: List[str]
    materials: List[str]
    energy_return_on_investment: float    # EROI
    scalability: float                    # 0-1
    environment_fit: Dict[str, float] = field(default_factory=dict)
    # environment_fit: tag -> 0-1 suitability (e.g. "arid": 0.9)


# ------------------
# Practice Library
# ------------------


class PracticeLibrary:
    """
    Registry of energy practices.
    Populate via register(); no hardcoded entries.
    """

    def __init__(self):
        self.practices: Dict[str, EnergyPractice] = {}

    def register(self, practice: EnergyPractice):
        self.practices[practice.name] = practice

    def by_origin(self, origin: EnergyOrigin) -> List[EnergyPractice]:
        return [p for p in self.practices.values() if p.origin == origin]

    def by_domain(self, domain: EnergyDomain) -> List[EnergyPractice]:
        return [p for p in self.practices.values() if domain in p.domains]

    def by_environment(self, tag: str, threshold: float = 0.5) -> List[EnergyPractice]:
        """Practices suitable for a given environment tag above threshold."""
        return [
            p for p in self.practices.values()
            if p.environment_fit.get(tag, 0) >= threshold
        ]

    def by_material(self, material: str) -> List[EnergyPractice]:
        return [p for p in self.practices.values() if material in p.materials]


# ------------------
# Synergy Rule Engine
# ------------------


@dataclass
class SynergyRule:
    """A rule that detects synergy between two practices."""
    name: str
    match_a: Callable[[EnergyPractice], bool]
    match_b: Callable[[EnergyPractice], bool]
    description: str
    bonus: float = 0.1  # EROI multiplier bonus


class SynergyEngine:
    """Detects synergies between practices using pluggable rules."""

    def __init__(self):
        self.rules: List[SynergyRule] = []

    def add_rule(self, rule: SynergyRule):
        self.rules.append(rule)

    def detect(
        self, practices: List[EnergyPractice]
    ) -> List[Dict[str, Any]]:
        """Find all synergies among a set of practices."""
        found = []
        for p1, p2 in itertools.combinations(practices, 2):
            for rule in self.rules:
                if (rule.match_a(p1) and rule.match_b(p2)) or \
                   (rule.match_a(p2) and rule.match_b(p1)):
                    found.append({
                        "rule": rule.name,
                        "practices": [p1.name, p2.name],
                        "description": rule.description,
                        "bonus": rule.bonus
                    })
        return found


# ------------------
# Energy System Weaver
# ------------------


class EnergyWeaver:
    """Weaves energy practices into integrated systems."""

    def __init__(
        self,
        library: PracticeLibrary,
        synergy_engine: Optional[SynergyEngine] = None
    ):
        self.library = library
        self.synergy_engine = synergy_engine or SynergyEngine()
        self.weavings: List[Dict[str, Any]] = []

    def weave(
        self,
        practices: List[EnergyPractice],
        name: str
    ) -> Dict[str, Any]:
        """
        Weave practices into an integrated energy system.

        Returns
        -------
        dict with combined metrics, synergies, material list, domain coverage.
        """
        all_domains: Set[EnergyDomain] = set()
        all_materials: Set[str] = set()
        all_origins: Set[str] = set()

        for p in practices:
            all_domains.update(p.domains)
            all_materials.update(p.materials)
            all_origins.add(p.origin.value)

        # Synergy detection
        synergies = self.synergy_engine.detect(practices)
        synergy_bonus = sum(s["bonus"] for s in synergies)

        # Combined EROI (average + synergy)
        base_eroi = sum(p.energy_return_on_investment for p in practices) / len(practices)
        combined_eroi = base_eroi * (1 + synergy_bonus)

        # Environment fit (intersection across all practices)
        env_tags: Set[str] = set()
        for p in practices:
            env_tags.update(p.environment_fit.keys())
        env_scores = {}
        for tag in env_tags:
            scores = [p.environment_fit.get(tag, 0) for p in practices]
            env_scores[tag] = sum(scores) / len(scores)

        # Scalability (geometric mean)
        scalabilities = [p.scalability for p in practices if p.scalability > 0]
        combined_scalability = (
            math.prod(scalabilities) ** (1 / len(scalabilities))
            if scalabilities else 0
        )

        # Novelty: how many distinct origins
        novelty = len(all_origins) / max(1, len(practices))

        weaving = {
            "name": name,
            "practices": [p.name for p in practices],
            "origins": sorted(all_origins),
            "domains": sorted(d.value for d in all_domains),
            "materials": sorted(all_materials),
            "synergies": synergies,
            "combined_eroi": combined_eroi,
            "combined_scalability": combined_scalability,
            "environment_fit": env_scores,
            "novelty_score": novelty,
            "practice_count": len(practices),
            "domain_coverage": len(all_domains) / len(EnergyDomain),
        }

        self.weavings.append(weaving)
        return weaving

    def weave_by_environment(
        self,
        tag: str,
        name: str,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Auto-select practices suited to an environment and weave them."""
        suited = self.library.by_environment(tag, threshold)
        if not suited:
            return {"name": name, "error": f"No practices found for '{tag}' >= {threshold}"}
        return self.weave(suited, name)

    def weave_by_domain(
        self,
        domain: EnergyDomain,
        name: str
    ) -> Dict[str, Any]:
        """Auto-select practices covering a domain and weave them."""
        matching = self.library.by_domain(domain)
        if not matching:
            return {"name": name, "error": f"No practices found for domain '{domain.value}'"}
        return self.weave(matching, name)

    def compare_weavings(self) -> List[Dict[str, Any]]:
        """Compare all weavings on key metrics."""
        return [
            {
                "name": w["name"],
                "eroi": w.get("combined_eroi", 0),
                "scalability": w.get("combined_scalability", 0),
                "novelty": w.get("novelty_score", 0),
                "domain_coverage": w.get("domain_coverage", 0),
                "synergy_count": len(w.get("synergies", [])),
            }
            for w in self.weavings
        ]


# ------------------
# Demo / CLI
# ------------------


def _build_demo_library() -> PracticeLibrary:
    """Build a small demonstration library of energy practices."""
    lib = PracticeLibrary()

    lib.register(EnergyPractice(
        name="Piezo Floor Tiles",
        origin=EnergyOrigin.PIEZOELECTRIC,
        domains=[EnergyDomain.GENERATION, EnergyDomain.RECLAMATION],
        description="Harvest kinetic energy from foot traffic via piezoelectric tiles.",
        mechanism="Mechanical stress on PZT ceramics generates charge separation.",
        parameters={"watts_per_step": 0.005, "tile_area_m2": 0.25},
        dependencies=["foot_traffic"],
        materials=["PZT ceramic", "copper electrode", "polymer substrate"],
        energy_return_on_investment=1.8,
        scalability=0.6,
        environment_fit={"urban": 0.9, "transit_hub": 0.95, "rural": 0.1},
    ))

    lib.register(EnergyPractice(
        name="Thermal Mass Wall",
        origin=EnergyOrigin.THERMAL_MASS,
        domains=[EnergyDomain.STORAGE, EnergyDomain.HEAT_MANAGEMENT, EnergyDomain.EFFICIENCY],
        description="Dense wall absorbs daytime heat, radiates at night — passive HVAC.",
        mechanism="High specific-heat material stores enthalpy across diurnal cycle.",
        parameters={"heat_capacity_kJ_per_K": 850, "wall_thickness_m": 0.4},
        dependencies=["diurnal_temperature_swing"],
        materials=["rammed earth", "adobe", "concrete"],
        energy_return_on_investment=5.2,
        scalability=0.8,
        environment_fit={"arid": 0.95, "desert": 0.9, "tropical": 0.3, "urban": 0.5},
    ))

    lib.register(EnergyPractice(
        name="Rooftop CSP Stirling",
        origin=EnergyOrigin.CONCENTRATED_SOLAR,
        domains=[EnergyDomain.GENERATION],
        description="Parabolic dish concentrates sunlight onto a Stirling engine.",
        mechanism="Concentrated thermal energy drives a closed-cycle Stirling engine.",
        parameters={"concentration_ratio": 600, "engine_efficiency": 0.30},
        dependencies=["direct_normal_irradiance"],
        materials=["mirrored glass", "steel frame", "Stirling engine"],
        energy_return_on_investment=9.0,
        scalability=0.5,
        environment_fit={"arid": 0.9, "desert": 0.95, "tropical": 0.4, "urban": 0.3},
    ))

    lib.register(EnergyPractice(
        name="TEG Waste Heat Recovery",
        origin=EnergyOrigin.THERMOELECTRIC,
        domains=[EnergyDomain.GENERATION, EnergyDomain.RECLAMATION],
        description="Thermoelectric generators recover electricity from waste heat.",
        mechanism="Seebeck effect across bismuth-telluride junctions.",
        parameters={"delta_T_K": 150, "efficiency": 0.08},
        dependencies=["waste_heat_source"],
        materials=["bismuth telluride", "alumina substrate", "copper leads"],
        energy_return_on_investment=3.5,
        scalability=0.7,
        environment_fit={"industrial": 0.9, "urban": 0.6, "rural": 0.3},
    ))

    lib.register(EnergyPractice(
        name="Wind Catcher Tower",
        origin=EnergyOrigin.WIND_PASSIVE,
        domains=[EnergyDomain.EFFICIENCY, EnergyDomain.HEAT_MANAGEMENT],
        description="Vernacular wind tower cools buildings via passive airflow.",
        mechanism="Pressure differential and thermal buoyancy drive ventilation.",
        parameters={"airflow_m3_per_s": 2.5, "cooling_equiv_kW": 3.0},
        dependencies=["prevailing_wind"],
        materials=["mud brick", "timber", "plaster"],
        energy_return_on_investment=12.0,
        scalability=0.4,
        environment_fit={"arid": 0.95, "desert": 0.9, "urban": 0.4, "tropical": 0.5},
    ))

    return lib


def _build_demo_synergy_engine() -> SynergyEngine:
    """Build a synergy engine with a few demonstration rules."""
    engine = SynergyEngine()

    engine.add_rule(SynergyRule(
        name="Heat Cascade",
        match_a=lambda p: EnergyDomain.HEAT_MANAGEMENT in p.domains,
        match_b=lambda p: p.origin == EnergyOrigin.THERMOELECTRIC,
        description="Waste heat from thermal management feeds thermoelectric recovery.",
        bonus=0.15,
    ))

    engine.add_rule(SynergyRule(
        name="Solar-Thermal Duo",
        match_a=lambda p: p.origin == EnergyOrigin.CONCENTRATED_SOLAR,
        match_b=lambda p: p.origin == EnergyOrigin.THERMAL_MASS,
        description="CSP excess heat stored in thermal mass for night-time release.",
        bonus=0.12,
    ))

    engine.add_rule(SynergyRule(
        name="Passive Ventilation Boost",
        match_a=lambda p: p.origin == EnergyOrigin.WIND_PASSIVE,
        match_b=lambda p: EnergyDomain.EFFICIENCY in p.domains and p.origin != EnergyOrigin.WIND_PASSIVE,
        description="Passive wind cooling reduces active cooling load, improving net efficiency.",
        bonus=0.08,
    ))

    return engine


def _format_weaving(w: Dict[str, Any]) -> str:
    """Format a single weaving result for human-readable output."""
    lines = []
    lines.append(f"=== {w['name']} ===")
    if "error" in w:
        lines.append(f"  Error: {w['error']}")
        return "\n".join(lines)

    lines.append(f"  Practices ({w['practice_count']}): {', '.join(w['practices'])}")
    lines.append(f"  Origins:  {', '.join(w['origins'])}")
    lines.append(f"  Domains:  {', '.join(w['domains'])}")
    lines.append(f"  Materials: {', '.join(w['materials'])}")
    lines.append(f"  Combined EROI:        {w['combined_eroi']:.2f}")
    lines.append(f"  Combined Scalability: {w['combined_scalability']:.3f}")
    lines.append(f"  Novelty Score:        {w['novelty_score']:.2f}")
    lines.append(f"  Domain Coverage:      {w['domain_coverage']:.1%}")

    if w["synergies"]:
        lines.append(f"  Synergies ({len(w['synergies'])}):")
        for s in w["synergies"]:
            lines.append(f"    - {s['rule']}: {s['description']} (bonus +{s['bonus']:.0%})")

    if w["environment_fit"]:
        lines.append("  Environment Fit:")
        for tag, score in sorted(w["environment_fit"].items(), key=lambda x: -x[1]):
            lines.append(f"    {tag:20s} {score:.2f}")

    return "\n".join(lines)


def _format_comparison(comparisons: List[Dict[str, Any]]) -> str:
    """Format comparison table for human-readable output."""
    lines = []
    lines.append("\n--- Weaving Comparison ---")
    header = f"  {'Name':30s} {'EROI':>8s} {'Scale':>8s} {'Novelty':>8s} {'DomCov':>8s} {'Synergies':>9s}"
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))
    for c in comparisons:
        lines.append(
            f"  {c['name']:30s} {c['eroi']:8.2f} {c['scalability']:8.3f} "
            f"{c['novelty']:8.2f} {c['domain_coverage']:8.1%} {c['synergy_count']:>9d}"
        )
    return "\n".join(lines)


def run_demo(as_json: bool = False):
    """Run a demonstration weaving scenario."""
    lib = _build_demo_library()
    engine = _build_demo_synergy_engine()
    weaver = EnergyWeaver(lib, engine)

    # Weave all practices together
    all_practices = list(lib.practices.values())
    w_all = weaver.weave(all_practices, "Full Integration")

    # Weave by environment: arid
    w_arid = weaver.weave_by_environment("arid", "Arid Climate System")

    # Weave by domain: generation
    w_gen = weaver.weave_by_domain(EnergyDomain.GENERATION, "Generation Focus")

    comparisons = weaver.compare_weavings()

    if as_json:
        output = {
            "weavings": [w_all, w_arid, w_gen],
            "comparison": comparisons,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        for w in [w_all, w_arid, w_gen]:
            print(_format_weaving(w))
            print()
        print(_format_comparison(comparisons))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Curiosity-Driven Energy System Exploration — weave heterogeneous "
            "energy practices into novel integrated configurations, detect "
            "synergies, and score the resulting systems."
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a built-in demonstration with sample practices and synergy rules.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit output as JSON instead of human-readable text.",
    )

    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        print("\nPass --demo to run the built-in demonstration scenario.")
        sys.exit(0)

    run_demo(as_json=args.json)


if __name__ == "__main__":
    main()
