#!/usr/bin/env python3
"""
geometric_boo.py -- Geometric Base of Operations: Distributed Infrastructure Systems

Purpose
-------
Models distributed infrastructure as a geometric system where multiple
independent vectors (components) are coupled together so that no single
point of failure can cascade into total system collapse. Selects
infrastructure components based on environmental context, identifies
coupling relationships between them, and computes geometric integrity
metrics that quantify systemic resilience.

Core concepts:
  - BOOComponent: a modular infrastructure unit (solar panel, well, etc.)
    characterised by mass, volume, power, water output, cost, and lifespan.
  - CouplingRule: a named relationship that exists when a specific set of
    components are all present, representing synergistic interaction.
  - GeometricBOO: the design engine that selects components for a given
    context (available resources / conditions), discovers active couplings,
    and produces geometric metrics (coupling density, average coupling
    strength, geometric area, and overall integrity score).

Metrics
-------
  vectors            Number of selected components.
  couplings          Number of active coupling rules.
  coupling_density   Active couplings / maximum possible pairwise couplings.
  avg_coupling_strength  Mean strength across active couplings.
  geometric_area     vectors * density * avg_strength (synthetic area).
  integrity          min(1.0, geometric_area / 10), a normalised score.

References
----------
  - Meadows, D. (2008). Thinking in Systems: A Primer. Chelsea Green.
  - Ostrom, E. (1990). Governing the Commons. Cambridge University Press.
  - Prigogine, I. & Stengers, I. (1984). Order Out of Chaos. Bantam.
  - Newman, M. (2010). Networks: An Introduction. Oxford University Press.
"""

import argparse
import json
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ------------------
# BOO Component
# ------------------

@dataclass
class BOOComponent:
    """A modular infrastructure component."""
    name: str
    function: str
    mass_kg: float
    volume_m3: float
    power_w: float               # watts generated (negative = consumed)
    water_l_per_day: float       # liters/day produced
    cost_usd: float
    deployment_time_hours: float
    lifespan_years: float
    dependencies: List[str]      # what it needs to operate
    provides: List[str]          # what it outputs
    tags: Dict[str, str] = field(default_factory=dict)


# ------------------
# Coupling Rule
# ------------------

@dataclass
class CouplingRule:
    """Detects a coupling between two components."""
    name: str
    requires: List[str]           # component names that must all be present
    description: str
    strength: float = 0.7


# ------------------
# Component Library
# ------------------

class BOOComponentLibrary:
    """Registry of BOO components. Populate via register()."""

    def __init__(self):
        self.components: Dict[str, BOOComponent] = {}

    def register(self, component: BOOComponent):
        self.components[component.name] = component

    def by_provides(self, resource: str) -> List[BOOComponent]:
        return [c for c in self.components.values() if resource in c.provides]

    def by_dependency(self, dep: str) -> List[BOOComponent]:
        return [c for c in self.components.values() if dep in c.dependencies]

    def all(self) -> List[BOOComponent]:
        return list(self.components.values())


# ------------------
# Geometric BOO
# ------------------

class GeometricBOO:
    """
    Distributed, coupled infrastructure system.
    Selects components based on context, computes geometric metrics.
    """

    def __init__(
        self,
        library: BOOComponentLibrary,
        coupling_rules: Optional[List[CouplingRule]] = None,
        water_per_person_l: float = 15.0,
        power_per_person_w: float = 100.0,
    ):
        self.library = library
        self.coupling_rules = coupling_rules or []
        self.water_per_person_l = water_per_person_l
        self.power_per_person_w = power_per_person_w

    def requirements(self, population: int) -> Dict[str, float]:
        return {
            "population": population,
            "water_l_per_day": population * self.water_per_person_l,
            "power_w": population * self.power_per_person_w,
        }

    def select_components(
        self,
        context: Dict[str, Any],
        selector: Optional[Callable[[BOOComponent, Dict], bool]] = None,
    ) -> List[str]:
        """
        Select components suitable for context.

        Parameters
        ----------
        context : dict
            Available resources / conditions (e.g. sunlight, wind, groundwater).
        selector : callable, optional
            (component, context) -> bool. Defaults to dependency check.

        Returns
        -------
        list of component names
        """
        if selector is None:
            def selector(comp, ctx):
                return all(
                    ctx.get(dep, False)
                    for dep in comp.dependencies
                    if dep not in ("human_power", "gravity", "elevation_difference")
                )

        return [
            name for name, comp in self.library.components.items()
            if selector(comp, context)
        ]

    def identify_couplings(self, selected: List[str]) -> List[Dict[str, Any]]:
        """Find active coupling rules for selected components."""
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
        """Compute geometric integrity metrics."""
        n = len(selected)
        nc = len(couplings)
        max_c = n * (n - 1) / 2 if n > 1 else 1
        density = nc / max_c if max_c > 0 else 0
        avg_str = (
            sum(c.get("strength", 0) for c in couplings) / nc if nc > 0 else 0
        )
        area = n * density * avg_str
        integrity = min(1.0, area / 10)
        return {
            "vectors": n,
            "couplings": nc,
            "coupling_density": density,
            "avg_coupling_strength": avg_str,
            "geometric_area": area,
            "integrity": integrity,
        }

    def design(
        self,
        population: int,
        context: Dict[str, Any],
        selector: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Full system design.

        Returns
        -------
        dict with requirements, selected components, capacity, couplings, metrics.
        """
        reqs = self.requirements(population)
        selected = self.select_components(context, selector)
        couplings = self.identify_couplings(selected)

        total_power = sum(
            self.library.components[n].power_w
            for n in selected if n in self.library.components
        )
        total_water = sum(
            self.library.components[n].water_l_per_day
            for n in selected if n in self.library.components
        )

        multiplier = 1
        if total_power > 0:
            multiplier = max(multiplier, math.ceil(reqs["power_w"] / total_power))
        if total_water > 0:
            multiplier = max(multiplier, math.ceil(reqs["water_l_per_day"] / total_water))

        total_cost = sum(
            self.library.components[n].cost_usd
            for n in selected if n in self.library.components
        ) * multiplier

        deploy_time = max(
            (self.library.components[n].deployment_time_hours
             for n in selected if n in self.library.components),
            default=0,
        ) * multiplier

        metrics = self.geometric_metrics(selected, couplings)

        return {
            "requirements": reqs,
            "context": context,
            "selected_components": selected,
            "multiplier": multiplier,
            "total_power_w": total_power * multiplier,
            "total_water_l_per_day": total_water * multiplier,
            "total_cost_usd": total_cost,
            "deployment_time_hours": deploy_time,
            "couplings": couplings,
            "geometric_metrics": metrics,
        }


# ------------------
# Demo library
# ------------------

def _build_demo_library() -> Tuple[BOOComponentLibrary, List[CouplingRule]]:
    """Build a small demo library with sample components and coupling rules."""
    lib = BOOComponentLibrary()

    lib.register(BOOComponent(
        name="solar_panel_200w",
        function="electricity_generation",
        mass_kg=12.0, volume_m3=0.04, power_w=200.0,
        water_l_per_day=0.0, cost_usd=150.0,
        deployment_time_hours=2.0, lifespan_years=25.0,
        dependencies=["sunlight"],
        provides=["electricity"],
    ))
    lib.register(BOOComponent(
        name="hand_pump_well",
        function="water_extraction",
        mass_kg=45.0, volume_m3=0.1, power_w=0.0,
        water_l_per_day=2000.0, cost_usd=800.0,
        deployment_time_hours=24.0, lifespan_years=15.0,
        dependencies=["groundwater", "human_power"],
        provides=["water"],
    ))
    lib.register(BOOComponent(
        name="biosand_filter",
        function="water_purification",
        mass_kg=80.0, volume_m3=0.12, power_w=0.0,
        water_l_per_day=600.0, cost_usd=50.0,
        deployment_time_hours=4.0, lifespan_years=10.0,
        dependencies=["water", "gravity"],
        provides=["clean_water"],
    ))
    lib.register(BOOComponent(
        name="small_wind_turbine",
        function="electricity_generation",
        mass_kg=25.0, volume_m3=0.3, power_w=400.0,
        water_l_per_day=0.0, cost_usd=600.0,
        deployment_time_hours=8.0, lifespan_years=20.0,
        dependencies=["wind"],
        provides=["electricity"],
    ))
    lib.register(BOOComponent(
        name="gravity_fed_irrigation",
        function="food_production_support",
        mass_kg=5.0, volume_m3=0.02, power_w=0.0,
        water_l_per_day=0.0, cost_usd=30.0,
        deployment_time_hours=6.0, lifespan_years=10.0,
        dependencies=["water", "elevation_difference"],
        provides=["irrigation"],
    ))

    rules = [
        CouplingRule(
            name="solar_well",
            requires=["solar_panel_200w", "hand_pump_well"],
            description="Solar can power electric pump upgrade for well.",
            strength=0.8,
        ),
        CouplingRule(
            name="well_filter",
            requires=["hand_pump_well", "biosand_filter"],
            description="Well water feeds directly into biosand filter.",
            strength=0.9,
        ),
        CouplingRule(
            name="well_irrigation",
            requires=["hand_pump_well", "gravity_fed_irrigation"],
            description="Well output supplies gravity-fed irrigation.",
            strength=0.7,
        ),
        CouplingRule(
            name="solar_wind",
            requires=["solar_panel_200w", "small_wind_turbine"],
            description="Complementary generation — solar by day, wind by night.",
            strength=0.85,
        ),
    ]

    return lib, rules


# ------------------
# CLI
# ------------------

def _print_human(result: Dict[str, Any]) -> None:
    """Pretty-print a design result for humans."""
    reqs = result["requirements"]
    metrics = result["geometric_metrics"]

    print("=" * 60)
    print("  Geometric BOO -- System Design")
    print("=" * 60)

    print(f"\nPopulation       : {reqs['population']}")
    print(f"Water needed     : {reqs['water_l_per_day']:.0f} L/day")
    print(f"Power needed     : {reqs['power_w']:.0f} W")

    print(f"\nContext          : {result['context']}")
    print(f"Selected ({len(result['selected_components'])})     : "
          + ", ".join(result["selected_components"]))
    print(f"Unit multiplier  : {result['multiplier']}x")

    print(f"\nTotal power      : {result['total_power_w']:.0f} W")
    print(f"Total water      : {result['total_water_l_per_day']:.0f} L/day")
    print(f"Total cost       : ${result['total_cost_usd']:,.0f}")
    print(f"Deploy time      : {result['deployment_time_hours']:.1f} hours")

    print(f"\n--- Couplings ({len(result['couplings'])}) ---")
    for c in result["couplings"]:
        print(f"  [{c['strength']:.2f}] {' + '.join(c['components'])}")
        print(f"         {c['description']}")

    print(f"\n--- Geometric Metrics ---")
    print(f"  Vectors              : {metrics['vectors']}")
    print(f"  Couplings            : {metrics['couplings']}")
    print(f"  Coupling density     : {metrics['coupling_density']:.3f}")
    print(f"  Avg coupling strength: {metrics['avg_coupling_strength']:.3f}")
    print(f"  Geometric area       : {metrics['geometric_area']:.3f}")
    print(f"  Integrity            : {metrics['integrity']:.3f}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Geometric Base of Operations (BOO): model distributed "
            "infrastructure as coupled geometric vectors and compute "
            "resilience metrics."
        ),
    )
    parser.add_argument(
        "--population", type=int, default=50,
        help="Number of people the system must support (default: 50).",
    )
    parser.add_argument(
        "--context", type=str, nargs="*", default=None,
        help=(
            "Available resources as key=value pairs, e.g. "
            "sunlight=true wind=true groundwater=true. "
            "Values 'true'/'1'/'yes' are truthy; anything else is falsy. "
            "Default: sunlight, groundwater."
        ),
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Output results as JSON instead of human-readable text.",
    )
    args = parser.parse_args()

    # Parse context
    truthy = {"true", "1", "yes"}
    if args.context is not None:
        context: Dict[str, Any] = {}
        for pair in args.context:
            if "=" in pair:
                k, v = pair.split("=", 1)
                context[k] = v.lower() in truthy
            else:
                context[pair] = True
    else:
        context = {"sunlight": True, "groundwater": True}

    lib, rules = _build_demo_library()
    boo = GeometricBOO(library=lib, coupling_rules=rules)
    result = boo.design(population=args.population, context=context)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result)


if __name__ == "__main__":
    main()
