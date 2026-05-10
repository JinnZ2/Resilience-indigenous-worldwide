"""
copper_deposit_vitamin_amendment.py

Translation of Depression-era "vitamins for plants" practice into a
human-readable, falsifiable model.

Frame:
A copper-mesh filtration screen sits in a urine flow path
(closed-loop tank, or steam-engine pre-filter). Over weeks to
months, ions plate out onto the mesh as a mineral deposit:
- copper sulfate / copper hydroxide   (primary)
- iron oxides / hydroxides            (from rust + urine Fe)
- zinc compounds                      (if galvanized contact)
- manganese, trace nickel             (from steel alloys)
- phosphate co-precipitate            (with Fe and Cu)

The deposit is scraped off, dried, and mixed into compost in small
crop-specific doses. Practitioners called it "vitamins for plants":
a little is essential, too much is toxic. Same logic as human
vitamins.

The biomass / compost itself can be applied freely (carbon and N
rebuilding); only the mineral deposit needs precision dosing.

CC0. Stdlib only. Falsifiable: every claim is field- or lab-measurable.
"""

from dataclasses import dataclass, field

# ----- deposit formation -----

@dataclass
class CopperMeshFilter:
    """Filtration mesh in urine flow path. Mass and area determine
    deposit accumulation rate."""
    mesh_mass_kg: float = 1.5
    mesh_surface_area_m2: float = 2.5
    flow_l_per_day: float = 6.0          # 4 adults' urine
    operating_days: int = 60
    # 'pure_copper' / 'copper_brass' / 'tinned_copper'
    copper_type: str = "pure_copper"


def deposit_accumulation_rate_g_per_day(filter_: CopperMeshFilter) -> float:
    """Approximate mineral deposit mass per day under typical urine flow.
    Empirical: ~0.3 to 0.8 g/day per square meter of active copper
    surface in covered tank conditions. Higher with higher flow,
    higher acidity, lower temperature."""
    base_rate_g_m2 = 0.55
    if filter_.copper_type == "pure_copper":
        cu_factor = 1.0
    elif filter_.copper_type == "copper_brass":
        cu_factor = 0.85       # zinc dilutes plating
    elif filter_.copper_type == "tinned_copper":
        cu_factor = 0.40       # tin layer slows ion exchange
    else:
        cu_factor = 0.7
    flow_factor = min(filter_.flow_l_per_day / 6.0, 2.0)
    return base_rate_g_m2 * filter_.mesh_surface_area_m2 * cu_factor * flow_factor


@dataclass
class DepositComposition:
    """Approximate dry mass fractions of scraped deposit. Site samples
    will vary widely. Use these as starting point; lab any actual batch
    before bulk application to food crops."""
    copper_pct: float = 18.0
    iron_pct: float = 22.0
    zinc_pct: float = 3.0
    manganese_pct: float = 1.5
    phosphate_pct: float = 12.0
    sulfate_pct: float = 14.0
    organic_residue_pct: float = 18.0
    moisture_water_pct: float = 8.0
    other_trace_pct: float = 3.5


def deposit_yield(filter_: CopperMeshFilter) -> dict:
    daily_g = deposit_accumulation_rate_g_per_day(filter_)
    total_g = daily_g * filter_.operating_days
    return {
        "daily_g": round(daily_g, 2),
        "harvest_g": round(total_g, 1),
        "harvest_kg": round(total_g / 1000, 3),
    }


# ----- crop tolerance matrix -----

# Sahelian crops, copper sensitivity from agronomic literature
# (Marschner, Kabata-Pendias).  Values are deposit kg/ha,
# converted from Cu-equivalent thresholds at 18% Cu in deposit.

@dataclass
class CropTolerance:
    name: str
    deposit_kg_ha_optimal: float       # gives positive yield response
    deposit_kg_ha_max_safe: float      # toxicity threshold
    cu_sensitivity: str                # "low", "moderate", "high"
    benefits_from_deposit: str         # short rationale
    notes: str = ""


CROP_TOLERANCE = {
    "sorghum":      CropTolerance("sorghum",       8,  25, "low",
                        "tolerates Cu well; iron uplift improves laterite yield",
                        "staple cereal; safe broad application"),
    "millet":       CropTolerance("millet",        6,  20, "low",
                        "drought-tolerant, mild Cu uptake, Fe benefit",
                        "staple cereal; safe broad application"),
    "cowpea":       CropTolerance("cowpea",        4,  10, "moderate",
                        "legume; Cu helps nodulation up to threshold",
                        "drop dose if soil Cu already adequate"),
    "groundnut":    CropTolerance("groundnut",     3,   8, "moderate",
                        "Cu deficiency causes hollow heart; small dose useful",
                        "very precise dosing; legume"),
    "okra":         CropTolerance("okra",          5,  15, "low",
                        "robust; tolerates wide Cu range",
                        ""),
    "moringa":      CropTolerance("moringa",       6,  18, "low",
                        "deep-rooted; mineral hungry",
                        "perennial; apply at planting + annual"),
    "amaranth":     CropTolerance("amaranth",      3,   8, "moderate",
                        "leafy; can hyperaccumulate metals (food safety)",
                        "lower dose for leaf greens; lab-test deposit before use"),
    "tomato":       CropTolerance("tomato",        4,  10, "moderate",
                        "Cu deficiency causes leaf curl; small dose helps",
                        "do not exceed; fruit copper accumulation"),
    "onion":        CropTolerance("onion",         3,   7, "high",
                        "Allium family Cu-sensitive; minimal dose only",
                        "apply away from onion bed when in doubt"),
    "sweet_potato": CropTolerance("sweet_potato",  4,  12, "moderate",
                        "responds to Fe and Cu in laterite",
                        ""),
    "bissap":       CropTolerance("bissap",        4,  12, "moderate",
                        "moderate Cu response",
                        ""),
}


# ----- soil status interpreter -----

@dataclass
class SoilCopperStatus:
    available_cu_ppm: float = 0.6      # DTPA-extractable
    available_fe_ppm: float = 8.0
    available_zn_ppm: float = 1.5
    ph: float = 6.0

    def cu_status(self) -> str:
        # DTPA-extractable Cu interpretation:
        # <0.2 deficient, 0.2-1.5 adequate, >2.5 high, >4 toxicity risk
        v = self.available_cu_ppm
        if v < 0.2:
            return "deficient"
        if v < 1.5:
            return "adequate"
        if v < 2.5:
            return "high"
        return "toxic_risk"

    def deposit_recommendation(self) -> str:
        s = self.cu_status()
        if s == "deficient":
            return "apply at optimal rate; deposit fills real deficit"
        if s == "adequate":
            return "apply at half optimal rate; targeted to Cu-loving crops"
        if s == "high":
            return "skip deposit this season; apply biomass / compost only"
        return "DO NOT APPLY deposit; remediate soil first"


# ----- visual/tactile readiness signals -----
# Translation of "feel and experience" into observation checklist.

DEPOSIT_READINESS_SIGNALS = {
    "color": {
        "blue_green_bright":   "fresh Cu(OH)2 / CuSO4 - highly soluble, dose CAREFULLY",
        "blue_green_dull":     "aged deposit, partially oxidized - safer to handle",
        "red_brown":           "iron-dominant; Cu fraction lower; gentler on plants",
        "black_streaked":      "manganese / sulfide present; lab-test before food crop use",
        "white_crusted":       "salt-dominant (NaCl, KCl, struvite); not vitamin deposit, just scale",
    },
    "texture": {
        "powdery_dry":         "well-aged, ready to mix into compost",
        "crystalline_chunky":  "scrape and grind before composting",
        "wet_paste":           "still active; dry on covered rack 1-2 weeks before use",
        "sticky_organic":      "incomplete; let urine residue decompose 2-4 more weeks",
    },
    "smell": {
        "earthy_metallic":     "ready - ammonia has finished off-gassing",
        "ammonia_strong":      "not ready - continue covered drying",
        "rotten_sulfide":      "anaerobic contamination; do not use on edibles",
        "neutral_dry":         "fully aged; ideal",
    },
}


# ----- application calculator -----

def application_plan(
    deposit_harvest_g: float,
    soil: SoilCopperStatus,
    plot_size_ha: float = 0.1,
    crops: list = None,
) -> dict:
    """Suggest distribution of a deposit harvest across crop areas given
    soil status and tolerance thresholds."""
    if crops is None:
        crops = ["sorghum", "millet", "cowpea", "moringa"]

    status = soil.cu_status()
    if status == "toxic_risk":
        return {
            "verdict": "DO NOT APPLY",
            "reason": "soil Cu already at toxicity risk",
            "alternative": "use biomass/compost only; consider lime + organic matter to remediate",
        }

    # scale recommendation by status
    if status == "deficient":
        scale = 1.0
    elif status == "adequate":
        scale = 0.5
    else:  # "high"
        scale = 0.1

    # First pass: compute target dose per crop based on tolerance + scale
    targets = {}
    total_target_g = 0.0
    for crop in crops:
        if crop not in CROP_TOLERANCE:
            continue
        t = CROP_TOLERANCE[crop]
        per_crop_area_ha = plot_size_ha / max(len(crops), 1)
        target_kg_ha = t.deposit_kg_ha_optimal * scale
        target_g = target_kg_ha * 1000 * per_crop_area_ha
        max_g = t.deposit_kg_ha_max_safe * 1000 * per_crop_area_ha
        target_g = min(target_g, max_g)
        targets[crop] = {
            "area_ha": per_crop_area_ha,
            "target_g": target_g,
            "max_g": max_g,
            "tolerance": t,
        }
        total_target_g += target_g

    # Second pass: if harvest < total target, scale every crop proportionally
    # so each gets a fair share. If harvest > total target, apply full target
    # to each (don't overdose just because surplus exists).
    if total_target_g > 0:
        ratio = min(deposit_harvest_g / total_target_g, 1.0)
    else:
        ratio = 0.0

    plan = {}
    total_used_g = 0.0
    for crop, info in targets.items():
        applied_g = info["target_g"] * ratio
        applied_g = min(applied_g, info["max_g"])
        total_used_g += applied_g
        plan[crop] = {
            "area_ha": round(info["area_ha"], 4),
            "applied_g": round(applied_g, 1),
            "rate_kg_ha": round(applied_g / 1000 / max(info["area_ha"], 1e-6), 2),
            "max_safe_kg_ha": info["tolerance"].deposit_kg_ha_max_safe,
            "sensitivity": info["tolerance"].cu_sensitivity,
        }

    deposit_remaining_g = deposit_harvest_g - total_used_g

    return {
        "soil_status": status,
        "scale_factor": scale,
        "soil_recommendation": soil.deposit_recommendation(),
        "total_applied_g": round(total_used_g, 1),
        "deposit_unused_g": round(deposit_remaining_g, 1),
        "per_crop": plan,
    }


# ----- vitamin-frame summary -----

VITAMIN_FRAME = """
Vitamins-for-plants frame (translated from Depression-era practice):

- Deposit is concentrated micronutrient: think multivitamin, not food.
- Compost / biomass is food: apply freely to soil need.
- A little deposit fills real deficits (Cu, Fe, Zn, Mn).
- Too much causes burn (leaf chlorosis, root damage, Allium worst).
- Different crops want different doses (Allium / amaranth / groundnut
  are sensitive; sorghum / millet / moringa are tolerant).
- If soil is already high in Cu, SKIP deposit; apply biomass alone.
- Always lab-test or field-trial new batches before bulk food-crop
  application; deposit composition varies with mesh, urine, season.
"""


# ----- falsifiable claims -----

CLAIMS = [
    "C1: copper mesh in covered urine tank accumulates >=15 g of mineral "
    "deposit per m2 mesh per month at 6 L/day flow "
    "(measurable: dry mass before/after)",
    "C2: scraped deposit assays at 10-25% Cu, 15-30% Fe, 1-5% Zn, "
    "5-15% PO4 by dry mass under typical Sahelian household conditions "
    "(measurable: ICP-OES or field XRF)",
    "C3: applied at <=8 kg/ha to sorghum on Cu-deficient laterite, "
    "deposit increases yield by >=15% vs unfertilized control "
    "(measurable: paired plot yield)",
    "C4: applied at >=15 kg/ha to onion / amaranth, deposit causes "
    "visible leaf burn or yield loss within 3 weeks "
    "(measurable: leaf chlorosis index, paired plot yield)",
    "C5: aged deposit (>=4 weeks covered drying) emits no detectable "
    "ammonia and shows no anaerobic sulfide odor; signals composting "
    "completion before mixing into amendment "
    "(measurable: olfactory + draeger tube)",
]


# ----- runnable example -----

if __name__ == "__main__":
    f = CopperMeshFilter()
    yield_ = deposit_yield(f)
    soil = SoilCopperStatus(available_cu_ppm=0.4)  # mildly deficient
    plan = application_plan(
        deposit_harvest_g=yield_["harvest_g"],
        soil=soil,
        plot_size_ha=0.2,
        crops=["sorghum", "millet", "cowpea", "moringa", "onion", "amaranth"],
    )

    print("Burkina Faso reference -- copper-deposit vitamin amendment")
    print("=" * 64)
    print("\n[deposit harvest, 60-day cycle]")
    for k, v in yield_.items():
        print(f"  {k}: {v}")

    print("\n[application plan]")
    for k, v in plan.items():
        if k != "per_crop":
            print(f"  {k}: {v}")
    print("  per_crop:")
    for crop, info in plan["per_crop"].items():
        print(f"    {crop}: {info}")

    print("\n[readiness signals]")
    for sense, options in DEPOSIT_READINESS_SIGNALS.items():
        print(f"  {sense}:")
        for k, v in options.items():
            print(f"    {k} -> {v}")

    print(VITAMIN_FRAME)

    print("[falsifiable claims]")
    for c in CLAIMS:
        print(f"  - {c}")
