"""gravity_battery_metamaterial_sim.py

Simulator for a hypothetical metamaterial gravity battery.
Material descends a gradient. Internal mechanisms absorb kinetic
energy without transferring it to the substrate. Stored energy is
extracted at the bottom; extraction reduces transport mass. Ascent
is lighter than descent.

Two descent modes:
  - Free descent: theoretical upper bound, PE = m g h with no losses
  - Slope rolling: unit rolls down a real incline; PE is reduced by
    rolling-resistance work (Crr * m g cos(theta) * L) and a simple
    air-drag fraction before the metamaterial can absorb it

CC0. Standard library only.
"""

import math
from dataclasses import dataclass

G = 9.81
HUMAN_METABOLIC_EFFICIENCY = 0.25


@dataclass
class Metamaterial:
    name: str
    absorption_efficiency: float
    storage_efficiency: float
    extraction_efficiency: float
    mass_loss_fraction_per_kj: float
    reset_energy_fraction: float


@dataclass
class SlopeProfile:
    name: str
    angle_deg: float
    length_m: float
    rolling_resistance: float
    air_drag_factor: float

    @property
    def elevation_m(self) -> float:
        return self.length_m * math.sin(math.radians(self.angle_deg))


CANDIDATES = [
    Metamaterial(
        name="Hydrogel composite (water desorption)",
        absorption_efficiency=0.60,
        storage_efficiency=0.55,
        extraction_efficiency=0.70,
        mass_loss_fraction_per_kj=0.0008,
        reset_energy_fraction=0.10,
    ),
    Metamaterial(
        name="Shape-memory alloy (Nitinol-class)",
        absorption_efficiency=0.75,
        storage_efficiency=0.65,
        extraction_efficiency=0.55,
        mass_loss_fraction_per_kj=0.00005,
        reset_energy_fraction=0.30,
    ),
    Metamaterial(
        name="Endothermic chemical composite",
        absorption_efficiency=0.70,
        storage_efficiency=0.75,
        extraction_efficiency=0.65,
        mass_loss_fraction_per_kj=0.0005,
        reset_energy_fraction=0.40,
    ),
    Metamaterial(
        name="Viscoelastic polymer baseline",
        absorption_efficiency=0.80,
        storage_efficiency=0.40,
        extraction_efficiency=0.50,
        mass_loss_fraction_per_kj=0.00001,
        reset_energy_fraction=0.05,
    ),
    Metamaterial(
        name="Hybrid hydrogel-SMA composite (target)",
        absorption_efficiency=0.78,
        storage_efficiency=0.70,
        extraction_efficiency=0.75,
        mass_loss_fraction_per_kj=0.0006,
        reset_energy_fraction=0.15,
    ),
]


SLOPES = [
    SlopeProfile("Gentle dirt path  ( 5 deg, 1000 m)",  5.0, 1000.0, 0.020, 0.01),
    SlopeProfile("Moderate cart road (15 deg,  500 m)", 15.0,  500.0, 0.030, 0.02),
    SlopeProfile("Steep mountain track (25 deg, 250 m)", 25.0,  250.0, 0.050, 0.03),
    SlopeProfile("Water flume / streambed (10 deg, 800 m)", 10.0, 800.0, 0.005, 0.05),
    SlopeProfile("Smooth rail/track (8 deg, 700 m)",     8.0,  700.0, 0.002, 0.02),
]


@dataclass
class CycleResult:
    material_name: str
    pe_kj: float
    rolling_loss_kj: float
    drag_loss_kj: float
    available_kj: float
    absorbed_kj: float
    stored_kj: float
    extracted_kj: float
    mass_loss_kg: float
    ascent_mass_kg: float
    ascent_metabolic_kj: float
    reset_kj: float
    net_useful_kj: float
    eroi_human: float
    cycle_efficiency_pct: float


def slope_descent_energy(mass_kg, slope):
    """PE released and losses along the incline.

    Rolling-resistance work = Crr * m * g * cos(theta) * L.
    Air drag is modeled as a fixed fraction of PE (simple stand-in for
    velocity-dependent drag integrated over the roll).
    """
    theta = math.radians(slope.angle_deg)
    pe_kj = mass_kg * G * slope.elevation_m / 1000.0
    rolling_loss = slope.rolling_resistance * mass_kg * G * math.cos(theta) * slope.length_m / 1000.0
    drag_loss = pe_kj * slope.air_drag_factor
    available = max(0.0, pe_kj - rolling_loss - drag_loss)
    return pe_kj, rolling_loss, drag_loss, available


def simulate_cycle(material, mass_kg, elevation_m, slope=None):
    if slope is not None:
        pe_kj, rolling_loss, drag_loss, available = slope_descent_energy(mass_kg, slope)
        ascent_elev = slope.elevation_m
    else:
        pe_kj = mass_kg * G * elevation_m / 1000.0
        rolling_loss = 0.0
        drag_loss = 0.0
        available = pe_kj
        ascent_elev = elevation_m

    absorbed = available * material.absorption_efficiency
    stored = absorbed * material.storage_efficiency
    extracted = stored * material.extraction_efficiency

    mass_loss = mass_kg * material.mass_loss_fraction_per_kj * extracted
    mass_loss = min(mass_loss, mass_kg * 0.5)
    ascent_mass = mass_kg - mass_loss

    reset_kj = extracted * material.reset_energy_fraction
    ascent_mech = ascent_mass * G * ascent_elev / 1000.0
    ascent_metabolic = ascent_mech / HUMAN_METABOLIC_EFFICIENCY

    net_useful = extracted - reset_kj
    eroi = net_useful / ascent_metabolic if ascent_metabolic > 0 else 0
    eff = (net_useful / pe_kj * 100.0) if pe_kj > 0 else 0

    return CycleResult(
        material_name=material.name,
        pe_kj=pe_kj,
        rolling_loss_kj=rolling_loss,
        drag_loss_kj=drag_loss,
        available_kj=available,
        absorbed_kj=absorbed,
        stored_kj=stored,
        extracted_kj=extracted,
        mass_loss_kg=mass_loss,
        ascent_mass_kg=ascent_mass,
        ascent_metabolic_kj=ascent_metabolic,
        reset_kj=reset_kj,
        net_useful_kj=net_useful,
        eroi_human=eroi,
        cycle_efficiency_pct=eff,
    )


def daily_throughput(material, mass_kg, elevation_m, cycles_per_day, slope=None):
    s = simulate_cycle(material, mass_kg, elevation_m, slope=slope)
    return {
        "material": material.name,
        "daily_extracted_kj": s.extracted_kj * cycles_per_day,
        "daily_net_useful_kj": s.net_useful_kj * cycles_per_day,
        "daily_human_cost_kj": s.ascent_metabolic_kj * cycles_per_day,
        "daily_kwh": s.net_useful_kj * cycles_per_day / 3600.0,
        "eroi_human": s.eroi_human,
        "cycle_efficiency_pct": s.cycle_efficiency_pct,
    }


def slope_angle_sweep(material, mass_kg, length_m, rolling_resistance, air_drag_factor, angles_deg):
    """How EROI varies with slope angle holding incline length constant."""
    rows = []
    for a in angles_deg:
        sp = SlopeProfile(f"sweep_{a}", a, length_m, rolling_resistance, air_drag_factor)
        r = simulate_cycle(material, mass_kg, sp.elevation_m, slope=sp)
        rows.append((a, sp.elevation_m, r.pe_kj, r.rolling_loss_kj + r.drag_loss_kj,
                     r.available_kj, r.extracted_kj, r.eroi_human, r.cycle_efficiency_pct))
    return rows


def parameter_sensitivity(material, mass_kg, elevation_m, slope=None):
    base = simulate_cycle(material, mass_kg, elevation_m, slope=slope).eroi_human
    out = {}
    fields = [
        "absorption_efficiency",
        "storage_efficiency",
        "extraction_efficiency",
        "mass_loss_fraction_per_kj",
        "reset_energy_fraction",
    ]
    for f in fields:
        orig = getattr(material, f)
        setattr(material, f, orig * 1.30)
        hi = simulate_cycle(material, mass_kg, elevation_m, slope=slope).eroi_human
        setattr(material, f, orig * 0.70)
        lo = simulate_cycle(material, mass_kg, elevation_m, slope=slope).eroi_human
        setattr(material, f, orig)
        out[f] = {"low": lo, "base": base, "high": hi, "range": hi - lo}
    return out


if __name__ == "__main__":
    MASS = 50.0
    BASELINE_ELEV = 300.0
    CYCLES = 6
    target = CANDIDATES[-1]

    print("=" * 74)
    print("GRAVITY BATTERY METAMATERIAL SIMULATOR -- SLOPE ROLLING")
    print("=" * 74)
    print(f"  Mass: {MASS} kg   Cycles/day: {CYCLES}")
    print(f"  Target: {target.name}")
    print()

    print("-" * 74)
    print("FREE-DESCENT BASELINE (no losses, 300 m drop)")
    print("-" * 74)
    r = simulate_cycle(target, MASS, BASELINE_ELEV)
    d = daily_throughput(target, MASS, BASELINE_ELEV, CYCLES)
    print(f"  PE: {r.pe_kj:7.2f} kJ   available: {r.available_kj:7.2f} kJ")
    print(f"  extracted: {r.extracted_kj:7.2f} kJ   net useful: {r.net_useful_kj:7.2f} kJ")
    print(f"  EROI: {r.eroi_human:5.2f}   cycle eff: {r.cycle_efficiency_pct:5.1f}%   daily kWh: {d['daily_kwh']:5.3f}")
    print()

    print("=" * 74)
    print("SLOPE-ROLLING DESCENT")
    print("=" * 74)
    for slope in SLOPES:
        r = simulate_cycle(target, MASS, slope.elevation_m, slope=slope)
        d = daily_throughput(target, MASS, slope.elevation_m, CYCLES, slope=slope)
        loss_pct = (r.rolling_loss_kj + r.drag_loss_kj) / r.pe_kj * 100.0 if r.pe_kj > 0 else 0.0
        print()
        print(f"  {slope.name}")
        print(f"    elevation drop:    {slope.elevation_m:7.2f} m")
        print(f"    gross PE:          {r.pe_kj:7.2f} kJ")
        print(f"    rolling loss:      {r.rolling_loss_kj:7.2f} kJ")
        print(f"    drag loss:         {r.drag_loss_kj:7.2f} kJ")
        print(f"    total descent loss:{r.rolling_loss_kj + r.drag_loss_kj:7.2f} kJ ({loss_pct:4.1f}% of PE)")
        print(f"    KE at bottom:      {r.available_kj:7.2f} kJ")
        print(f"    extracted:         {r.extracted_kj:7.2f} kJ")
        print(f"    net useful:        {r.net_useful_kj:7.2f} kJ")
        print(f"    ascent labor:      {r.ascent_metabolic_kj:7.2f} kJ  ({r.ascent_mass_kg:.2f} kg up {slope.elevation_m:.0f} m)")
        print(f"    EROI (human):      {r.eroi_human:7.2f}")
        print(f"    cycle eff:         {r.cycle_efficiency_pct:6.1f} %")
        print(f"    daily kWh:         {d['daily_kwh']:7.3f}")

    print()
    print("=" * 74)
    print("MATERIAL COMPARISON ON MODERATE CART ROAD (15 deg, 500 m)")
    print("=" * 74)
    mod = SLOPES[1]
    for m in CANDIDATES:
        r = simulate_cycle(m, MASS, mod.elevation_m, slope=mod)
        d = daily_throughput(m, MASS, mod.elevation_m, CYCLES, slope=mod)
        print(f"  {m.name:46s}  EROI {r.eroi_human:5.2f}   eff {r.cycle_efficiency_pct:5.1f}%   {d['daily_kwh']:5.3f} kWh/d")

    print()
    print("=" * 74)
    print("SLOPE-ANGLE SWEEP (target material, 500 m incline, Crr=0.03, drag=0.02)")
    print("=" * 74)
    print(f"  {'angle':>6}  {'drop':>7}  {'PE':>8}  {'loss':>8}  {'avail':>8}  {'extract':>8}  {'EROI':>6}  {'eff%':>6}")
    rows = slope_angle_sweep(target, MASS, 500.0, 0.03, 0.02,
                             [2, 5, 10, 15, 20, 25, 30, 40, 50, 60])
    for a, h, pe, loss, avail, ext, eroi, eff in rows:
        print(f"  {a:5.0f}d  {h:6.1f}m  {pe:6.2f}kJ  {loss:6.2f}kJ  {avail:6.2f}kJ  {ext:6.2f}kJ  {eroi:5.2f}   {eff:5.1f}")
