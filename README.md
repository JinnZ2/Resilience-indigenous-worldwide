# Resilience-indigenous-worldwide

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

Helpful resources 

## Case studies

- [`docs/greenland/`](docs/greenland/) — Greenland-specific analysis.
- [`docs/venezuela/`](docs/venezuela/) — Venezuela-specific analysis.
- [`docs/boundary-waters/`](docs/boundary-waters/) — Twin Metals
  sulfide-mine cascade against the 1854 Treaty Bands (Bois Forte,
  Grand Portage, Fond du Lac) and the Boundary Waters Treaty of 1909.
  Ported model from
  [JinnZ2/earth-systems-physics/boundary_waters](https://github.com/JinnZ2/earth-systems-physics/tree/main/boundary_waters).
- [`docs/strategy/`](docs/strategy/) — cross-cutting legal and media
  strategies.

## Computational modeling: `architecture/`

Standalone, stdlib-only Python modules. Each runs with
`python -m architecture.<module_name>` and prints a structured report.

- **`biome_cooperation_layer.py`** — models cross-border cooperation
  as a fourth cascade lever (alongside variances, institutional
  relaxation, and village closure). Seven channels anchored to real
  historical analogues — Rhine ICPR, HELCOM Baltic, ITPGRFA Plant
  Treaty, Svalbard Seed Vault, WHO 2006 sanitation guidelines, FAO
  Locust Watch / FEWS NET, Mesoamerican Biological Corridor — with
  citations and skeptical/central/optimistic plausibility ranges.
- **`historical_analogue.py`** — inverts the cascade audit's output:
  instead of a single mortality number, matches the current situation
  in log-space against a famine corpus (Bengal 1943, Ireland, Great
  Leap Forward, Ethiopia, North Korea, Somalia, Tigray, Yemen, Sudan,
  2008, Ukraine 2022, Sahel 1972-74) and a cooperation corpus
  (Montreal, Marshall Plan, Berlin Airlift, smallpox eradication, WFP,
  ITPGRFA, Rhine, Wadden Sea, Mesoamerican Corridor). Every figure is
  a documented historical range with citation.
- **`audit_authority_scope.py`** — models audit authority as itself
  scope-conditional. Higher tiers of government hold first right to
  audit a community's crisis response only inside a declared resource
  and time window; if they fail to exercise it, the next-tier-down
  audit becomes the legal record.
- **`biological_response_infrastructure.py`** — distributed-response
  infrastructure modeled on biological immune/metabolic systems:
  local nodes sense damage and respond immediately, central authority
  validates afterward. Inverts the current permit-before-respond
  pattern that lets local systems degrade while waiting for approval.
- **`corporate_charter_scope_audit.py`** — treats corporate operating
  privileges as scope-conditional: a charter is a conditional
  permission, not a permanent grant. When a corporation refuses to
  respond to a local crisis it has profited from, the community's
  claim on its locally held resources supersedes the corporation's
  disposal logic for the duration of the crisis.
- **`hormuz_cascade_audit.py`** — thermodynamic + Earth-systems audit
  of the Hormuz fertilizer cascade, testing whether the published
  118M–225M excess-deaths claim is physically reachable. Calibrated
  against Sudan 2024 and Ukraine 2023 mortality anchors; structural
  ceiling sits at ~321M (30% of the 1.07B import-dependent population).
- **`institutional_bottleneck_audit.py`** — names the regulatory
  choke points (EPA 503, EU 86/278, MN 7080/7083, Codex, Manual
  Scavenging Act, WHO sanitation framing) that block the closed-loop
  N pathway. Quantifies lives-at-risk per month of regulatory
  inaction and pre-rebuts six "we didn't know" institutional defenses.
- **`monte_carlo_resilience_sim.py`** — stochastic comparison of
  distributed vs centralized crisis-response architectures under
  randomized scenarios. Same seed reproduces identical outcomes;
  reports survival, infrastructure preservation, cascade failures,
  trust, recovery time.
- **`regulatory_cascade_crosslink.py`** — bridges the institutional
  and cascade audits. Maps each regulatory choke point to its
  contribution to the cascade's `vulnerable_absorption` parameter and
  shows that single relaxations are invisible — the full regulatory
  stack must move to bring mortality below the structural ceiling.
- **`regulatory_scope_audit.py`** — audits regulations against their
  declared operating envelope. Every rule was written for a specific
  thermal, population, substrate, or infrastructure scope; when real
  conditions exit that envelope, the rule is outside its scope and
  enforcing it inverts the rule's original intent.
- **`region_presets.py`** — pre-built `Village` configurations for
  Greenland (coastal arctic), Venezuela (Orinoco basin), Burkina Faso
  (Sahel), and the India delta. Lets `village_n_closure` run
  out-of-box on regions the repository already covers.
- **`substrate_damage_audit.py`** — flags when behavioral and
  collapse-prediction models are trained on populations several
  generations into institutional damage rather than baseline human
  capacity. Encodes the cascade as falsifiable claims so measured
  fragility is not misread as biological universal.
- **`variance_pathway_templates.py`** — one-page emergency-variance
  request drafts (legal basis, requested action, finding of fact,
  calendar gate, safeguards) for each regulatory node named in
  `institutional_bottleneck_audit`. Pre-drafted so the planting-
  calendar deadline does not slip on paperwork.
- **`village_n_closure.py`** — village-scale nutrient-closure toolkit.
  Given population, planted crops, and locally available substrates,
  computes N/P/K need vs supply, deficits, and a priority-ranked
  dispatch sequence with composting/fermentation protocols.

Tests pinning the cascade-mortality calibration (Sudan 2024,
Ukraine 2023) live at `tests/test_cascade_audit.py`. Run with
`python -m pytest tests/test_cascade_audit.py`.

## Why This Matters

Indigenous communities on every continent face an accelerating pattern:
a corporation or state actor secures legal cover (a BIT clause, an ESG
certification, a peace-prize photo-op), then extracts resources while
regulatory and disclosure frameworks treat the resulting harm as an
externality. By the time the legal case is built, the damage is done.

This repository gives communities, lawyers, and researchers
computational tools to map the risk *before* the machinery moves —
and evidentiary frameworks to act *while* there is still time.

See [`docs/venezuela/`](docs/venezuela/) for legal templates including
the LP-squeeze shareholder notice and risk-assessment memos.

## Tools (`tools/`)

Standalone, offline-capable tools (CC0, stdlib-only unless noted):

- **[`al-contamination-scanner/`](tools/al-contamination-scanner/)** — Monte Carlo EWRI scanner for recycled-aluminum contamination risk across vulnerable regions. `python3 tools/al-contamination-scanner/run_hotspot_scan.py`
- **[`elder-value-claims/`](tools/elder-value-claims/)** — Falsifiable-claim protocol testing AI age bias and cross-cultural elder value. `python3 tools/elder-value-claims/run_all_claims.py`
- **[`guild-resilience/`](tools/guild-resilience/)** — Gaussian fitness model for 18 indigenous food guilds across a 4-axis environmental condition space.
- **[`human-food-grain-monitor/`](tools/human-food-grain-monitor/)** — dX/dt crop monitoring with Gaussian portfolio coverage by geographic cell.
- **[`oral-corpus/`](tools/oral-corpus/)** — Append-only, SHA-256-deduplicated corpus of oral knowledge segments with physics annotations.
- **[`warning-cycle-corpus/`](tools/warning-cycle-corpus/)** — Structured archive of indigenous climate-cycle warning stories.

## Computational modeling: `resilience/`

```python
from resilience.stress_model import StressPropagator, PropagationConfig
from resilience.network import CommunityNetwork

net = CommunityNetwork()
net.add_node("Bois Forte", )
prop = StressPropagator(net, PropagationConfig())
result = prop.run()
```
