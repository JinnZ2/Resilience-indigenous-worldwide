"""
Export run histories as CSV for plotting / downstream use.
"""

import csv
import os

from resilience.boundary_waters.cascade import run_cascade

SCENARIOS = [
    ("protected",        "20-year withdrawal holds"),
    ("proceed",          "CRA reversal - mine operates"),
    ("tailings_failure", "Mine + tailings dam failure"),
]

FIELDS = [
    "year", "mine_active", "tailings_failed", "cumulative_waste_Mt",
    "sulfate_mg_l", "hg_ng_l", "methyl_hg_ng_l", "canada_sulfate_mg_l",
    "manoomin_acres_lost", "lake_trout_hg_ppm", "loon_mortality_frac",
    "forest_acres_lost", "amphibian_collapse",
    "wells_contaminated", "forced_migrants", "treaty_harvesters_displaced",
    "mine_jobs", "tourism_jobs_lost", "lumber_jobs_lost", "net_jobs",
    "lake_superior_hg_loading", "reservoir_km3_lost",
    "port_jobs_at_risk", "users_losing_safe_water",
    "total_breach_days", "ijc_referral_triggered",
    "trail_smelter_liability", "liability_npv_usd",
]

DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def export_all(output_dir=DEFAULT_OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    for key, label in SCENARIOS:
        hist = run_cascade(scenario=key)
        path = os.path.join(output_dir, f"output_{key}.csv")
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            for row in hist:
                w.writerow(row)
        print(f"  wrote {path}  ({len(hist)} rows)  -- {label}")


if __name__ == "__main__":
    export_all()
