# Model Results — 500-year Cascade

Source scenarios pulled directly from the upstream `boundary_waters`
repo (CC0) and reproduced by
`python -m resilience.boundary_waters.export`. Reference CSVs are
stored in `resilience/boundary_waters/data/`.

## Scenarios

| key | label | mine active? | tailings failure? |
|-----|-------|:------------:|:-----------------:|
| `protected` | 20-year withdrawal holds (status quo 2023) | no | no |
| `proceed` | CRA reversal → mine operates | yes, yr 5–25 | stochastic, 1.2%/yr |
| `tailings_failure` | Mine operates + Mount Polley-class event yr 12 | yes, yr 5–25 | yes, forced yr 12 |

## Peak impact (any year, 500-year horizon)

### `protected`
- peak sulfate: **0.0 mg/L**
- peak forced migrants: **0**
- peak wells poisoned: **0**
- peak forest lost: **0 acres**
- treaty harvesters displaced: **0**
- treaty liability NPV: **$0.00 B**

### `proceed`
- peak sulfate at border: **11.8 mg/L** — crosses manoomin
  threshold briefly but stays sub-lethal
- peak forced migrants: **3,107**
- peak wells contaminated: **3,059**
- peak forest lost: **13,748 acres**
- peak net jobs: **−13,440** (mine +700; tourism + lumber −14k)
- treaty harvesters displaced: partial (proportional to manoomin loss)

### `tailings_failure`
- peak sulfate at border: **58.8 mg/L** — past lethal threshold for
  manoomin, sustained **300+ years**
- peak forced migrants: **8,060**
- peak wells contaminated: **10,416**
- peak forest lost: **68,742 acres**
- peak net jobs: **−17,616**
- treaty harvesters displaced: **~8,700** (all enrolled members of
  Bois Forte + Grand Portage + Fond du Lac)
- treaty liability NPV: **$1.08 trillion** under Trail Smelter
  precedent

## Interpretation

The tailings-failure curve never drops back below the treaty
threshold within the 500-year simulation. That is the
thermodynamic signature of acid mine drainage:

1. ΔG for pyrite oxidation is strongly negative.
2. *Acidithiobacillus ferrooxidans* amplifies the abiotic rate by
   ~10⁶.
3. Canadian Shield granite provides essentially zero carbonate
   buffering (`CARBONATE_BUFFER_EQ_KG_M2 = 0.04`).

Once the reaction is initiated, it runs until the sulfide substrate
is consumed, which takes centuries. There is no engineered remedy
that terminates this reaction on human timescales; "perpetual
treatment" is the industry-accepted euphemism.

## Known limitations (upstream notes)

- Monte Carlo over tailings failure timing (currently single-seed).
- Wildfire–AMD interaction (dry tailings + wildfire = airborne
  metal dispersal).
- Climate cascade: rising temperatures accelerate oxidation
  kinetics (~2× per 10 °C).
- Port layer simplified — Duluth-Superior coupling needs a
  separate St. Louis River tributary pathway.
- Boundary Waters Treaty enforcement assumed on a per-year breach
  basis; real IJC referral dynamics are more political than the
  `IJC_TRIGGER_DAYS = 90` threshold captures.
