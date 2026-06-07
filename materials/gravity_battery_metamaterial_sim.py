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

Mass loss is intrinsic to the material: kg released per kJ extracted
(rather than a coefficient on total mass). This keeps the model
well-behaved when scaling from a 50 kg daypack up to a multi-tonne
rail cart -- the same material chemistry applies at every scale.

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
    mass_loss_kg_per_kj: float
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


@dataclass
class Application:
    name: str
    kwh_per_day: float


@dataclass
class HaulScenario:
    name: str
    mass_kg: float
    cycles_per_day: int
    slope_index: int
    note: str


CANDIDATES = [
    Metamaterial("Hydrogel composite (water desorption)",
                 0.60, 0.55, 0.70, 0.040, 0.10),
    Metamaterial("Shape-memory alloy (Nitinol-class)",
                 0.75, 0.65, 0.55, 0.0025, 0.30),
    Metamaterial("Endothermic chemical composite",
                 0.70, 0.75, 0.65, 0.025, 0.40),
    Metamaterial("Viscoelastic polymer baseline",
                 0.80, 0.40, 0.50, 0.0005, 0.05),
    Metamaterial("Hybrid hydrogel-SMA composite (target)",
                 0.78, 0.70, 0.75, 0.030, 0.15),
]


SLOPES = [
    SlopeProfile("Gentle dirt path  ( 5 deg, 1000 m)",       5.0, 1000.0, 0.020, 0.01),
    SlopeProfile("Moderate cart road (15 deg,  500 m)",     15.0,  500.0, 0.030, 0.02),
    SlopeProfile("Steep mountain track (25 deg,  250 m)",   25.0,  250.0, 0.050, 0.03),
    SlopeProfile("Water flume / streambed (10 deg, 800 m)", 10.0,  800.0, 0.005, 0.05),
    SlopeProfile("Smooth rail/track  ( 8 deg,  700 m)",      8.0,  700.0, 0.002, 0.02),
    SlopeProfile("Engineered rail   (10 deg, 1150 m)",      10.0, 1150.0, 0.001, 0.02),
]


# Typical household DC loads, kWh per day. Tuned to match the
# "survival-grade" use cases discussed in the design brief.
APPLICATIONS = [
    Application("LED household lighting (4 bulbs, 4 h)",         0.08),
    Application("Radio + phone charging",                        0.10),
    Application("Communications (HF/VHF radio, day use)",        0.20),
    Application("Water pumping (head tank, daily)",              0.20),
    Application("Small appliance bank (sewing/mill/mixer)",      0.30),
    Application("Tool operation (drill, grinder, intermittent)", 0.60),
    Application("Refrigeration of essentials (DC chest)",        0.80),
    Application("Workshop / heavier intermittent loads",         1.20),
]


SCENARIOS = [
    HaulScenario("Solo human carry (daypack)",     50.0, 6, 1, "one person, moderate cart road"),
    HaulScenario("One-person rail cart",          200.0, 6, 4, "smooth rail, push/pull return"),
    HaulScenario("Single-ox cart on rail",       1500.0, 6, 4, "draft animal, loaded cart"),
    HaulScenario("Two-ox community cart",        3000.0, 5, 4, "team of oxen, fewer cycles"),
    HaulScenario("Engineered haul, long rail",   5000.0, 6, 5, "winch/animal team, engineered rail"),
    HaulScenario("Heavy engineered system",      8000.0, 5, 5, "large loaded car, long rail"),
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

    mass_loss = min(material.mass_loss_kg_per_kj * extracted, mass_kg * 0.5)
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


def application_coverage(daily_kwh):
    used = 0.0
    covered = []
    remaining = []
    for app in APPLICATIONS:
        if used + app.kwh_per_day <= daily_kwh + 1e-9:
            covered.append(app)
            used += app.kwh_per_day
        else:
            remaining.append(app)
    return covered, used, daily_kwh - used, remaining


def required_mass_for_target(material, target_kwh, cycles_per_day, slope):
    trial = daily_throughput(material, 100.0, slope.elevation_m, cycles_per_day, slope=slope)
    if trial["daily_kwh"] <= 0:
        return float("inf")
    return target_kwh / trial["daily_kwh"] * 100.0


def slope_angle_sweep(material, mass_kg, length_m, rolling_resistance, air_drag_factor, angles_deg):
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
    fields = ["absorption_efficiency", "storage_efficiency", "extraction_efficiency",
              "mass_loss_kg_per_kj", "reset_energy_fraction"]
    for f in fields:
        orig = getattr(material, f)
        setattr(material, f, orig * 1.30)
        hi = simulate_cycle(material, mass_kg, elevation_m, slope=slope).eroi_human
        setattr(material, f, orig * 0.70)
        lo = simulate_cycle(material, mass_kg, elevation_m, slope=slope).eroi_human
        setattr(material, f, orig)
        out[f] = {"low": lo, "base": base, "high": hi, "range": hi - lo}
    return out


def print_scenario(material, scenario):
    slope = SLOPES[scenario.slope_index]
    r = simulate_cycle(material, scenario.mass_kg, slope.elevation_m, slope=slope)
    d = daily_throughput(material, scenario.mass_kg, slope.elevation_m,
                         scenario.cycles_per_day, slope=slope)
    covered, used, surplus, remaining = application_coverage(d["daily_kwh"])

    print()
    print(f"  {scenario.name}")
    print(f"    ({scenario.note})")
    print(f"    mass {scenario.mass_kg:>5.0f} kg | drop {slope.elevation_m:5.1f} m | cycles {scenario.cycles_per_day}/day | {slope.name}")
    print(f"    PE/cycle {r.pe_kj:7.1f} kJ -> net/cycle {r.net_useful_kj:7.1f} kJ -> DAILY NET {d['daily_kwh']:6.3f} kWh   eff {r.cycle_efficiency_pct:5.1f}%")
    if covered:
        print(f"    covers ({used:.2f} kWh, surplus {surplus:+.2f} kWh):")
        for app in covered:
            print(f"      [x] {app.name:50s} {app.kwh_per_day:5.2f} kWh")
    else:
        print(f"    covers no full application ({d['daily_kwh']:.3f} kWh < smallest app at {APPLICATIONS[0].kwh_per_day:.2f} kWh)")
    if remaining:
        nxt = remaining[0]
        print(f"    next:  [ ] {nxt.name:50s} {nxt.kwh_per_day:5.2f} kWh  (gap {nxt.kwh_per_day - surplus:+.2f} kWh)")


if __name__ == "__main__":
    target = CANDIDATES[-1]
    SURVIVAL_TARGET_KWH = 3.0

    print("=" * 80)
    print("GRAVITY BATTERY -- HAUL SCENARIOS AND APPLICATION COVERAGE")
    print("=" * 80)
    print(f"  Target material: {target.name}")
    print(f"  Survival-grade design target: {SURVIVAL_TARGET_KWH:.1f} kWh / day")
    print()

    print("APPLICATIONS REFERENCE (typical household DC loads)")
    print("-" * 80)
    total = 0.0
    for app in APPLICATIONS:
        total += app.kwh_per_day
        print(f"  {app.name:52s} {app.kwh_per_day:5.2f} kWh   cum {total:5.2f}")
    print(f"  {'(full stack):':52s} {'':5s}        {total:5.2f}")
    print()

    print("=" * 80)
    print("HAUL SCENARIOS")
    print("=" * 80)
    for sc in SCENARIOS:
        print_scenario(target, sc)

    print()
    print("=" * 80)
    print(f"REVERSE: WORKING MASS NEEDED PER CYCLE TO HIT {SURVIVAL_TARGET_KWH:.1f} kWh/DAY")
    print("=" * 80)
    print(f"  {'slope':46s}  {'cycles':>6}  {'mass needed':>14}")
    for slope in SLOPES:
        for cycles in (4, 6):
            m = required_mass_for_target(target, SURVIVAL_TARGET_KWH, cycles, slope)
            print(f"  {slope.name:46s}  {cycles:>6}  {m:>11.0f} kg")

    print()
    print("=" * 80)
    print("HUMAN-LABOR CEILING NOTE")
    print("=" * 80)
    print(f"  Sustained human mechanical output: ~75 W * 8 h = 0.6 kWh/day per person.")
    print(f"  A {SURVIVAL_TARGET_KWH:.1f} kWh/day per-participant figure therefore requires either:")
    print(f"    - shared system serving many households,")
    print(f"    - draft animals or winches doing the mass uplift, or")
    print(f"    - natural-flow assist (water/wind moving mass uphill on its own).")
    print(f"  Solo human carry is honest but only delivers survival-grade lighting,")
    print(f"  not refrigeration or tools.")
