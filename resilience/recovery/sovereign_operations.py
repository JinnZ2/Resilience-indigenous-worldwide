#!/usr/bin/env python3
"""
sovereign_operations.py -- Autonomous base operations monitoring.

Manages the operational layer of a self-sufficient base: water recovery,
power field balancing, and system coherence monitoring.  Designed for
off-grid sites where water is a working fluid and thermal carrier, not
a utility.

Core components:
  - WaterRecovery: monitors pH, turbidity, and recovery rate for
    process water (alumina line) and grey water (domestic).  Flags
    chemical drift and particle contamination.
  - PowerFieldBalancer: monitors battery voltage and sheds non-essential
    loads when energy signature drops.  Prioritizes essential services
    (sCO2 PID, cure monitor, core compute) over heavy loads (CNC, grinder).
  - SiteChecklist: pre-acquisition geometric constraints for cold-climate
    autonomous sites (slope, elevation, snow drift, water table).
  - SystemCoherence: aggregates subsystem health into a single coherence
    score with alert generation.

Design principles:
  - DC-primary bus eliminates 15% inverter loss
  - Gravity-fed water eliminates pumping energy
  - Buried cisterns inside heated slabs prevent freeze damage
  - Faraday enclosure protects compute from EMP/static

References
----------
- Sphere Association (2018). The Sphere Handbook -- minimum water
  quality standards (pH 6.5-8.5, turbidity < 5 NTU).
- IEEE 1547 (2018). Standard for interconnection of distributed energy
  resources -- battery management and load shedding.
- Prigogine, I. & Stengers, I. (1984). Order Out of Chaos.

Usage
-----
    python3 sovereign_operations.py --demo
    python3 sovereign_operations.py --demo --json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------
# Water Recovery
# ---------------------------

@dataclass
class WaterQuality:
    """Water quality reading."""
    ph: float
    turbidity_ntu: float
    source: str              # "process", "grey", "distilled"
    temperature_c: float = 20.0


class WaterRecovery:
    """
    Monitor and classify water streams for reuse.

    Process water (alumina line): heavily contaminated with caustics and
    dissolved metals.  Requires vacuum distillation.

    Grey water (domestic): moderate contamination.  Requires biofiltering
    and UV treatment.

    Distilled water: clean output, ready for reuse in alumina processing
    or domestic systems.
    """

    def __init__(
        self,
        ph_target: tuple = (6.5, 8.5),
        turbidity_limit: float = 5.0,
    ):
        self.ph_target = ph_target
        self.turbidity_limit = turbidity_limit

    def analyze(self, reading: WaterQuality) -> Dict[str, Any]:
        """Analyze a water quality reading and classify it."""
        alerts = []
        status = "clean"

        if not (self.ph_target[0] <= reading.ph <= self.ph_target[1]):
            alerts.append(
                f"pH {reading.ph:.1f} outside target range "
                f"({self.ph_target[0]}-{self.ph_target[1]}). "
                f"Divert to secondary bio-filter."
            )
            status = "chemical_drift"

        if reading.turbidity_ntu > self.turbidity_limit:
            alerts.append(
                f"Turbidity {reading.turbidity_ntu:.1f} NTU exceeds "
                f"limit ({self.turbidity_limit}). Increase filter flow."
            )
            status = "particulate_contamination"

        if reading.turbidity_ntu > self.turbidity_limit * 3:
            status = "critical_contamination"

        return {
            "source": reading.source,
            "ph": reading.ph,
            "turbidity_ntu": reading.turbidity_ntu,
            "temperature_c": reading.temperature_c,
            "status": status,
            "alerts": alerts,
            "reusable": status == "clean",
        }

    def recovery_summary(
        self, readings: List[WaterQuality]
    ) -> Dict[str, Any]:
        """Summarize recovery across multiple readings."""
        results = [self.analyze(r) for r in readings]
        clean = sum(1 for r in results if r["reusable"])
        return {
            "total_readings": len(results),
            "clean": clean,
            "contaminated": len(results) - clean,
            "recovery_rate": clean / len(results) if results else 0,
            "by_source": {
                source: [r for r in results if r["source"] == source]
                for source in set(r["source"] for r in results)
            },
        }


# ---------------------------
# Power Field Balancer
# ---------------------------

@dataclass
class PowerLoad:
    """A power load on the DC bus."""
    name: str
    draw_watts: float
    essential: bool           # True = never shed
    zone: int = 1             # 1 = core, 2 = workshop, 3 = auxiliary


class PowerFieldBalancer:
    """
    Monitor battery voltage and shed non-essential loads to maintain
    system coherence during low-energy events (cold snaps, cloudy days).

    Operates on a 24V DC-primary bus.  Essential services (sCO2 PID,
    cure monitor, core compute) are never shed.  Heavy loads (CNC,
    grinder) are shed first.
    """

    def __init__(
        self,
        critical_voltage: float = 23.8,
        nominal_voltage: float = 25.2,
        loads: Optional[List[PowerLoad]] = None,
    ):
        self.critical_voltage = critical_voltage
        self.nominal_voltage = nominal_voltage
        self.loads = loads or self._default_loads()

    @staticmethod
    def _default_loads() -> List[PowerLoad]:
        return [
            PowerLoad("sco2_pid", 50, True, 1),
            PowerLoad("cure_monitor", 15, True, 1),
            PowerLoad("compute_core", 200, True, 1),
            PowerLoad("lighting", 60, False, 1),
            PowerLoad("cnc_router", 800, False, 2),
            PowerLoad("alumina_grinder", 600, False, 2),
            PowerLoad("water_pump", 100, False, 2),
            PowerLoad("ventilation", 40, False, 3),
        ]

    def evaluate(self, battery_voltage: float) -> Dict[str, Any]:
        """Evaluate power field and determine load shedding."""
        felt_level = min(1.0, battery_voltage / self.nominal_voltage)
        shed = []
        active = []

        if battery_voltage < self.critical_voltage:
            # Shed all non-essential loads, heaviest first
            non_essential = sorted(
                [l for l in self.loads if not l.essential],
                key=lambda l: -l.draw_watts,
            )
            shed = [l.name for l in non_essential]
            active = [l.name for l in self.loads if l.essential]
            status = "critical"
        elif battery_voltage < self.nominal_voltage:
            # Shed zone 2+ non-essential loads
            for load in self.loads:
                if not load.essential and load.zone >= 2:
                    shed.append(load.name)
                else:
                    active.append(load.name)
            status = "warning"
        else:
            active = [l.name for l in self.loads]
            status = "nominal"

        active_draw = sum(
            l.draw_watts for l in self.loads if l.name in active
        )

        return {
            "battery_voltage": battery_voltage,
            "felt_level": round(felt_level, 3),
            "status": status,
            "active_loads": active,
            "shed_loads": shed,
            "active_draw_watts": active_draw,
        }


# ---------------------------
# Site Checklist
# ---------------------------

SITE_CHECKLIST = [
    {
        "item": "south_facing_slope",
        "description": "South-facing slope for solar-microwave hybrid and passive heating",
        "critical": True,
    },
    {
        "item": "above_water_table",
        "description": "sCO2 block and sand battery above water table to prevent heat sinking",
        "critical": True,
    },
    {
        "item": "snow_drift_analysis",
        "description": "Position pre-cooler where snow accumulates for passive vacuum cooling",
        "critical": False,
    },
    {
        "item": "wind_exposure",
        "description": "Assess prevailing wind for turbine siting and thermal losses",
        "critical": False,
    },
    {
        "item": "road_access",
        "description": "Year-round access for initial material delivery",
        "critical": True,
    },
    {
        "item": "soil_bearing_capacity",
        "description": "Verify soil can support geopolymer slab and equipment loads",
        "critical": True,
    },
    {
        "item": "utility_setback",
        "description": "Confirm no utility easements cross build zones",
        "critical": True,
    },
    {
        "item": "water_source",
        "description": "Well, spring, or surface water within feasible distance",
        "critical": True,
    },
]


# ---------------------------
# System Coherence
# ---------------------------

class SystemCoherence:
    """
    Aggregate subsystem health into overall base coherence score.

    Each subsystem reports a 0-1 health value.  Coherence is the
    weighted mean, with critical systems weighted 2x.
    """

    def __init__(self):
        self.subsystems: Dict[str, Dict[str, Any]] = {}

    def update(self, name: str, health: float, critical: bool = False):
        """Update a subsystem's health reading."""
        self.subsystems[name] = {
            "health": max(0.0, min(1.0, health)),
            "critical": critical,
        }

    def coherence(self) -> Dict[str, Any]:
        """Compute overall system coherence."""
        if not self.subsystems:
            return {"coherence": 0.0, "status": "no_data"}

        total_weight = 0.0
        weighted_sum = 0.0
        alerts = []

        for name, sub in self.subsystems.items():
            weight = 2.0 if sub["critical"] else 1.0
            total_weight += weight
            weighted_sum += sub["health"] * weight

            if sub["health"] < 0.5:
                alerts.append(f"{name}: health {sub['health']:.2f}")

        score = weighted_sum / total_weight if total_weight > 0 else 0

        if score > 0.85:
            status = "nominal"
        elif score > 0.60:
            status = "degraded"
        else:
            status = "critical"

        return {
            "coherence": round(score, 3),
            "status": status,
            "subsystems": {
                name: sub["health"]
                for name, sub in self.subsystems.items()
            },
            "alerts": alerts,
        }


# ---------------------------
# Demo / CLI
# ---------------------------

def run_demo(as_json: bool = False) -> Dict[str, Any]:
    """Run demonstration of sovereign operations monitoring."""
    results: Dict[str, Any] = {}

    # Water recovery
    wr = WaterRecovery()
    readings = [
        WaterQuality(ph=7.2, turbidity_ntu=2.0, source="distilled"),
        WaterQuality(ph=11.0, turbidity_ntu=1.5, source="process"),
        WaterQuality(ph=6.8, turbidity_ntu=8.0, source="grey"),
        WaterQuality(ph=7.0, turbidity_ntu=3.0, source="distilled"),
        WaterQuality(ph=5.5, turbidity_ntu=15.0, source="process"),
    ]
    results["water_recovery"] = wr.recovery_summary(readings)

    # Power balancing -- normal conditions
    pfb = PowerFieldBalancer()
    results["power_nominal"] = pfb.evaluate(25.5)
    # Power balancing -- cold snap
    results["power_critical"] = pfb.evaluate(23.5)

    # Site checklist
    results["site_checklist"] = SITE_CHECKLIST

    # System coherence
    sc = SystemCoherence()
    sc.update("power", 0.92, critical=True)
    sc.update("water", 0.75, critical=True)
    sc.update("thermal", 0.88, critical=True)
    sc.update("compute", 0.95, critical=False)
    sc.update("workshop", 0.60, critical=False)
    results["coherence"] = sc.coherence()

    if as_json:
        print(json.dumps(results, indent=2))
        return results

    print("=" * 60)
    print("SOVEREIGN OPERATIONS MONITOR")
    print("=" * 60)

    wr_sum = results["water_recovery"]
    print(f"\n--- Water Recovery ---")
    print(f"  Readings: {wr_sum['total_readings']}  |  "
          f"Clean: {wr_sum['clean']}  |  "
          f"Contaminated: {wr_sum['contaminated']}  |  "
          f"Recovery rate: {wr_sum['recovery_rate']:.0%}")
    for source, source_results in wr_sum["by_source"].items():
        for r in source_results:
            status_mark = "OK" if r["reusable"] else "FAIL"
            print(f"    [{status_mark}] {r['source']:10s}  "
                  f"pH={r['ph']:.1f}  turb={r['turbidity_ntu']:.1f}NTU")
            for alert in r["alerts"]:
                print(f"         {alert}")

    for label, key in [("Nominal", "power_nominal"), ("Cold Snap", "power_critical")]:
        pf = results[key]
        print(f"\n--- Power Field ({label}: {pf['battery_voltage']}V) ---")
        print(f"  Status: {pf['status']}  |  Felt: {pf['felt_level']}")
        print(f"  Active: {', '.join(pf['active_loads'])}  ({pf['active_draw_watts']}W)")
        if pf["shed_loads"]:
            print(f"  Shed: {', '.join(pf['shed_loads'])}")

    print(f"\n--- Site Checklist ---")
    for item in SITE_CHECKLIST:
        crit = "CRITICAL" if item["critical"] else "optional"
        print(f"  [ ] {item['item']:25s}  [{crit:8s}]  {item['description']}")

    coh = results["coherence"]
    print(f"\n--- System Coherence: {coh['coherence']:.3f} [{coh['status']}] ---")
    for name, health in coh["subsystems"].items():
        bar = "#" * int(health * 20) + "." * (20 - int(health * 20))
        print(f"  [{bar}] {health:.2f}  {name}")
    for alert in coh["alerts"]:
        print(f"  ALERT: {alert}")

    print()
    return results


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Sovereign operations monitoring -- water recovery, power "
            "field balancing, site checklist, and system coherence for "
            "autonomous off-grid bases."
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
