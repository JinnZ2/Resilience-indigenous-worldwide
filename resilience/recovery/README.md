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

## Materials Processing and Autonomous Operations

### geometric_alumina.py -- Turn Waste Into Industry

Geometric alumina processing framework. The industrial Bayer process is a
line (one vector, high waste). Geometric processing is a polygon -- coupling
thermodynamics, waste streams, energy inputs, and materials science so that
waste from one process feeds another. Includes 10 processing methods, a
coupling explorer that discovers waste/thermal/energy synergies, 8 novel
pathways (solar-microwave hybrid, bio-microwave cascade, red mud geopolymer,
hydrogen plasma reduction), and thermodynamic efficiency analysis.

```bash
python3 geometric_alumina.py
python3 geometric_alumina.py --json
```

**Who it helps:** Communities near bauxite deposits or alumina refineries
who can turn red mud waste into iron, titanium, rare earths, and construction
materials instead of accepting it as pollution.

---

### geopolymer_construction.py -- Build Structures from Salvaged Waste

Geopolymer construction from industrial byproducts: red mud, reclaimed
gypsum (drywall), glass cullet, and fiber reinforcement. Simulates slab
structural integrity, models the three-phase cure sequence (initial set,
polymerization, strength gain) with temperature gradient monitoring, and
calculates pressure vessel wall thickness for sCO2 or caustic-environment
systems from salvaged stainless steel.

```bash
python3 geopolymer_construction.py --demo
```

**Who it helps:** Anyone building foundations, floors, or structural
elements from waste materials instead of importing Portland cement. Works
with drywall salvaged from demolished buildings, red mud from alumina
processing, and glass from debris.

---

### sovereign_operations.py -- Run an Autonomous Base

Operational monitoring for self-sufficient sites: water recovery (process
and grey water with pH/turbidity classification), power field balancing
(24V DC bus with automatic load shedding during cold snaps), site
acquisition checklist for cold-climate autonomous bases, and system
coherence scoring that aggregates all subsystem health into a single
dashboard.

```bash
python3 sovereign_operations.py --demo
```

**Who it helps:** Communities operating off-grid bases that need to
monitor water purity, manage battery power through extreme weather,
and maintain visibility across all systems simultaneously.

---

## Biological Systems and Site Security

### biogas_systems.py -- Turn Waste Into Energy and Soil

Human and kitchen waste are a chemical battery and thermal feedstock.
Compost C:N balancer (single and multi-feedstock), anaerobic digester
health monitoring (temperature, methane, pH), flexible gas holder sizing
with energy content calculations, and an integrated daily mass balance
model.  Includes seasonal heating adjustment for cold climates -- sCO2
waste heat keeps the digester at 37C even at -30C ambient.

```bash
python3 biogas_systems.py --demo
```

**Who it helps:** Any community that needs cooking fuel, soil fertility,
and sanitation from a single closed-loop system with no external inputs.

---

### perimeter_defense.py -- Protect the Base Autonomously

Threat classification (human, predator, wildlife, vehicle) with
distance-scaled deterrent response.  Species-specific deterrents (sonic
for wolves, electric mesh for bears, strobe for cougars, alert for
humans) activate at proportional intensity based on proximity.  Includes
cold-climate camera hardening specs (-40C operation) and remote status
aggregation for operators away from site.

```bash
python3 perimeter_defense.py --demo
```

**Who it helps:** Remote or autonomous sites that need wildlife and
intruder defense without constant human presence.  Decision logic runs
on any Python installation; actual camera hardware is pluggable.

---

## Integrated Infrastructure

### bio_step_system.py -- Single Chamber Does Everything

A biomimetic reactor that purifies water, generates energy, and stores
hydraulic/pneumatic potential in one 2-hour cycle.  Four phases: iron
oxidation (heats water, binds metals), steam-pressure (lifts counterweight,
compresses air), bio-filtration (living plants polish water), distribution
(gravity generates electricity).  Single pass removes 97% contaminants;
triple pass produces potable water.  Replaces $6.2M of separate systems
with a $900K integrated chamber.

```bash
python3 bio_step_system.py --demo
python3 bio_step_system.py --cycles 12 --water-input 5000 --bio-passes 3
```

**Who it helps:** Communities near contaminated water sources (mining
runoff, industrial waste, conflict damage) who need clean water AND
energy from a single affordable installation.

---

## Complete Settlement Design

### geometric_city.py -- The Geometric City

Everything above integrated into a single settlement design.  Sizes
energy, water, food, materials, waste, and detection systems for a given
population; discovers within-system and cross-system couplings; computes
geometric integrity metrics.  A 10,000-person geometric city uses 1/3 the
energy, 1/2 the water, recovers 92% of waste, and achieves 100%
self-sufficiency -- with 35x the geometric integrity of an industrial city.

```bash
python3 geometric_city.py
python3 geometric_city.py --population 5000 --location arid_inland
python3 geometric_city.py --json
```

**Who it helps:** Anyone planning a settlement, refugee camp, or community
rebuild who wants to start from first principles instead of replicating
the industrial model that failed.

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
