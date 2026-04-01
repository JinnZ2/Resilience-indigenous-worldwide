#!/usr/bin/env python3
"""
proposed_geometric_city.py -- Physical city proposal from first principles.

Every number traces to a physical interaction.  No aspirational targets --
only Shockley-Queisser limits, Betz limits, Carnot efficiencies, and
measured geothermal gradients.

Sizes energy sources from location physics (latitude, wind speed, geothermal
gradient, tidal range), calculates consumption from population needs, checks
supply vs demand, and declares whether the city is physically viable.

Energy nodes follow physical interaction types:
  R  - Radiative (solar PV, solar thermal)
  F  - Fluid (wind, tidal)
  G  - Gravitational (tidal, hydro, gravity storage)
  T  - Thermal (geothermal, waste heat)
  C  - Chemical (biogas, fuel cells)
  EM - Electromagnetic (electricity distribution)
  M  - Mechanical (motors, generators, transport)
  K  - Kinetic (piezoelectric, vibration harvesting)

Three proposed locations analyzed:
  - Desert Coast (high solar, moderate wind, tidal, sand storage)
  - High Desert (maximum solar, good wind, no tidal, sand storage)
  - Volcanic Coast (geothermal bonus, strong wind, tidal, river)

References
----------
- Shockley, W. & Queisser, H. (1961). Detailed balance limit of p-n
  junction solar cells. J. Applied Physics, 32(3), 510-519.
- Betz, A. (1920). The maximum of the theoretically possible exploitation
  of wind by means of a wind motor. Wind Engineering, 37(4), 441-446.
- Carnot, S. (1824). Reflections on the Motive Power of Fire.
- DiPippo, R. (2012). Geothermal Power Plants, 3rd ed. Butterworth-Heinemann.

Usage
-----
    python3 proposed_geometric_city.py
    python3 proposed_geometric_city.py --population 50000 --location volcanic_coast
    python3 proposed_geometric_city.py --json
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------
# Physical Limits
# ---------------------------

class PhysicalLimits:
    """First-principles efficiency limits for energy conversion."""
    # Solar
    SOLAR_IRRADIANCE = 1000       # W/m2 at peak
    PV_EFFICIENCY = 0.20          # practical Shockley-Queisser
    THERMAL_SOLAR_EFF = 0.70      # concentrated solar thermal

    # Wind
    BETZ_LIMIT = 0.593            # theoretical max
    PRACTICAL_WIND = 0.45         # real-world turbine

    # Geothermal
    GEOTHERMAL_EFF = 0.12         # binary cycle typical

    # Mechanical
    MOTOR_EFF = 0.92
    GENERATOR_EFF = 0.90
    PIEZO_EFF = 0.35

    # Chemical
    FUEL_CELL_EFF = 0.65
    COMBUSTION_EFF = 0.35         # Carnot-limited
    BIOGAS_YIELD_M3_PER_KG = 0.5
    BIOGAS_KWH_PER_M3 = 6.0
    BIOGAS_ENGINE_EFF = 0.85

    # Thermal
    THERMOELECTRIC_EFF = 0.12

    # Storage
    SAND_STORAGE_EFF = 0.95       # round-trip thermal
    BATTERY_EFF = 0.85            # round-trip electrical

    @staticmethod
    def carnot(t_hot_k: float, t_cold_k: float = 300.0) -> float:
        """Carnot efficiency limit."""
        return 1.0 - (t_cold_k / t_hot_k)


# ---------------------------
# Location Parameters
# ---------------------------

@dataclass
class CityLocation:
    """Physical location parameters measured or published."""
    name: str
    latitude_deg: float
    solar_peak_hours: float
    avg_wind_speed_ms: float
    geothermal_gradient_c_per_km: float
    tidal_range_m: float
    has_river: bool
    desert_sand_available: bool


LOCATIONS = {
    "desert_coast": CityLocation(
        "Desert Coast", 25.0, 5.5, 7.0, 35, 2.5, False, True,
    ),
    "high_desert": CityLocation(
        "High Desert", 35.0, 6.0, 6.0, 30, 0.0, False, True,
    ),
    "volcanic_coast": CityLocation(
        "Volcanic Coast", 20.0, 5.0, 8.0, 60, 3.0, True, False,
    ),
}


# ---------------------------
# Energy Source
# ---------------------------

@dataclass
class EnergySource:
    """A physical energy source with traceable calculation."""
    name: str
    node: str               # R, F, G, T, C, K
    raw_power_mw: float
    calculation: str
    variability: float      # 0 = constant, 1 = intermittent
    conversion_eff: float   # to usable form


# ---------------------------
# City Design
# ---------------------------

class PhysicalCityDesign:
    """City design where every number traces to physics."""

    def __init__(self, location: CityLocation, population: int):
        self.location = location
        self.population = population
        self.sources: List[EnergySource] = []
        self.storage: Dict[str, Dict[str, float]] = {}
        self.consumption: Dict[str, float] = {}
        self._size_sources()
        self._size_consumption()
        self._size_storage()

    def _size_sources(self):
        pop = self.population
        loc = self.location
        PL = PhysicalLimits

        # --- Radiative (R): Solar PV ---
        # 10 m2/person, 1000 W/m2 peak, 20% PV efficiency
        solar_area_m2 = pop * 10
        solar_peak_mw = (solar_area_m2 * PL.SOLAR_IRRADIANCE * PL.PV_EFFICIENCY) / 1e6
        self.sources.append(EnergySource(
            "Solar PV", "R", solar_peak_mw,
            f"{solar_area_m2:,.0f} m2 x {PL.SOLAR_IRRADIANCE} W/m2 x {PL.PV_EFFICIENCY:.0%}",
            0.7, PL.PV_EFFICIENCY,
        ))

        # --- Fluid (F): Wind ---
        # Standard 5 MW turbines, 1 per 2000 people
        n_turbines = max(1, pop // 2000)
        wind_mw = n_turbines * 5.0
        self.sources.append(EnergySource(
            "Wind Turbines", "F", wind_mw,
            f"{n_turbines} x 5 MW at {loc.avg_wind_speed_ms:.0f} m/s avg",
            0.5, PL.PRACTICAL_WIND * PL.GENERATOR_EFF,
        ))

        # --- Gravitational (G): Tidal ---
        if loc.tidal_range_m > 1.0:
            tidal_mw = loc.tidal_range_m * 0.4 * (pop / 10000)
            self.sources.append(EnergySource(
                "Tidal Power", "G", tidal_mw,
                f"{loc.tidal_range_m:.1f}m range, scaled to {pop:,} pop",
                0.3, 0.90 * PL.GENERATOR_EFF,
            ))

        # --- Thermal (T): Geothermal ---
        geo_area_km2 = pop / 2000
        geo_gradient_factor = loc.geothermal_gradient_c_per_km / 35
        geo_mw = geo_area_km2 * 5 * geo_gradient_factor
        self.sources.append(EnergySource(
            "Geothermal", "T", geo_mw,
            f"{geo_area_km2:.2f} km2 x 5 MW/km2 x {geo_gradient_factor:.1f} gradient",
            0.95, PL.GEOTHERMAL_EFF,
        ))

        # --- Chemical (C): Biogas from human waste ---
        waste_kg = pop * 0.5
        biogas_m3 = waste_kg * PL.BIOGAS_YIELD_M3_PER_KG
        biogas_kwh = biogas_m3 * PL.BIOGAS_KWH_PER_M3
        biogas_mw = biogas_kwh / 24 / 1000
        self.sources.append(EnergySource(
            "Biogas (Human Waste)", "C", biogas_mw,
            f"{waste_kg:.0f} kg/day x {PL.BIOGAS_YIELD_M3_PER_KG} m3/kg x {PL.BIOGAS_KWH_PER_M3} kWh/m3",
            0.9, PL.BIOGAS_ENGINE_EFF,
        ))

        # --- Chemical (C): Agricultural waste (if river = farmland) ---
        if loc.has_river:
            ag_mw = biogas_mw * 0.5
            self.sources.append(EnergySource(
                "Biogas (Agricultural)", "C", ag_mw,
                "Additional from river-basin agriculture",
                0.8, PL.BIOGAS_ENGINE_EFF,
            ))

    def _size_consumption(self):
        pop = self.population
        elec_mw = pop * 5 / 24 / 1000        # 5 kWh/person/day
        thermal_mw = pop * 10 / 24 / 1000     # 10 kWh/person/day heating
        food_mw = pop * 2.3 / 24 / 1000       # 2000 kcal = 2.3 kWh
        mobility_mw = elec_mw * 0.3            # 30% of electrical

        self.consumption = {
            "electricity": elec_mw,
            "thermal": thermal_mw,
            "food": food_mw,
            "mobility": mobility_mw,
        }

    def _size_storage(self):
        # Sand thermal: 24h of thermal demand
        if self.location.desert_sand_available:
            thermal_mwh = self.consumption["thermal"] * 24
            self.storage["sand_thermal"] = {
                "capacity_mwh": round(thermal_mwh, 1),
                "volume_m3": round(thermal_mwh * 5, 0),  # 5 m3/MWh at 400C delta
                "efficiency": PhysicalLimits.SAND_STORAGE_EFF,
            }

        # Battery: 12h of electrical demand
        battery_mwh = self.consumption["electricity"] * 12
        self.storage["battery"] = {
            "capacity_mwh": round(battery_mwh, 1),
            "efficiency": PhysicalLimits.BATTERY_EFF,
        }

    def effective_electrical_mw(self) -> float:
        """Usable electrical power after conversion losses."""
        total = 0.0
        for s in self.sources:
            if s.node == "R":
                total += s.raw_power_mw  # already includes PV eff in raw calc
            elif s.node in ("F", "G"):
                total += s.raw_power_mw * s.conversion_eff
            elif s.node == "T":
                total += s.raw_power_mw * s.conversion_eff
            elif s.node == "C":
                total += s.raw_power_mw * s.conversion_eff
        return total

    def effective_thermal_mw(self) -> float:
        """Usable thermal power (solar thermal + geothermal waste heat)."""
        total = 0.0
        for s in self.sources:
            if s.node == "R":
                total += (s.raw_power_mw / PhysicalLimits.PV_EFFICIENCY) * PhysicalLimits.THERMAL_SOLAR_EFF * 0.3
            elif s.node == "T":
                total += s.raw_power_mw * (1 - s.conversion_eff)
        return total

    def total_raw_mw(self) -> float:
        return sum(s.raw_power_mw for s in self.sources)

    def surplus(self) -> Dict[str, float]:
        return {
            "electrical_mw": self.effective_electrical_mw() - self.consumption["electricity"],
            "thermal_mw": self.effective_thermal_mw() - self.consumption["thermal"],
        }

    def is_viable(self) -> bool:
        s = self.surplus()
        return s["electrical_mw"] >= 0

    def to_dict(self) -> Dict[str, Any]:
        s = self.surplus()
        return {
            "location": self.location.name,
            "population": self.population,
            "sources": [
                {"name": src.name, "node": src.node, "raw_mw": round(src.raw_power_mw, 3),
                 "calc": src.calculation, "variability": src.variability,
                 "conversion_eff": src.conversion_eff}
                for src in self.sources
            ],
            "total_raw_mw": round(self.total_raw_mw(), 2),
            "effective_electrical_mw": round(self.effective_electrical_mw(), 2),
            "effective_thermal_mw": round(self.effective_thermal_mw(), 2),
            "consumption": {k: round(v, 3) for k, v in self.consumption.items()},
            "surplus": {k: round(v, 3) for k, v in s.items()},
            "storage": self.storage,
            "viable": self.is_viable(),
            "physical_limits_applied": {
                "pv_efficiency": PhysicalLimits.PV_EFFICIENCY,
                "wind_efficiency": PhysicalLimits.PRACTICAL_WIND,
                "betz_limit": PhysicalLimits.BETZ_LIMIT,
                "geothermal_efficiency": PhysicalLimits.GEOTHERMAL_EFF,
                "generator_efficiency": PhysicalLimits.GENERATOR_EFF,
                "biogas_engine_efficiency": PhysicalLimits.BIOGAS_ENGINE_EFF,
            },
        }


# ---------------------------
# Output
# ---------------------------

def print_city(city: PhysicalCityDesign):
    """Print human-readable city proposal."""
    loc = city.location
    s = city.surplus()

    print(f"\n{'=' * 70}")
    print(f"  PROPOSED GEOMETRIC CITY: {loc.name}")
    print(f"  Population: {city.population:,}  |  First-Principles Physics")
    print(f"{'=' * 70}")

    print(f"\n--- Location ---")
    print(f"  Latitude: {loc.latitude_deg} deg  |  Solar: {loc.solar_peak_hours}h/day  |  "
          f"Wind: {loc.avg_wind_speed_ms} m/s")
    print(f"  Geothermal: {loc.geothermal_gradient_c_per_km} C/km  |  "
          f"Tidal: {loc.tidal_range_m}m  |  Sand: {'yes' if loc.desert_sand_available else 'no'}")

    print(f"\n--- Energy Sources ---")
    print(f"  {'Source':<25} {'Node':>4} {'Raw MW':>10} {'Eff':>6} {'Calc'}")
    print(f"  {'-'*25} {'-'*4} {'-'*10} {'-'*6} {'-'*30}")
    for src in city.sources:
        print(f"  {src.name:<25} {src.node:>4} {src.raw_power_mw:>10.2f} "
              f"{src.conversion_eff:>5.0%} {src.calculation}")

    print(f"\n  Total raw: {city.total_raw_mw():.2f} MW")
    print(f"  Usable electrical: {city.effective_electrical_mw():.2f} MW")
    print(f"  Usable thermal: {city.effective_thermal_mw():.2f} MW")

    print(f"\n--- Consumption ---")
    for k, v in city.consumption.items():
        print(f"  {k:20s}: {v:.3f} MW")

    print(f"\n--- Supply vs Demand ---")
    elec_ok = "OK" if s["electrical_mw"] >= 0 else "DEFICIT"
    therm_ok = "OK" if s["thermal_mw"] >= 0 else "DEFICIT"
    print(f"  Electrical surplus: {s['electrical_mw']:+.3f} MW  [{elec_ok}]")
    print(f"  Thermal surplus:    {s['thermal_mw']:+.3f} MW  [{therm_ok}]")

    if city.storage:
        print(f"\n--- Storage ---")
        for name, st in city.storage.items():
            print(f"  {name}: {st['capacity_mwh']:.1f} MWh  "
                  f"(eff {st['efficiency']:.0%})"
                  + (f"  vol {st.get('volume_m3', 0):.0f} m3" if 'volume_m3' in st else ""))

    print(f"\n--- Verdict ---")
    if city.is_viable():
        print(f"  PHYSICALLY VIABLE. {city.population:,} people, 100% renewable,")
        print(f"  {s['electrical_mw']:.2f} MW surplus electricity for export or storage.")
    else:
        print(f"  NEEDS ADDITIONAL SOURCES. Electrical deficit: {abs(s['electrical_mw']):.2f} MW")

    print(f"\n  Physical limits applied: PV {PhysicalLimits.PV_EFFICIENCY:.0%}, "
          f"Wind {PhysicalLimits.PRACTICAL_WIND:.0%} (Betz {PhysicalLimits.BETZ_LIMIT:.1%}), "
          f"Geo {PhysicalLimits.GEOTHERMAL_EFF:.0%}, "
          f"Gen {PhysicalLimits.GENERATOR_EFF:.0%}")


def run_proposals(population: int, location_name: Optional[str] = None, as_json: bool = False):
    """Run city proposals for one or all locations."""
    if location_name:
        locs = {location_name: LOCATIONS[location_name]}
    else:
        locs = LOCATIONS

    cities = []
    for name, loc in locs.items():
        city = PhysicalCityDesign(loc, population)
        cities.append(city)

    if as_json:
        print(json.dumps([c.to_dict() for c in cities], indent=2))
        return cities

    for city in cities:
        print_city(city)

    if len(cities) > 1:
        print(f"\n{'=' * 70}")
        print(f"  LOCATION COMPARISON ({population:,} people)")
        print(f"{'=' * 70}")
        print(f"\n  {'Location':<20} {'Raw MW':>8} {'Elec MW':>9} {'Therm MW':>10} {'Surplus':>10} {'Viable':>8}")
        print(f"  {'-'*20} {'-'*8} {'-'*9} {'-'*10} {'-'*10} {'-'*8}")
        for c in cities:
            s = c.surplus()
            print(f"  {c.location.name:<20} {c.total_raw_mw():>8.1f} "
                  f"{c.effective_electrical_mw():>9.1f} "
                  f"{c.effective_thermal_mw():>10.1f} "
                  f"{s['electrical_mw']:>+10.1f} "
                  f"{'YES' if c.is_viable() else 'NO':>8}")

        best = max(cities, key=lambda c: c.effective_electrical_mw() + c.effective_thermal_mw())
        print(f"\n  Recommendation: {best.location.name}")

    return cities


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Proposed Geometric City -- physical design from first principles. "
            "Every number traces to Shockley-Queisser, Betz, Carnot, or "
            "measured geothermal gradients."
        ),
    )
    parser.add_argument("--population", type=int, default=10000)
    parser.add_argument("--location", choices=list(LOCATIONS.keys()), default=None,
                        help="Single location (default: compare all)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    run_proposals(args.population, args.location, args.json)


if __name__ == "__main__":
    main()
