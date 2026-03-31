# Recovery Toolkit for War-Torn and Post-Conflict Areas

Tools for communities rebuilding after conflict, disaster, or displacement.
Each module addresses a specific survival and recovery need using only
Python's standard library -- no external dependencies, no internet required.

Source: [JinnZ2/Inversion](https://github.com/JinnZ2/Inversion/tree/main/scripts)

---

## Immediate Survival (Days 1-30)

### geometric_boo_rubble.py -- Build from What's Left

Designs a functioning base of operations from **rubble and salvaged materials**.
Input your population size and available debris; it outputs a system design
meeting minimum water (15 L/person/day per Sphere Standards) and power targets.
Identifies which components are feasible from what you have, detects synergies
between them, and scores the design's resilience.

```bash
python3 geometric_boo_rubble.py --population 25
python3 geometric_boo_rubble.py --population 50 --threshold 0.2 --json
```

**Who it helps:** Families sheltering in bombed buildings, displaced groups
arriving at empty sites with only debris and salvage available.

---

### human_body_alerts.py -- Threat Detection Without Instruments

When medical equipment, air quality monitors, and water testing kits are
destroyed or unavailable, the human body itself is a sensor array. This
module maps biological symptoms to environmental threats -- connecting
headaches, skin reactions, breathing changes, and other signals to
possible contamination, gas exposure, or water toxicity.

```bash
python3 human_body_alerts.py --demo
```

**Who it helps:** Communities without functioning hospitals or labs who need
to detect chemical contamination, water poisoning, or environmental hazards
using only what their bodies tell them.

---

### geometric_boo.py -- Distributed Infrastructure (No Single Point of Failure)

Models infrastructure as a distributed system where **no single component's
failure can collapse the whole**. Selects modular components (solar panels,
wells, filters, shelters) based on what's available, identifies coupling
relationships, and computes geometric integrity scores.

```bash
python3 geometric_boo.py --demo
python3 geometric_boo.py --demo --json
```

**Who it helps:** Communities rebuilding water, power, and shelter systems
who cannot afford centralized infrastructure that one attack can destroy.

---

## Short-Term Recovery (Months 1-6)

### energy_wisdom_explorer.py -- Find Energy from Whatever You Have

Weaves together heterogeneous energy sources (solar thermal, biomass,
piezoelectric, thermoelectric, wind) into integrated configurations.
Detects synergies between available energy practices and scores systems
on EROI (Energy Return On Investment), scalability, and domain coverage.

```bash
python3 energy_wisdom_explorer.py --demo
```

**Who it helps:** Communities with partial infrastructure -- some solar panels
here, a wind setup there, biomass available -- who need to combine what
exists into a working energy system.

---

### field_system.py -- Restart Food Production

Models agricultural systems as thermodynamic entities. Tracks soil
regeneration capacity, water retention, and ecological coupling.
Demonstrates that small plots with high ecological coupling (companion
planting, wild edges) can outproduce large monoculture plots -- critical
when arable land is scarce or contaminated.

```bash
python3 field_system.py --demo
```

**Who it helps:** Communities restarting agriculture on damaged land, with
limited acreage, who need to maximize food output from what soil remains.

---

### system_weaver.py -- Discover Optimal Configurations

Treats complex systems (water, energy, food, shelter) as assemblies of
swappable components. A stochastic search explores combinations, scoring
each on biodiversity, carbon impact, dependency, cost externalization,
and coupling synergy. Finds configurations you wouldn't think to try.

```bash
python3 system_weaver.py --demo
python3 system_weaver.py --search --iterations 200
```

**Who it helps:** Recovery planners trying to figure out the best way to
combine limited resources across water, energy, food, and shelter systems.

---

## Long-Term Rebuilding (6+ Months)

### geometric_exploration.py -- Proven Ancient Technologies

Surfaces historical technologies that were **marginalized or erased** but
remain thermodynamically valid: Terra Preta (Amazonian dark earth), Qanats
(Persian underground water channels), Roman self-healing concrete, Three
Sisters polyculture, and more. Generates novel combinations constrained by
physics feasibility.

```bash
python3 geometric_exploration.py --demo
```

**Who it helps:** Communities that cannot access modern supply chains but
can implement proven ancient technologies using local materials -- many of
which outperform modern equivalents in durability and sustainability.

---

### unified_geometric_framework.py -- Measure Overall System Health

Models any coupled system as vectors in a health-space. Tracks how water,
energy, food, shelter, and governance dimensions interact. Computes
polygon area (integration proxy), coupling density, vector balance, and
an overall integrity score. Use it to identify which dimension of recovery
is lagging and where coupling is weak.

```bash
python3 unified_geometric_framework.py --demo
```

**Who it helps:** Community leaders and NGO coordinators who need a
dashboard view of recovery progress across all dimensions, identifying
where to focus next.

---

### viewpoint_comparison.py -- Bridge Different Recovery Approaches

When multiple organizations (local community, NGOs, military, government)
are involved in recovery, each sees different things and has different
blind spots. This module maps what each viewpoint sees, asks, assumes,
and misses -- then computes pairwise gap analyses to surface conflicts
and complementarities.

```bash
python3 viewpoint_comparison.py --demo
```

**Who it helps:** Coordination between local communities, international
organizations, and government bodies who need to understand each other's
blind spots before making joint decisions.

---

## Design Principles

These tools share common characteristics that make them suitable for
post-conflict deployment:

- **Zero external dependencies** -- pure Python standard library
- **Offline operation** -- no internet, API, or cloud required
- **Configurable** -- all parameters adjustable via CLI or code
- **JSON output** -- machine-readable for integration with other systems
- **Human-readable output** -- terminal-friendly for direct use
- **Physics-grounded** -- based on thermodynamic constraints, not assumptions
- **Modular** -- each tool works standalone or integrates with others

## Related

See also [`ancient_persia.py`](../ancient_persia.py) in the parent directory,
which consolidates 11 additional modules for contamination detection, resource
flow dynamics, operational risk monitoring, dependency auditing, validation,
zero-infrastructure alerts, salvage reclamation, energy coupling, desalination,
soil protection, and organizational topology.
