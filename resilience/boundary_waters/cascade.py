"""
Cascade engine. Forcing propagates L0 -> L5 each year.
Tracks threshold crossings, self-amplifying loops, cumulative damage.
"""

import random

from resilience.boundary_waters.constants import (
    MINE_JOB_DURATION_YR,
    MINE_START_YEAR,
    ORE_TONNES_ANNUAL,
    SIM_YEARS,
    TAILINGS_FAILURE_P,
    WASTE_ROCK_RATIO,
)
from resilience.boundary_waters.layers import (
    chemistry_layer,
    community_layer,
    ecology_layer,
    hydrology_layer,
    intl_law_layer,
    port_layer,
)


def run_cascade(seed=42, scenario="proceed"):
    """
    scenario: "proceed"   -> mine permitted and operates
    "protected" -> CRA reversal overturned, 20-yr withdrawal holds
    "tailings_failure" -> forces Mount Polley-class event yr 12
    """
    random.seed(seed)
    history = []
    cumulative_waste = 0.0
    breach_days = 0
    tailings_failed = False

    for yr in range(SIM_YEARS):
        # ── Mine operational state ────────────────────────────
        if scenario == "protected":
            mine_active = False
        else:
            mine_active = MINE_START_YEAR <= yr < (MINE_START_YEAR + MINE_JOB_DURATION_YR)

        # Waste rock accumulation (persists after closure)
        if mine_active:
            annual_waste = ORE_TONNES_ANNUAL * WASTE_ROCK_RATIO
            cumulative_waste += annual_waste

        # ── Stochastic tailings dam failure ───────────────────
        # Mount Polley (2014), Brumadinho (2019): tailings dams fail.
        # Historical rate: ~1.2% per year per active major facility.
        if mine_active and not tailings_failed:
            if scenario == "tailings_failure" and yr == MINE_START_YEAR + 7:
                tailings_failed = True
            elif random.random() < TAILINGS_FAILURE_P:
                tailings_failed = True

        if tailings_failed and mine_active:
            # Sudden release of ~10 yr worth of tailings
            cumulative_waste += ORE_TONNES_ANNUAL * WASTE_ROCK_RATIO * 10

        # ── Layer propagation ─────────────────────────────────
        chem  = chemistry_layer(yr, mine_active, cumulative_waste)
        hydro = hydrology_layer(chem, max(0, yr - MINE_START_YEAR))
        ecol  = ecology_layer(hydro, max(0, yr - MINE_START_YEAR))
        comm  = community_layer(hydro, ecol, mine_active, max(0, yr - MINE_START_YEAR))
        port  = port_layer(hydro, ecol, max(0, yr - MINE_START_YEAR))
        intl  = intl_law_layer(hydro, yr, breach_days)
        breach_days = intl["total_breach_days"]

        history.append({
            "year": yr,
            "mine_active": mine_active,
            "tailings_failed": tailings_failed,
            "cumulative_waste_Mt": cumulative_waste / 1e6,
            **chem, **hydro, **ecol, **comm, **port, **intl,
        })

    return history


def summarize(history, label):
    """Extract headline metrics at year 50, 100, 500."""
    snapshot_yrs = [20, 50, 100, 499]
    print(f"\n{'═'*62}")
    print(f"  SCENARIO: {label}")
    print(f"{'═'*62}")
    print(f"{'Year':>5} {'SO4 mg/L':>10} {'Hg ng/L':>9} {'Manoomin':>10} "
          f"{'NetJobs':>9} {'Migrants':>9} {'Treaty?':>8}")
    print("-" * 62)
    for yr in snapshot_yrs:
        h = history[yr]
        breach = "BREACH" if h["trail_smelter_liability"] else ("IJC" if h["ijc_referral_triggered"] else "ok")
        print(f"{yr:>5} {h['sulfate_mg_l']:>10.2f} {h['hg_ng_l']:>9.3f} "
              f"{h['manoomin_acres_lost']:>10.0f} {h['net_jobs']:>9} "
              f"{h['forced_migrants']:>9} {breach:>8}")


def main():
    scenarios = [
        ("protected",        "20-year withdrawal holds (status quo 2023)"),
        ("proceed",          "CRA reversal -> mine operates"),
        ("tailings_failure", "Mine operates + Mount Polley-class dam failure"),
    ]
    all_runs = {}
    for key, label in scenarios:
        hist = run_cascade(scenario=key)
        all_runs[key] = hist
        summarize(hist, label)

    # ── Peak impact comparison ────────────────────────────────
    print(f"\n{'═'*62}")
    print("  PEAK IMPACT (any year, 500-yr horizon)")
    print(f"{'═'*62}")
    for key, label in scenarios:
        h = all_runs[key]
        peak_so4 = max(r["sulfate_mg_l"] for r in h)
        peak_migr = max(r["forced_migrants"] for r in h)
        peak_forest = max(r["forest_acres_lost"] for r in h)
        peak_wells = max(r["wells_contaminated"] for r in h)
        peak_liability = max(r["liability_npv_usd"] for r in h)
        peak_treaty = max(r["treaty_harvesters_displaced"] for r in h)
        print(f"\n  {label}")
        print(f"    peak sulfate        : {peak_so4:>10.1f} mg/L  (toxic@10, lethal@50)")
        print(f"    peak forced migrants: {peak_migr:>10,}")
        print(f"    peak wells poisoned : {peak_wells:>10,}")
        print(f"    peak forest lost    : {peak_forest:>10,.0f} acres")
        print(f"    treaty harvesters   : {peak_treaty:>10,}  (1854 Treaty bands)")
        print(f"    treaty liability NPV: ${peak_liability/1e9:>9.2f} B")


if __name__ == "__main__":
    main()
