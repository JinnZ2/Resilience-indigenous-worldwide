"""gravity_battery_metamaterial_sim.py

Simulator for a hypothetical metamaterial gravity battery.
Material descends a gradient. Internal mechanisms absorb kinetic
energy without transferring it to the substrate. Stored energy is
extracted at the bottom; extraction reduces transport mass. Ascent
is lighter than descent.

CC0. Standard library only.
"""

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


@dataclass
class CycleResult:
    material_name: str
    pe_kj: float
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


def simulate_cycle(material, mass_kg, elevation_m):
    pe_kj = mass_kg * G * elevation_m / 1000.0
    absorbed = pe_kj * material.absorption_efficiency
    stored = absorbed * material.storage_efficiency
    extracted = stored * material.extraction_efficiency

    mass_loss = mass_kg * material.mass_loss_fraction_per_kj * extracted
    mass_loss = min(mass_loss, mass_kg * 0.5)
    ascent_mass = mass_kg - mass_loss

    reset_kj = extracted * material.reset_energy_fraction
    ascent_mech = ascent_mass * G * elevation_m / 1000.0
    ascent_metabolic = ascent_mech / HUMAN_METABOLIC_EFFICIENCY

    net_useful = extracted - reset_kj
    eroi = net_useful / ascent_metabolic if ascent_metabolic > 0 else 0
    eff = (net_useful / pe_kj * 100.0) if pe_kj > 0 else 0

    return CycleResult(
        material_name=material.name,
        pe_kj=pe_kj,
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


def daily_throughput(material, mass_kg, elevation_m, cycles_per_day):
    s = simulate_cycle(material, mass_kg, elevation_m)
    return {
        "material": material.name,
        "daily_extracted_kj": s.extracted_kj * cycles_per_day,
        "daily_net_useful_kj": s.net_useful_kj * cycles_per_day,
        "daily_human_cost_kj": s.ascent_metabolic_kj * cycles_per_day,
        "daily_kwh": s.net_useful_kj * cycles_per_day / 3600.0,
        "eroi_human": s.eroi_human,
        "cycle_efficiency_pct": s.cycle_efficiency_pct,
    }


def parameter_sensitivity(material, mass_kg, elevation_m):
    base = simulate_cycle(material, mass_kg, elevation_m).eroi_human
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
        hi = simulate_cycle(material, mass_kg, elevation_m).eroi_human
        setattr(material, f, orig * 0.70)
        lo = simulate_cycle(material, mass_kg, elevation_m).eroi_human
        setattr(material, f, orig)
        out[f] = {"low": lo, "base": base, "high": hi, "range": hi - lo}
    return out


if __name__ == "__main__":
    MASS = 50.0
    ELEV = 300.0
    CYCLES = 6

    print("=" * 70)
    print("GRAVITY BATTERY METAMATERIAL SIMULATOR")
    print("=" * 70)
    print(f"  Mass: {MASS} kg   Elevation: {ELEV} m   Cycles/day: {CYCLES}")
    print()

    pe = MASS * G * ELEV / 1000.0
    print(f"  PE per descent: {pe:7.2f} kJ")
    print(f"  PE per day:     {pe * CYCLES:7.2f} kJ")
    print()

    for m in CANDIDATES:
        r = simulate_cycle(m, MASS, ELEV)
        d = daily_throughput(m, MASS, ELEV, CYCLES)
        print("-" * 70)
        print(f"MATERIAL: {m.name}")
        print(f"  Absorbed:        {r.absorbed_kj:7.2f} kJ")
        print(f"  Stored:          {r.stored_kj:7.2f} kJ")
        print(f"  Extracted:       {r.extracted_kj:7.2f} kJ")
        print(f"  Mass loss:       {r.mass_loss_kg:7.3f} kg  ->  ascent {r.ascent_mass_kg:6.2f} kg")
        print(f"  Reset cost:      {r.reset_kj:7.2f} kJ")
        print(f"  Net useful:      {r.net_useful_kj:7.2f} kJ")
        print(f"  Ascent cost:     {r.ascent_metabolic_kj:7.2f} kJ")
        print(f"  EROI (human):    {r.eroi_human:7.2f} : 1")
        print(f"  Cycle eff:       {r.cycle_efficiency_pct:6.1f} %")
        print(f"  Daily kWh:       {d['daily_kwh']:7.3f}")
        print()

    print("=" * 70)
    print("PARAMETER SENSITIVITY (Hybrid hydrogel-SMA target)")
    print("=" * 70)
    sens = parameter_sensitivity(CANDIDATES[-1], MASS, ELEV)
    for p, v in sens.items():
        print(f"  {p}")
        print(f"    -30%: {v['low']:6.2f}   base: {v['base']:6.2f}   +30%: {v['high']:6.2f}   range: {v['range']:6.2f}")
