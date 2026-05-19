"""
village_n_closure.py
====================

A village-scale nutrient-closure toolkit.

Given:
  - population
  - planted area & target crops
  - locally available substrates (animals, biomass, legumes, ash,
    fish waste, seaweed, wood, water hyacinth, etc.)
  - climate band / planting calendar

Computes:
  - N, P, K need for the target yield
  - N, P, K supply from each available substrate
  - deficit/surplus per nutrient
  - dispatch sequence: which substrate to process first, by leverage
  - composting/fermentation timeline aligned to planting window
  - safe-handling protocol summary

No external dependencies. No network. No accounts. Runs on any phone
with a Python interpreter. CC0 — public domain.

Usage:
    python3 village_n_closure.py            # runs demo village
    python3 -c "import village_n_closure as v; v.run_custom(...)"

Or edit the EXAMPLE_VILLAGE dict at bottom and re-run.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import math


# ============================================================
# 1. CROP REQUIREMENTS  (kg nutrient per tonne of grain yield)
#    Sources: FAO fertilizer use guides, soil science consensus
# ============================================================

CROP_NUTRIENT_NEED = {
    # crop:      (N, P2O5, K2O)  kg per tonne grain
    "maize":       (22.0,  8.0,  18.0),
    "wheat":       (25.0,  9.0,  17.0),
    "rice":        (20.0,  7.0,  25.0),
    "sorghum":     (20.0,  8.0,  18.0),
    "millet":      (18.0,  7.0,  16.0),
    "barley":      (22.0,  8.0,  17.0),
    "potato":      ( 4.0,  1.5,   6.0),   # per tonne fresh tuber
    "cassava":     ( 6.0,  1.0,   8.0),
    "teff":        (20.0,  7.0,  16.0),
    "quinoa":      (25.0,  9.0,  20.0),
    "oats":        (22.0,  8.0,  17.0),
}

TYPICAL_YIELD_T_PER_HA = {     # rough subsistence-to-moderate range
    "maize":   3.5,
    "wheat":   3.0,
    "rice":    4.0,
    "sorghum": 2.5,
    "millet":  1.8,
    "barley":  2.8,
    "potato": 18.0,
    "cassava":12.0,
    "teff":    1.5,
    "quinoa":  2.0,
    "oats":    2.5,
}

# ============================================================
# 2. SUBSTRATE NUTRIENT CONTENT  (% dry matter or kg/yr/unit)
# ============================================================
# Each substrate gives N, P2O5, K2O per UNIT (defined below)

SUBSTRATES = {
    # humanure & related
    "humanure_composted": {
        "unit":     "person-year",
        "yield":    {"N": 4.0,  "P2O5": 1.4, "K2O": 1.5},
        "lag_mo":   6,
        "notes":    "thermophilic compost 55C, 3-day kill, cure 6mo",
        "safety":   "WHO 2-stage protocol; never apply raw",
        "scale":    "household-to-village",
    },
    "urine_diverted": {
        "unit":     "person-year",
        "yield":    {"N": 4.0,  "P2O5": 0.4, "K2O": 1.0},
        "lag_mo":   1,
        "notes":    "stored sealed 1 month (pH >9 self-sterilizes)",
        "safety":   "low pathogen risk if stored; dilute 1:10 for application",
        "scale":    "household",
    },
    # livestock
    "cattle_manure": {
        "unit":     "animal-year",
        "yield":    {"N": 60.0, "P2O5": 20.0, "K2O": 40.0},
        "lag_mo":   3,
        "notes":    "compost 90+ days; mix with straw 3:1",
        "safety":   "kills weed seeds + pathogens via thermophilic phase",
        "scale":    "household-to-village",
    },
    "chicken_manure": {
        "unit":     "10 birds-year",
        "yield":    {"N": 5.0,  "P2O5": 4.0, "K2O": 2.5},
        "lag_mo":   3,
        "notes":    "very hot — must compost 90 days, never apply fresh",
        "safety":   "high N concentration; burns roots if uncomposted",
        "scale":    "household",
    },
    "goat_sheep_manure": {
        "unit":     "animal-year",
        "yield":    {"N": 12.0, "P2O5": 4.0, "K2O": 9.0},
        "lag_mo":   2,
        "notes":    "drier than cattle, faster compost",
        "safety":   "standard composting; turn 3-4x",
        "scale":    "household",
    },
    "pig_manure": {
        "unit":     "animal-year",
        "yield":    {"N": 25.0, "P2O5": 18.0, "K2O": 15.0},
        "lag_mo":   3,
        "notes":    "high P — pair with low-P substrate",
        "safety":   "compost 90 days; pathogen risk requires thermophilic",
        "scale":    "household",
    },
    "rabbit_manure": {
        "unit":     "animal-year",
        "yield":    {"N": 8.0,  "P2O5": 4.0, "K2O": 6.0},
        "lag_mo":   0,
        "notes":    "cold-applicable — rare among manures",
        "safety":   "can apply directly to soil without composting",
        "scale":    "household",
    },
    # legumes (N-fixing crops)
    "legume_residue_inplace": {
        "unit":     "ha of legume cover",
        "yield":    {"N": 80.0, "P2O5": 5.0, "K2O": 30.0},
        "lag_mo":   1,
        "notes":    "cowpea, mungbean, vetch, clover — incorporate at flowering",
        "safety":   "no pathogen risk; chop and turn in",
        "scale":    "any",
    },
    "azolla_pond": {
        "unit":     "100 m2 pond-year",
        "yield":    {"N": 50.0, "P2O5": 8.0, "K2O": 20.0},
        "lag_mo":   1,
        "notes":    "aquatic fern; fixes N from air via cyanobacteria",
        "safety":   "no pathogen; classic rice-paddy intercrop",
        "scale":    "any (needs standing water)",
    },
    # plant biomass / green manure
    "green_manure_grass": {
        "unit":     "tonne dry biomass",
        "yield":    {"N": 12.0, "P2O5": 3.0, "K2O": 15.0},
        "lag_mo":   2,
        "notes":    "chop, wilt, compost or trench-in",
        "safety":   "no pathogen risk",
        "scale":    "any",
    },
    "water_hyacinth": {
        "unit":     "tonne fresh",
        "yield":    {"N": 3.0,  "P2O5": 0.7, "K2O": 4.0},
        "lag_mo":   2,
        "notes":    "invasive aquatic — abundant in tropics, free input",
        "safety":   "no pathogen; chop before composting",
        "scale":    "village-scale where present",
    },
    "seaweed_kelp": {
        "unit":     "tonne fresh",
        "yield":    {"N": 4.0,  "P2O5": 1.0, "K2O": 20.0},
        "lag_mo":   1,
        "notes":    "rinse salt; high K + trace minerals",
        "safety":   "no pathogen; coastal communities only",
        "scale":    "coastal",
    },
    "fish_waste": {
        "unit":     "tonne fresh",
        "yield":    {"N": 30.0, "P2O5": 25.0, "K2O": 5.0},
        "lag_mo":   2,
        "notes":    "ferment as fish emulsion or bokashi",
        "safety":   "pathogen-low; smell-control via bokashi/EM",
        "scale":    "coastal + fish-processing areas",
    },
    # ash + biochar
    "wood_ash": {
        "unit":     "tonne",
        "yield":    {"N": 0.0,  "P2O5": 20.0, "K2O": 50.0},
        "lag_mo":   0,
        "notes":    "high pH — use carefully on acid soils; not on alkaline",
        "safety":   "no pathogen; raises soil pH",
        "scale":    "any with biomass burning",
    },
    "biochar_charged": {
        "unit":     "tonne",
        "yield":    {"N": 5.0,  "P2O5": 8.0, "K2O": 12.0},
        "lag_mo":   1,
        "notes":    "charge in urine or compost tea before applying",
        "safety":   "no pathogen; long-term soil carbon",
        "scale":    "any with biomass + kiln",
    },
    "bokashi_food_scrap": {
        "unit":     "tonne fresh scrap",
        "yield":    {"N": 6.0,  "P2O5": 2.0, "K2O": 4.0},
        "lag_mo":   1,
        "notes":    "anaerobic ferment with EM/LAB; 2 weeks then bury",
        "safety":   "low pathogen risk if pH < 4",
        "scale":    "household-to-village",
    },
    "rock_phosphate_local": {
        "unit":     "tonne",
        "yield":    {"N": 0.0,  "P2O5": 280.0, "K2O": 0.0},
        "lag_mo":   0,
        "notes":    "if local deposits — slow release, finely ground",
        "safety":   "no pathogen; check for cadmium in source",
        "scale":    "regional",
    },
}


# ============================================================
# 3. CLIMATE / CALENDAR BANDS
# ============================================================

CALENDAR_BANDS = {
    "NH_temperate":    {"plant": "Apr-May",    "compost_start_by": "Oct prev yr"},
    "NH_subtropical":  {"plant": "Mar-Apr",    "compost_start_by": "Sep prev yr"},
    "NH_monsoon":      {"plant": "Jun-Jul",    "compost_start_by": "Dec prev yr"},
    "equatorial":      {"plant": "year-round", "compost_start_by": "any 6mo prior"},
    "SH_temperate":    {"plant": "Oct-Nov",    "compost_start_by": "Apr same yr"},
    "SH_subtropical":  {"plant": "Sep-Oct",    "compost_start_by": "Mar same yr"},
    "highland_short":  {"plant": "May-Jun",    "compost_start_by": "Nov prev yr"},
    "arid_winter_rain":{"plant": "Nov-Dec",    "compost_start_by": "May same yr"},
}


# ============================================================
# 4. VILLAGE INPUT STRUCTURE
# ============================================================

@dataclass
class Village:
    name:           str
    population:     int
    climate_band:   str
    crops:          dict      # {crop_name: hectares_planted}
    substrates:     dict      # {substrate_name: units_available}
    target_yield_pct: float = 1.0     # fraction of typical yield (1.0 = full)

    # filled by compute()
    nutrient_need:  dict = field(default_factory=dict)
    nutrient_supply:dict = field(default_factory=dict)
    deficit:        dict = field(default_factory=dict)
    dispatch:       list = field(default_factory=list)


# ============================================================
# 5. CORE COMPUTATION
# ============================================================

def compute_need(village: Village) -> dict:
    """kg N, P2O5, K2O required for all planted crops"""
    need = {"N": 0.0, "P2O5": 0.0, "K2O": 0.0}
    for crop, ha in village.crops.items():
        if crop not in CROP_NUTRIENT_NEED:
            continue
        target_t = (TYPICAL_YIELD_T_PER_HA.get(crop, 2.0) *
                    village.target_yield_pct * ha)
        n, p, k = CROP_NUTRIENT_NEED[crop]
        need["N"]    += n * target_t
        need["P2O5"] += p * target_t
        need["K2O"]  += k * target_t
    return need


def compute_supply(village: Village) -> dict:
    """kg N, P2O5, K2O available from all listed substrates"""
    supply = {"N": 0.0, "P2O5": 0.0, "K2O": 0.0}
    by_substrate = {}
    for sub_name, units in village.substrates.items():
        if sub_name not in SUBSTRATES:
            continue
        s = SUBSTRATES[sub_name]
        contrib = {nut: s["yield"][nut] * units for nut in ("N","P2O5","K2O")}
        by_substrate[sub_name] = contrib
        for nut in ("N","P2O5","K2O"):
            supply[nut] += contrib[nut]
    village.nutrient_supply_breakdown = by_substrate
    return supply


def compute_deficit(need: dict, supply: dict) -> dict:
    """positive = shortfall, negative = surplus"""
    return {nut: need[nut] - supply[nut] for nut in need}


def build_dispatch(village: Village, deficit: dict) -> list:
    """
    Ranked sequence of actions village should take.
    Priority order:
      1. Substrates already available — process now
      2. Fast-cycle substrates (lag <= 2mo) to cover deficits
      3. N-fixing pathways (legumes, azolla) for chronic N deficit
      4. P/K specific substrates if those are limiting
      5. Calendar-driven start dates
    """
    dispatch = []

    # Phase 1: process what's already on hand
    for sub_name, units in village.substrates.items():
        if sub_name in SUBSTRATES and units > 0:
            s = SUBSTRATES[sub_name]
            dispatch.append({
                "priority": 1,
                "action":   f"Begin processing {sub_name}",
                "units":    units,
                "lag_mo":   s["lag_mo"],
                "start_by": "immediately",
                "notes":    s["notes"],
                "safety":   s["safety"],
            })

    # Phase 2: if N deficit, recommend N-fixing additions
    if deficit.get("N", 0) > 0:
        ha_legume_needed = deficit["N"] / SUBSTRATES["legume_residue_inplace"]["yield"]["N"]
        dispatch.append({
            "priority": 2,
            "action":   "Plant N-fixing cover crop / intercrop",
            "units":    f"~{ha_legume_needed:.2f} ha legume cover",
            "lag_mo":   3,
            "start_by": "previous planting cycle",
            "notes":    "cowpea/vetch/clover; incorporate at flowering",
            "safety":   "no pathogen risk",
        })
        # If water available, suggest azolla
        if village.climate_band in ("NH_monsoon", "equatorial",
                                     "SH_subtropical"):
            ponds = deficit["N"] / SUBSTRATES["azolla_pond"]["yield"]["N"]
            dispatch.append({
                "priority": 2,
                "action":   "Establish azolla in standing water (paddies, ponds)",
                "units":    f"~{ponds:.1f} × 100 m² pond surface",
                "lag_mo":   1,
                "start_by": "1 month before planting",
                "notes":    "doubles biomass every 3-5 days; harvest weekly",
                "safety":   "no pathogen",
            })

    # Phase 3: P deficit
    if deficit.get("P2O5", 0) > 0:
        dispatch.append({
            "priority": 3,
            "action":   "Source P: bone meal, fish waste, rock phosphate, ash",
            "units":    f"~{deficit['P2O5']:.0f} kg P2O5 needed",
            "lag_mo":   1,
            "start_by": "as soon as substrate located",
            "notes":    "co-compost with N-rich for slow release",
            "safety":   "varies by substrate",
        })

    # Phase 4: K deficit
    if deficit.get("K2O", 0) > 0:
        dispatch.append({
            "priority": 3,
            "action":   "Source K: wood ash, banana stems, seaweed, water hyacinth",
            "units":    f"~{deficit['K2O']:.0f} kg K2O needed",
            "lag_mo":   0,
            "start_by": "immediate; ash is fast-acting",
            "notes":    "ash raises pH — test soil first",
            "safety":   "no pathogen",
        })

    # Phase 5: calendar alignment
    cal = CALENDAR_BANDS.get(village.climate_band)
    if cal:
        dispatch.append({
            "priority": 4,
            "action":   "Calendar gate",
            "units":    "—",
            "lag_mo":   0,
            "start_by": cal["compost_start_by"],
            "notes":    f"Planting window: {cal['plant']}. "
                        f"Composting must start by: {cal['compost_start_by']}.",
            "safety":   "—",
        })

    dispatch.sort(key=lambda d: (d["priority"], d["lag_mo"]))
    return dispatch


# ============================================================
# 6. FERMENTATION / REMEDIATION ADD-ONS
# ============================================================

REMEDIATION_DISPATCHERS = {
    "soil_acidic": [
        "apply wood ash (test pH first; ~500 kg/ha to raise 0.5 pH unit)",
        "add crushed shells or limestone if available",
        "biochar charged with compost tea improves CEC",
    ],
    "soil_alkaline": [
        "avoid wood ash",
        "elemental sulfur (if available) lowers pH",
        "compost & green manure gradually buffer pH down",
    ],
    "soil_depleted_organic_matter": [
        "minimum-till + cover cropping rotation",
        "compost application 5-10 t/ha annually",
        "biochar 1-2 t/ha as long-term carbon",
        "mulch with crop residue, no burning",
    ],
    "soil_compacted": [
        "deep-rooted cover crops (daikon, tillage radish)",
        "broadfork before planting",
        "avoid heavy machinery on wet soil",
    ],
    "salinity_high": [
        "leaching with clean water where possible",
        "salt-tolerant crops (barley, quinoa, certain millets)",
        "gypsum if available",
        "raised beds + organic mulch",
    ],
    "drought_prone": [
        "swales + water-harvesting earthworks",
        "mulch heavily — 5-10 cm",
        "drought-tolerant varieties (sorghum, millet, teff)",
        "biochar improves water retention",
    ],
    "pest_pressure": [
        "fermented plant extracts: garlic, chili, neem",
        "trap crops at field margins",
        "interplanting / polyculture breaks pest cycles",
        "beneficial insect habitat",
    ],
    "low_microbial_activity": [
        "indigenous microorganism (IMO) culture from forest litter",
        "compost tea applications",
        "EM (effective microorganism) bokashi",
        "fermented plant juice (FPJ) and fermented fruit juice (FFJ)",
    ],
}


FERMENTATION_PROTOCOLS = {
    "bokashi": {
        "inputs":   "food scraps + bran + EM/LAB inoculant",
        "container":"sealed bucket, drain valve",
        "time":     "2 weeks anaerobic + 2 weeks soil bury",
        "output":   "pre-digested organic matter, low pH",
        "use":      "direct soil incorporation",
    },
    "EM_lactic_acid_bacteria": {
        "inputs":   "rice wash water + milk + molasses",
        "container":"glass jar, loose lid",
        "time":     "7-10 days",
        "output":   "lactic acid bacteria culture",
        "use":      "inoculant for compost, foliar spray, bokashi starter",
    },
    "FPJ_fermented_plant_juice": {
        "inputs":   "fast-growing plant tips (early morning) + brown sugar 1:1",
        "container":"clay or glass jar, breathable cloth lid",
        "time":     "7 days",
        "output":   "plant-growth-stage extract",
        "use":      "foliar spray, 1:500 dilution",
    },
    "FAA_fish_amino_acid": {
        "inputs":   "fish waste + brown sugar 1:1",
        "container":"sealed jar",
        "time":     "3-6 months",
        "output":   "amino acid concentrate, high N",
        "use":      "soil drench, 1:1000 dilution",
    },
    "IMO_indigenous_microorganism": {
        "inputs":   "cooked rice + forest leaf-mold + brown sugar",
        "container":"wooden box buried in forest floor",
        "time":     "5-7 days collect, then expand 7 days",
        "output":   "local-adapted microbial culture",
        "use":      "compost inoculant, soil drench",
    },
    "compost_tea_aerated": {
        "inputs":   "finished compost + water + molasses + air pump 24hr",
        "container":"bucket with aquarium pump",
        "time":     "24 hours",
        "output":   "aerobic microbial bloom",
        "use":      "foliar or soil drench within 4 hrs",
    },
    "urine_fertilizer": {
        "inputs":   "fresh urine, sealed container",
        "container":"sealed jerrycan, no light",
        "time":     "1 month sealed (self-sterilizes via ammonia/pH)",
        "output":   "stabilized N-P-K liquid",
        "use":      "dilute 1:10 with water; soil application only",
    },
}


# ============================================================
# 7. REPORT
# ============================================================

def fmt_kg(n):
    if abs(n) >= 1000:
        return f"{n/1000:.2f} t"
    return f"{n:.1f} kg"


def report(village: Village):
    need    = compute_need(village)
    supply  = compute_supply(village)
    deficit = compute_deficit(need, supply)
    dispatch = build_dispatch(village, deficit)

    village.nutrient_need = need
    village.nutrient_supply = supply
    village.deficit = deficit
    village.dispatch = dispatch

    print("=" * 68)
    print(f"VILLAGE N-CLOSURE REPORT: {village.name}")
    print("=" * 68)
    print(f"  population:    {village.population}")
    print(f"  climate:       {village.climate_band}")
    print(f"  target yield:  {village.target_yield_pct*100:.0f}% of typical")
    print()

    print("CROPS PLANTED")
    print("-" * 68)
    for crop, ha in village.crops.items():
        y = TYPICAL_YIELD_T_PER_HA.get(crop, 2.0) * village.target_yield_pct
        print(f"  {crop:<12} {ha:>6.2f} ha   target yield: {y*ha:.1f} t")

    print()
    print("NUTRIENT BUDGET (kg/season)")
    print("-" * 68)
    print(f"  {'nutrient':<8} {'need':>12} {'supply':>12} {'deficit':>12}")
    for nut in ("N", "P2O5", "K2O"):
        d = deficit[nut]
        flag = "SHORTFALL" if d > 0 else "SURPLUS"
        print(f"  {nut:<8} {fmt_kg(need[nut]):>12} "
              f"{fmt_kg(supply[nut]):>12} {fmt_kg(d):>12}   {flag}")

    print()
    print("SUPPLY BREAKDOWN BY SUBSTRATE")
    print("-" * 68)
    if hasattr(village, "nutrient_supply_breakdown"):
        for sub, contrib in village.nutrient_supply_breakdown.items():
            n, p, k = contrib["N"], contrib["P2O5"], contrib["K2O"]
            print(f"  {sub:<28} N:{n:>7.1f}  P:{p:>6.1f}  K:{k:>6.1f}")

    print()
    print("DISPATCH SEQUENCE (do in this order)")
    print("-" * 68)
    for i, d in enumerate(dispatch, 1):
        print(f"  [{i}] (priority {d['priority']}) {d['action']}")
        print(f"      units:    {d['units']}")
        print(f"      lag:      {d['lag_mo']} months")
        print(f"      start by: {d['start_by']}")
        print(f"      notes:    {d['notes']}")
        if d['safety'] != '—':
            print(f"      safety:   {d['safety']}")
        print()

    print("=" * 68)
    print("CALENDAR")
    print("=" * 68)
    cal = CALENDAR_BANDS.get(village.climate_band, {})
    print(f"  planting window:        {cal.get('plant', '—')}")
    print(f"  composting must start:  {cal.get('compost_start_by', '—')}")
    print()
    print("=" * 68)
    print("REMEDIATION DISPATCHERS AVAILABLE")
    print("=" * 68)
    print("  Call remediate(condition) where condition is one of:")
    for c in REMEDIATION_DISPATCHERS:
        print(f"    - {c}")
    print()
    print("  Call ferment(protocol) where protocol is one of:")
    for p in FERMENTATION_PROTOCOLS:
        print(f"    - {p}")


def remediate(condition: str):
    """Print remediation steps for a soil/field condition."""
    if condition not in REMEDIATION_DISPATCHERS:
        print(f"Unknown condition. Available: {list(REMEDIATION_DISPATCHERS)}")
        return
    print(f"\nREMEDIATION: {condition}")
    print("-" * 60)
    for step in REMEDIATION_DISPATCHERS[condition]:
        print(f"  • {step}")


def ferment(protocol: str):
    """Print fermentation protocol details."""
    if protocol not in FERMENTATION_PROTOCOLS:
        print(f"Unknown protocol. Available: {list(FERMENTATION_PROTOCOLS)}")
        return
    p = FERMENTATION_PROTOCOLS[protocol]
    print(f"\nFERMENTATION: {protocol}")
    print("-" * 60)
    for k, v in p.items():
        print(f"  {k:<12} {v}")


# ============================================================
# 8. CUSTOMIZATION ENTRY POINT
# ============================================================

def run_custom(name, population, climate_band, crops, substrates,
               target_yield_pct=1.0):
    """
    Build and report on a custom village.

    Example:
        run_custom(
          name="My Village",
          population=200,
          climate_band="NH_temperate",
          crops={"maize": 8, "wheat": 4, "potato": 2},
          substrates={"humanure_composted": 200,
                      "cattle_manure": 30,
                      "chicken_manure": 5,
                      "legume_residue_inplace": 3,
                      "wood_ash": 0.5},
          target_yield_pct=0.8,
        )
    """
    v = Village(
        name           = name,
        population     = population,
        climate_band   = climate_band,
        crops          = crops,
        substrates     = substrates,
        target_yield_pct = target_yield_pct,
    )
    report(v)
    return v


# ============================================================
# 9. DEMO VILLAGE
# ============================================================

EXAMPLE_VILLAGE = Village(
    name           = "Example Village (Northern Plains)",
    population     = 250,
    climate_band   = "NH_temperate",
    crops          = {
        "maize":   10.0,
        "wheat":    5.0,
        "potato":   2.0,
    },
    substrates     = {
        "humanure_composted":     250,   # person-years
        "urine_diverted":         100,   # person-years (partial collection)
        "cattle_manure":           40,   # animal-years
        "chicken_manure":           8,   # 10-bird units
        "goat_sheep_manure":       30,
        "legume_residue_inplace":   3,   # ha
        "wood_ash":               0.5,   # tonnes
        "bokashi_food_scrap":     1.5,
    },
    target_yield_pct = 0.85,             # realistic small-village target
)


if __name__ == "__main__":
    report(EXAMPLE_VILLAGE)
    print()
    print("=" * 68)
    print("SAMPLE REMEDIATION CALL")
    print("=" * 68)
    remediate("soil_depleted_organic_matter")
    print()
    print("=" * 68)
    print("SAMPLE FERMENTATION CALL")
    print("=" * 68)
    ferment("IMO_indigenous_microorganism")
