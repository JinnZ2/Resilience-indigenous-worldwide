#!/usr/bin/env python3
"""
biogas_systems.py -- Biological waste-to-energy cycling.

Human and kitchen waste are not problems to hide -- they are a chemical
battery and a thermal feedstock.  Pairing a compost toilet with an
anaerobic digester creates a closed loop where biological output drives
heat production and soil fertility.

Core components:
  - CompostBalancer: computes carbon-to-nitrogen ratios and prescribes
    brown material additions (shredded paper, wood chips) to hit the
    30:1 thermophilic target.
  - DigestorMonitor: tracks digester temperature and methane production,
    flags bacterial stalling (low temp) or acidification (low pH).
  - GasHolder: models a flexible bladder gas holder (salvaged truck
    tarp) with pressure, volume, and energy content calculations.
  - BiogasSystem: integrates all components into a single system
    model with thermal coupling to external heat sources (sCO2 waste
    heat, solar thermal).

Key couplings:
  - sCO2 waste heat (150C+) keeps digester at 37C through a water jacket
  - Methane output feeds cooking or backup generator
  - Digestate becomes liquid fertilizer for food production
  - Compost solids become soil amendment after 12-month thermophilic aging

References
----------
- Jenkins, J. (2005). The Humanure Handbook, 3rd ed. Jenkins Publishing.
- Marchaim, U. (1992). Biogas processes for sustainable development.
  FAO Agricultural Services Bulletin 95.
- Sphere Association (2018). The Sphere Handbook -- excreta management
  minimum standards.
- Rynk, R. (1992). On-Farm Composting Handbook. NRAES-54.
  Target C:N ratio 25:1-35:1 for thermophilic composting.

Usage
-----
    python3 biogas_systems.py --demo
    python3 biogas_systems.py --demo --json
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------
# Compost C:N Balancer
# ---------------------------

# Typical C:N ratios for common feedstocks
CN_RATIOS = {
    "humanure": 8,
    "kitchen_scraps": 15,
    "grass_clippings": 17,
    "coffee_grounds": 20,
    "shredded_paper": 175,
    "cardboard": 350,
    "wood_chips": 400,
    "sawdust": 500,
    "drywall_paper": 200,
    "straw": 80,
    "leaves_dry": 60,
    "algae_biomass": 10,
}

TARGET_CN_RATIO = 30  # optimal for thermophilic composting


def compost_balance(
    nitrogen_source: str,
    nitrogen_kg: float,
    carbon_source: str = "shredded_paper",
    target_ratio: float = TARGET_CN_RATIO,
) -> Dict[str, Any]:
    """
    Calculate brown material needed to hit target C:N ratio.

    Parameters
    ----------
    nitrogen_source : str
        Key into CN_RATIOS for the nitrogen-rich material.
    nitrogen_kg : float
        Mass of nitrogen-rich material in kg.
    carbon_source : str
        Key into CN_RATIOS for the carbon-rich material.
    target_ratio : float
        Target C:N ratio (default 30:1).

    Returns
    -------
    dict with carbon_needed_kg, actual_ratio, and assessment.
    """
    n_ratio = CN_RATIOS.get(nitrogen_source, 15)
    c_ratio = CN_RATIOS.get(carbon_source, 200)

    if c_ratio <= target_ratio:
        return {
            "error": f"Carbon source {carbon_source} (C:N={c_ratio}) "
                     f"is not high enough to balance to {target_ratio}:1",
        }

    # (C1*m1 + C2*m2) / (N1*m1 + N2*m2) = target
    # Simplified: carbon_needed = nitrogen_kg * (target - n_ratio) / (c_ratio - target)
    carbon_needed = nitrogen_kg * (target_ratio - n_ratio) / (c_ratio - target_ratio)
    carbon_needed = max(0, carbon_needed)

    total_mass = nitrogen_kg + carbon_needed
    actual_cn = (n_ratio * nitrogen_kg + c_ratio * carbon_needed) / total_mass if total_mass > 0 else 0

    if 25 <= actual_cn <= 35:
        assessment = "optimal"
    elif actual_cn < 25:
        assessment = "nitrogen_heavy"
    else:
        assessment = "carbon_heavy"

    return {
        "nitrogen_source": nitrogen_source,
        "nitrogen_kg": nitrogen_kg,
        "nitrogen_cn": n_ratio,
        "carbon_source": carbon_source,
        "carbon_needed_kg": round(carbon_needed, 2),
        "carbon_cn": c_ratio,
        "actual_cn_ratio": round(actual_cn, 1),
        "target_cn_ratio": target_ratio,
        "assessment": assessment,
    }


def multi_feedstock_balance(
    feedstocks: Dict[str, float],
    target_ratio: float = TARGET_CN_RATIO,
) -> Dict[str, Any]:
    """
    Analyze C:N ratio for a multi-feedstock mix.

    Parameters
    ----------
    feedstocks : dict
        {feedstock_name: mass_kg}

    Returns
    -------
    dict with blended ratio, per-feedstock breakdown, and recommendation.
    """
    total_c = 0.0
    total_n = 0.0
    breakdown = []

    for name, mass in feedstocks.items():
        cn = CN_RATIOS.get(name, 30)
        # Approximate: C = cn * N, and C + N = mass (simplified)
        # More precisely: C/N = cn, so C = cn/(cn+1) * mass, N = 1/(cn+1) * mass
        n_fraction = mass / (cn + 1)
        c_fraction = mass * cn / (cn + 1)
        total_n += n_fraction
        total_c += c_fraction
        breakdown.append({
            "feedstock": name,
            "mass_kg": mass,
            "cn_ratio": cn,
            "carbon_kg": round(c_fraction, 3),
            "nitrogen_kg": round(n_fraction, 3),
        })

    blended = total_c / total_n if total_n > 0 else 0
    deficit = target_ratio - blended

    if abs(deficit) < 3:
        recommendation = "Mix is near target. No adjustment needed."
    elif deficit > 0:
        recommendation = f"Add high-carbon material (paper, wood chips). Deficit: {deficit:.0f} points."
    else:
        recommendation = f"Add nitrogen material (kitchen scraps, humanure). Excess: {-deficit:.0f} points."

    return {
        "blended_cn_ratio": round(blended, 1),
        "target_cn_ratio": target_ratio,
        "total_carbon_kg": round(total_c, 3),
        "total_nitrogen_kg": round(total_n, 3),
        "total_mass_kg": sum(feedstocks.values()),
        "recommendation": recommendation,
        "breakdown": breakdown,
    }


# ---------------------------
# Digester Monitor
# ---------------------------

@dataclass
class DigesterReading:
    """A single reading from the anaerobic digester."""
    temperature_c: float
    methane_ppm: float
    ph: float = 7.0
    co2_ppm: float = 0.0


class DigesterMonitor:
    """
    Monitor anaerobic digester health.

    Methanogenic bacteria operate optimally at 35-40C (mesophilic) or
    50-60C (thermophilic).  Below 20C, activity effectively stops.
    pH below 6.5 indicates acidification (volatile fatty acid buildup).
    Methane below 500 ppm suggests low bacterial activity.
    """

    def __init__(
        self,
        target_temp_c: float = 37.0,
        temp_tolerance_c: float = 5.0,
        min_methane_ppm: float = 500.0,
        ph_range: tuple = (6.5, 8.0),
    ):
        self.target_temp_c = target_temp_c
        self.temp_tolerance_c = temp_tolerance_c
        self.min_methane_ppm = min_methane_ppm
        self.ph_range = ph_range

    def evaluate(self, reading: DigesterReading) -> Dict[str, Any]:
        """Evaluate digester health from sensor reading."""
        alerts = []
        status = "nominal"

        temp_delta = abs(self.target_temp_c - reading.temperature_c)
        if temp_delta > self.temp_tolerance_c:
            alerts.append(
                f"Temperature {reading.temperature_c:.1f}C deviates "
                f"{temp_delta:.1f}C from target {self.target_temp_c}C. "
                f"Bacteria stalling. Increase thermal coupling."
            )
            status = "thermal_drift"

        if reading.temperature_c < 20:
            alerts.append("Temperature below 20C. Methanogenesis effectively stopped.")
            status = "inactive"

        if reading.methane_ppm < self.min_methane_ppm:
            alerts.append(
                f"Methane {reading.methane_ppm:.0f} ppm below minimum "
                f"({self.min_methane_ppm:.0f}). Add feedstock "
                f"(algae biomass, kitchen scraps)."
            )
            if status == "nominal":
                status = "low_production"

        if reading.ph < self.ph_range[0]:
            alerts.append(
                f"pH {reading.ph:.1f} below {self.ph_range[0]}. "
                f"Acidification detected. Add alkaline buffer (wood ash, lime)."
            )
            status = "acidified"
        elif reading.ph > self.ph_range[1]:
            alerts.append(
                f"pH {reading.ph:.1f} above {self.ph_range[1]}. "
                f"Over-alkaline. Reduce buffer additions."
            )

        # Efficiency estimate: methane production relative to optimal
        temp_efficiency = max(0, 1.0 - (temp_delta / 20.0))
        gas_efficiency = min(1.0, reading.methane_ppm / 2000.0)
        overall = (temp_efficiency + gas_efficiency) / 2

        return {
            "temperature_c": reading.temperature_c,
            "methane_ppm": reading.methane_ppm,
            "ph": reading.ph,
            "temp_efficiency": round(temp_efficiency, 3),
            "gas_efficiency": round(gas_efficiency, 3),
            "overall_efficiency": round(overall, 3),
            "status": status,
            "alerts": alerts,
        }


# ---------------------------
# Gas Holder
# ---------------------------

@dataclass
class GasHolderSpec:
    """Specifications for a flexible gas holder (bladder)."""
    volume_liters: float = 1000.0
    pressure_kpa: float = 1.5        # low pressure, gravity-weighted
    material: str = "heavy_duty_vinyl"
    material_weight_oz_sqft: float = 18.0
    methane_fraction: float = 0.60   # typical biogas: 60% CH4, 40% CO2


def gas_holder_energy(spec: GasHolderSpec) -> Dict[str, Any]:
    """
    Calculate energy content and cooking time from gas holder.

    Methane energy content: ~10 kWh/m3 at STP.
    Typical cooking burner: 1.5-2.0 kW.
    """
    volume_m3 = spec.volume_liters / 1000.0
    methane_m3 = volume_m3 * spec.methane_fraction
    energy_kwh = methane_m3 * 10.0  # kWh per m3 methane at STP
    cooking_hours = energy_kwh / 1.75  # assume 1.75 kW burner

    return {
        "total_volume_liters": spec.volume_liters,
        "methane_fraction": spec.methane_fraction,
        "methane_volume_m3": round(methane_m3, 3),
        "energy_kwh": round(energy_kwh, 2),
        "cooking_hours": round(cooking_hours, 1),
        "material": spec.material,
        "safety_notes": [
            "Install water-trap bubbler between digester and bladder to prevent backfire",
            "Weight bladder with plywood sheets for constant pressure gradient",
            "H2S scrubbing through bubbler removes corrosive hydrogen sulfide",
            "Keep bladder sheltered from UV and wind",
        ],
    }


# ---------------------------
# Integrated System Model
# ---------------------------

class BiogasSystem:
    """
    Integrated biological waste-to-energy system.

    Inputs: human waste, kitchen scraps, algae biomass
    Outputs: methane (cooking/heat), compost (soil), digestate (fertilizer)
    Thermal coupling: sCO2 waste heat maintains digester at 37C
    """

    def __init__(self):
        self.monitor = DigesterMonitor()
        self.gas_holder = GasHolderSpec()

    def daily_mass_balance(
        self,
        humanure_kg: float = 1.5,
        kitchen_scraps_kg: float = 2.0,
        algae_biomass_kg: float = 0.5,
        paper_kg: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Estimate daily mass balance and outputs.

        Typical household: 1.5 kg humanure, 2 kg kitchen scraps per day.
        Biogas yield: ~0.3-0.5 m3 per kg volatile solids.
        """
        total_input = humanure_kg + kitchen_scraps_kg + algae_biomass_kg

        # Volatile solids fraction (approximate)
        vs_fractions = {
            "humanure": 0.75,
            "kitchen_scraps": 0.85,
            "algae_biomass": 0.80,
        }
        total_vs = (
            humanure_kg * vs_fractions["humanure"]
            + kitchen_scraps_kg * vs_fractions["kitchen_scraps"]
            + algae_biomass_kg * vs_fractions["algae_biomass"]
        )

        # Biogas yield: 0.4 m3 per kg VS (mesophilic average)
        biogas_m3 = total_vs * 0.4
        methane_m3 = biogas_m3 * 0.60
        energy_kwh = methane_m3 * 10.0

        # Digestate (liquid fertilizer): ~60% of input mass
        digestate_kg = total_input * 0.60

        # C:N check for compost fraction
        compost_mix = {}
        if humanure_kg > 0:
            compost_mix["humanure"] = humanure_kg
        if kitchen_scraps_kg > 0:
            compost_mix["kitchen_scraps"] = kitchen_scraps_kg
        if algae_biomass_kg > 0:
            compost_mix["algae_biomass"] = algae_biomass_kg
        if paper_kg > 0:
            compost_mix["shredded_paper"] = paper_kg

        cn_analysis = multi_feedstock_balance(compost_mix)

        return {
            "daily_input_kg": round(total_input, 2),
            "volatile_solids_kg": round(total_vs, 2),
            "biogas_m3": round(biogas_m3, 3),
            "methane_m3": round(methane_m3, 3),
            "energy_kwh": round(energy_kwh, 2),
            "digestate_kg": round(digestate_kg, 2),
            "cn_analysis": cn_analysis,
            "thermal_requirement_kwh": round(total_input * 0.05, 2),
        }

    def seasonal_adjustment(
        self, ambient_temp_c: float
    ) -> Dict[str, Any]:
        """
        Calculate additional heating needed to maintain digester temperature
        in cold climates.

        Parameters
        ----------
        ambient_temp_c : float
            Outdoor temperature (affects insulation losses).

        Returns
        -------
        dict with heating requirement and coupling recommendations.
        """
        target = 37.0
        delta = max(0, target - ambient_temp_c)

        # Simplified: heating = mass * specific_heat * delta / efficiency
        # For 500L water jacket, specific heat of water = 4.186 kJ/(kg*K)
        # Daily heat loss through insulation (approximate)
        jacket_volume_l = 500
        insulation_r_value = 3.0  # reasonable insulated tank
        daily_loss_kwh = (delta * jacket_volume_l * 4.186) / (3600 * insulation_r_value)

        if delta <= 0:
            source = "none_needed"
        elif daily_loss_kwh < 2:
            source = "sco2_waste_heat"
        elif daily_loss_kwh < 5:
            source = "sco2_waste_heat_with_solar_backup"
        else:
            source = "dedicated_heating_required"

        return {
            "ambient_temp_c": ambient_temp_c,
            "target_temp_c": target,
            "delta_c": round(delta, 1),
            "daily_heat_loss_kwh": round(daily_loss_kwh, 2),
            "recommended_source": source,
        }


# ---------------------------
# Demo / CLI
# ---------------------------

def run_demo(as_json: bool = False) -> Dict[str, Any]:
    """Run demonstration of biogas system components."""
    results: Dict[str, Any] = {}

    # C:N balancing
    results["simple_balance"] = compost_balance("humanure", 5.0, "shredded_paper")
    results["multi_feedstock"] = multi_feedstock_balance({
        "humanure": 1.5,
        "kitchen_scraps": 2.0,
        "algae_biomass": 0.5,
        "shredded_paper": 1.0,
    })

    # Digester monitoring
    monitor = DigesterMonitor()
    results["digester_healthy"] = monitor.evaluate(
        DigesterReading(temperature_c=36.5, methane_ppm=1200, ph=7.1)
    )
    results["digester_cold"] = monitor.evaluate(
        DigesterReading(temperature_c=22.0, methane_ppm=200, ph=6.8)
    )
    results["digester_acidified"] = monitor.evaluate(
        DigesterReading(temperature_c=37.0, methane_ppm=800, ph=5.8)
    )

    # Gas holder
    results["gas_holder"] = gas_holder_energy(GasHolderSpec(volume_liters=1000))

    # Integrated system
    system = BiogasSystem()
    results["daily_balance"] = system.daily_mass_balance(
        humanure_kg=1.5, kitchen_scraps_kg=2.0,
        algae_biomass_kg=0.5, paper_kg=1.0,
    )
    results["winter_heating"] = system.seasonal_adjustment(ambient_temp_c=-30.0)
    results["summer_heating"] = system.seasonal_adjustment(ambient_temp_c=25.0)

    if as_json:
        print(json.dumps(results, indent=2))
        return results

    print("=" * 60)
    print("BIOGAS SYSTEMS -- Biological Waste-to-Energy Cycling")
    print("=" * 60)

    sb = results["simple_balance"]
    print(f"\n--- C:N Balance (Simple) ---")
    print(f"  {sb['nitrogen_kg']}kg {sb['nitrogen_source']} (C:N={sb['nitrogen_cn']})")
    print(f"  + {sb['carbon_needed_kg']}kg {sb['carbon_source']} (C:N={sb['carbon_cn']})")
    print(f"  = C:N ratio {sb['actual_cn_ratio']}:1  [{sb['assessment']}]")

    mf = results["multi_feedstock"]
    print(f"\n--- C:N Balance (Multi-Feedstock) ---")
    print(f"  Blended C:N: {mf['blended_cn_ratio']}:1  (target: {mf['target_cn_ratio']}:1)")
    print(f"  Total mass: {mf['total_mass_kg']}kg")
    print(f"  {mf['recommendation']}")

    for label, key in [("Healthy", "digester_healthy"),
                       ("Cold", "digester_cold"),
                       ("Acidified", "digester_acidified")]:
        d = results[key]
        print(f"\n--- Digester ({label}) ---")
        print(f"  Temp: {d['temperature_c']}C  |  CH4: {d['methane_ppm']}ppm  |  pH: {d['ph']}")
        print(f"  Efficiency: {d['overall_efficiency']}  |  Status: {d['status']}")
        for alert in d["alerts"]:
            print(f"  ALERT: {alert}")

    gh = results["gas_holder"]
    print(f"\n--- Gas Holder ({gh['total_volume_liters']}L) ---")
    print(f"  Methane: {gh['methane_volume_m3']}m3  |  Energy: {gh['energy_kwh']}kWh")
    print(f"  Cooking time: {gh['cooking_hours']} hours")

    db = results["daily_balance"]
    print(f"\n--- Daily Mass Balance ---")
    print(f"  Input: {db['daily_input_kg']}kg  |  VS: {db['volatile_solids_kg']}kg")
    print(f"  Biogas: {db['biogas_m3']}m3  |  Methane: {db['methane_m3']}m3  |  Energy: {db['energy_kwh']}kWh")
    print(f"  Digestate: {db['digestate_kg']}kg  |  Heating needed: {db['thermal_requirement_kwh']}kWh")

    wh = results["winter_heating"]
    print(f"\n--- Winter Heating (-30C) ---")
    print(f"  Heat loss: {wh['daily_heat_loss_kwh']}kWh/day  |  Source: {wh['recommended_source']}")

    print()
    return results


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Biogas systems -- compost C:N balancing, anaerobic digester "
            "monitoring, gas holder sizing, and integrated waste-to-energy "
            "system modeling for autonomous bases."
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
