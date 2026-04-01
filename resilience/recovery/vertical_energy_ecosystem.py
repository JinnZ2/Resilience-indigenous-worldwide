#!/usr/bin/env python3
"""
vertical_energy_ecosystem.py -- 3D city from bedrock to sky.

A living organism where energy flows like blood, information like nerves,
materials like nutrients.  Ten vertical layers from -1000 ft (bedrock
geothermal) to 2000+ ft (atmospheric harvesting), each coupled to
adjacent layers through physical interactions.

Vertical layers (biological analogy):
  Bedrock      (-1000 to -500 ft): Deep geothermal, iron formations
  Deep Root    (-500 to -100 ft):  Taproot conduits, pressure vessels
  Root Zone    (-100 to -20 ft):   Distribution tunnels, mycorrhizal net
  Rhizosphere  (-20 to 0 ft):     Foundation exchange, heat pumps
  Surface      (0 to 20 ft):      Metabolic center, pedestrian energy
  Understory   (20 to 80 ft):     Mid-rise collectors, vertical farms
  Canopy       (80 to 200 ft):    High-rise solar/wind, sky gardens
  Emergent     (200 to 500 ft):   Transmission towers, energy beaming
  Atmospheric  (500 to 2000 ft):  Kite turbines, air purification
  Stratospheric (2000+ ft):       Orbital interface, direct air capture

Energy flow patterns:
  - Helical circulation (DNA/tornado): spiraling up through taproots
  - Spherical zones (atomic orbitals): concentric energy shells
  - Fractal distribution (blood vessels): self-similar branching
  - Direct jumps (quantum tunneling): bypass intermediate layers

Biomimetic models:
  - Tree: xylem up (energy), phloem down (waste)
  - Body: heart (core node), arteries, capillaries, nerves, lymph
  - Forest: canopy capture, understory filter, root storage, mycelium
  - Beehive: hexagonal efficiency, phase-change walls
  - Coral reef: self-building, symbiotic, tidal-rhythmic

References
----------
- Yeang, K. (2006). Ecodesign: A Manual for Ecological Design. Wiley.
- Benyus, J. (1997). Biomimicry: Innovation Inspired by Nature. Morrow.
- Bejan, A. (2000). Shape and Structure, from Engineering to Nature.
  Cambridge. (constructal law)
- Odum, H. T. (1971). Environment, Power, and Society. Wiley.

Usage
-----
    python3 vertical_energy_ecosystem.py
    python3 vertical_energy_ecosystem.py --population 50000
    python3 vertical_energy_ecosystem.py --json
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------
# Vertical Layers
# ---------------------------

class Layer(Enum):
    BEDROCK = "bedrock"
    DEEP_ROOT = "deep_root"
    ROOT_ZONE = "root_zone"
    RHIZOSPHERE = "rhizosphere"
    SURFACE = "surface"
    UNDERSTORY = "understory"
    CANOPY = "canopy"
    EMERGENT = "emergent"
    ATMOSPHERIC = "atmospheric"
    STRATOSPHERIC = "stratospheric"


LAYER_DEPTHS = {
    Layer.BEDROCK:       (-1000, -500),
    Layer.DEEP_ROOT:     (-500, -100),
    Layer.ROOT_ZONE:     (-100, -20),
    Layer.RHIZOSPHERE:   (-20, 0),
    Layer.SURFACE:       (0, 20),
    Layer.UNDERSTORY:    (20, 80),
    Layer.CANOPY:        (80, 200),
    Layer.EMERGENT:      (200, 500),
    Layer.ATMOSPHERIC:   (500, 2000),
    Layer.STRATOSPHERIC: (2000, 100000),
}


# ---------------------------
# Layer Element
# ---------------------------

@dataclass
class LayerElement:
    """A physical element within a vertical layer."""
    name: str
    description: str
    power_mw: float = 0.0
    capacity_mwh: float = 0.0
    count: int = 1


# ---------------------------
# Layer Builder
# ---------------------------

def build_layer(layer: Layer, population: int) -> Dict[str, Any]:
    """Build a single vertical layer sized to population."""
    pop = population
    depths = LAYER_DEPTHS[layer]
    elements: List[Dict[str, Any]] = []

    if layer == Layer.BEDROCK:
        n_wells = max(4, pop // 1000)
        elements = [
            {"name": "geothermal_wells", "count": n_wells,
             "power_mw": 5.0 * n_wells, "depth_ft": 800,
             "description": "Deep wells tapping Earth's core heat"},
            {"name": "iron_formation_storage", "capacity_mwh": pop * 0.5,
             "description": "Iron-air batteries in natural iron deposits"},
            {"name": "magma_interface", "power_mw": pop * 0.005,
             "description": "Geothermal gradient base power"},
        ]

    elif layer == Layer.DEEP_ROOT:
        n_conduits = max(8, pop // 500)
        elements = [
            {"name": "taproot_conduits", "count": n_conduits,
             "capacity_mw": 20.0 * n_conduits,
             "description": "Major energy conduits like tree taproots"},
            {"name": "pressure_vessels", "count": n_conduits * 4,
             "capacity_mwh": pop * 0.01,
             "description": "Compressed air storage in rock chambers"},
            {"name": "mineral_extraction", "annual_tons": pop * 0.1,
             "description": "Mine energy minerals while extracting heat"},
        ]

    elif layer == Layer.ROOT_ZONE:
        n_buildings = pop // 50
        elements = [
            {"name": "distribution_tunnels", "length_miles": pop * 0.005,
             "capacity_mw": pop * 0.01,
             "description": "Underground energy highways in fractal pattern"},
            {"name": "building_connections", "count": n_buildings,
             "description": "Every building roots into the energy network"},
            {"name": "pumped_hydro_caverns", "capacity_mwh": pop * 0.2,
             "description": "Water pumped between caverns for storage"},
            {"name": "mycorrhizal_network", "length_miles": pop * 0.02,
             "description": "Triple-function conduits: power, data, heat"},
        ]

    elif layer == Layer.RHIZOSPHERE:
        n_buildings = pop // 50
        elements = [
            {"name": "energy_active_foundations", "count": n_buildings,
             "capacity_kw": 100 * n_buildings,
             "description": "Every foundation is an energy exchange node"},
            {"name": "ground_source_heat_pumps", "power_mw": pop * 0.002,
             "description": "Soil as thermal battery for all buildings"},
            {"name": "subsurface_cisterns", "capacity_m3": pop * 1.0,
             "description": "Rainwater harvesting and storage"},
            {"name": "waste_to_soil", "capacity_tons_day": pop * 0.0005,
             "description": "Human waste processed into soil nutrients"},
        ]

    elif layer == Layer.SURFACE:
        elements = [
            {"name": "piezoelectric_pavements", "power_kw": pop * 0.05,
             "description": "Footsteps generate power"},
            {"name": "green_infrastructure", "area_ha": pop * 0.0005,
             "description": "Living walls, bioswales, food production"},
            {"name": "market_hubs", "count": max(4, pop // 1000),
             "description": "Community energy exchange centers"},
            {"name": "water_features", "description":
             "Canals, fountains, ponds for cooling and storage"},
        ]

    elif layer == Layer.UNDERSTORY:
        n_buildings = pop // 100
        elements = [
            {"name": "mid_rise_buildings", "count": n_buildings,
             "description": "Buildings with integrated solar, wind, thermal"},
            {"name": "vertical_farms", "count": max(4, pop // 500),
             "food_tons_year": pop * 0.05,
             "description": "Aeroponic towers in filtered light"},
            {"name": "energy_bridges", "length_miles": pop * 0.001,
             "description": "Horizontal energy sharing at mid-level"},
        ]

    elif layer == Layer.CANOPY:
        n_towers = pop // 500
        elements = [
            {"name": "high_rise_towers", "count": n_towers,
             "solar_mw": 0.5 * n_towers, "wind_mw": 0.2 * n_towers,
             "description": "Towers optimized for energy capture"},
            {"name": "solar_canopy", "area_m2": pop * 5,
             "power_mw": pop * 5 * 0.2 / 1e6,
             "description": "Every rooftop surface collects energy"},
            {"name": "wind_corridors", "power_mw": pop * 0.0002,
             "description": "Venturi-optimized building spacing"},
            {"name": "sky_gardens", "count": max(10, pop // 200),
             "description": "Rooftop food production, thermal buffering"},
        ]

    elif layer == Layer.EMERGENT:
        n_towers = max(4, pop // 1500)
        elements = [
            {"name": "transmission_towers", "count": n_towers,
             "power_mw": 50 * n_towers,
             "description": "Wireless energy transmission across city"},
            {"name": "energy_beaming", "range_miles": 5, "efficiency": 0.85,
             "description": "Point-to-point energy without wires"},
            {"name": "atmospheric_sensors",
             "description": "Weather, pollution, energy flux monitoring"},
        ]

    elif layer == Layer.ATMOSPHERIC:
        elements = [
            {"name": "kite_turbines", "power_mw": pop * 0.002,
             "description": "Tethered aerostats harvesting high-altitude wind"},
            {"name": "air_purification", "co2_tons_year": pop * 1.0,
             "description": "Direct air capture at city scale"},
        ]

    elif layer == Layer.STRATOSPHERIC:
        elements = [
            {"name": "orbital_receivers", "power_mw": pop * 0.01,
             "description": "Beamed power from orbital solar arrays"},
            {"name": "communication_relay",
             "description": "Global data connectivity"},
        ]

    return {
        "layer": layer.value,
        "depth_ft": depths,
        "elements": elements,
        "couples_to": _adjacent_layers(layer),
    }


def _adjacent_layers(layer: Layer) -> List[str]:
    """Get layers this one couples to (adjacent + skip-one)."""
    ordered = list(Layer)
    idx = ordered.index(layer)
    neighbors = []
    for offset in [-2, -1, 1, 2]:
        ni = idx + offset
        if 0 <= ni < len(ordered):
            neighbors.append(ordered[ni].value)
    return neighbors


# ---------------------------
# Flow Patterns
# ---------------------------

FLOW_PATTERNS = [
    {
        "name": "helical_circulation",
        "pattern": "DNA helix from bedrock to sky",
        "analogy": "tornado, DNA, galaxy formation",
        "efficiency": 0.95,
        "description": "Energy spirals up through taproots, down through transmission",
    },
    {
        "name": "spherical_zones",
        "pattern": "Concentric energy shells around core nodes",
        "analogy": "electron shells, cell membranes",
        "radii_miles": [0.5, 1, 2, 5],
        "description": "Energy clusters in predictable orbital zones",
    },
    {
        "name": "fractal_distribution",
        "pattern": "Self-similar branching at all scales",
        "analogy": "blood vessels, river networks, lightning",
        "description": "Large arteries to capillaries, minimal transport loss",
    },
    {
        "name": "direct_jumps",
        "pattern": "Energy bypasses intermediate layers when efficient",
        "analogy": "quantum tunneling, neural shortcuts",
        "description": "Bedrock to canopy direct when gradient justifies it",
    },
]


# ---------------------------
# Biomimetic Models
# ---------------------------

BIOMIMETIC_MODELS = [
    {
        "name": "Tree Vascular",
        "inspiration": "Xylem (up) and phloem (down) circulation",
        "mapping": {
            "bark": "Exterior protection + energy collection",
            "xylem": "Clean resources up from roots (energy, water)",
            "phloem": "Processed materials down (waste, nutrients)",
            "cambium": "Active control layer between flows",
            "canopy": "Maximum capture at top",
        },
    },
    {
        "name": "Body Circulatory",
        "inspiration": "Heart, arteries, capillaries, nerves, lymph",
        "mapping": {
            "heart": "Central energy node (geothermal core)",
            "arteries": "Main conduits (taproot conductors)",
            "capillaries": "Building connections",
            "nerves": "Control and sensor networks",
            "lymph": "Waste collection and recycling",
        },
    },
    {
        "name": "Forest Ecosystem",
        "inspiration": "Canopy, understory, floor, roots, mycelium",
        "mapping": {
            "canopy": "Maximum solar/wind capture at height",
            "understory": "Filtered distribution, vertical farms",
            "floor": "Processing, human activity",
            "roots": "Storage, mineral exchange",
            "mycelium": "Communication network connecting all",
        },
    },
    {
        "name": "Beehive",
        "inspiration": "Hexagonal efficiency, collective intelligence",
        "mapping": {
            "hexagonal_cells": "Maximum space, minimum material",
            "wax_thermal": "Phase-change storage in walls",
            "ventilation": "Passive airflow through structure",
            "swarm_logic": "Distributed coordination without central control",
        },
    },
]


# ---------------------------
# 3D Geometry
# ---------------------------

def compute_geometry(population: int, radius_miles: float = 2.0) -> Dict[str, float]:
    """Compute 3D geometric metrics for the vertical city."""
    height_ft = 3000  # bedrock to atmospheric
    height_miles = height_ft / 5280

    volume = math.pi * radius_miles**2 * height_miles
    surface = (2 * math.pi * radius_miles * height_miles +
               2 * math.pi * radius_miles**2)
    fractal_dim = 2.7  # 3D branching between 2D and 3D

    n_layers = len(Layer)
    n_nodes = population // 10 + n_layers * 20
    couplings_per_layer = 3  # avg adjacent + skip-one
    total_couplings = n_layers * couplings_per_layer
    elements_per_layer = 4  # avg
    total_vectors = n_layers * elements_per_layer

    max_couplings = n_layers * (n_layers - 1) / 2
    coupling_density = total_couplings / max_couplings if max_couplings > 0 else 0

    geo_area = round(total_vectors * total_couplings * fractal_dim / 100, 2)

    return {
        "radius_miles": radius_miles,
        "height_ft": height_ft,
        "volume_cubic_miles": round(volume, 3),
        "surface_area_sq_miles": round(surface, 3),
        "fractal_dimension": fractal_dim,
        "n_layers": n_layers,
        "total_vectors": total_vectors,
        "total_couplings": total_couplings,
        "coupling_density": round(coupling_density, 3),
        "total_nodes": n_nodes,
        "geometric_area": geo_area,
    }


# ---------------------------
# Full Build
# ---------------------------

def build_ecosystem(population: int) -> Dict[str, Any]:
    """Build the complete vertical energy ecosystem."""
    layers = {}
    for layer in Layer:
        layers[layer.value] = build_layer(layer, population)

    geometry = compute_geometry(population)

    # Total power from all layers
    total_power = 0
    total_storage = 0
    for ldata in layers.values():
        for elem in ldata["elements"]:
            total_power += elem.get("power_mw", 0)
            total_storage += elem.get("capacity_mwh", 0)

    return {
        "name": f"Vertical Living City ({population:,} people)",
        "population": population,
        "layers": layers,
        "flow_patterns": FLOW_PATTERNS,
        "biomimetic_models": BIOMIMETIC_MODELS,
        "geometry": geometry,
        "totals": {
            "power_mw": round(total_power, 1),
            "storage_mwh": round(total_storage, 1),
            "power_per_capita_kw": round(total_power * 1000 / population, 1) if population > 0 else 0,
        },
    }


# ---------------------------
# Output
# ---------------------------

def print_ecosystem(eco: Dict[str, Any]):
    """Print human-readable vertical ecosystem report."""
    print("=" * 70)
    print(f"  VERTICAL ENERGY ECOSYSTEM: {eco['name']}")
    print(f"  From Bedrock (-1000 ft) to Stratosphere (2000+ ft)")
    print("=" * 70)

    for layer_name, ldata in eco["layers"].items():
        d = ldata["depth_ft"]
        n_elem = len(ldata["elements"])
        couples = ", ".join(ldata["couples_to"][:3])
        print(f"\n  {layer_name.upper():15s}  {d[0]:>6} to {d[1]:>6} ft  "
              f"({n_elem} elements)  couples: {couples}")
        for elem in ldata["elements"][:3]:
            name = elem["name"]
            desc = elem["description"][:50]
            power = elem.get("power_mw", 0)
            if not power and "power_kw" in elem:
                power = elem["power_kw"] / 1000  # convert kW to MW
            if power:
                print(f"    {name:30s}  {power:>8} MW  {desc}")
            else:
                print(f"    {name:30s}           {desc}")

    print(f"\n--- Flow Patterns ---")
    for fp in eco["flow_patterns"]:
        print(f"  {fp['name']:25s}  analogy: {fp['analogy']}")

    print(f"\n--- Biomimetic Models ---")
    for bm in eco["biomimetic_models"]:
        print(f"  {bm['name']:25s}  {bm['inspiration']}")

    g = eco["geometry"]
    print(f"\n--- 3D Geometry ---")
    print(f"  Volume: {g['volume_cubic_miles']:.3f} mi3  |  "
          f"Surface: {g['surface_area_sq_miles']:.3f} mi2")
    print(f"  Fractal dim: {g['fractal_dimension']}  |  "
          f"Layers: {g['n_layers']}  |  Nodes: {g['total_nodes']:,}")
    print(f"  Vectors: {g['total_vectors']}  |  "
          f"Couplings: {g['total_couplings']}  |  "
          f"Density: {g['coupling_density']:.0%}")
    print(f"  Geometric area: {g['geometric_area']}")

    t = eco["totals"]
    print(f"\n--- Totals ---")
    print(f"  Power: {t['power_mw']:.1f} MW  |  "
          f"Storage: {t['storage_mwh']:.1f} MWh  |  "
          f"Per capita: {t['power_per_capita_kw']:.1f} kW")

    # 2D vs 3D comparison
    print(f"\n--- 2D vs 3D ---")
    print(f"  {'Metric':<25} {'2D City':>10} {'3D Vertical':>12}")
    print(f"  {'-'*25} {'-'*10} {'-'*12}")
    print(f"  {'Geometric area':<25} {'17.6':>10} {g['geometric_area']:>12}")
    print(f"  {'Vectors':<25} {'49':>10} {g['total_vectors']:>12}")
    print(f"  {'Couplings':<25} {'36':>10} {g['total_couplings']:>12}")
    print(f"  {'Fractal dimension':<25} {'1.0':>10} {g['fractal_dimension']:>12}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Vertical Energy Ecosystem -- 3D city from bedrock to sky. "
            "Ten vertical layers coupled through helical, spherical, "
            "and fractal energy flow patterns."
        ),
    )
    parser.add_argument("--population", type=int, default=10000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    eco = build_ecosystem(args.population)

    if args.json:
        # Remove non-serializable bits
        output = {k: v for k, v in eco.items()}
        print(json.dumps(output, indent=2))
    else:
        print_ecosystem(eco)


if __name__ == "__main__":
    main()
