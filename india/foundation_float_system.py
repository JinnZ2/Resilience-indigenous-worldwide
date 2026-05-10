"""
foundation_float_system.py

India deltas / subsiding megacities: adjustable bearing foundation
framework. Constraint-following design -- structures absorb substrate
motion instead of resisting it.

## Source pattern

Centuries-tested floating / stilt structures from Alaska-Mississippi
nomadic corridors: floating bladder anchors on permafrost and rising
water, adjustable bearing heights re-shimmed across visits, structures
designed *into* the substrate's motion rather than against it.

## Translation target

Indian delta and groundwater-subsidence zones (Ganga-Brahmaputra,
Chennai coastal strip, Kolkata Salt Lake / Bidhannagar, Delhi /
Mumbai / Bengaluru aquifer-drawdown areas).

## Physics

Differential settlement is a vector field across the footprint.
Rigid foundations integrate that field as structural stress until
yield. Adjustable bearings re-zero the field at scheduled intervals,
holding cumulative stress near zero. Stress integral over the design
horizon is the diagnostic.

## Bonus mode

Floating bladder anchors capture vertical water-column motion as
gravitational potential. That potential is a power source, not a
nuisance -- same principle as the small-motor charge harvest from
the Alaska stories.

License: CC0
Stdlib only.
"""

from dataclasses import dataclass
from typing import Iterable
import math

# -----------------------------------------------------------
# 1. Bearing: an adjustable foundation point
# -----------------------------------------------------------

@dataclass
class Bearing:
    """
    A single adjustable foundation point. Re-shimmed on a schedule
    to re-zero accumulated differential settlement.
    """
    id: str
    x_m: float
    y_m: float
    nominal_height_m: float
    current_shim_mm: float = 0.0
    max_shim_mm: float = 300.0    # adjustment range before re-engineering

    def settle(self, settlement_mm: float) -> None:
        self.current_shim_mm += settlement_mm

    def adjust(self) -> float:
        """Re-shim to zero. Returns adjustment magnitude in mm."""
        delta = self.current_shim_mm
        self.current_shim_mm = 0.0
        return abs(delta)

    def out_of_range(self) -> bool:
        return abs(self.current_shim_mm) >= self.max_shim_mm


# -----------------------------------------------------------
# 2. Footprint: collection of bearings under a structure
# -----------------------------------------------------------

@dataclass
class Footprint:
    name: str
    bearings: list[Bearing]

    def differential_settlement_mm(self) -> float:
        """Max minus min current shim across the footprint."""
        shims = [b.current_shim_mm for b in self.bearings]
        return max(shims) - min(shims)

    def apply_subsidence_field(self, field_fn) -> None:
        """field_fn(x, y) -> mm of settlement this interval."""
        for b in self.bearings:
            b.settle(field_fn(b.x_m, b.y_m))

    def adjust_all(self) -> dict:
        adjustments = [b.adjust() for b in self.bearings]
        return {
            "n_bearings": len(adjustments),
            "total_shim_mm": sum(adjustments),
            "max_single_shim_mm": max(adjustments) if adjustments else 0.0,
        }

    def any_out_of_range(self) -> bool:
        return any(b.out_of_range() for b in self.bearings)


# -----------------------------------------------------------
# 3. Float-bladder energy harvest
# -----------------------------------------------------------

def bladder_potential_energy_kj(
    volume_m3: float,
    rise_m: float,
    water_density_kg_m3: float = 1000.0,
    g: float = 9.81,
) -> float:
    """
    Gravitational potential captured by a buoyant float lifted through
    `rise_m` of water column. Convertible to mechanical work via a
    tether-and-ratchet or piston linkage.
    """
    mass_displaced = volume_m3 * water_density_kg_m3
    return (mass_displaced * g * rise_m) / 1000.0


def annual_harvest_kwh(
    bladder_volume_m3: float,
    seasonal_rise_m: float,
    cycles_per_year: int,
    conversion_efficiency: float = 0.35,
) -> float:
    """
    Estimate annual mechanical energy harvest from a single bladder
    cycling between seasonal water levels.
    """
    kj_per_cycle = bladder_potential_energy_kj(bladder_volume_m3, seasonal_rise_m)
    annual_kj = kj_per_cycle * cycles_per_year * conversion_efficiency
    return annual_kj / 3600.0


# -----------------------------------------------------------
# 4. Lifecycle simulation
# -----------------------------------------------------------

def simulate(
    footprint: Footprint,
    subsidence_field_fn,
    horizon_years: int,
    adjustment_interval_years: float,
) -> dict:
    """
    Run an annual loop. Apply subsidence field each year. Adjust
    bearings on schedule. Return diagnostic series.
    """
    diff_series = []
    adjustments = []
    out_of_range_year = None

    for year in range(1, horizon_years + 1):
        footprint.apply_subsidence_field(subsidence_field_fn)
        diff_series.append(footprint.differential_settlement_mm())

        if year % max(1, int(adjustment_interval_years)) == 0:
            adjustments.append({"year": year, **footprint.adjust_all()})

        if footprint.any_out_of_range() and out_of_range_year is None:
            out_of_range_year = year

    return {
        "horizon_years": horizon_years,
        "max_differential_mm": max(diff_series) if diff_series else 0.0,
        "n_adjustments": len(adjustments),
        "total_shim_mm_lifecycle": sum(a["total_shim_mm"] for a in adjustments),
        "out_of_range_year": out_of_range_year,
    }


# -----------------------------------------------------------
# 5. Falsifiable claims
# -----------------------------------------------------------

CLAIMS = [
    "Adjustable bearings hold cumulative differential settlement bounded; rigid foundations integrate it to yield.",
    "Adjustment-cycle energy is bounded; counteraction (rigid + repair after collapse) is not.",
    "Vertical water-column motion is harvestable potential energy, not a nuisance variable.",
    "A delta foundation without a re-survey cycle has no diagnostic signature for failure approach.",
    "Bearings going out of shim range is a scope-exit signal, not a structural failure.",
    "Centuries of nomadic floating-structure design carry an empirically validated maintenance cycle that current Indian building codes lack.",
]


if __name__ == "__main__":
    bearings = [
        Bearing(f"b{i}", x_m=float(i % 4) * 3.0, y_m=float(i // 4) * 3.0,
                nominal_height_m=1.5)
        for i in range(16)
    ]
    fp = Footprint("delta_residence", bearings)

    def subsidence_field(x, y):
        # gradient: stronger subsidence toward one edge, mm/year
        base = 8.0
        gradient = 0.6 * x + 0.4 * y
        return base + gradient

    result = simulate(fp, subsidence_field,
                      horizon_years=50,
                      adjustment_interval_years=2.0)
    print(f"Foundation simulation: {result}")

    # Realistic deployment: bank of 20 bladders, 2 m^3 each, monsoon + tidal
    # cycling. Per-cycle PE is small (gravity is a gentle harvester); value
    # comes from many bladders x many cycles.
    per_bladder = annual_harvest_kwh(
        bladder_volume_m3=2.0,
        seasonal_rise_m=3.5,
        cycles_per_year=2,
    )
    bank_with_tidal = annual_harvest_kwh(
        bladder_volume_m3=2.0,
        seasonal_rise_m=0.5,
        cycles_per_year=720,   # ~ twice daily tidal in coastal delta
    ) * 20
    print(f"Annual bladder harvest (single, monsoon-only): {per_bladder:.4f} kWh")
    print(f"Annual harvest (20-bladder bank, tidal): {bank_with_tidal:.2f} kWh")
