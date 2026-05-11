# Boundary Waters — Sulfide Mine Cascade

This folder integrates the `boundary_waters` cascade model from
[JinnZ2/earth-systems-physics](https://github.com/JinnZ2/earth-systems-physics/tree/main/boundary_waters)
(CC0) into the Resilience-indigenous-worldwide repo as a new threat case
study alongside Greenland and Venezuela.

## Context

A Chilean multinational (Antofagasta PLC, via its U.S. subsidiary Twin
Metals Minnesota) has sought to build a copper-nickel sulfide mine at
the headwaters of the Boundary Waters Canoe Area Wilderness (BWCA) in
the Superior National Forest. The proposed mine sits in the Rainy River
watershed — water flows north, directly into the BWCA, Voyageurs
National Park, and across the U.S.-Canada border into Quetico
Provincial Park and the Rainy–Lake of the Woods system.

In 2023, the Department of the Interior withdrew 225,378 acres of the
Superior National Forest from mineral leasing for 20 years. Antofagasta
has since sued to reverse that withdrawal, and Congress has introduced
multiple bills (including a 2025 Congressional Review Act resolution)
to overturn it.

The question the model answers: **what happens to the native communities
of the 1854 Treaty ceded territory if the withdrawal is reversed?**

## Files

- [`indigenous-impact.md`](indigenous-impact.md) — focused analysis of
  impact on the Bois Forte, Grand Portage, and Fond du Lac Bands of Lake
  Superior Chippewa, and on manoomin (wild rice) as protected property.
- [`legal-framework.md`](legal-framework.md) — 1854 Treaty usufructuary
  rights, Boundary Waters Treaty of 1909, Trail Smelter precedent,
  UNDRIP Article 29, FPIC, and SEC/CSDDD disclosure triggers.
- [`model-results.md`](model-results.md) — scenario outputs and peak
  impacts from the 500-year cascade simulation.

## Running the model

```bash
python -m resilience.boundary_waters.cascade       # prints summary
python -m resilience.boundary_waters.export        # writes CSVs
```

Source constants and layer definitions live in
`resilience/boundary_waters/` — ported with no algorithmic changes from
the upstream repo. Reference outputs (`output_protected.csv`,
`output_proceed.csv`, `output_tailings_failure.csv`) are stored in
`resilience/boundary_waters/data/` for reproducibility checks.
