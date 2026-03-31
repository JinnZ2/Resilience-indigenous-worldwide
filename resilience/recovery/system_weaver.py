#!/usr/bin/env python3
"""
system_weaver.py — Curiosity-Driven System Exploration Engine

Purpose
-------
Mix, match, and discover novel system configurations by treating complex
systems (water, energy, data, ecology, supply chains, etc.) as assemblies
of swappable components.  A stochastic search explores the combinatorial
space via mutation and recombination, scoring each configuration on a
composite efficiency metric that balances biodiversity, carbon impact,
dependency, cost externalization, and coupling synergy.

Methodology
-----------
- Components are typed (water, air, energy, …) and carry parameter vectors,
  dependency profiles, and cost structures (direct / hidden / externalized).
- Coupling synergy between component pairs is modulated by origin-class
  bonuses (components that share an origin cooperate more effectively).
- Composite efficiency is a weighted sum:
      0.3 × biodiversity + 0.2 × |carbon_impact|
    + 0.2 × (1 − dependency) + 0.2 × (1 − externalization)
    + 0.1 × coupling_synergy
- Exploration uses random generation, point mutation (component swap),
  and two-parent recombination (uniform crossover per component type).
- Emergent-property detection applies heuristic rules over origin
  distributions and dependency scores.

References
----------
- Holland, J. H. (1992). Adaptation in Natural and Artificial Systems.
  MIT Press.  (genetic algorithms, schema theory)
- Kauffman, S. A. (1993). The Origins of Order. Oxford University Press.
  (NK fitness landscapes, combinatorial search in complex systems)
- Prigogine, I. & Stengers, I. (1984). Order Out of Chaos.
  (dissipative structures, self-organization far from equilibrium)
- Ostrom, E. (2009). A General Framework for Analyzing Sustainability
  of Social-Ecological Systems. Science, 325(5939), 419-422.

Usage
-----
    python3 scripts/system_weaver.py --demo
    python3 scripts/system_weaver.py --demo --json
    python3 scripts/system_weaver.py --search --iterations 200
    python3 scripts/system_weaver.py --explore --iterations 50 --mutation-rate 0.5
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum
from collections import defaultdict
import argparse
import itertools
import json
import math
import random
import sys

# ------------------
# System Component Types
# ------------------


class ComponentType(Enum):
    """Swappable system component types."""
    WATER_SYSTEM = "water_system"
    AIR_SYSTEM = "air_system"
    DATA_SYSTEM = "data_system"
    GENETIC_SYSTEM = "genetic_system"
    ENERGY_SYSTEM = "energy_system"
    KNOWLEDGE_SYSTEM = "knowledge_system"
    SUPPLY_CHAIN = "supply_chain"
    REGULATORY_FRAMEWORK = "regulatory_framework"
    ECOLOGICAL_STRATEGY = "ecological_strategy"


@dataclass
class SystemComponent:
    """A swappable system component."""
    name: str
    type: ComponentType
    description: str
    parameters: Dict[str, float]
    dependencies: Dict[str, float]       # dependency_name -> intensity (0-1)
    cost_structure: Dict[str, float]     # direct, hidden, externalized
    emergent_properties: List[str] = field(default_factory=list)
    origin: str = ""                     # classification tag


@dataclass
class SystemConfiguration:
    """A complete system assembled from components."""
    name: str
    components: Dict[ComponentType, SystemComponent]
    coupling_strengths: Dict[Tuple[ComponentType, ComponentType], float]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    emergent_behaviors: List[str] = field(default_factory=list)

    def calculate_metrics(self, calculator: 'SystemCalculator') -> Dict[str, float]:
        self.performance_metrics = calculator.calculate(self)
        return self.performance_metrics

    def clone(self) -> 'SystemConfiguration':
        return SystemConfiguration(
            name=self.name + "_copy",
            components=dict(self.components),
            coupling_strengths=dict(self.coupling_strengths),
            performance_metrics=dict(self.performance_metrics),
            emergent_behaviors=list(self.emergent_behaviors)
        )


# ------------------
# Component Library
# ------------------


class ComponentLibrary:
    """
    Registry of swappable components.
    Populate via register() or load from external config.
    """

    def __init__(self):
        self.components: Dict[ComponentType, List[SystemComponent]] = defaultdict(list)

    def register(self, component: SystemComponent):
        """Add a component to the library."""
        self.components[component.type].append(component)

    def get_options(self, comp_type: ComponentType) -> List[SystemComponent]:
        return self.components.get(comp_type, [])

    def get_by_origin(self, origin: str) -> List[SystemComponent]:
        """All components with a given origin tag."""
        return [
            c for comps in self.components.values()
            for c in comps if c.origin == origin
        ]

    def types_with_options(self) -> List[ComponentType]:
        """Component types that have at least one option registered."""
        return [t for t, comps in self.components.items() if comps]


# ------------------
# System Calculator
# ------------------


class SystemCalculator:
    """Calculates system performance metrics from a configuration."""

    def __init__(self, coupling_origin_bonuses: Optional[Dict[str, float]] = None):
        """
        Parameters
        ----------
        coupling_origin_bonuses : dict, optional
            origin_tag -> coupling bonus multiplier.
            When two components share an origin, this bonus applies.
        """
        self.coupling_origin_bonuses = coupling_origin_bonuses or {}

    def calculate(self, config: SystemConfiguration) -> Dict[str, float]:
        metrics: Dict[str, float] = {}
        n = max(1, len(config.components))

        # Aggregate per-component parameters
        agg: Dict[str, float] = defaultdict(float)
        for comp in config.components.values():
            for key, val in comp.parameters.items():
                agg[key] += val
            agg["dependency_score"] += (
                sum(comp.dependencies.values()) / max(1, len(comp.dependencies))
            )
            agg["direct_cost"] += comp.cost_structure.get("direct", 0)
            agg["hidden_cost"] += comp.cost_structure.get("hidden", 0)

        # Normalize
        for key in list(agg):
            if key not in ("direct_cost", "hidden_cost"):
                agg[key] /= n

        metrics["dependency_score"] = agg["dependency_score"]
        metrics["total_cost"] = agg["direct_cost"]
        metrics["hidden_subsidy"] = agg["hidden_cost"]
        total = agg["direct_cost"] + agg["hidden_cost"]
        metrics["externalization_ratio"] = agg["hidden_cost"] / total if total > 0 else 0

        # Pass through averaged parameters
        for key in ("water_use", "carbon_impact", "biodiversity"):
            if key in agg:
                metrics[key] = agg[key]

        # Coupling synergy
        coupling_bonus = 0.0
        for (t1, t2), strength in config.coupling_strengths.items():
            if t1 in config.components and t2 in config.components:
                o1 = config.components[t1].origin
                o2 = config.components[t2].origin
                if o1 == o2 and o1 in self.coupling_origin_bonuses:
                    coupling_bonus += strength * self.coupling_origin_bonuses[o1]

        metrics["coupling_synergy"] = coupling_bonus

        # Composite efficiency
        bio = metrics.get("biodiversity", 0)
        carbon = abs(metrics.get("carbon_impact", 0))
        dep = metrics.get("dependency_score", 0)
        ext = metrics.get("externalization_ratio", 0)
        syn = metrics.get("coupling_synergy", 0)

        metrics["system_efficiency"] = (
            bio * 0.3 +
            carbon * 0.2 +
            (1 - dep) * 0.2 +
            (1 - ext) * 0.2 +
            syn * 0.1
        )
        return metrics


# ------------------
# Curiosity Explorer
# ------------------


class CuriosityExplorer:
    """Explores novel system combinations through mutation and recombination."""

    def __init__(self, library: ComponentLibrary, calculator: SystemCalculator):
        self.library = library
        self.calculator = calculator
        self.history: List[Dict] = []

    def generate_random(self, name: str = "random") -> SystemConfiguration:
        """Generate a random configuration from the library."""
        components = {}
        for comp_type in self.library.types_with_options():
            options = self.library.get_options(comp_type)
            if options:
                components[comp_type] = random.choice(options)

        coupling = {}
        active_types = list(components.keys())
        for t1, t2 in itertools.combinations(active_types, 2):
            coupling[(t1, t2)] = random.uniform(0, 1)

        return SystemConfiguration(name, components, coupling)

    def mutate(self, config: SystemConfiguration, rate: float = 0.3) -> SystemConfiguration:
        """Mutate a configuration by swapping components at given rate."""
        new = config.clone()
        for comp_type in list(new.components.keys()):
            if random.random() < rate:
                options = self.library.get_options(comp_type)
                current = new.components[comp_type]
                alts = [o for o in options if o.name != current.name]
                if alts:
                    new.components[comp_type] = random.choice(alts)
        return new

    def combine(
        self,
        a: SystemConfiguration,
        b: SystemConfiguration,
        name: str = "hybrid",
        selector: Optional[Callable[[SystemComponent, SystemComponent], SystemComponent]] = None
    ) -> SystemConfiguration:
        """
        Combine two configurations.

        Parameters
        ----------
        selector : callable, optional
            (comp_a, comp_b) -> chosen_component.
            Defaults to random choice.
        """
        if selector is None:
            selector = lambda c1, c2: random.choice([c1, c2])

        combined_components = {}
        all_types = set(a.components) | set(b.components)
        for t in all_types:
            ca = a.components.get(t)
            cb = b.components.get(t)
            if ca and cb:
                combined_components[t] = selector(ca, cb)
            elif ca:
                combined_components[t] = ca
            elif cb:
                combined_components[t] = cb

        coupling = {}
        active = list(combined_components.keys())
        for t1, t2 in itertools.combinations(active, 2):
            s1 = a.coupling_strengths.get((t1, t2), 0)
            s2 = b.coupling_strengths.get((t1, t2), 0)
            coupling[(t1, t2)] = (s1 + s2) / 2

        return SystemConfiguration(name, combined_components, coupling)

    def explore(
        self,
        base: SystemConfiguration,
        iterations: int = 100,
        mutation_rate: float = 0.4
    ) -> List[Tuple[SystemConfiguration, float]]:
        """
        Explore mutations around a base configuration.

        Returns
        -------
        list[(config, efficiency)] sorted best-first
        """
        results = []
        for i in range(iterations):
            candidate = self.mutate(base, rate=mutation_rate)
            metrics = candidate.calculate_metrics(self.calculator)
            eff = metrics.get("system_efficiency", 0)
            results.append((candidate, eff))
            self.history.append({
                "iteration": i,
                "efficiency": eff,
                "components": {t.value: c.name for t, c in candidate.components.items()}
            })
        results.sort(key=lambda x: -x[1])
        return results

    def search_optimal(self, iterations: int = 500, refine_rate: float = 0.3) -> SystemConfiguration:
        """
        Search for optimal configuration via random generation + refinement.

        Returns best configuration found.
        """
        best: Optional[SystemConfiguration] = None
        best_eff = -1.0

        for i in range(iterations):
            if best and random.random() < refine_rate:
                candidate = self.mutate(best)
            else:
                candidate = self.generate_random(f"search_{i}")

            metrics = candidate.calculate_metrics(self.calculator)
            eff = metrics.get("system_efficiency", 0)

            if eff > best_eff:
                best_eff = eff
                best = candidate
                candidate.name = f"optimal_e{best_eff:.3f}"

        return best

    def detect_emergent(
        self,
        config: SystemConfiguration,
        rules: Optional[List[Callable[[SystemConfiguration], Optional[str]]]] = None
    ) -> List[str]:
        """
        Detect emergent properties from component combinations.

        Parameters
        ----------
        rules : list[callable], optional
            Each rule takes a config and returns a description string or None.
            Defaults to built-in origin-counting heuristics.

        Returns
        -------
        list[str] -- emergent property descriptions
        """
        emergent = []

        if rules:
            for rule in rules:
                result = rule(config)
                if result:
                    emergent.append(result)
            return emergent

        # Default heuristics based on origin distribution
        origin_counts: Dict[str, int] = defaultdict(int)
        for comp in config.components.values():
            origin_counts[comp.origin] += 1

        n = len(config.components)
        if n == 0:
            return emergent

        # Dominant origin
        for origin, count in origin_counts.items():
            if count >= n * 0.75:
                emergent.append(f"Dominant-{origin} synergy: >=75% components share origin")

        # Multi-origin hybrid
        if len(origin_counts) >= 3:
            emergent.append("Multi-paradigm hybrid: components drawn from 3+ origin classes")

        # Low dependency across all components
        dep_scores = [
            sum(c.dependencies.values()) / max(1, len(c.dependencies))
            for c in config.components.values()
        ]
        if dep_scores and all(d < 0.3 for d in dep_scores):
            emergent.append("System sovereignty: all components have low external dependency")

        return emergent


# ------------------
# Demo Library Setup
# ------------------


def build_demo_library() -> ComponentLibrary:
    """Populate a component library with illustrative demo components."""
    lib = ComponentLibrary()

    # Water systems
    lib.register(SystemComponent(
        name="rainwater_harvest",
        type=ComponentType.WATER_SYSTEM,
        description="Decentralized rainwater collection and filtration",
        parameters={"water_use": 0.2, "carbon_impact": -0.1, "biodiversity": 0.6},
        dependencies={"rainfall": 0.7},
        cost_structure={"direct": 500, "hidden": 50},
        origin="ecological",
    ))
    lib.register(SystemComponent(
        name="centralized_treatment",
        type=ComponentType.WATER_SYSTEM,
        description="Municipal water treatment plant",
        parameters={"water_use": 0.8, "carbon_impact": 0.4, "biodiversity": 0.1},
        dependencies={"grid_power": 0.9, "chemical_supply": 0.7},
        cost_structure={"direct": 2000, "hidden": 800},
        origin="industrial",
    ))

    # Energy systems
    lib.register(SystemComponent(
        name="community_solar",
        type=ComponentType.ENERGY_SYSTEM,
        description="Distributed community-owned solar arrays",
        parameters={"water_use": 0.05, "carbon_impact": -0.3, "biodiversity": 0.4},
        dependencies={"sunlight": 0.8},
        cost_structure={"direct": 1200, "hidden": 100},
        origin="ecological",
    ))
    lib.register(SystemComponent(
        name="fossil_grid",
        type=ComponentType.ENERGY_SYSTEM,
        description="Centralized fossil fuel power grid",
        parameters={"water_use": 0.6, "carbon_impact": 0.9, "biodiversity": -0.2},
        dependencies={"fuel_import": 0.95, "grid_infra": 0.8},
        cost_structure={"direct": 800, "hidden": 3000},
        origin="industrial",
    ))

    # Knowledge systems
    lib.register(SystemComponent(
        name="open_knowledge_commons",
        type=ComponentType.KNOWLEDGE_SYSTEM,
        description="Distributed open-access knowledge sharing",
        parameters={"water_use": 0.0, "carbon_impact": -0.05, "biodiversity": 0.5},
        dependencies={"community_participation": 0.6},
        cost_structure={"direct": 100, "hidden": 10},
        origin="commons",
    ))
    lib.register(SystemComponent(
        name="proprietary_ip",
        type=ComponentType.KNOWLEDGE_SYSTEM,
        description="Patent-walled proprietary knowledge",
        parameters={"water_use": 0.0, "carbon_impact": 0.1, "biodiversity": -0.1},
        dependencies={"legal_enforcement": 0.9, "licensing_fees": 0.8},
        cost_structure={"direct": 3000, "hidden": 1500},
        origin="industrial",
    ))

    # Supply chains
    lib.register(SystemComponent(
        name="local_cooperative",
        type=ComponentType.SUPPLY_CHAIN,
        description="Regional cooperative supply network",
        parameters={"water_use": 0.1, "carbon_impact": -0.2, "biodiversity": 0.3},
        dependencies={"local_producers": 0.5},
        cost_structure={"direct": 600, "hidden": 50},
        origin="ecological",
    ))
    lib.register(SystemComponent(
        name="global_just_in_time",
        type=ComponentType.SUPPLY_CHAIN,
        description="Global JIT supply chain with single-source dependencies",
        parameters={"water_use": 0.3, "carbon_impact": 0.7, "biodiversity": -0.1},
        dependencies={"global_shipping": 0.95, "single_supplier": 0.85},
        cost_structure={"direct": 400, "hidden": 2000},
        origin="industrial",
    ))

    return lib


# ------------------
# Formatting Helpers
# ------------------


def format_config(config: SystemConfiguration, emergent: List[str]) -> str:
    """Format a system configuration for human-readable output."""
    lines = []
    lines.append(f"=== {config.name} ===")
    lines.append("Components:")
    for ctype, comp in sorted(config.components.items(), key=lambda x: x[0].value):
        lines.append(f"  [{ctype.value}] {comp.name} (origin: {comp.origin})")
    lines.append("Metrics:")
    for key, val in sorted(config.performance_metrics.items()):
        lines.append(f"  {key}: {val:.4f}")
    if emergent:
        lines.append("Emergent properties:")
        for prop in emergent:
            lines.append(f"  - {prop}")
    return "\n".join(lines)


def config_to_dict(config: SystemConfiguration, emergent: List[str]) -> Dict[str, Any]:
    """Serialize a system configuration to a JSON-compatible dict."""
    return {
        "name": config.name,
        "components": {
            ctype.value: {
                "name": comp.name,
                "origin": comp.origin,
                "description": comp.description,
            }
            for ctype, comp in config.components.items()
        },
        "metrics": config.performance_metrics,
        "emergent_properties": emergent,
    }


# ------------------
# CLI
# ------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="system_weaver",
        description=(
            "Curiosity-driven system exploration engine. "
            "Assembles, mutates, and recombines system configurations "
            "to discover high-efficiency designs."
        ),
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--demo",
        action="store_true",
        help="Run a short demo: random config, search, combine, and emergent detection",
    )
    mode.add_argument(
        "--search",
        action="store_true",
        help="Search for an optimal configuration from the demo library",
    )
    mode.add_argument(
        "--explore",
        action="store_true",
        help="Explore mutations around a random base configuration",
    )

    parser.add_argument(
        "--iterations", type=int, default=100,
        help="Number of iterations for search or explore (default: 100)",
    )
    parser.add_argument(
        "--mutation-rate", type=float, default=0.4,
        help="Mutation rate for explore mode (default: 0.4)",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # Default to --demo when no mode is specified
    if not (args.demo or args.search or args.explore):
        args.demo = True

    lib = build_demo_library()
    calc = SystemCalculator(coupling_origin_bonuses={
        "ecological": 0.3,
        "industrial": 0.1,
        "commons": 0.25,
    })
    explorer = CuriosityExplorer(lib, calc)

    output: Dict[str, Any] = {}

    if args.demo:
        # Random configuration
        rand_config = explorer.generate_random("demo_random")
        rand_config.calculate_metrics(calc)
        rand_emergent = explorer.detect_emergent(rand_config)

        # Search for optimal
        optimal = explorer.search_optimal(iterations=args.iterations)
        opt_emergent = explorer.detect_emergent(optimal)

        # Combine the two
        hybrid = explorer.combine(rand_config, optimal, name="demo_hybrid")
        hybrid.calculate_metrics(calc)
        hyb_emergent = explorer.detect_emergent(hybrid)

        if args.json:
            output = {
                "mode": "demo",
                "random": config_to_dict(rand_config, rand_emergent),
                "optimal": config_to_dict(optimal, opt_emergent),
                "hybrid": config_to_dict(hybrid, hyb_emergent),
            }
        else:
            print(format_config(rand_config, rand_emergent))
            print()
            print(format_config(optimal, opt_emergent))
            print()
            print(format_config(hybrid, hyb_emergent))

    elif args.search:
        optimal = explorer.search_optimal(iterations=args.iterations)
        emergent = explorer.detect_emergent(optimal)

        if args.json:
            output = {
                "mode": "search",
                "iterations": args.iterations,
                "best": config_to_dict(optimal, emergent),
            }
        else:
            print(f"Search complete ({args.iterations} iterations)")
            print()
            print(format_config(optimal, emergent))

    elif args.explore:
        base = explorer.generate_random("explore_base")
        base.calculate_metrics(calc)
        results = explorer.explore(base, iterations=args.iterations, mutation_rate=args.mutation_rate)

        top_n = min(5, len(results))
        top_results = results[:top_n]

        if args.json:
            output = {
                "mode": "explore",
                "iterations": args.iterations,
                "mutation_rate": args.mutation_rate,
                "base": config_to_dict(base, explorer.detect_emergent(base)),
                "top_results": [
                    {
                        "rank": i + 1,
                        "efficiency": eff,
                        "config": config_to_dict(cfg, explorer.detect_emergent(cfg)),
                    }
                    for i, (cfg, eff) in enumerate(top_results)
                ],
            }
        else:
            print(f"Exploration complete ({args.iterations} iterations, "
                  f"mutation_rate={args.mutation_rate})")
            print()
            print("Base configuration:")
            print(format_config(base, explorer.detect_emergent(base)))
            print()
            print(f"Top {top_n} results:")
            for i, (cfg, eff) in enumerate(top_results):
                print(f"\n--- Rank {i + 1} (efficiency: {eff:.4f}) ---")
                print(format_config(cfg, explorer.detect_emergent(cfg)))

    if args.json and output:
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
