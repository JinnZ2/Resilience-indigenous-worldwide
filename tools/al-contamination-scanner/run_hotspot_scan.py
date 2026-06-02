"""
run_hotspot_scan.py  --  CC0

Main entry point. Runs the full Monte Carlo hotspot scan and emits a
constraint-frame report: ranked exposure-weighted risk index per region,
dominant injury vector per product class, and the field-test escalation for
the worst vector.

USAGE
  python3 run_hotspot_scan.py
  python3 run_hotspot_scan.py --batches 50000 --seed 7
  python3 run_hotspot_scan.py --local regions_local.json   # overlay ground truth
  python3 run_hotspot_scan.py --json                        # machine-readable out

LOCAL OVERLAY (regions_local.json)
  {
    "cuba": {"qc_capacity": 0.10, "recycled_fraction": 0.92, "source": "field_2026"},
    ...
  }
  Any field present overwrites the first-pass estimate. Provenance preserved
  via the "source" tag.
"""

import argparse
import json
import sys

from cascade import run_scan
from regions import REGIONS, Region
from field_test import protocol, verdict_from_xrf
from contaminants import PRODUCT_CLASSES


def apply_local_overlay(path):
    with open(path) as f:
        overlay = json.load(f)
    for key, fields in overlay.items():
        if key not in REGIONS:
            print(f"# WARN: overlay key '{key}' not a known region, skipped", file=sys.stderr)
            continue
        r = REGIONS[key]
        for k, v in fields.items():
            if hasattr(r, k):
                setattr(r, k, v)
            else:
                print(f"# WARN: region '{key}' has no field '{k}'", file=sys.stderr)


def render_report(results):
    line = "=" * 74
    print(line)
    print("ALUMINIUM CONTAMINATION HOTSPOT SCAN  --  exposure_weighted_risk_index")
    print(line)
    print(f"{'rank':<5}{'region':<24}{'EWRI':>7}{'p95':>7}{'mult':>7}{'IACS%':>7}")
    print("-" * 74)
    for i, r in enumerate(results, 1):
        print(f"{i:<5}{r.name:<24}{r.ewri:>7.3f}{r.ewri_p95:>7.3f}"
              f"{r.multiplier:>7.2f}{r.mean_iacs:>7.1f}")
    print(line)
    print("DOMINANT INJURY VECTOR per region per product class")
    print("-" * 74)
    header = f"{'region':<24}" + "".join(f"{pc:>12}" for pc in PRODUCT_CLASSES)
    print(header)
    for r in results:
        row = f"{r.name:<24}"
        for pc in PRODUCT_CLASSES:
            sev = r.per_product[pc]
            dom = r.dominant_vector[pc]
            row += f"{dom}:{sev:.2f}".rjust(12)
        print(row)
    print(line)

    # worst region -> field protocol for its worst product class
    worst = results[0]
    worst_pc = max(worst.per_product.items(), key=lambda kv: kv[1])[0]
    print(f"FIELD PROTOCOL  (worst hotspot: {worst.name} / {worst_pc})")
    print("-" * 74)
    p = protocol(worst_pc)
    print(f"  ingestion_risk      : {p['ingestion_risk']}")
    print(f"  tier2 decisive      : {p['tier2_conductivity_decisive']}")
    print(f"  tier3 req (ingest)  : {p['tier3_required_for_ingestion']}")
    print(f"  escalation_rule     : {p['escalation_rule']}")
    print("  tier1 spot test:")
    for ln in p["tier1_spot"]:
        print(f"     {ln}")
    print(line)


def to_json(results):
    return json.dumps([
        {
            "rank": i + 1,
            "key": r.key, "name": r.name,
            "ewri": round(r.ewri, 4), "ewri_p95": round(r.ewri_p95, 4),
            "multiplier": round(r.multiplier, 3),
            "mean_iacs": round(r.mean_iacs, 2),
            "per_product": {pc: round(r.per_product[pc], 3) for pc in PRODUCT_CLASSES},
            "dominant_vector": r.dominant_vector,
        }
        for i, r in enumerate(results)
    ], indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--local", type=str, default=None,
                    help="path to regions_local.json overlay")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if args.local:
        apply_local_overlay(args.local)

    results = run_scan(n_batches=args.batches, seed=args.seed)

    if args.json:
        print(to_json(results))
    else:
        render_report(results)


if __name__ == "__main__":
    main()
