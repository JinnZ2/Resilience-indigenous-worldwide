"""
urine_soil_recovery.py

Soil recovery for depleted Sahelian laterite using stabilized urine as
a nitrogen + phosphorus + potassium delivery vehicle.

Primary frame: SOIL RECOVERY.
Secondary (footnote): surplus or rejected stabilized urine can feed a
closed-loop low-pressure steam circuit. See urine_steam_filtration.py
for that path. This module assumes soil application is the goal.

Core problem:
Sahelian laterite is iron/aluminum-rich, low in organic matter,
low cation exchange capacity, and phosphate-fixing. Three failure
modes for unsupplemented soil:
1. Nitrogen deficit          (OM typically <0.5%)
2. Phosphate fixation        (Fe/Al oxides bind PO4)
3. Cation leaching           (Na+, K+, NH4+ wash out in rain)

Urine carries the missing nutrients but loses them fast:
  Urea -> ammonia volatilization (50-80% lost if surface-applied)
  P binds to iron oxides on contact with laterite (becomes
    plant-unavailable)
  K+ leaches in first heavy rain

Mitigation chain (this module):
1. Metal-mesh holding tank: scrap iron mesh slows urea hydrolysis,
   creates Fe-N complexes that release N over weeks, not hours.
2. Charcoal/biochar co-application: high CEC sponge holds NH4+
   and K+ against leaching.
3. Subsurface placement: 15-20 cm depth, NOT surface broadcast,
   cuts NH3 volatilization >70%.
4. Acid root-zone P liberation: place near legume / cereal roots
   that exude organic acids (citrate, oxalate) to free P from
   iron oxide bonds.
5. Timing: apply at planting + early vegetative stage, when
   roots are present to capture N before next rain leaches it.

CC0. Stdlib only. Falsifiable: every claim is field-measurable with
TDR moisture probes, soil test kits, or yield comparison plots.
"""

from dataclasses import dataclass

# ----- urine reference (soil delivery frame) -----

@dataclass
class UrineNutrients:
    """Mean values for adult urine. Override with site samples; varies
    with diet (high-protein diets give higher N concentration)."""
    n_total_g_per_l: float = 8.0       # 6-12 typical, mostly as urea
    p_total_g_per_l: float = 0.8       # 0.5-1.2
    k_total_g_per_l: float = 2.0       # 1.5-2.5
    ph: float = 6.5
    daily_volume_l_per_adult: float = 1.4

    def npk_per_adult_per_year_kg(self) -> dict:
        annual_l = self.daily_volume_l_per_adult * 365
        return {
            "N_kg": round(annual_l * self.n_total_g_per_l / 1000, 2),
            "P_kg": round(annual_l * self.p_total_g_per_l / 1000, 2),
            "K_kg": round(annual_l * self.k_total_g_per_l / 1000, 2),
        }


# ----- soil baseline -----

@dataclass
class LateriteSoilStatus:
    """Field-measurable soil parameters."""
    organic_matter_pct: float = 0.4
    total_n_pct: float = 0.03
    available_p_ppm: float = 5.0       # very low; >15 needed for crops
    exchangeable_k_ppm: float = 50.0
    cation_exchange_capacity_meq_100g: float = 4.0  # low; ideal >10
    iron_oxide_pct: float = 6.0        # high in laterite, P-fixing
    ph: float = 6.0

    def p_fixation_severity(self) -> float:
        """0..1, higher = more phosphate locked by iron oxides."""
        return min(self.iron_oxide_pct / 10.0, 1.0)

    def leaching_vulnerability(self) -> float:
        """0..1, higher = more nutrient loss in rain."""
        cec_factor = max(0.0, 1.0 - (self.cation_exchange_capacity_meq_100g / 15.0))
        om_factor = max(0.0, 1.0 - (self.organic_matter_pct / 2.0))
        return (cec_factor + om_factor) / 2.0


# ----- stabilization: iron mesh holding tank -----

@dataclass
class IronMeshStabilizer:
    """Scrap iron mesh in covered holding tank. Slows urea hydrolysis,
    forms Fe-N complexes, captures some P as iron phosphate (which is
    plant-AVAILABLE under root acid exudates, unlike soil-fixed P)."""
    mesh_surface_area_m2: float = 4.0  # per cubic meter of urine
    holding_time_days: float = 7.0
    covered_tank: bool = True          # critical: open tank loses NH3

    def n_retention_factor(self) -> float:
        """Fraction of urine N retained vs open evaporative storage."""
        if not self.covered_tank:
            return 0.30   # open tank loses 70% to atmosphere
        # Fe mesh slows hydrolysis; longer hold = more complex formation
        # but diminishing return after ~10 days
        retention = 0.85 - 0.02 * max(self.holding_time_days - 10, 0)
        return max(min(retention, 0.90), 0.50)

    def p_bioavailability_factor(self) -> float:
        """Fraction of urine P that remains plant-accessible after
        Fe-mesh contact. Fe-P complex is releasable by root acids."""
        # better than soil-fixed P (~0.1) but not as good as fresh urine (1.0)
        return 0.65


# ----- biochar amendment -----

@dataclass
class BiocharAmendment:
    """Charcoal from local woody biomass (millet stalks, acacia, shea
    nut shells). Acts as cation-exchange sponge."""
    application_rate_t_per_ha: float = 5.0
    cec_meq_100g: float = 30.0          # high CEC vs laterite ~4
    particle_size_mm: float = 5.0       # crushed, not powdered

    def cec_uplift(self, baseline_cec: float,
                   active_layer_mass_t_per_ha: float = 750) -> float:
        """New effective CEC in the top 5 cm active root zone after
        biochar mix-in. Uses active layer mass (~750 t/ha for top 5 cm
        at typical bulk density), not the full 15 cm plough layer,
        because biochar concentrates where it is incorporated.

        Empirical basis: Lehmann 2007, Glaser 2002, Cornelissen 2013.
        5 t/ha in low-CEC tropical soils: ~2x baseline CEC by season 2."""
        biochar_fraction = self.application_rate_t_per_ha / active_layer_mass_t_per_ha
        # surface-area dominated exchange: biochar contributes well above
        # its mass fraction
        effective_fraction = min(biochar_fraction * 6.0, 0.6)
        blended = (baseline_cec * (1 - effective_fraction)
                   + self.cec_meq_100g * effective_fraction)
        return round(blended, 2)


# ----- application method -----

@dataclass
class ApplicationMethod:
    placement_depth_cm: float = 18.0    # subsurface band
    timing: str = "planting_plus_early_veg"
    # options: "surface_broadcast" (worst), "surface_irrigation",
    # "subsurface_band" (best), "fertigation_drip"
    paired_with_biochar: bool = True
    paired_with_legume: bool = True     # cowpea, groundnut: roots exude
    # acids that liberate Fe-bound P

    def nh3_volatilization_loss(self) -> float:
        """Fraction of N lost as ammonia gas. 0..1."""
        if self.placement_depth_cm < 2:
            return 0.70
        if self.placement_depth_cm < 8:
            return 0.35
        if self.placement_depth_cm < 15:
            return 0.15
        return 0.05

    def p_liberation_factor(self) -> float:
        """Boost to phosphate availability from root acid exudates."""
        return 1.5 if self.paired_with_legume else 1.0


# ----- integrated nutrient delivery -----

def deliver_to_soil(
    urine: UrineNutrients,
    stabilizer: IronMeshStabilizer,
    biochar: BiocharAmendment,
    method: ApplicationMethod,
    soil: LateriteSoilStatus,
    n_adults_contributing: int = 4,
) -> dict:
    """Compute effective N, P, K reaching the plant root zone per year."""
    annual = urine.npk_per_adult_per_year_kg()
    raw_n = annual["N_kg"] * n_adults_contributing
    raw_p = annual["P_kg"] * n_adults_contributing
    raw_k = annual["K_kg"] * n_adults_contributing

    # stabilization stage
    n_after_tank = raw_n * stabilizer.n_retention_factor()
    p_after_tank = raw_p * stabilizer.p_bioavailability_factor()
    k_after_tank = raw_k  # K is not lost in covered tank

    # application stage
    n_after_app = n_after_tank * (1.0 - method.nh3_volatilization_loss())
    p_after_app = p_after_tank * method.p_liberation_factor()
    # K leaching depends on biochar uplift
    new_cec = biochar.cec_uplift(soil.cation_exchange_capacity_meq_100g)
    k_retention = min(new_cec / 15.0, 1.0)  # CEC of 15 = full retention
    k_after_app = k_after_tank * k_retention

    # available to roots (P fixation still partial in laterite)
    p_root_available = p_after_app * (1.0 - 0.5 * soil.p_fixation_severity())

    return {
        "raw_input": {"N_kg_yr": round(raw_n, 2),
                      "P_kg_yr": round(raw_p, 2),
                      "K_kg_yr": round(raw_k, 2)},
        "after_iron_mesh_tank": {
            "N_kg_yr": round(n_after_tank, 2),
            "P_kg_yr": round(p_after_tank, 2),
            "K_kg_yr": round(k_after_tank, 2),
            "n_retention_pct": round(stabilizer.n_retention_factor() * 100, 1),
        },
        "after_application": {
            "N_kg_yr_to_root_zone": round(n_after_app, 2),
            "P_kg_yr_plant_available": round(p_root_available, 2),
            "K_kg_yr_held_in_soil": round(k_after_app, 2),
            "nh3_loss_pct": round(method.nh3_volatilization_loss() * 100, 1),
        },
        "soil_uplift": {
            "new_effective_CEC_meq_100g": new_cec,
            "p_fixation_severity": round(soil.p_fixation_severity(), 2),
            "leaching_vulnerability_remaining":
                round(soil.leaching_vulnerability() *
                      (1 - min(new_cec / 15.0, 1.0)), 2),
        },
    }


# ----- crop coverage estimate -----

# typical N requirements, kg/ha/season for Sahelian crops
CROP_N_DEMAND_KG_HA = {
    "sorghum":      60,
    "millet":       40,
    "cowpea":       20,   # legume, mostly self-supplied
    "okra":         70,
    "amaranth":     50,
    "moringa":      30,
    "tomato":      100,
    "onion":        80,
    "sweet_potato": 60,
}


def hectares_supportable(delivered: dict, crop: str) -> float:
    n_kg = delivered["after_application"]["N_kg_yr_to_root_zone"]
    demand = CROP_N_DEMAND_KG_HA.get(crop, 60)
    return round(n_kg / demand, 3)


# ----- falsifiable claims -----

CLAIMS = [
    "C1: covered iron-mesh holding tank retains >=70% of urine N "
    "vs <=30% retention in open evaporative storage "
    "(measurable: total-N test before/after 7 days)",
    "C2: subsurface band placement at 15-20 cm reduces NH3 "
    "volatilization by >=70% vs surface broadcast "
    "(measurable: ammonia trap above plot)",
    "C3: biochar at 5 t/ha raises laterite active-zone CEC by >=25% "
    "in season 1, accumulating to >=2x baseline by season 3 with "
    "repeat application "
    "(measurable: standard CEC soil test on top 5 cm)",
    "C4: legume-paired application liberates >=40% more soil P "
    "than monoculture cereal application "
    "(measurable: Bray-1 available P test)",
    "C5: 4 adults' annual urine + biochar + iron mesh sustains "
    ">=0.1 ha of cereal at full N demand without external fertilizer "
    "(measurable: yield comparison plot vs unfertilized control)",
]


# ----- secondary use note -----

SECONDARY_USES = [
    "Surplus stabilized urine beyond crop demand can feed a closed-loop "
    "low-pressure steam circuit (see urine_steam_filtration.py). The "
    "iron mesh in the holding tank already performs the filtration the "
    "steam circuit would otherwise need separately, so the systems "
    "share infrastructure. Steam engine output is bonus mechanical "
    "energy, not the primary purpose. Soil recovery first.",
    "Reject condensate from any steam stage returns to the holding "
    "tank or directly to non-edible plantings (moringa, jatropha, "
    "windbreak trees), never wasted.",
]


# ----- runnable example -----

if __name__ == "__main__":
    urine = UrineNutrients()
    stabilizer = IronMeshStabilizer()
    biochar = BiocharAmendment()
    method = ApplicationMethod()
    soil = LateriteSoilStatus()

    result = deliver_to_soil(
        urine, stabilizer, biochar, method, soil,
        n_adults_contributing=4,
    )
    print("Burkina Faso reference -- urine soil recovery (4 adults)")
    print("=" * 64)
    for section, data in result.items():
        print(f"\n[{section}]")
        for k, v in data.items():
            print(f"  {k}: {v}")

    print("\n[crop coverage]")
    n_to_root = result["after_application"]["N_kg_yr_to_root_zone"]
    print(f"  total deliverable N to root zone: {n_to_root} kg/yr")
    for crop in ["sorghum", "millet", "okra", "amaranth", "moringa"]:
        ha = hectares_supportable(result, crop)
        print(f"  {crop}: {ha} ha at full N demand")

    print("\n[falsifiable claims]")
    for c in CLAIMS:
        print(f"  - {c}")

    print("\n[secondary uses]")
    for u in SECONDARY_USES:
        print(f"  * {u}")
