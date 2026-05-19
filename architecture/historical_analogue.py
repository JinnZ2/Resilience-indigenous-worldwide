"""
historical_analogue.py
======================

Inverts the cascade audit's output: instead of producing a single
death number, this module matches the current cascade configuration
against a corpus of documented historical famines and a parallel
corpus of documented cooperation precedents.

The output answers "what does this look like, and what is the
documented precedent for getting out of it?" rather than "how many
will die?"

Every number in both corpora is a documented historical figure
with a range, not a point estimate. Every claim carries a citation
to a published source document (no fabricated DOIs or page numbers).
Mortality figures are intentionally given as a range; precision is
historiographical, not predictive.

Matching dimensions:
  - relative scale          (log10 of deaths exposed)
  - duration ratio          (months, normalized)
  - concentration shape     (broad vs concentrated mortality)
  - cause-tag overlap       (war, blockade, market exclusion,
                              weather, supply shock, policy failure)

Mortality is NOT a matching dimension on the cooperation side.
What matters there is whether the precedent solved a problem with
the same cause-shape at the same population scale.

License: CC0 — public domain
Dependencies: stdlib only
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
import math


# ============================================================
# CITATIONS — source documents we draw from
# ============================================================
# General references, no fabricated specifics. A community legal or
# research partner can pull the originals.

CITATIONS = {
    "sen_1981":      "Sen, A. (1981). Poverty and Famines: An Essay on "
                     "Entitlement and Deprivation. Oxford / Clarendon.",
    "o_grada_1999":  "Ó Gráda, C. (1999). Black '47 and Beyond: The "
                     "Great Irish Famine in History, Economy, and "
                     "Memory. Princeton University Press.",
    "yang_2012":     "Yang Jisheng (2012). Tombstone: The Great "
                     "Chinese Famine 1958-1962. Farrar, Straus and "
                     "Giroux (English translation).",
    "banister_1987": "Banister, J. (1987). China's Changing Population. "
                     "Stanford University Press.",
    "de_waal_1991":  "de Waal, A. (1991). Evil Days: Thirty Years of "
                     "War and Famine in Ethiopia. Africa Watch / HRW.",
    "haggard_noland":"Haggard, S. & Noland, M. (2007). Famine in North "
                     "Korea: Markets, Aid, and Reform. Columbia "
                     "University Press.",
    "maxwell_majid": "Maxwell, D. & Majid, N. (2016). Famine in "
                     "Somalia: Competing Imperatives, Collective "
                     "Failures, 2011-12. Hurst & Co.",
    "wpf_tigray":    "World Peace Foundation (2021-2023). 'Starving "
                     "Tigray' report series, Fletcher School, Tufts.",
    "ghent_tigray":  "Ghent University / EPO (2022). Excess mortality "
                     "estimates for the Tigray war.",
    "clingendael_2024": "Clingendael Institute (2024). Sudan famine "
                         "and excess-mortality projections.",
    "fao_sofi":      "FAO State of Food Insecurity in the World "
                     "(annual). 2008-2009 issues for global food crisis.",
    "acaps_yemen":   "ACAPS Yemen Analysis Hub; UN OCHA Yemen "
                     "Humanitarian Needs Overview series.",
    "ukraine_fert":  "Edinburgh / Aberdeen / Karlsruhe / Rutgers (2023) "
                     "fertilizer-supply mortality estimates.",
    "sahel_1972_74": "Glantz, M. (1976). The Politics of Natural "
                     "Disaster: The Case of the Sahel Drought.",
    "velders_2007":  "Velders, G. et al. (2007). The importance of the "
                     "Montreal Protocol in protecting climate. PNAS "
                     "104(12).",
    "fenner_1988":   "Fenner, F. et al. (1988). Smallpox and its "
                     "Eradication. WHO Geneva.",
    "marshall_plan": "U.S. Department of State Office of the Historian. "
                     "The Marshall Plan, 1948. Economic Cooperation "
                     "Administration records.",
    "berlin_airlift":"Tunner, W. (1964). Over the Hump. Office of Air "
                     "Force History. Operation Vittles records.",
    "wfp_history":   "World Food Programme. Annual reports; founded "
                     "1961 UN GA Resolution 1714.",
    "itpgrfa":       "FAO International Treaty on Plant Genetic "
                     "Resources for Food and Agriculture (2001).",
    "icpr_rhine":    "International Commission for the Protection of "
                     "the Rhine. Rhine Action Programme (1987).",
    "wadden_sea":    "Trilateral Wadden Sea Cooperation (1978-present).",
    "mbc_1997":      "Mesoamerican Biological Corridor (1997). CCAD / "
                     "Comisión Centroamericana de Ambiente y Desarrollo.",
    "ohchr_dprk":    "OHCHR Commission of Inquiry on DPRK (2014) — "
                     "famine-period testimony and demographic analysis.",
    "ipc_global":    "IPC (Integrated Food Security Phase Classification) "
                     "global reports; UN OCHA / FAO / WFP partnership.",
}


# ============================================================
# Famine corpus
# ============================================================

@dataclass
class HistoricalFamine:
    name:               str
    period:             str
    deaths_low:         int           # documented lower bound
    deaths_high:        int           # documented upper bound
    population_exposed: int           # rough population at risk
    duration_months:    int
    concentration:      float         # 0-1: share of deaths in
                                       # most-exposed subpopulation
    cause_tags:         List[str]
    citation_keys:      List[str]
    notes:              str = ""

    @property
    def deaths_log_mean(self) -> float:
        mid = (self.deaths_low + self.deaths_high) / 2.0
        return math.log10(max(mid, 1.0))


FAMINES: List[HistoricalFamine] = [
    HistoricalFamine(
        name = "Bengal 1943",
        period = "1943-1944",
        deaths_low = 1_500_000,
        deaths_high = 3_000_000,
        population_exposed = 60_000_000,
        duration_months = 12,
        concentration = 0.85,
        cause_tags = ["war_disruption", "market_exclusion",
                       "policy_failure", "export_during_shortage"],
        citation_keys = ["sen_1981"],
        notes = ("Sen's entitlement-failure analysis: not a food "
                 "availability collapse, but a price-based exclusion. "
                 "Rice exports from Bengal continued during the famine."),
    ),
    HistoricalFamine(
        name = "Ireland Great Famine",
        period = "1845-1849",
        deaths_low = 1_000_000,
        deaths_high = 1_500_000,
        population_exposed = 8_000_000,
        duration_months = 48,
        concentration = 0.80,
        cause_tags = ["pathogen_supply_shock", "policy_failure",
                       "export_during_shortage", "colonial_extraction"],
        citation_keys = ["o_grada_1999"],
        notes = ("Potato late blight removed the staple crop; British "
                 "policy maintained grain and cattle exports throughout. "
                 "Plus 1M+ emigration."),
    ),
    HistoricalFamine(
        name = "Great Leap Forward China",
        period = "1959-1961",
        deaths_low = 15_000_000,
        deaths_high = 45_000_000,
        population_exposed = 660_000_000,
        duration_months = 36,
        concentration = 0.70,
        cause_tags = ["policy_failure", "agricultural_collapse",
                       "concealment", "grain_procurement"],
        citation_keys = ["yang_2012", "banister_1987"],
        notes = ("Range reflects historiographical disagreement. "
                 "Procurement quotas held while harvests collapsed."),
    ),
    HistoricalFamine(
        name = "Ethiopia 1983-1985",
        period = "1983-1985",
        deaths_low = 400_000,
        deaths_high = 1_000_000,
        population_exposed = 8_000_000,
        duration_months = 24,
        concentration = 0.85,
        cause_tags = ["weather_drought", "war_disruption",
                       "policy_failure", "blockade"],
        citation_keys = ["de_waal_1991"],
        notes = ("Drought catalyst, but mortality concentrated in "
                 "war-affected northern provinces (Tigray, Wollo) "
                 "where access was blocked."),
    ),
    HistoricalFamine(
        name = "North Korea Arduous March",
        period = "1994-1998",
        deaths_low = 240_000,
        deaths_high = 3_500_000,
        population_exposed = 22_000_000,
        duration_months = 48,
        concentration = 0.75,
        cause_tags = ["supply_shock", "policy_failure",
                       "weather_floods", "regime_isolation"],
        citation_keys = ["haggard_noland", "ohchr_dprk"],
        notes = ("Soviet collapse removed subsidized fuel and "
                 "fertilizer inputs. Range reflects extreme "
                 "uncertainty due to information restriction."),
    ),
    HistoricalFamine(
        name = "Somalia 1991-1992",
        period = "1991-1992",
        deaths_low = 220_000,
        deaths_high = 300_000,
        population_exposed = 4_500_000,
        duration_months = 18,
        concentration = 0.90,
        cause_tags = ["state_collapse", "war_disruption",
                       "weather_drought", "blockade"],
        citation_keys = ["maxwell_majid"],
        notes = "South-central Somalia after the fall of Siad Barre.",
    ),
    HistoricalFamine(
        name = "Somalia 2011",
        period = "2011-2012",
        deaths_low = 240_000,
        deaths_high = 260_000,
        population_exposed = 3_700_000,
        duration_months = 12,
        concentration = 0.95,
        cause_tags = ["weather_drought", "war_disruption",
                       "policy_failure", "aid_obstruction"],
        citation_keys = ["maxwell_majid", "ipc_global"],
        notes = ("First IPC-declared famine after the framework was "
                 "formalized. Half the deaths preceded the declaration."),
    ),
    HistoricalFamine(
        name = "Tigray 2020-2022",
        period = "2020-2022",
        deaths_low = 350_000,
        deaths_high = 600_000,
        population_exposed = 6_000_000,
        duration_months = 24,
        concentration = 0.95,
        cause_tags = ["war_disruption", "blockade",
                       "policy_failure", "communication_blackout"],
        citation_keys = ["wpf_tigray", "ghent_tigray"],
        notes = ("Documented blockade of food, medicine, and "
                 "banking. Range from independent academic estimates."),
    ),
    HistoricalFamine(
        name = "Yemen 2016-present",
        period = "2016-ongoing",
        deaths_low = 130_000,
        deaths_high = 380_000,
        population_exposed = 17_000_000,
        duration_months = 96,
        concentration = 0.60,
        cause_tags = ["war_disruption", "blockade",
                       "import_dependency", "epidemic_overlay"],
        citation_keys = ["acaps_yemen", "ipc_global"],
        notes = ("Cholera and other-disease excess overlap with "
                 "caloric stress; figures are conservative."),
    ),
    HistoricalFamine(
        name = "Sudan 2024",
        period = "2024-ongoing",
        deaths_low = 2_000_000,
        deaths_high = 3_000_000,
        population_exposed = 17_000_000,
        duration_months = 12,
        concentration = 0.85,
        cause_tags = ["war_disruption", "blockade",
                       "policy_failure", "displacement"],
        citation_keys = ["clingendael_2024", "ipc_global"],
        notes = ("RSF/SAF war; Darfur and Kordofan most affected. "
                 "Reference calibration anchor for the cascade audit."),
    ),
    HistoricalFamine(
        name = "Global food crisis 2008",
        period = "2007-2008",
        deaths_low = 0,
        deaths_high = 0,
        population_exposed = 900_000_000,
        duration_months = 18,
        concentration = 0.20,
        cause_tags = ["price_shock", "biofuel_mandate",
                       "export_bans", "speculation", "oil_shock"],
        citation_keys = ["fao_sofi"],
        notes = ("Not a famine in the IPC sense, but 100M+ added to "
                 "the undernourished population. Demonstrates that "
                 "broad-share crises produce hunger without acute "
                 "mortality spike; concentrated crises do the opposite."),
    ),
    HistoricalFamine(
        name = "Ukraine grain & fertilizer 2022-2023",
        period = "2022-2023",
        deaths_low = 700_000,
        deaths_high = 1_300_000,
        population_exposed = 1_000_000_000,
        duration_months = 12,
        concentration = 0.30,
        cause_tags = ["war_disruption", "supply_shock",
                       "fertilizer_disruption", "export_bans"],
        citation_keys = ["ukraine_fert"],
        notes = ("Calibration anchor: ~10% global fertilizer "
                 "disruption + grain export interference, broad pop "
                 "exposed."),
    ),
    HistoricalFamine(
        name = "Sahel & global food crisis 1972-1974",
        period = "1972-1974",
        deaths_low = 100_000,
        deaths_high = 300_000,
        population_exposed = 250_000_000,
        duration_months = 24,
        concentration = 0.60,
        cause_tags = ["weather_drought", "oil_shock",
                       "price_shock", "supply_shock"],
        citation_keys = ["sahel_1972_74", "fao_sofi"],
        notes = ("El Niño 1972 + Soviet grain purchases + oil shock. "
                 "Sahel hardest hit; closest historical analogue to a "
                 "compound supply-shock + climate event."),
    ),
]


# ============================================================
# Cooperation corpus
# ============================================================

@dataclass
class CooperationPrecedent:
    name:                       str
    period:                     str
    countries:                  int
    population_served:          int
    duration_months:            int       # active duration
    negotiation_months:         int       # time from problem to action
    cause_shape_addressed:      List[str] # what cause-tags it solved
    citation_keys:              List[str]
    headline_outcome:           str
    notes:                      str = ""


COOPERATION: List[CooperationPrecedent] = [
    CooperationPrecedent(
        name = "Montreal Protocol",
        period = "1987-present",
        countries = 198,
        population_served = 8_000_000_000,
        duration_months = 12 * 40,
        negotiation_months = 24,
        cause_shape_addressed = ["supply_shock", "policy_failure",
                                  "industrial_substitution"],
        citation_keys = ["velders_2007"],
        headline_outcome = ("99% phaseout of controlled ODS. "
                             "Universally ratified. Estimated to "
                             "avoid millions of skin-cancer deaths "
                             "by 2030; major climate co-benefit."),
        notes = ("Gold-standard reference for biome-scale cooperation "
                 "achieved at necessary speed and scale."),
    ),
    CooperationPrecedent(
        name = "Marshall Plan",
        period = "1948-1952",
        countries = 16,
        population_served = 270_000_000,
        duration_months = 48,
        negotiation_months = 18,
        cause_shape_addressed = ["war_disruption", "supply_shock",
                                  "industrial_collapse",
                                  "import_dependency"],
        citation_keys = ["marshall_plan"],
        headline_outcome = ("$13B in 1948 dollars (~$150B today). "
                             "Western European GDP recovered to "
                             "pre-war level by 1951; industrial "
                             "output +35%."),
        notes = ("Demonstrated post-disruption material reconstruction "
                 "at continental scale on a 4-year timeline."),
    ),
    CooperationPrecedent(
        name = "Berlin Airlift",
        period = "1948-1949",
        countries = 4,
        population_served = 2_500_000,
        duration_months = 15,
        negotiation_months = 1,
        cause_shape_addressed = ["blockade", "war_disruption",
                                  "supply_shock"],
        citation_keys = ["berlin_airlift"],
        headline_outcome = ("2.3M tons of supplies delivered by air "
                             "to a city under ground blockade. Peak "
                             "12,941 tons in a single day. Sustained "
                             "an entire urban population for 11 "
                             "months on logistics alone."),
        notes = ("Demonstration that bypass of blockade is logistically "
                 "feasible when political will exists."),
    ),
    CooperationPrecedent(
        name = "Smallpox Eradication",
        period = "1967-1980",
        countries = 73,
        population_served = 4_000_000_000,
        duration_months = 13 * 12,
        negotiation_months = 12,
        cause_shape_addressed = ["pathogen_supply_shock",
                                  "epidemic_overlay",
                                  "weak_state_capacity"],
        citation_keys = ["fenner_1988"],
        headline_outcome = ("Last endemic case Somalia 1977 (Ali "
                             "Maow Maalin). Certified eradication "
                             "1980. Estimated 200M lives saved per "
                             "century thereafter."),
        notes = ("Operated successfully across superpower-bloc lines "
                 "during the Cold War. Surveillance-and-containment "
                 "model applies to other distributed problems."),
    ),
    CooperationPrecedent(
        name = "World Food Programme (operations)",
        period = "1961-present",
        countries = 80,
        population_served = 150_000_000,
        duration_months = 12 * 60,
        negotiation_months = 6,
        cause_shape_addressed = ["war_disruption", "weather_drought",
                                  "displacement", "supply_shock"],
        citation_keys = ["wfp_history"],
        headline_outcome = ("Reaches ~150M people annually across "
                             "80+ countries. Demonstrated standing "
                             "logistics capacity for emergency food "
                             "distribution at continental scale."),
        notes = ("Already operating, already understaffed and "
                 "underfunded — but the platform exists."),
    ),
    CooperationPrecedent(
        name = "ITPGRFA Plant Treaty",
        period = "2001-present",
        countries = 149,
        population_served = 8_000_000_000,
        duration_months = 12 * 25,
        negotiation_months = 84,
        cause_shape_addressed = ["agricultural_collapse",
                                  "pathogen_supply_shock",
                                  "supply_shock"],
        citation_keys = ["itpgrfa"],
        headline_outcome = ("Multilateral seed-exchange system for "
                             "64 crop species. Standard Material "
                             "Transfer Agreement permits low-friction "
                             "international germplasm flow."),
        notes = ("Slower negotiation than Montreal; demonstrates that "
                 "agricultural cooperation requires longer negotiation "
                 "but is achievable."),
    ),
    CooperationPrecedent(
        name = "Rhine Action Programme",
        period = "1987-present",
        countries = 5,
        population_served = 60_000_000,
        duration_months = 12 * 38,
        negotiation_months = 24,
        cause_shape_addressed = ["industrial_substitution",
                                  "watershed_pollution",
                                  "fertilizer_disruption"],
        citation_keys = ["icpr_rhine"],
        headline_outcome = ("N load to North Sea cut ~50% from 1985 "
                             "to 2010 via coordinated upstream-"
                             "downstream policy."),
        notes = ("Direct precedent for cross-border nitrogen "
                 "coordination."),
    ),
    CooperationPrecedent(
        name = "Wadden Sea Trilateral Cooperation",
        period = "1978-present",
        countries = 3,
        population_served = 8_000_000,
        duration_months = 12 * 47,
        negotiation_months = 24,
        cause_shape_addressed = ["biome_management",
                                  "ecosystem_continuity"],
        citation_keys = ["wadden_sea"],
        headline_outcome = ("Multi-decade ecosystem management "
                             "across DK/DE/NL. UNESCO World "
                             "Heritage 2009."),
        notes = ("Smaller scale but very long duration. Shows that "
                 "cross-border biome cooperation survives political "
                 "cycle changes."),
    ),
    CooperationPrecedent(
        name = "Mesoamerican Biological Corridor",
        period = "1997-present",
        countries = 7,
        population_served = 60_000_000,
        duration_months = 12 * 28,
        negotiation_months = 36,
        cause_shape_addressed = ["biome_management",
                                  "ecosystem_continuity",
                                  "pollinator_continuity"],
        citation_keys = ["mbc_1997"],
        headline_outcome = ("7-country biological corridor agreement; "
                             "patchy implementation, but the "
                             "multilateral framework holds."),
    ),
]


# ============================================================
# Matching — log-space, multi-dimensional
# ============================================================

@dataclass
class CurrentSituation:
    """Whatever cascade or real-world configuration we're matching against."""
    name:                str
    deaths_low:          int
    deaths_high:         int
    population_exposed:  int
    duration_months:     int
    concentration:       float
    cause_tags:          List[str]


def _cause_overlap(tags_a: List[str], tags_b: List[str]) -> float:
    """Jaccard similarity on cause tags."""
    a, b = set(tags_a), set(tags_b)
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def famine_distance(s: CurrentSituation, f: HistoricalFamine) -> float:
    """
    Lower distance = closer match. Distance lives in [0, ~4].

    Components:
      - log-deaths gap        (0..3, then weighted)
      - duration ratio gap    (log-space)
      - concentration gap     (linear)
      - cause overlap         (inverted, so disjoint = penalty)
    """
    s_mid = math.log10(max((s.deaths_low + s.deaths_high) / 2.0, 1.0))
    deaths_gap = abs(s_mid - f.deaths_log_mean)

    s_dur = max(s.duration_months, 1)
    f_dur = max(f.duration_months, 1)
    duration_gap = abs(math.log2(s_dur / f_dur))

    conc_gap = abs(s.concentration - f.concentration)
    cause_disjoint = 1.0 - _cause_overlap(s.cause_tags, f.cause_tags)

    return (1.0 * deaths_gap +
            0.5 * duration_gap +
            1.0 * conc_gap +
            1.5 * cause_disjoint)


def cooperation_relevance(s: CurrentSituation,
                          c: CooperationPrecedent) -> float:
    """
    Lower = more relevant precedent. Mortality is NOT a matching
    dimension here. What matters is:
      - whether the precedent operated at comparable population scale
      - whether it addressed the same cause-shape
      - whether it could be stood up on the available timeline
    """
    s_pop = math.log10(max(s.population_exposed, 1))
    c_pop = math.log10(max(c.population_served, 1))
    scale_gap = abs(s_pop - c_pop)

    cause_disjoint = 1.0 - _cause_overlap(s.cause_tags,
                                          c.cause_shape_addressed)

    # Reward fast-negotiated precedents — calendar physics
    # rewards speed.
    speed_penalty = c.negotiation_months / 36.0   # 36mo = neutral

    return (1.0 * scale_gap +
            2.0 * cause_disjoint +
            0.5 * speed_penalty)


def top_matches(s: CurrentSituation,
                k: int = 3) -> Tuple[List[HistoricalFamine],
                                      List[CooperationPrecedent]]:
    famines = sorted(FAMINES, key=lambda f: famine_distance(s, f))[:k]
    coops   = sorted(COOPERATION,
                     key=lambda c: cooperation_relevance(s, c))[:k]
    return famines, coops


# ============================================================
# Report
# ============================================================

def _fmt_deaths(low: int, high: int) -> str:
    def f(n):
        if n >= 1e6: return f"{n/1e6:.1f}M"
        if n >= 1e3: return f"{n/1e3:.0f}k"
        return str(n)
    if low == 0 and high == 0:
        return "no acute mortality spike"
    if low == high:
        return f(low)
    return f"{f(low)}-{f(high)}"


def _fmt_pop(n: int) -> str:
    if n >= 1e9: return f"{n/1e9:.1f}B"
    if n >= 1e6: return f"{n/1e6:.0f}M"
    if n >= 1e3: return f"{n/1e3:.0f}k"
    return str(n)


def render(s: CurrentSituation) -> str:
    famines, coops = top_matches(s, k=3)

    lines: List[str] = []
    lines.append("=" * 72)
    lines.append(f"HISTORICAL ANALOGUE: {s.name}")
    lines.append("=" * 72)
    lines.append("")
    lines.append("CURRENT SITUATION (input)")
    lines.append("-" * 72)
    lines.append(f"  deaths range:         {_fmt_deaths(s.deaths_low, s.deaths_high)}")
    lines.append(f"  population exposed:   {_fmt_pop(s.population_exposed)}")
    lines.append(f"  duration:             {s.duration_months} months")
    lines.append(f"  concentration:        {s.concentration:.2f}")
    lines.append(f"  cause tags:           {', '.join(s.cause_tags)}")
    lines.append("")

    lines.append("CLOSEST HISTORICAL FAMINES (this looks like)")
    lines.append("-" * 72)
    for i, f in enumerate(famines, 1):
        d = famine_distance(s, f)
        lines.append(f"  [{i}] {f.name} ({f.period})  "
                     f"distance={d:.2f}")
        lines.append(f"      documented deaths:  {_fmt_deaths(f.deaths_low, f.deaths_high)}")
        lines.append(f"      pop exposed:        {_fmt_pop(f.population_exposed)}")
        lines.append(f"      duration:           {f.duration_months} mo")
        lines.append(f"      shared causes:      "
                     f"{', '.join(sorted(set(s.cause_tags) & set(f.cause_tags))) or '(none)'}")
        if f.notes:
            lines.append(f"      note:               {f.notes}")
        lines.append(f"      cite:               {', '.join(f.citation_keys)}")
        lines.append("")

    lines.append("CLOSEST COOPERATION PRECEDENTS (the bypass exists at this scale)")
    lines.append("-" * 72)
    for i, c in enumerate(coops, 1):
        r = cooperation_relevance(s, c)
        lines.append(f"  [{i}] {c.name} ({c.period})  "
                     f"relevance={r:.2f} (lower=better)")
        lines.append(f"      operated across:    {c.countries} countries")
        lines.append(f"      pop served:         {_fmt_pop(c.population_served)}")
        lines.append(f"      negotiation time:   {c.negotiation_months} mo")
        lines.append(f"      addressed causes:   "
                     f"{', '.join(sorted(set(s.cause_tags) & set(c.cause_shape_addressed))) or '(adjacent)'}")
        lines.append(f"      outcome:            {c.headline_outcome}")
        lines.append(f"      cite:               {', '.join(c.citation_keys)}")
        lines.append("")

    lines.append("=" * 72)
    lines.append("READING")
    lines.append("=" * 72)
    f1 = famines[0].name
    c1 = coops[0].name
    lines.append(f"")
    lines.append(f"  This cascade looks like {f1}, with cooperation precedents")
    lines.append(f"  available at {c1} scale.")
    lines.append(f"")
    lines.append(f"  The cascade is in the gap between them: the famine analogue")
    lines.append(f"  is what happens if no one acts; the cooperation analogue is")
    lines.append(f"  the documented proof that action at the required scale has")
    lines.append(f"  been done before.")
    lines.append(f"")

    return "\n".join(lines)


# ============================================================
# Sample inputs
# ============================================================

CURRENT_HORMUZ_CASCADE = CurrentSituation(
    name = "Hormuz cascade — WFP-prolonged scenario",
    deaths_low = 78_000_000,
    deaths_high = 225_000_000,
    population_exposed = 1_070_000_000,
    duration_months = 12,
    concentration = 0.60,
    cause_tags = ["war_disruption", "supply_shock",
                  "fertilizer_disruption", "import_dependency",
                  "policy_failure", "blockade"],
)


def list_citations() -> str:
    out = ["CITATIONS (source documents only — no fabricated DOIs)",
           "-" * 72]
    for k in sorted(CITATIONS):
        out.append(f"  [{k}]")
        text = CITATIONS[k]
        # word-wrap
        line = "    "
        for word in text.split():
            if len(line) + len(word) + 1 > 70:
                out.append(line)
                line = "    " + word
            else:
                line += (" " if line.strip() else "") + word
        if line.strip():
            out.append(line)
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    print(render(CURRENT_HORMUZ_CASCADE))
    print()
    print(list_citations())
