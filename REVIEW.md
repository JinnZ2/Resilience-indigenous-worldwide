# Repository Review — Resilience Indigenous Worldwide
<!-- auto-generated against CLAUDE.md 2026-07-09 -->

---

## 1. Structural Consistency with CLAUDE.md

### Undocumented directories (not mentioned in CLAUDE.md)

| Directory | Contents | Action needed |
|---|---|---|
| `tools/` | 6 standalone tool packages | Add to CLAUDE.md structure block |
| `architecture/` | 14 standalone Python modules | Already documented in README, missing from CLAUDE.md |
| `resilience_stack/` | Cognition/context/mutual-audit modules | Add to CLAUDE.md |
| `may_2026_build/` | Build artifacts | Add to CLAUDE.md or gitignore build outputs |
| `hardware/` | `gravity_battery_metamaterial_sim.py` | Add to CLAUDE.md |
| `india/` | `foundation_float_system.py` | Add to CLAUDE.md |
| `burkina_faso/` | 4 substrate/recovery scripts | Add to CLAUDE.md |
| `materials/` | `collapse_substrate_mapping.py` + 3 more | Add to CLAUDE.md |
| `constraint_resilience_audit/` | 6 constraint modules | Add to CLAUDE.md |
| `webapp/` | Web application | Add to CLAUDE.md |
| `Model/` | `Hidden-variable.py` | Rename dir and file (see below); add to CLAUDE.md |

### Undocumented resilience/ sub-modules

CLAUDE.md lists 4 modules + `data/`. The package also contains:

- `ancient_persia.py` + `ANCIENT-PERSIA-README.md`
- `geometric_coupling_optimizer.py`
- `innovation_engine.py`
- `boundary_waters/` (cascade, constants, export, layers)
- `detectors/` (notices, signals, templates)
- `recovery/` (16+ modules)

**Action:** Extend the `resilience/` section in CLAUDE.md or add a `resilience/MODULES.md`.

### Naming convention violations

CLAUDE.md mandates: Python → `lowercase_underscore`, Markdown → `lowercase-hyphens`, directories → `lowercase`.

| File/Dir | Violation | Fix |
|---|---|---|
| `Model/` | Directory should be lowercase | Rename to `model/` |
| `Model/Hidden-variable.py` | Should be `lowercase_underscore.py` | Rename to `model/hidden_variable.py` |
| `resilience/ANCIENT-PERSIA-README.md` | Should be lowercase-hyphens | Rename to `resilience/ancient-persia-readme.md` |
| `Todo.md` | Should be lowercase | Rename to `todo.md` |

```bash
git mv Model model
git mv model/Hidden-variable.py model/hidden_variable.py
git mv resilience/ANCIENT-PERSIA-README.md resilience/ancient-persia-readme.md
git mv Todo.md todo.md
```

### Import order

`stress_model.py`, `network.py`, `risk_matrix.py` all follow the `stdlib → third-party → local` rule correctly. No violations found in the core `resilience/` package.

### Type hints

All public functions in the 4 documented `resilience/` modules (`network.py`, `stress_model.py`, `risk_matrix.py`, `visualization.py`) carry type hints. Private helpers in `ancient_persia.py` (prefixed `_`) are exempt per convention. No violations found.

---

## 2. README & Discoverability

### Current README problems

- Lines 100–243 of `README.md` are Venezuela shareholder letter content (a legal template), not repository documentation. This content belongs in `docs/venezuela/` or `docs/strategy/`, not the root README. The last true README sentence ends at line 98 (`python -m pytest tests/test_cascade_audit.py`).
- `tools/` is not mentioned anywhere in the README.
- The `resilience/` Python package has no usage example.

### Missing: license badge

Paste at top of `README.md`, below the title:

```markdown
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
```

### Missing: "Why This Matters" urgency statement

Paste as second section in `README.md`:

```markdown
## Why This Matters

Indigenous communities on every continent face an accelerating pattern:
a corporation or state actor secures legal cover (a BIT clause, an ESG
certification, a peace-prize photo-op), then extracts resources while
regulatory and disclosure frameworks treat the resulting harm as an
externality. By the time the legal case is built, the damage is done.

This repository gives communities, lawyers, and researchers
computational tools to map the risk *before* the machinery moves —
and evidentiary frameworks to act *while* there is still time.
```

### Missing: one-liner import example

Add to the README under a `## Computational Modeling` heading:

```python
from resilience.stress_model import StressPropagator, PropagationConfig
from resilience.network import CommunityNetwork

net = CommunityNetwork()
net.add_community("Bois Forte", stress=0.4, resilience=0.7)
prop = StressPropagator(net, PropagationConfig())
result = prop.run()
```

### Missing: CITATION.cff

Create `CITATION.cff` at repo root:

```yaml
cff-version: 1.2.0
message: "If you use this work, please cite it as below."
type: software
title: "Resilience Indigenous Worldwide"
abstract: >
  Legal research and computational modeling tools supporting indigenous
  communities facing resource extraction, military intervention, and
  corporate colonization. Covers multi-jurisdictional legal analysis,
  financial risk assessment, and network stress modeling.
license: CC0-1.0
repository-code: "https://github.com/JinnZ2/resilience-indigenous-worldwide"
keywords:
  - indigenous-rights
  - legal-research
  - resource-extraction
  - fpic
  - undrip
  - network-stress
  - corporate-accountability
  - isds
  - esg
  - human-rights
```

### Missing: KEYWORDS.txt

Create `KEYWORDS.txt` at repo root:

```
indigenous-rights
legal-research
resource-extraction
fpic
undrip
network-stress
corporate-accountability
isds
esg
human-rights
aluminum-contamination
food-security
oral-tradition
elder-knowledge
agent-based-model
```

---

## 3. Obvious Inconsistencies

### README contamination (high priority)

`README.md` lines 100–243 are a copy of a Venezuela shareholder letter. This makes the README misleading as a project landing page. Move that content to `docs/venezuela/shareholder-letter.md` and replace those lines in README with a pointer:

```markdown
See [`docs/venezuela/`](docs/venezuela/) for legal templates, including
the LP-squeeze shareholder notice.
```

### `tools/` entirely absent from README

The six tool packages (`al-contamination-scanner`, `elder-value-claims`, `guild-resilience`, `human-food-grain-monitor`, `oral-corpus`, `warning-cycle-corpus`) are not mentioned anywhere in the README or CLAUDE.md. Add a `## Tools` section to README:

```markdown
## Tools (`tools/`)

Standalone, offline-capable tools (CC0, stdlib-only unless noted):

- **`al-contamination-scanner/`** — Monte Carlo EWRI scanner for recycled-aluminum contamination risk across vulnerable regions. Run: `python3 tools/al-contamination-scanner/run_hotspot_scan.py`
- **`elder-value-claims/`** — Falsifiable-claim protocol testing AI age bias and cross-cultural elder value. Run: `python3 tools/elder-value-claims/run_all_claims.py`
- **`guild-resilience/`** — Gaussian fitness model for 18 indigenous food guilds across a 4-axis environmental condition space.
- **`human-food-grain-monitor/`** — dX/dt crop monitoring with Gaussian portfolio coverage by geographic cell.
- **`oral-corpus/`** — Append-only, SHA-256-deduplicated corpus of oral knowledge segments with physics annotations.
- **`warning-cycle-corpus/`** — Structured archive of indigenous climate-cycle warning stories.
```

### Missing tests for core resilience modules

| Module | Test file | Status |
|---|---|---|
| `network.py` | none | **missing** |
| `visualization.py` | none | **missing** |
| `stress_model.py` | `test_stress_model.py` | present |
| `risk_matrix.py` | `test_risk_matrix.py` | present |
| `detectors/` | `test_detectors.py` | present |
| `boundary_waters/cascade.py` | `test_cascade_audit.py` | present |

Create `tests/test_network.py` at minimum (it is the foundational graph layer that `stress_model` depends on).

### Cross-document: `docs/boundary-waters/` is in README but not in CLAUDE.md

CLAUDE.md documents `docs/greenland/`, `docs/venezuela/`, `docs/strategy/`. The boundary-waters case study exists and has its own README, but CLAUDE.md omits it.

---

## 4. Documentation Gaps

### docs/ subdirectories lack README/index files

| Directory | Files | README? |
|---|---|---|
| `docs/greenland/` | `conflict-of-interest.md`, `corporate-us-leverage.md`, `sovereignty.md` | **missing** |
| `docs/venezuela/` | `risk-assessment.md` | **missing** |
| `docs/strategy/` | `don-lemon.md`, `legal-possibilities.md`, `monetary-beneficiary.md`, `press-release.md`, `voting.md`, `ways-to-help.md` | **missing** |
| `docs/boundary-waters/` | `README.md`, `indigenous-impact.md`, `legal-framework.md`, `model-results.md` | present |

Minimum viable index for each missing dir:

```markdown
# docs/greenland/

| Document | Description |
|---|---|
| [`conflict-of-interest.md`](conflict-of-interest.md) | … |
| [`corporate-us-leverage.md`](corporate-us-leverage.md) | … |
| [`sovereignty.md`](sovereignty.md) | … |
```

### tools/ missing READMEs

| Tool | README? |
|---|---|
| `al-contamination-scanner/` | present |
| `elder-value-claims/` | present |
| `guild-resilience/` | **missing** |
| `human-food-grain-monitor/` | **missing** |
| `oral-corpus/` | **missing** |
| `warning-cycle-corpus/` | **missing** |

### stress_model methodology underdocumented

`stress_model.py` has a module docstring but does not explain the hidden-variable model. The original source (`Model/Hidden-variable.py`) contains this logic. A companion `docs/stress-model-methodology.md` would close this gap. Key items to cover:

- What `hidden_climate` and `hidden_infra` node attributes represent
- How `amplification_factor` maps to empirical propagation parameters
- The relationship between `PropagationConfig.threshold` and legal/ecological risk thresholds

### risk_matrix scoring criteria undocumented

`risk_matrix.py` defines `RiskCategory` enum and scoring logic but there is no companion document explaining the calibration of weights. Add `docs/risk-scoring-criteria.md` or a module-level docstring expansion.

---

## 5. Proposed Repository Topics

Apply these via GitHub repository Settings → Topics:

```
indigenous-rights
legal-research
resource-extraction
fpic
undrip
network-stress
corporate-accountability
isds
esg
human-rights
aluminum-contamination
food-security
computational-modeling
agent-based-model
oral-tradition
```
