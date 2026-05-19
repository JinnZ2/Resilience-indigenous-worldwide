"""
biome_cooperation_layer.py
==========================

A fourth lever on the cascade, alongside (1) variance pathways,
(2) institutional relaxation, and (3) village-scale closure.

Where regulatory_cascade_crosslink.py measures what *removing*
prohibitions buys, this module measures what *adding* positive
cross-border cooperative redundancy buys. The biome does not
recognize national borders; this module asks what happens to
the cascade if institutional response stops recognizing them
either.

Each channel is anchored to a real historical analogue, so the
parameter effects are plausibility-modeled rather than guessed.
Three effect levels are exposed per channel: skeptical / central /
optimistic — because biome-scale cooperation has fewer mortality-
anchored studies than the regulatory-failure case has.

CHANNELS MODELED
----------------
  1. watershed N management
  2. germplasm and seed-variety sharing
  3. microbial culture exchange
  4. composting standards harmonization
  5. forecasting and early-warning networks
  6. pollinator and biological corridors
  7. biome-scale N sinks (wetland/forest cooperation)

License: CC0 — public domain
Dependencies: stdlib + sibling cascade module
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict

from architecture.hormuz_cascade_audit import CascadeRun


# ============================================================
# Citations — real historical analogues we draw from
# ============================================================
#
# Specific page numbers and DOIs are intentionally omitted; these are
# the source documents and headline findings each channel is anchored
# to. A working community legal partner should pull the originals.

CITATIONS = {
    "rhine_icpr": (
        "International Commission for the Protection of the Rhine "
        "(ICPR). Rhine Action Programme (1987) and Rhine 2020 / "
        "Rhine 2040 plans. Headline result: nitrogen load to the "
        "North Sea reduced by roughly half between 1985 and 2010 "
        "via coordinated action across Switzerland, France, "
        "Germany, Luxembourg, and the Netherlands."
    ),
    "helcom_bsap": (
        "HELCOM (Baltic Marine Environment Protection Commission). "
        "Baltic Sea Action Plan, 2007 (revised 2021). Coordinated "
        "nutrient-load reduction targets across nine Baltic states; "
        "partial success on phosphorus, more uneven on nitrogen, "
        "but the cooperative frame survived political shocks."
    ),
    "danube_icpdr": (
        "International Commission for the Protection of the Danube "
        "River (ICPDR). Danube River Basin Management Plan, 2009 / "
        "2015 / 2021 cycles. 14 countries; demonstrated that "
        "watershed-scale cooperation is possible across very "
        "different political systems."
    ),
    "itpgrfa": (
        "FAO International Treaty on Plant Genetic Resources for "
        "Food and Agriculture (2001), the 'Plant Treaty.' "
        "Multilateral System covers 64 crops and forages; 149+ "
        "contracting parties as of mid-2020s. Facilitates "
        "germplasm exchange under standard material transfer "
        "agreement."
    ),
    "svalbard": (
        "Svalbard Global Seed Vault, opened 2008. Operated by "
        "Norway, NordGen, and the Crop Trust. Holds 1M+ seed "
        "samples from 6000+ crop species as a backup to national "
        "gene banks. Withdrawals to Syria (ICARDA, 2015) after "
        "the Aleppo gene bank was compromised demonstrated the "
        "system works in crisis."
    ),
    "cgiar": (
        "CGIAR system: IRRI (rice), CIMMYT (maize/wheat), ICRISAT "
        "(dryland cereals), ICARDA (drylands), CIAT (tropical "
        "agriculture). Cross-border germplasm distribution since "
        "the 1960s; foundational to the Green Revolution and to "
        "current climate-resilient variety release. See Pingali, "
        "P. (2012). 'Green Revolution: Impacts, limits, and the "
        "path ahead.' PNAS 109(31)."
    ),
    "who_2006_excreta": (
        "WHO (2006). Guidelines for the Safe Use of Wastewater, "
        "Excreta and Greywater. Four volumes. Already provides "
        "an internationally harmonized safety framework; the "
        "barrier is not the science but the regulatory adoption."
    ),
    "fao_locust_watch": (
        "FAO Desert Locust Information Service (DLIS). Multi-"
        "country early warning since the 1970s, anchored at "
        "FAO Rome with national locust centers in affected "
        "states. 2020-2022 East Africa upsurge response shows "
        "both the value and the funding-dependence of the system."
    ),
    "fews_net": (
        "Famine Early Warning Systems Network (FEWS NET). USAID-"
        "funded, operating since 1985 across ~30 countries. "
        "Integrated Phase Classification (IPC) outputs feed "
        "humanitarian response planning."
    ),
    "montreal_protocol": (
        "Montreal Protocol on Substances that Deplete the Ozone "
        "Layer (1987). Universally ratified; 99% phaseout of "
        "controlled substances. Velders et al. (2007), 'The "
        "importance of the Montreal Protocol in protecting "
        "climate,' PNAS 104(12). The reference case for biome-"
        "scale cooperation that actually worked at the necessary "
        "speed and scale."
    ),
    "wadden_sea": (
        "Trilateral Wadden Sea Cooperation (Denmark, Germany, "
        "Netherlands), 1978-present. UNESCO World Heritage "
        "(2009). Demonstrates multi-decade ecosystem-scale "
        "coordination across national borders."
    ),
    "mesoamerican_corridor": (
        "Mesoamerican Biological Corridor (Corredor Biológico "
        "Mesoamericano), 1997. Seven Central American countries "
        "plus southern Mexico. Patchy implementation but "
        "established the framework that pollinator/migration "
        "corridors are a multilateral object."
    ),
    "azolla_irri": (
        "International Rice Research Institute (IRRI) Azolla "
        "collection, Los Baños, Philippines. Long-running "
        "germplasm and protocol exchange for biological N "
        "fixation in rice paddies. Lumpkin & Plucknett (1982), "
        "'Azolla as a green manure: use and management in crop "
        "production,' Westview Press."
    ),
}


# ============================================================
# Cooperation channel structure
# ============================================================

@dataclass
class CooperationChannel:
    name:                 str
    description:          str
    historical_analogue:  str
    citation_keys:        List[str]
    # Cascade parameter shifts at the central plausibility estimate.
    # Negative = reduces; positive = increases. Applied multiplicatively
    # except for buffer_redistribution which is additive (capped 0-0.7).
    cascade_effects:      Dict[str, float]
    plausibility:         str   # "high" | "medium" | "low"
    lead_time_months:     int
    notes:                str = ""


# ============================================================
# The seven channels
# ============================================================

CHANNELS: List[CooperationChannel] = [
    CooperationChannel(
        name = "watershed_N_management",
        description = (
            "Cross-border coordination of fertilizer application, runoff "
            "control, and riparian buffers across shared river basins. "
            "Reduces effective N loss from the agricultural system, so "
            "less synthetic input is needed for the same yield."
        ),
        historical_analogue = (
            "Rhine Action Programme (1987-present); Danube River Basin "
            "Management Plan; HELCOM Baltic Sea Action Plan. The Rhine "
            "case is the strongest: coordinated, measured, durable, "
            "achieved real nutrient-load reductions across five states."
        ),
        citation_keys = ["rhine_icpr", "danube_icpdr", "helcom_bsap"],
        cascade_effects = {
            "substitution_lag_months": -2.0,   # alt N pathways come online faster
            "buffer_stock_months":     +1.0,
        },
        plausibility = "high",
        lead_time_months = 24,
        notes = (
            "Rhine cooperation survived German reunification and EU "
            "expansion shocks. Strongest analogue for nitrogen-specific "
            "cross-border coordination."
        ),
    ),

    CooperationChannel(
        name = "germplasm_seed_sharing",
        description = (
            "Open multilateral exchange of crop varieties adapted to "
            "lower-N, higher-stress conditions: N-efficient cereals, "
            "drought-tolerant legumes, locally-adapted heritage lines."
        ),
        historical_analogue = (
            "ITPGRFA Plant Treaty (2001) Multilateral System; CGIAR "
            "cross-border germplasm flow; Svalbard Global Seed Vault "
            "as backup; ICARDA's Syria-Lebanon-Morocco emergency "
            "retrieval (2015) as proof-of-concept under crisis."
        ),
        citation_keys = ["itpgrfa", "cgiar", "svalbard"],
        cascade_effects = {
            "weeks_planting_delay":    -1.5,   # better-adapted varieties plant on time
            "buffer_redistribution":   +0.05,  # more options = more sharing
        },
        plausibility = "high",
        lead_time_months = 12,
        notes = (
            "Infrastructure already exists. The bottleneck is national-"
            "level seed-law harmonization, not the cooperation framework "
            "itself."
        ),
    ),

    CooperationChannel(
        name = "microbial_culture_exchange",
        description = (
            "Cross-border sharing of N-fixing inoculants (Rhizobium, "
            "Bradyrhizobium, Azospirillum), Azolla strains for rice "
            "paddies, mycorrhizal cultures, and locally-adapted IMO/EM "
            "starters. Each shaves weeks-to-months off the substitution "
            "lag for closed-loop N."
        ),
        historical_analogue = (
            "IRRI Azolla collection (Los Baños); USDA-ARS / CABI culture "
            "collections; ad-hoc Rhizobium inoculant exchange across "
            "African agricultural research networks."
        ),
        citation_keys = ["azolla_irri", "cgiar"],
        cascade_effects = {
            "substitution_lag_months": -1.5,
        },
        plausibility = "medium",
        lead_time_months = 6,
        notes = (
            "Less institutionally formalized than germplasm. Biosecurity "
            "concerns make some jurisdictions cautious. The science is "
            "settled; the trust framework is the bottleneck."
        ),
    ),

    CooperationChannel(
        name = "composting_standards_harmonization",
        description = (
            "Internationally recognized standards for source-separated "
            "humanure composting (already published by WHO in 2006), "
            "applied as the basis for cross-border food trade rather "
            "than the Codex source-process distinction. Closes the "
            "international trade leg of the closed-loop pathway."
        ),
        historical_analogue = (
            "WHO 2006 Guidelines for the Safe Use of Wastewater, Excreta "
            "and Greywater already provide the harmonized framework; "
            "IFOAM Organic standards demonstrate that international "
            "process standards are routinely operationalized."
        ),
        citation_keys = ["who_2006_excreta"],
        cascade_effects = {
            "buffer_redistribution":   +0.10,  # trade barriers down -> sharing up
            "substitution_lag_months": -1.0,
        },
        plausibility = "high",
        lead_time_months = 18,
        notes = (
            "The standard exists. Adoption is the gap. This is the "
            "cooperation channel most directly paired with the Codex "
            "variance request in variance_pathway_templates.py."
        ),
    ),

    CooperationChannel(
        name = "forecasting_early_warning",
        description = (
            "Shared monsoon, drought, pest, and pathogen forecasting "
            "across borders. Gives exposed populations time to store, "
            "redistribute, and substitute before a shortage hits."
        ),
        historical_analogue = (
            "FAO Desert Locust Information Service (1970s-present); "
            "FEWS NET / IPC (1985-present); WMO data exchange protocols; "
            "IRI Climate Forecasts. The Sahel 2020-2022 desert-locust "
            "response shows both what the system can do and what "
            "happens when its funding lapses."
        ),
        citation_keys = ["fao_locust_watch", "fews_net"],
        cascade_effects = {
            "vulnerable_absorption":   -0.05,  # early warning -> less concentration
            "buffer_redistribution":   +0.10,
        },
        plausibility = "high",
        lead_time_months = 6,
        notes = (
            "Largest effect comes from coupling forecasts to actual pre-"
            "positioning. A forecast that nobody acts on is a forecast "
            "wasted."
        ),
    ),

    CooperationChannel(
        name = "pollinator_biological_corridors",
        description = (
            "Cross-border conservation of pollinator and species-"
            "migration corridors. Maintains the ecosystem services on "
            "which crop yields depend: pollination, pest predation, "
            "soil biota continuity."
        ),
        historical_analogue = (
            "Mesoamerican Biological Corridor (1997, 7 countries); "
            "Wadden Sea Trilateral Cooperation (1978, 3 countries); "
            "Natura 2000 across the EU."
        ),
        citation_keys = ["mesoamerican_corridor", "wadden_sea"],
        cascade_effects = {
            # Acts as a yield-floor stabilizer rather than a direct N
            # substitute. Modeled as a small reduction in solar/climate
            # drag, since pollinator continuity buffers extreme years.
            "solar_min_intensity":     -0.10,
        },
        plausibility = "medium",
        lead_time_months = 36,
        notes = (
            "Long lead time; reaches steady-state effect only after a "
            "decade. Included because it's the channel that most "
            "explicitly recognizes that the biome does not stop at the "
            "border."
        ),
    ),

    CooperationChannel(
        name = "biome_scale_N_sinks",
        description = (
            "Cross-border protection and restoration of wetlands, "
            "mangroves, peatlands, and forests as biological N sinks "
            "and sources. Mangrove and wetland systems are major N "
            "buffers; deforestation has measurable impacts on regional "
            "N cycling."
        ),
        historical_analogue = (
            "Ramsar Convention on Wetlands (1971); Congo Basin Forest "
            "Partnership; Coral Triangle Initiative. Mixed records on "
            "enforcement but established frameworks for cross-border "
            "biome management."
        ),
        citation_keys = ["wadden_sea"],   # closest formally-cited analogue
        cascade_effects = {
            "buffer_stock_months":     +1.5,
            "solar_min_intensity":     -0.05,
        },
        plausibility = "medium",
        lead_time_months = 48,
        notes = (
            "Longest lead time of any channel. Climate-stacking "
            "protection rather than acute-crisis substitution."
        ),
    ),
]


# ============================================================
# Applying cooperation to a cascade scenario
# ============================================================

# Two backdrops, because different cooperation channels bind on
# different constraints. At fao, timing-loss dominates the cascade's
# max(n_loss, timing_loss) envelope; channels that target N supply
# (watershed coordination, microbial cultures) appear to have zero
# effect there because timing is the binding constraint. They become
# visible at wfp_prolonged, where N-loss dominates instead. Showing
# both is the honest way to communicate which channel helps when.

FAO_BACKDROP = dict(
    scenario               = "biome_coop_fao",
    hormuz_throughput_frac = 0.10,
    substitution_lag_months= 4.0,
    buffer_stock_months    = 2.0,
    weeks_planting_delay   = 2.0,
    duration_months        = 6.0,
    buffer_redistribution  = 0.30,
    solar_min_intensity    = 0.2,
    vulnerable_absorption  = 0.60,   # current regulatory-stack baseline
)

WFP_BACKDROP = dict(
    scenario               = "biome_coop_wfp",
    hormuz_throughput_frac = 0.05,
    substitution_lag_months= 9.0,
    buffer_stock_months    = 2.0,
    weeks_planting_delay   = 4.0,
    duration_months        = 12.0,
    buffer_redistribution  = 0.20,
    solar_min_intensity    = 0.2,
    vulnerable_absorption  = 0.30,   # below saturation so gradient visible
)


def _apply_channels(base: dict, channels: List[CooperationChannel],
                    scale: float = 1.0) -> dict:
    """
    Apply cooperation channel effects on top of a scenario dict.
    `scale` lets the caller run skeptical (0.5), central (1.0),
    or optimistic (1.5) variants of every effect.
    """
    out = dict(base)
    for ch in channels:
        for param, delta in ch.cascade_effects.items():
            scaled = delta * scale
            current = out.get(param, 0.0)
            new = current + scaled
            # Constrain to physical ranges
            if param == "buffer_redistribution":
                new = min(max(new, 0.0), 0.70)
            elif param == "vulnerable_absorption":
                new = min(max(new, 0.0), 1.0)
            elif param == "hormuz_throughput_frac":
                new = min(max(new, 0.0), 1.0)
            elif param == "solar_min_intensity":
                new = min(max(new, 0.0), 1.0)
            elif param in ("substitution_lag_months", "buffer_stock_months",
                           "weeks_planting_delay", "duration_months"):
                new = max(new, 0.0)
            out[param] = new
    return out


def run_with_cooperation(channels: List[CooperationChannel],
                         scale: float = 1.0,
                         backdrop: str = "fao") -> float:
    base = FAO_BACKDROP if backdrop == "fao" else WFP_BACKDROP
    cfg = _apply_channels(base, channels, scale=scale)
    run = CascadeRun(**cfg)
    run.execute()
    return run.results["excess_deaths"]


def run_baseline(backdrop: str = "fao") -> float:
    base = FAO_BACKDROP if backdrop == "fao" else WFP_BACKDROP
    run = CascadeRun(**base)
    run.execute()
    return run.results["excess_deaths"]


# ============================================================
# Report
# ============================================================

def report():
    print("=" * 72)
    print("BIOME COOPERATION LAYER")
    print("=" * 72)
    print()
    print("Cross-border channels modeled on real historical analogues.")
    print("Run on top of two cascade backdrops, because different channels")
    print("bind on different cascade constraints:")
    print("  - fao: short broad-sharing disruption, timing-loss dominates")
    print("  - wfp: 12-month prolonged disruption, N-loss dominates")
    print()

    for backdrop_name, backdrop_label in [
        ("fao", "FAO BACKDROP (6-month broad-sharing; timing dominates)"),
        ("wfp", "WFP BACKDROP (12-month prolonged; N-loss dominates)"),
    ]:
        baseline = run_baseline(backdrop_name)
        print("=" * 72)
        print(backdrop_label)
        print("=" * 72)
        print(f"  baseline (no cooperation): {baseline/1e6:>7.1f} M deaths")
        print()

        print("  PER-CHANNEL CONTRIBUTION (central plausibility)")
        print("  " + "-" * 70)
        print(f"  {'channel':<38} {'plaus.':>8} {'lead':>6} {'saved':>11}")
        for ch in CHANNELS:
            d = run_with_cooperation([ch], scale=1.0, backdrop=backdrop_name)
            saved = baseline - d
            print(f"  {ch.name:<38} {ch.plausibility:>8} "
                  f"{ch.lead_time_months:>3} mo {saved/1e6:>8.2f} M")
        print()

        print("  CUMULATIVE STACK (high-plausibility channels first)")
        print("  " + "-" * 70)
        stack: List[CooperationChannel] = []
        order = sorted(CHANNELS,
                       key=lambda c: ({"high":0,"medium":1,"low":2}[c.plausibility],
                                       c.lead_time_months))
        print(f"  {'+ add channel':<46} {'deaths':>11} {'saved':>11}")
        for ch in order:
            stack.append(ch)
            d = run_with_cooperation(stack, scale=1.0,
                                      backdrop=backdrop_name)
            print(f"  + {ch.name:<44} "
                  f"{d/1e6:>8.1f} M {((baseline-d)/1e6):>8.1f} M")
        print()

        print("  PLAUSIBILITY SENSITIVITY (full stack)")
        print("  " + "-" * 70)
        for label, scale in [("skeptical (0.5x)", 0.5),
                              ("central (1.0x)",  1.0),
                              ("optimistic (1.5x)", 1.5)]:
            d = run_with_cooperation(CHANNELS, scale=scale,
                                      backdrop=backdrop_name)
            print(f"  {label:<25} -> {d/1e6:>7.1f} M deaths "
                  f"({(baseline-d)/1e6:>+6.1f} M vs baseline)")
        print()

    print()
    print("=" * 72)
    print("WHY CHANNELS BEHAVE DIFFERENTLY ACROSS BACKDROPS")
    print("=" * 72)
    print("""
  The cascade computes effective_loss = max(n_loss, timing_loss).
  Whichever is larger binds; reducing the smaller one is invisible.

  Channels that act on N SUPPLY:
    - watershed_N_management         (substitution_lag, buffer_stock)
    - microbial_culture_exchange     (substitution_lag)
    - composting_standards           (substitution_lag + redistribution)
    - biome_scale_N_sinks            (buffer_stock)

  Channels that act on TIMING:
    - germplasm_seed_sharing         (planting_delay)

  Channels that act on REDISTRIBUTION / CONCENTRATION:
    - composting_standards           (buffer_redistribution)
    - forecasting_early_warning      (absorption + redistribution)

  Channels that act on YIELD FLOOR:
    - pollinator_biological_corridors (solar_drag)
    - biome_scale_N_sinks             (solar_drag)

  Watershed coordination delivers real engineering value but appears
  invisible in both backdrops shown above because timing (or N) is
  binding harder than the channel can shift on its own. It becomes
  visible only when paired with a channel from the other constraint
  family — germplasm sharing pulls timing_loss down far enough that
  watershed's N-supply effect can register.

  Reading: there is no single 'best' cooperation channel. The
  portfolio matters more than any single one, because biome-scale
  cooperation moves multiple cascade parameters at once and the
  cascade's mortality is set by whichever one is largest.
""")
    print()

    print("CITATIONS")
    print("-" * 72)
    used_keys: set[str] = set()
    for ch in CHANNELS:
        for k in ch.citation_keys:
            used_keys.add(k)
    for k in sorted(used_keys):
        print(f"  [{k}]")
        # word-wrap to 70 cols
        text = CITATIONS[k]
        line = "    "
        for word in text.split():
            if len(line) + len(word) + 1 > 70:
                print(line)
                line = "    " + word
            else:
                line += (" " if line.strip() else "") + word
        if line.strip():
            print(line)
        print()

    print("=" * 72)
    print("READING")
    print("=" * 72)
    print("""
  Regulatory relaxation (regulatory_cascade_crosslink) and biome
  cooperation are not substitutes. They are complements:

    - regulatory relaxation lowers vulnerable_absorption by removing
      the prohibition on the closed-loop pathway

    - biome cooperation lowers substitution_lag_months, raises
      buffer_redistribution, and stabilizes the yield floor by
      ADDING positive cross-border redundancy

  The biome does not recognize national borders. The mortality
  cascade does not either: it concentrates wherever the local
  pathway has been removed AND the cross-border pathway is closed.

  Open one and the floor lifts. Open both and the cascade is no
  longer at its structural ceiling.
""")


if __name__ == "__main__":
    report()
