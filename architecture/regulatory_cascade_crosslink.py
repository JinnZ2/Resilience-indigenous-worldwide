"""
regulatory_cascade_crosslink.py
===============================

Makes explicit what is otherwise implicit across two modules:

  institutional_bottleneck_audit.py
      names the regulatory choke points that block the closed-loop
      N pathway and quantifies lives-per-month of inaction.

  hormuz_cascade_audit.py
      runs a physical cascade whose mortality is dominated by the
      `vulnerable_absorption` parameter — the fraction of caloric
      loss that concentrates on import-dependent populations.

These two are linked: every regulatory node in the institutional
audit, while in force, raises `vulnerable_absorption` because it
removes the closed-loop redundancy that would otherwise let
exposed populations partially substitute for the lost synthetic N.

This module builds the mapping table and exposes:

  - cascade-parameter contribution per regulatory node
  - aggregate `vulnerable_absorption` delta if all are in force
    versus all relaxed
  - the inverse: which regulatory relaxations would have to ship
    to bring presenter-scale mortality below institutional-baseline
    levels

License: CC0 — public domain
Dependencies: stdlib only (imports from sibling modules)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List

from architecture.institutional_bottleneck_audit import (
    REGULATORY_BOTTLENECKS,
    RegulatoryNode,
)
from architecture.hormuz_cascade_audit import (
    CascadeRun,
    POP_DEPENDENT_ON_IMPORT_N,
)


# ============================================================
# Mapping: regulatory node -> cascade parameter contribution
# ============================================================

@dataclass
class CrosslinkEntry:
    node:                          RegulatoryNode
    population_share:              float   # fraction of 1.07B import-
                                            # dependent pop affected
    absorption_contribution:       float   # how much this rule adds to
                                            # `vulnerable_absorption`
    rationale:                     str


# These contributions are not survey numbers. They are coarse weights
# proportional to the lives-per-month figures from the institutional
# audit, normalized so the full stack contributes ~0.6 to
# vulnerable_absorption (the difference between "broad sharing" and
# "extreme concentration" scenarios in the cascade audit).
#
# Total lives-per-month across the institutional audit = ~730,500.
# We scale each contribution by (lives_per_month / total) * 0.60.

def _build_crosslinks() -> List[CrosslinkEntry]:
    total_lpm = sum(n.lives_per_month_delay for n in REGULATORY_BOTTLENECKS)
    out: List[CrosslinkEntry] = []
    for n in REGULATORY_BOTTLENECKS:
        share = n.lives_per_month_delay / total_lpm
        out.append(CrosslinkEntry(
            node                     = n,
            population_share         = share,   # proxy: weight by exposure
            absorption_contribution  = share * 0.60,
            rationale                = (
                f"{n.authority} prohibits the closed-loop pathway that "
                f"would otherwise let dependent populations partially "
                f"substitute for lost synthetic N. While in force, the "
                f"caloric loss is forced to concentrate on those "
                f"populations rather than dissipate through redundancy."
            ),
        ))
    return out


CROSSLINKS: List[CrosslinkEntry] = _build_crosslinks()


# ============================================================
# Aggregate analysis
# ============================================================

def total_absorption_if_all_in_force() -> float:
    """vulnerable_absorption contributed by the full regulatory stack."""
    return sum(c.absorption_contribution for c in CROSSLINKS)


def absorption_if_relaxed(relaxed_node_ids: list[str]) -> float:
    """
    Hypothetical absorption if the listed nodes are relaxed.
    `relaxed_node_ids` matches the `jurisdiction` field of RegulatoryNode.
    """
    relaxed = set(relaxed_node_ids)
    return sum(c.absorption_contribution
               for c in CROSSLINKS
               if c.node.jurisdiction not in relaxed)


def deaths_under_absorption(absorption: float,
                            scenario_kind: str = "wfp_prolonged") -> float:
    """
    Run the cascade with a given vulnerable_absorption value and return
    excess deaths. `scenario_kind` selects the cascade backdrop:
        "fao"            -> short broad-sharing disruption
        "wfp_prolonged"  -> 12-month moderate disruption (default)
        "presenter_high" -> compound cascade
    """
    presets = {
        "fao": dict(
            scenario               = "crosslink_fao",
            hormuz_throughput_frac = 0.10,
            substitution_lag_months= 4.0,
            buffer_stock_months    = 2.0,
            weeks_planting_delay   = 2.0,
            duration_months        = 6.0,
            buffer_redistribution  = 0.30,
            solar_min_intensity    = 0.0,
        ),
        "wfp_prolonged": dict(
            scenario               = "crosslink_wfp",
            hormuz_throughput_frac = 0.05,
            substitution_lag_months= 9.0,
            buffer_stock_months    = 2.0,
            weeks_planting_delay   = 4.0,
            duration_months        = 12.0,
            buffer_redistribution  = 0.20,
            solar_min_intensity    = 0.0,
        ),
        "presenter_high": dict(
            scenario               = "crosslink_high",
            hormuz_throughput_frac = 0.00,
            substitution_lag_months= 18.0,
            buffer_stock_months    = 1.0,
            weeks_planting_delay   = 8.0,
            duration_months        = 24.0,
            buffer_redistribution  = 0.05,
            solar_min_intensity    = 0.8,
        ),
    }
    if scenario_kind not in presets:
        raise KeyError(f"Unknown scenario {scenario_kind!r}. "
                       f"Choose from {list(presets)}.")
    run = CascadeRun(**presets[scenario_kind],
                     vulnerable_absorption=absorption)
    run.execute()
    return run.results["excess_deaths"]


# ============================================================
# Report
# ============================================================

def report():
    full = total_absorption_if_all_in_force()
    print("=" * 72)
    print("REGULATORY <-> CASCADE CROSSLINK")
    print("=" * 72)
    print()
    print("Each regulatory node listed in institutional_bottleneck_audit.py")
    print("raises `vulnerable_absorption` in hormuz_cascade_audit.py because")
    print("it removes the closed-loop redundancy that would otherwise allow")
    print("dependent populations to substitute for lost synthetic N.")
    print()
    print(f"{'jurisdiction':<42} {'lives/mo':>10} {'+absorb':>9}")
    print("-" * 72)
    for c in CROSSLINKS:
        print(f"{c.node.jurisdiction:<42} "
              f"{c.node.lives_per_month_delay/1e3:>8.0f}k "
              f"{c.absorption_contribution:>9.3f}")
    print("-" * 72)
    print(f"{'TOTAL (full stack in force)':<42} "
          f"{sum(c.node.lives_per_month_delay for c in CROSSLINKS)/1e3:>8.0f}k "
          f"{full:>9.3f}")
    print()
    print("DEATH CURVE vs ABSORPTION (fao backdrop)")
    print("-" * 72)
    print("  fao = 6-month, broad-sharing disruption. The cascade")
    print("  saturates near absorption ~ 0.33 because kcal_deficit_pct")
    print("  hits its 0.60 ceiling. Below that, the gradient is steep.")
    print()
    print(f"  {'absorption':>12} {'deaths':>14}")
    for va in (0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.60):
        d = deaths_under_absorption(va, "fao")
        bar = "#" * int(d / 5e6)
        print(f"  {va:>12.2f} {d/1e6:>11.1f} M  {bar}")
    print()
    print("CUMULATIVE RELAXATION (fao backdrop)")
    print("-" * 72)
    print("  Single relaxations vanish into saturation. The PROGRESSIVE")
    print("  stack — relaxing the largest contributor first, then the")
    print("  next — is what brings the cascade below ceiling.")
    print()
    # Sort by contribution descending
    by_size = sorted(CROSSLINKS,
                     key=lambda c: c.absorption_contribution,
                     reverse=True)
    running_abs = full
    running_deaths = deaths_under_absorption(running_abs, "fao")
    print(f"  {'step':<46} {'absorption':>10} {'deaths':>12}")
    print(f"  {'(baseline: full stack in force)':<46} "
          f"{running_abs:>10.3f} {running_deaths/1e6:>10.1f} M")
    for c in by_size:
        running_abs -= c.absorption_contribution
        running_deaths = deaths_under_absorption(running_abs, "fao")
        label = f"+ relax {c.node.jurisdiction}"
        print(f"  {label:<46} "
              f"{running_abs:>10.3f} {running_deaths/1e6:>10.1f} M")
    print()
    print("  Under wfp_prolonged or presenter_high backdrops, the cascade")
    print("  remains at the 321M structural ceiling until the cumulative")
    print("  stack drops absorption below ~0.20. This is the regulatory")
    print("  audit's central finding in numerical form: partial action")
    print("  is invisible; coordinated full-stack action is required.")
    print()
    print("=" * 72)
    print("USE")
    print("=" * 72)
    print("""
  Combine with variance_pathway_templates.py:

    for c in CROSSLINKS:
        if c.absorption_contribution > THRESHOLD:
            print(render_one(c.node.jurisdiction))

  to prioritize which variance request to file first, by physical
  mortality impact rather than by political accessibility.
""")


if __name__ == "__main__":
    report()
