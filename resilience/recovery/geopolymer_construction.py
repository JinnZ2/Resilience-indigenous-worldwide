#!/usr/bin/env python3
"""
geopolymer_construction.py -- Structural materials from industrial waste.

Simulates geopolymer construction using salvaged materials: red mud
(alumina processing waste), reclaimed gypsum (drywall), glass cullet,
and fiber reinforcement.  Unlike Portland cement (linear, high-waste),
red mud geopolymer is a geometric coupling of industrial byproducts.

Core components:
  - SlabSimulator: computes structural integrity from material ratios,
    curing temperature, and fiber reinforcement.
  - CureProfile: models the three-phase geopolymer cure sequence
    (initial set, polymerization, strength gain) with temperature
    gradient monitoring.
  - PressureVessel: thin-wall hoop stress calculation for sCO2 or
    caustic-environment vessels from salvaged metal.

Chemistry: sulfate-activated geopolymerization.  Gypsum provides
sulfate to accelerate ettringite formation; red mud provides the
aluminosilicate backbone; glass cullet contributes reactive silica.

References
----------
- Davidovits, J. (2008). Geopolymer Chemistry and Applications.
  Institut Geopolymere.
- Ye, N. et al. (2014). Synthesis and characterization of geopolymer
  from Bayer red mud. Cement and Concrete Research, 55, 82-89.
- Provis, J. L. & van Deventer, J. S. J. (2009). Geopolymers:
  Structure, Processing, Properties and Industrial Applications.
  Woodhead Publishing.

Usage
-----
    python3 geopolymer_construction.py --demo
    python3 geopolymer_construction.py --demo --json
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------
# Slab Simulator
# ---------------------------

@dataclass
class SlabMix:
    """Material proportions for a geopolymer slab (fractions, sum ~1)."""
    red_mud: float = 0.45       # aluminosilicate source
    gypsum: float = 0.20        # binder / sulfate source
    glass_cullet: float = 0.20  # reactive silica
    fiber: float = 0.05         # tensile reinforcement
    water_ratio: float = 0.10   # water-to-solids ratio


class SlabSimulator:
    """Simulate structural integrity of salvaged-material geopolymer slabs."""

    def __init__(self, mix: SlabMix, cure_temp_c: float = 40.0):
        self.mix = mix
        self.cure_temp_c = cure_temp_c

    def integrity_score(self) -> float:
        """
        Compute structural integrity (0-100).

        Al/Si ratio from red_mud/glass drives geopolymer bond strength.
        Gypsum binding factor scales with cure temperature.
        Fiber provides tensile reinforcement at high weight.
        """
        al_si_ratio = self.mix.red_mud / (self.mix.glass_cullet + 0.01)
        binding_factor = self.mix.gypsum * (self.cure_temp_c / 40.0)
        reinforcement = self.mix.fiber * 5.0

        score = (al_si_ratio * binding_factor) + reinforcement
        return max(0.0, min(100.0, score))

    def evaluate(self) -> Dict[str, Any]:
        """Evaluate slab and return assessment."""
        score = self.integrity_score()

        if score > 75:
            grade = "high_efficiency"
            note = "High-efficiency foundation. Minimal entropy loss."
        elif score > 50:
            grade = "stable"
            note = "Functional for light equipment. Monitor for heat leaks."
        else:
            grade = "insufficient"
            note = "Structural failure likely. Increase gypsum or cure temperature."

        return {
            "integrity_score": round(score, 2),
            "grade": grade,
            "note": note,
            "mix": {
                "red_mud": self.mix.red_mud,
                "gypsum": self.mix.gypsum,
                "glass_cullet": self.mix.glass_cullet,
                "fiber": self.mix.fiber,
                "water_ratio": self.mix.water_ratio,
            },
            "cure_temp_c": self.cure_temp_c,
        }


# ---------------------------
# Cure Profile
# ---------------------------

@dataclass
class CurePhase:
    """A phase in the geopolymer cure sequence."""
    name: str
    duration_hours: float
    target_temp_c: float
    tolerance_c: float        # acceptable deviation
    description: str


CURE_SEQUENCE = [
    CurePhase(
        "initial_set", 6.0, 37.5, 2.5,
        "Maintain 35-40C for initial ettringite formation",
    ),
    CurePhase(
        "polymerization", 42.0, 40.0, 3.0,
        "Hold constant gradient for Al-O-Si bond densification",
    ),
    CurePhase(
        "strength_gain", 24.0, 30.0, 5.0,
        "Slow ramp-down to ambient for final strength gain",
    ),
]


def simulate_cure(
    sensor_temps: List[float],
    target_temp: float = 40.0,
    max_variance_c: float = 5.0,
) -> Dict[str, Any]:
    """
    Simulate cure monitoring from embedded temperature sensors.

    Parameters
    ----------
    sensor_temps : list of float
        Current temperature readings from sensors embedded in slab.
    target_temp : float
        Target cure temperature.
    max_variance_c : float
        Maximum acceptable temperature variance across slab.

    Returns
    -------
    dict with average temp, variance, integrity, and alerts.
    """
    if not sensor_temps:
        return {"error": "no sensor data"}

    avg = sum(sensor_temps) / len(sensor_temps)
    variance = max(sensor_temps) - min(sensor_temps)
    integrity = max(0.0, 1.0 - (variance / max_variance_c))

    alerts = []
    if variance > max_variance_c:
        alerts.append(
            f"Thermal gradient too high ({variance:.1f}C). "
            f"Risk of differential curing and cracking."
        )
    if avg < target_temp - 5:
        alerts.append(
            f"Average temperature ({avg:.1f}C) below target "
            f"({target_temp}C). Reaction may stall."
        )
    if avg > target_temp + 10:
        alerts.append(
            f"Average temperature ({avg:.1f}C) above target. "
            f"Risk of thermal cracking."
        )

    return {
        "avg_temp_c": round(avg, 1),
        "variance_c": round(variance, 1),
        "integrity": round(integrity, 3),
        "alerts": alerts,
        "status": "nominal" if not alerts else "warning",
    }


# ---------------------------
# Pressure Vessel Calculator
# ---------------------------

def pressure_vessel_thickness(
    internal_pressure_mpa: float,
    inside_diameter_mm: float,
    allowable_stress_mpa: float = 137.0,
    safety_factor: float = 3.0,
    corrosion_allowance_mm: float = 1.5,
) -> Dict[str, Any]:
    """
    Thin-wall hoop stress calculation for cylindrical pressure vessels.

    Suitable for sCO2 cycle components or caustic-environment vessels
    built from salvaged stainless steel.

    Parameters
    ----------
    internal_pressure_mpa : float
        Operating pressure in MPa.
    inside_diameter_mm : float
        Inside diameter in mm.
    allowable_stress_mpa : float
        Allowable stress for material (316SS default: 137 MPa).
    safety_factor : float
        Safety factor (3.0 recommended for salvaged metal).
    corrosion_allowance_mm : float
        Additional thickness for corrosion in caustic environment.

    Returns
    -------
    dict with wall thickness, test pressure, and specifications.
    """
    # Hoop stress: t = P * d / (2 * S / SF)
    effective_stress = allowable_stress_mpa / safety_factor
    wall_thickness = (internal_pressure_mpa * inside_diameter_mm) / (2 * effective_stress)
    total_thickness = wall_thickness + corrosion_allowance_mm
    test_pressure = internal_pressure_mpa * 1.5

    return {
        "wall_thickness_mm": round(total_thickness, 2),
        "min_thickness_mm": round(wall_thickness, 2),
        "corrosion_allowance_mm": corrosion_allowance_mm,
        "test_pressure_mpa": round(test_pressure, 2),
        "safety_factor": safety_factor,
        "notes": [
            "Use shielded arc welds; threaded fittings are leak-prone in sCO2 cycles",
            "316 stainless preferred for caustic red mud environment",
            f"Test at {test_pressure:.1f} MPa before service",
        ],
    }


# ---------------------------
# Demo / CLI
# ---------------------------

def run_demo(as_json: bool = False) -> Dict[str, Any]:
    """Run demonstration of all geopolymer construction tools."""
    results: Dict[str, Any] = {}

    # Slab simulation
    mix = SlabMix(red_mud=0.45, gypsum=0.20, glass_cullet=0.20, fiber=0.05)
    slab = SlabSimulator(mix, cure_temp_c=40.0)
    results["slab_evaluation"] = slab.evaluate()

    # Cure monitoring simulation
    sensor_readings = [38.5, 39.2, 37.8, 40.1, 36.5]
    results["cure_check"] = simulate_cure(sensor_readings)

    # Cure sequence
    results["cure_sequence"] = [
        {
            "phase": p.name,
            "duration_hours": p.duration_hours,
            "target_temp_c": p.target_temp_c,
            "tolerance_c": p.tolerance_c,
            "description": p.description,
        }
        for p in CURE_SEQUENCE
    ]

    # Pressure vessel for sCO2 block
    results["pressure_vessel"] = pressure_vessel_thickness(
        internal_pressure_mpa=10.0,
        inside_diameter_mm=150.0,
    )

    if as_json:
        print(json.dumps(results, indent=2))
        return results

    print("=" * 60)
    print("GEOPOLYMER CONSTRUCTION -- Structural Materials from Waste")
    print("=" * 60)

    ev = results["slab_evaluation"]
    print(f"\n--- Slab Evaluation ---")
    print(f"  Mix: red_mud={ev['mix']['red_mud']}, gypsum={ev['mix']['gypsum']}, "
          f"glass={ev['mix']['glass_cullet']}, fiber={ev['mix']['fiber']}")
    print(f"  Cure temp: {ev['cure_temp_c']}C")
    print(f"  Integrity: {ev['integrity_score']}/100  [{ev['grade']}]")
    print(f"  {ev['note']}")

    cc = results["cure_check"]
    print(f"\n--- Cure Monitor ---")
    print(f"  Avg temp: {cc['avg_temp_c']}C  |  Variance: {cc['variance_c']}C")
    print(f"  Integrity: {cc['integrity']}  |  Status: {cc['status']}")
    for alert in cc["alerts"]:
        print(f"  ALERT: {alert}")

    print(f"\n--- Cure Sequence ---")
    for p in results["cure_sequence"]:
        print(f"  {p['phase']:20s}  {p['duration_hours']:5.0f}h  "
              f"{p['target_temp_c']:.0f}C +/-{p['tolerance_c']:.0f}C")
        print(f"    {p['description']}")

    pv = results["pressure_vessel"]
    print(f"\n--- Pressure Vessel (sCO2) ---")
    print(f"  Wall thickness: {pv['wall_thickness_mm']} mm "
          f"(min {pv['min_thickness_mm']} + {pv['corrosion_allowance_mm']} corrosion)")
    print(f"  Test pressure: {pv['test_pressure_mpa']} MPa")
    print(f"  Safety factor: {pv['safety_factor']}x")
    for note in pv["notes"]:
        print(f"  * {note}")

    print()
    return results


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Geopolymer construction from industrial waste. Simulates "
            "red mud + gypsum + glass cullet structural slabs, cure "
            "monitoring, and pressure vessel sizing for sCO2 systems."
        ),
    )
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        sys.exit(0)

    run_demo(as_json=args.json)


if __name__ == "__main__":
    main()
