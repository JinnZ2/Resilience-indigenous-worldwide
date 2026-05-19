"""
region_presets.py
=================

Pre-built Village configurations for the regions this repository
already covers in docs/ and region-specific code folders:

  - Greenland          (docs/greenland/)
  - Venezuela / Orinoco (docs/venezuela/)
  - Burkina Faso       (burkina_faso/)
  - India delta        (india/)

Each preset is a STARTING POINT, not a survey. Local numbers (actual
parcel size, actual livestock counts, actual climate band) should be
substituted by the community using the toolkit. The presets exist so
the village_n_closure model runs out-of-box without forcing every
user to invent a config.

License: CC0 — public domain
Dependencies: stdlib + village_n_closure (same package)
"""

from __future__ import annotations
from architecture.village_n_closure import Village, report


# ============================================================
# Greenland — coastal, arctic, very short growing season
# ============================================================
# Notes:
#  - "Highland_short" calendar band is the closest match in the
#    base toolkit; actual Greenland calendar is shorter still.
#  - Cereals are not the primary subsistence crop; potato and
#    forage barley are realistic. Fish waste and seaweed dominate
#    the substrate stack on the coast.

GREENLAND_COASTAL = Village(
    name            = "Greenland coastal settlement (preset)",
    population      = 200,
    climate_band    = "highland_short",
    crops           = {
        "potato":  2.0,
        "barley":  1.0,    # forage / experimental
    },
    substrates      = {
        "humanure_composted":     200,   # person-years
        "urine_diverted":         150,
        "fish_waste":              50,   # tonnes fresh / yr — coastal abundance
        "seaweed_kelp":            30,
        "goat_sheep_manure":       20,
        "wood_ash":               0.2,
        "bokashi_food_scrap":     1.0,
    },
    target_yield_pct = 0.70,             # conservative for sub-arctic
)


# ============================================================
# Venezuela — Orinoco basin, tropical, monsoon-fed
# ============================================================
# Notes:
#  - Crops reflect actual Orinoco-region subsistence: cassava,
#    maize, rice, plantain (plantain not in base crop table —
#    omitted from preset; community can add).
#  - Water hyacinth is locally abundant on the Orinoco and its
#    tributaries; azolla works in the seasonal floodplain.

VENEZUELA_ORINOCO = Village(
    name            = "Venezuela Orinoco-basin community (preset)",
    population      = 350,
    climate_band    = "equatorial",
    crops           = {
        "cassava":  8.0,
        "maize":    4.0,
        "rice":     3.0,
    },
    substrates      = {
        "humanure_composted":     350,
        "urine_diverted":         200,
        "cattle_manure":           25,
        "chicken_manure":          12,
        "pig_manure":              10,
        "water_hyacinth":         150,   # tonnes fresh / yr
        "azolla_pond":              8,   # 100-m² pond-years
        "fish_waste":              20,
        "wood_ash":               0.6,
        "biochar_charged":        1.0,
    },
    target_yield_pct = 0.85,
)


# ============================================================
# Burkina Faso — Sahel, arid, short rainy season
# ============================================================
# Notes:
#  - Sahel ecology favors sorghum and millet over wheat or rice.
#  - Cattle/goat herding is central; manure availability is
#    bottlenecked by herd mobility and seasonal water.
#  - This preset pairs with burkina_faso/laterite_embankment_garden.py
#    and burkina_faso/urine_soil_recovery.py — the substrate stack
#    here mirrors what those modules assume is locally producible.

BURKINA_FASO_SAHEL = Village(
    name            = "Burkina Faso Sahel village (preset)",
    population      = 400,
    climate_band    = "NH_monsoon",      # single short wet season
    crops           = {
        "sorghum":  10.0,
        "millet":    8.0,
        "maize":     3.0,
    },
    substrates      = {
        "humanure_composted":     400,
        "urine_diverted":         300,   # central to urine_soil_recovery.py
        "cattle_manure":           60,
        "goat_sheep_manure":       80,
        "chicken_manure":          15,
        "legume_residue_inplace":   4,   # cowpea is regionally dominant
        "wood_ash":               0.8,
        "biochar_charged":        0.5,
        "bokashi_food_scrap":     1.0,
    },
    target_yield_pct = 0.75,
)


# ============================================================
# India delta — Sundarbans / Ganges-Brahmaputra, monsoon, brackish
# ============================================================
# Notes:
#  - Pairs with india/foundation_float_system.py (delta foundation
#    floats), which assumes monsoon flooding and a brackish/freshwater
#    interface.
#  - Rice is the dominant crop; azolla is traditional paddy intercrop.
#  - Salinity is the soft constraint that breaks generic agronomic
#    advice — see crosslink to remediate("salinity_high").

INDIA_DELTA = Village(
    name            = "India delta community (preset)",
    population      = 500,
    climate_band    = "NH_monsoon",
    crops           = {
        "rice":     12.0,
        "potato":    2.0,
        "millet":    3.0,    # for higher-salinity plots
    },
    substrates      = {
        "humanure_composted":     500,
        "urine_diverted":         350,
        "cattle_manure":           80,
        "goat_sheep_manure":       40,
        "chicken_manure":          20,
        "azolla_pond":             20,   # paddy intercrop
        "water_hyacinth":         200,   # extremely abundant in delta
        "legume_residue_inplace":   3,
        "fish_waste":              25,
        "wood_ash":               0.5,
        "biochar_charged":        1.5,
    },
    target_yield_pct = 0.80,
)


# ============================================================
# Registry + entry point
# ============================================================

REGION_PRESETS = {
    "greenland":     GREENLAND_COASTAL,
    "venezuela":     VENEZUELA_ORINOCO,
    "burkina_faso":  BURKINA_FASO_SAHEL,
    "india_delta":   INDIA_DELTA,
}


def list_regions() -> list[str]:
    return list(REGION_PRESETS.keys())


def get_preset(region: str) -> Village:
    if region not in REGION_PRESETS:
        raise KeyError(f"Unknown region {region!r}. "
                       f"Available: {list_regions()}")
    return REGION_PRESETS[region]


def report_region(region: str):
    """Convenience: run the village_n_closure report on a named preset."""
    v = get_preset(region)
    report(v)
    return v


if __name__ == "__main__":
    print("Available region presets:")
    for r in list_regions():
        v = get_preset(r)
        print(f"  {r:<14} -> {v.name}")
    print()
    print("Run one with: python -m architecture.region_presets <region>")
    print()

    import sys
    if len(sys.argv) > 1:
        report_region(sys.argv[1])
    else:
        print("(no region argument given; printing Burkina Faso preset)")
        print()
        report_region("burkina_faso")
