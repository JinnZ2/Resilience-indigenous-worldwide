# aluminum_contamination_sim

CC0. stdlib-only Python. No dependencies. No network. Runs on a phone.

## What it is

A measurement model for **where recycled-aluminium contamination injures people
first** as primary smelting capacity goes offline and recycled content rises in
products that were previously made from virgin metal.

It is not a prediction of the metals market. It is a **buffer-building tool**:
detect the injury vector before the rupture reaches the people with zero slack
to absorb it.

## The constraint geometry

```
primary smelting offline (Hormuz / Middle East)
        |
        v
recycled fraction rises in finished goods
        |
        v  contaminants carry over: Fe Si Cu Pb Cd Mn Zn
        |
        +--> FOOD_CAN   : Pb/Cd migration, Cu pinhole corrosion   (ingestion)
        +--> ELECTRICAL : Mn/Fe conductivity collapse -> fire     (resistive heat)
        +--> MEDICAL    : Pb/Cd leaching, sterilization failure    (implant/ingest)
        +--> STRUCTURAL : Fe embrittlement (highest tolerance)     (fracture)
        |
        v  routed through regional channel:
           import_dependency x (1-qc_capacity) x price_pressure x (1-buffer)
        |
        v
   exposure_weighted_risk_index (EWRI) per region
```

The channel multiplier is the load-routing layer: a contaminated batch only
becomes a human-injury event when it lands somewhere with no detection, no
upstream leverage, and no buffer. **The channel matters more than the source**
(see CLAIM_TABLE C1, refuted-and-updated).

## Files

```
contaminants.py   physics: carryover ranges, injury thresholds, conductivity model
regions.py        regional vulnerability profiles + channel multiplier
cascade.py        Monte Carlo engine: batches x regions -> EWRI
field_test.py     escalating field protocol (spot -> conductivity -> XRF) -> GO/CAUTION/STOP
run_hotspot_scan.py   entry point + report + local-overlay + JSON out
CLAIM_TABLE.contamination.json   falsifiable predictions, one already refuted+updated
hotspot_scanner.html  browser version -- no Python, for field deployment
```

## Run

```
python3 run_hotspot_scan.py
python3 run_hotspot_scan.py --batches 50000 --seed 7
python3 run_hotspot_scan.py --json > scan.json
python3 run_hotspot_scan.py --local regions_local.json
```

## Override with ground truth

Every regional number is a first-pass estimate. Overlay measured values:

```json
{
  "cuba": {"qc_capacity": 0.10, "recycled_fraction": 0.92, "source": "field_2026"}
}
```

```
python3 run_hotspot_scan.py --local regions_local.json
```

Provenance preserved via the `source` tag. The model is meant to be corrected
by the people running it.

## Field protocol summary

```
TIER 1  spot test    $0      visual + magnet (Fe) + acid spot (Cu/Pb reactivity)
TIER 2  conductivity  ~$50    decisive for ELECTRICAL only (IACS floor 55%)
TIER 3  handheld XRF   ~$1.5-3k   quantitative per-element -> full verdict
```

Hard rule: **Pb and Cd are invisible to tier-1 tests.** Any food or medical use
requires tier-3 XRF. A clean-looking batch can carry lethal lead from painted or
soldered scrap stock.

## Methodology

If field data refutes a claim in CLAIM_TABLE, **update the claim — do not retune
the sim to fit.** C1 has already been refuted and updated this way.
