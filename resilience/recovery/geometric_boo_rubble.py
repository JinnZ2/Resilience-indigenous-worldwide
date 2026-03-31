#!/usr/bin/env python3
"""
geometric_boo_rubble.py — Base of Operations (BOO) Designer from Salvaged Materials

Purpose
-------
Generic framework for designing a Base of Operations from salvaged or locally
available materials in post-disruption scenarios. Maintains registries of
recoverable materials and buildable components, then computes a system design
that meets population-level water and power targets. Identifies inter-component
couplings and reports geometric metrics (coupling density, average strength,
integrity score) that characterise system resilience.

Methodology
-----------
1. **Material registry** — each SalvagedMaterial carries availability (0-1),
   processing energy (kWh/kg), and safety metadata.
2. **Component registry** — each SalvageComponent specifies required materials,
   output capacity (watts, litres/day), build time, and difficulty.
3. **Feasibility filter** — components whose materials all exceed an availability
   threshold are selected.
4. **Coupling detection** — CouplingRules fire when their prerequisite components
   are all present, surfacing synergies.
5. **Geometric metrics** — coupling density = active_couplings / max_possible,
   geometric area = n * density * avg_strength, integrity = min(1, area/10).
6. **Scaling** — a multiplier is computed so aggregate output meets per-capita
   water and power targets for the given population.

References
----------
- Alexander, C. (1977). *A Pattern Language*. Oxford University Press.
- Meadows, D. H. (2008). *Thinking in Systems*. Chelsea Green.
- UN-Habitat (2023). Minimum standards for emergency shelter and settlement.
- Sphere Association (2018). *The Sphere Handbook*, Water & Sanitation chapter
  (15 L/person/day minimum).

Usage
-----
    python3 scripts/geometric_boo_rubble.py --help
    python3 scripts/geometric_boo_rubble.py --population 25
    python3 scripts/geometric_boo_rubble.py --population 50 --threshold 0.2 --json
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import argparse
import json
import math
import sys

# ------------------------------------------------------------------
# Salvaged Material
# ------------------------------------------------------------------

@dataclass
class SalvagedMaterial:
    """A material recoverable from the environment or debris."""
    name: str
    source: str
    properties: List[str]
    applications: List[str]
    availability: float          # 0-1, how common
    energy_to_process: float     # kWh/kg
    safety_concerns: List[str] = field(default_factory=list)

# ------------------------------------------------------------------
# Salvage Component
# ------------------------------------------------------------------

@dataclass
class SalvageComponent:
    """A system component built from salvaged materials."""
    name: str
    function: str
    materials: List[str]         # material names required
    tools: List[str]             # basic tools needed
    output_w: float              # watts (if power)
    output_l_per_day: float      # liters/day (if water)
    build_time_hours: float
    lifespan_years: float
    difficulty: float            # 1-5
    tags: Dict[str, str] = field(default_factory=dict)

# ------------------------------------------------------------------
# Coupling Rule
# ------------------------------------------------------------------

@dataclass
class CouplingRule:
    """Detects a coupling between two salvage components."""
    name: str
    requires: List[str]
    description: str
    strength: float = 0.7

# ------------------------------------------------------------------
# Material Library
# ------------------------------------------------------------------

class MaterialLibrary:
    """Registry of salvageable materials. Populate via register()."""

    def __init__(self):
        self.materials: Dict[str, SalvagedMaterial] = {}

    def register(self, material: SalvagedMaterial):
        self.materials[material.name] = material

    def available(self, threshold: float = 0.3) -> List[SalvagedMaterial]:
        return [m for m in self.materials.values() if m.availability >= threshold]

    def by_property(self, prop: str) -> List[SalvagedMaterial]:
        return [m for m in self.materials.values() if prop in m.properties]

# ------------------------------------------------------------------
# Component Library
# ------------------------------------------------------------------

class SalvageComponentLibrary:
    """Registry of components buildable from salvaged materials."""

    def __init__(self):
        self.components: Dict[str, SalvageComponent] = {}

    def register(self, component: SalvageComponent):
        self.components[component.name] = component

    def all(self) -> List[SalvageComponent]:
        return list(self.components.values())

    def by_function(self, function_keyword: str) -> List[SalvageComponent]:
        return [
            c for c in self.components.values()
            if function_keyword.lower() in c.function.lower()
        ]

# ------------------------------------------------------------------
# Salvage BOO Designer
# ------------------------------------------------------------------

class SalvageBOO:
    """
    Design a BOO from salvaged materials.
    Selects components based on material availability,
    identifies couplings, computes geometric metrics.
    """

    def __init__(
        self,
        material_library: MaterialLibrary,
        component_library: SalvageComponentLibrary,
        coupling_rules: Optional[List[CouplingRule]] = None,
        water_per_person_l: float = 15.0,
        power_per_person_w: float = 100.0,
    ):
        self.materials = material_library
        self.components = component_library
        self.coupling_rules = coupling_rules or []
        self.water_per_person_l = water_per_person_l
        self.power_per_person_w = power_per_person_w

    def feasible_components(
        self,
        available_materials: Dict[str, float],
        threshold: float = 0.3,
    ) -> List[str]:
        """
        Components whose required materials are all available above threshold.
        """
        feasible = []
        for name, comp in self.components.components.items():
            if all(
                available_materials.get(mat, 0) >= threshold
                for mat in comp.materials
            ):
                feasible.append(name)
        return feasible

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

    def design(
        self,
        population: int,
        available_materials: Dict[str, float],
        threshold: float = 0.3,
    ) -> Dict[str, Any]:
        """Full system design from available materials."""
        target_water = population * self.water_per_person_l
        target_power = population * self.power_per_person_w

        selected = self.feasible_components(available_materials, threshold)
        couplings = self.identify_couplings(selected)

        total_water = sum(
            self.components.components[n].output_l_per_day
            for n in selected if n in self.components.components
        )
        total_power = sum(
            self.components.components[n].output_w
            for n in selected if n in self.components.components
        )
        total_build = sum(
            self.components.components[n].build_time_hours
            for n in selected if n in self.components.components
        )

        multiplier = 1
        if total_water > 0:
            multiplier = max(multiplier, math.ceil(target_water / total_water))
        if total_power > 0:
            multiplier = max(multiplier, math.ceil(target_power / total_power))

        metrics = self.geometric_metrics(selected, couplings)

        all_mats = sorted(set(
            mat
            for n in selected if n in self.components.components
            for mat in self.components.components[n].materials
        ))

        return {
            "population": population,
            "target_water_l_day": target_water,
            "target_power_w": target_power,
            "selected_components": selected,
            "multiplier": multiplier,
            "total_water_l_day": total_water * multiplier,
            "total_power_w": total_power * multiplier,
            "total_build_time_hours": total_build * multiplier,
            "materials_used": all_mats,
            "couplings": couplings,
            "geometric_metrics": metrics,
        }


# ------------------------------------------------------------------
# Demo data — a small illustrative registry
# ------------------------------------------------------------------

def _build_demo_registries():
    """Populate material and component registries with example data."""
    mat_lib = MaterialLibrary()
    mat_lib.register(SalvagedMaterial(
        name="concrete_rubble",
        source="collapsed structures",
        properties=["thermal_mass", "aggregate"],
        applications=["foundation", "wall_fill"],
        availability=0.9,
        energy_to_process=0.5,
        safety_concerns=["dust_inhalation", "rebar_cuts"],
    ))
    mat_lib.register(SalvagedMaterial(
        name="sheet_metal",
        source="roofing, vehicles",
        properties=["waterproof", "reflective", "conductive"],
        applications=["roofing", "water_collection", "heat_exchange"],
        availability=0.7,
        energy_to_process=1.0,
        safety_concerns=["sharp_edges"],
    ))
    mat_lib.register(SalvagedMaterial(
        name="plastic_sheeting",
        source="packaging, tarps",
        properties=["waterproof", "flexible", "UV_degradable"],
        applications=["water_collection", "shelter", "solar_still"],
        availability=0.8,
        energy_to_process=0.2,
    ))
    mat_lib.register(SalvagedMaterial(
        name="copper_wire",
        source="electrical wiring",
        properties=["conductive", "malleable"],
        applications=["electrical", "binding"],
        availability=0.5,
        energy_to_process=0.8,
    ))
    mat_lib.register(SalvagedMaterial(
        name="glass",
        source="windows, bottles",
        properties=["transparent", "thermal_mass"],
        applications=["greenhouse", "solar_still", "insulation"],
        availability=0.6,
        energy_to_process=0.3,
        safety_concerns=["sharp_fragments"],
    ))

    comp_lib = SalvageComponentLibrary()
    comp_lib.register(SalvageComponent(
        name="solar_still",
        function="water purification via solar distillation",
        materials=["plastic_sheeting", "glass"],
        tools=["knife", "shovel"],
        output_w=0.0,
        output_l_per_day=3.0,
        build_time_hours=4.0,
        lifespan_years=1.0,
        difficulty=2.0,
    ))
    comp_lib.register(SalvageComponent(
        name="thermoelectric_generator",
        function="power generation from temperature differential",
        materials=["sheet_metal", "copper_wire"],
        tools=["pliers", "hammer"],
        output_w=15.0,
        output_l_per_day=0.0,
        build_time_hours=8.0,
        lifespan_years=3.0,
        difficulty=4.0,
    ))
    comp_lib.register(SalvageComponent(
        name="rainwater_collector",
        function="water collection from precipitation",
        materials=["sheet_metal", "plastic_sheeting"],
        tools=["knife", "pliers"],
        output_w=0.0,
        output_l_per_day=20.0,
        build_time_hours=6.0,
        lifespan_years=2.0,
        difficulty=2.0,
    ))
    comp_lib.register(SalvageComponent(
        name="thermal_shelter",
        function="shelter with passive thermal regulation",
        materials=["concrete_rubble", "sheet_metal", "plastic_sheeting"],
        tools=["shovel", "hammer"],
        output_w=0.0,
        output_l_per_day=0.0,
        build_time_hours=24.0,
        lifespan_years=5.0,
        difficulty=3.0,
    ))

    coupling_rules = [
        CouplingRule(
            name="still_shelter_thermal",
            requires=["solar_still", "thermal_shelter"],
            description="Shelter thermal mass boosts still efficiency at night",
            strength=0.8,
        ),
        CouplingRule(
            name="collector_still_cascade",
            requires=["rainwater_collector", "solar_still"],
            description="Rainwater pre-filters feed into solar still for purification",
            strength=0.9,
        ),
        CouplingRule(
            name="generator_shelter_waste_heat",
            requires=["thermoelectric_generator", "thermal_shelter"],
            description="Generator waste heat supplements shelter warming",
            strength=0.6,
        ),
    ]

    return mat_lib, comp_lib, coupling_rules


# ------------------------------------------------------------------
# Human-readable output
# ------------------------------------------------------------------

def _print_design(result: Dict[str, Any]) -> None:
    """Pretty-print a BOO design result."""
    print("=" * 60)
    print("  SALVAGE BOO DESIGN REPORT")
    print("=" * 60)
    print(f"  Population           : {result['population']}")
    print(f"  Target water (L/day) : {result['target_water_l_day']:.1f}")
    print(f"  Target power (W)     : {result['target_power_w']:.1f}")
    print("-" * 60)
    print("  Selected Components:")
    for comp in result["selected_components"]:
        print(f"    - {comp}")
    print(f"  Unit multiplier      : {result['multiplier']}")
    print(f"  Total water (L/day)  : {result['total_water_l_day']:.1f}")
    print(f"  Total power (W)      : {result['total_power_w']:.1f}")
    print(f"  Total build time (h) : {result['total_build_time_hours']:.1f}")
    print("-" * 60)
    print("  Materials Required:")
    for mat in result["materials_used"]:
        print(f"    - {mat}")
    print("-" * 60)
    print("  Couplings Detected:")
    if result["couplings"]:
        for c in result["couplings"]:
            comps = ", ".join(c["components"])
            print(f"    [{c['strength']:.2f}] {comps}")
            print(f"           {c['description']}")
    else:
        print("    (none)")
    print("-" * 60)
    gm = result["geometric_metrics"]
    print("  Geometric Metrics:")
    print(f"    Vectors (components)     : {gm['vectors']}")
    print(f"    Active couplings         : {gm['couplings']}")
    print(f"    Coupling density         : {gm['coupling_density']:.4f}")
    print(f"    Avg coupling strength    : {gm['avg_coupling_strength']:.4f}")
    print(f"    Geometric area           : {gm['geometric_area']:.4f}")
    print(f"    System integrity (0-1)   : {gm['integrity']:.4f}")
    print("=" * 60)


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Salvage BOO Designer — design a Base of Operations from "
            "salvaged/local materials for a given population. Reports "
            "feasible components, inter-component couplings, and "
            "geometric integrity metrics."
        ),
    )
    parser.add_argument(
        "--population", type=int, default=10,
        help="Number of people the BOO must support (default: 10)",
    )
    parser.add_argument(
        "--threshold", type=float, default=0.3,
        help="Minimum material availability to consider (0-1, default: 0.3)",
    )
    parser.add_argument(
        "--water-per-person", type=float, default=15.0,
        help="Water target per person in litres/day (default: 15.0)",
    )
    parser.add_argument(
        "--power-per-person", type=float, default=100.0,
        help="Power target per person in watts (default: 100.0)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output results as JSON instead of human-readable text",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    mat_lib, comp_lib, coupling_rules = _build_demo_registries()

    # Build availability dict from the material library
    available_materials = {
        name: mat.availability
        for name, mat in mat_lib.materials.items()
    }

    designer = SalvageBOO(
        material_library=mat_lib,
        component_library=comp_lib,
        coupling_rules=coupling_rules,
        water_per_person_l=args.water_per_person,
        power_per_person_w=args.power_per_person,
    )

    result = designer.design(
        population=args.population,
        available_materials=available_materials,
        threshold=args.threshold,
    )

    if args.json_output:
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        _print_design(result)


if __name__ == "__main__":
    main()
