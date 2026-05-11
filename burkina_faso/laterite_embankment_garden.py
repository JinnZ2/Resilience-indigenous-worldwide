"""
laterite_embankment_garden.py

Integrated passive water-capture infrastructure for Sahelian climate
(Burkina Faso reference design).

Couples three substrate layers:
1. Geology   - laterite properties, capillarity, hygroscopic behavior
2. Hydrology - embankment geometry, infiltration, dry-season storage
3. Garden    - root-zone moisture coupling, seasonal planting windows

Frame:
Laterite is iron/aluminum-rich tropical soil that hardens on exposure
(plinthite -> hardened laterite). Properties relevant to passive water
capture:
- high porosity when freshly cut (~30-50%)
- capillary rise capacity (~40-80 cm depending on grain structure)
- hygroscopic: pulls humidity from night air below dew point
- thermal mass: stores diurnal temperature swing energy
- structural: holds geometry without binder once cured

Design principle:
A textured laterite embankment with engineered air gaps and
differential drainage angles becomes a passive atmospheric water
harvester + infiltration buffer + thermal regulator. Garden beds
placed on the leeward / lower face receive moisture by capillary
wicking through the dry season.

CC0. Stdlib only. Falsifiable: every parameter is field-measurable.
"""

import math
from dataclasses import dataclass, field

# ----- climate reference: Sahelian / Burkina Faso -----

@dataclass
class SahelianClimate:
    annual_rainfall_mm: float = 600.0       # 400-900 across country
    rainy_season_months: tuple = (6, 7, 8, 9)
    dry_season_months: tuple = (10, 11, 12, 1, 2, 3, 4, 5)
    avg_dry_season_rh_night: float = 0.55   # night relative humidity, dry season
    avg_dry_season_rh_day: float = 0.20
    avg_dry_season_temp_swing_c: float = 18.0  # 18-22 C diurnal swing typical
    avg_dry_season_dewpoint_c: float = 12.0
    peak_evaporation_mm_day: float = 8.0    # Penman estimate, hot dry months
    wet_season_rh_avg: float = 0.75


# ----- geology layer: laterite -----

@dataclass
class LateriteProperties:
    """Field-measurable properties. Defaults are mid-range for West African
    laterite. Override with site samples."""
    porosity: float = 0.38                  # 0..1   void fraction
    capillary_rise_cm: float = 60.0         # measured by wick test
    bulk_density_kg_m3: float = 1850.0
    thermal_mass_j_kg_k: float = 880.0      # specific heat
    hygroscopic_uptake_g_kg: float = 12.0   # water mass adsorbed per kg dry
    #   laterite at 60% RH, 25 C
    saturated_hydraulic_k_mm_hr: float = 8.0  # infiltration rate when wet
    air_dry_water_content: float = 0.04     # mass fraction at equilibrium

    def water_storage_per_m3(self) -> float:
        """Maximum gravitational water storage per cubic meter, kg (= liters)."""
        return self.porosity * 1000.0  # 1 m3 of pore space = 1000 L if filled

    def hygroscopic_yield_per_m3(self) -> float:
        """Water pulled from humid night air per m3 of laterite per cycle, L.
        Conservative: only the surface-exposed fraction participates."""
        kg_per_m3 = self.bulk_density_kg_m3
        # assume 5% of mass is in active exchange zone over a single night
        active_fraction = 0.05
        grams = kg_per_m3 * active_fraction * self.hygroscopic_uptake_g_kg
        return grams / 1000.0  # convert g to L (1 g water = 1 mL)


# ----- hydrology layer: embankment geometry -----

@dataclass
class EmbankmentGeometry:
    """Cross-section of a linear embankment. Length runs perpendicular to
    prevailing wet-season runoff direction (across slope, on contour)."""
    length_m: float = 30.0
    base_width_m: float = 3.0
    crest_width_m: float = 0.6
    height_m: float = 1.4
    windward_slope_deg: float = 35.0        # steeper, catches runoff
    leeward_slope_deg: float = 22.0         # gentler, garden side
    surface_texture_amplitude_cm: float = 8.0   # ridge-and-furrow on faces
    air_gap_layers: int = 2                 # internal coarse-rubble layers
    air_gap_thickness_cm: float = 12.0      # per layer
    contour_alignment: bool = True          # built on contour, not gradient

    def cross_section_area_m2(self) -> float:
        """Trapezoidal approximation."""
        return 0.5 * (self.base_width_m + self.crest_width_m) * self.height_m

    def volume_m3(self) -> float:
        return self.cross_section_area_m2() * self.length_m

    def windward_face_area_m2(self) -> float:
        slope_length = self.height_m / math.sin(math.radians(self.windward_slope_deg))
        textured_factor = 1.0 + (self.surface_texture_amplitude_cm / 100.0) * 2.0
        return slope_length * self.length_m * textured_factor

    def leeward_face_area_m2(self) -> float:
        slope_length = self.height_m / math.sin(math.radians(self.leeward_slope_deg))
        textured_factor = 1.0 + (self.surface_texture_amplitude_cm / 100.0) * 2.0
        return slope_length * self.length_m * textured_factor


# ----- coupled hydrology calculations -----

def runoff_capture_per_storm_l(
    geometry: EmbankmentGeometry,
    upslope_catchment_m2: float,
    storm_mm: float,
    runoff_coefficient: float = 0.45,
) -> float:
    """Liters of runoff intercepted by the embankment per storm event.
    runoff_coefficient ~0.4-0.6 for compacted Sahelian soils mid-season."""
    runoff_l = upslope_catchment_m2 * storm_mm * runoff_coefficient
    capture_capacity_l = geometry.volume_m3() * 1000.0 * 0.30
    return min(runoff_l, capture_capacity_l)


def night_atmospheric_yield_l(
    geometry: EmbankmentGeometry,
    laterite: LateriteProperties,
    nights: int = 1,
) -> float:
    """Water harvested from humid night air across the textured face."""
    yield_per_m3 = laterite.hygroscopic_yield_per_m3()
    return yield_per_m3 * geometry.volume_m3() * nights


def dry_season_storage_l(
    geometry: EmbankmentGeometry,
    laterite: LateriteProperties,
    end_of_wet_season_saturation: float = 0.70,
    evap_loss_fraction_per_month: float = 0.07,
    months_into_dry: int = 4,
) -> float:
    """Water remaining in embankment N months into dry season."""
    full_capacity_l = geometry.volume_m3() * laterite.water_storage_per_m3()
    starting_l = full_capacity_l * end_of_wet_season_saturation
    retention = (1.0 - evap_loss_fraction_per_month) ** months_into_dry
    return starting_l * retention


def capillary_root_zone_supply_mm_day(
    laterite: LateriteProperties,
    embankment_water_l: float,
    geometry: EmbankmentGeometry,
    garden_strip_width_m: float = 1.5,
) -> float:
    """Daily mm-equivalent water delivered to garden root zone via
    capillary wicking from saturated embankment core."""
    garden_area_m2 = geometry.length_m * garden_strip_width_m
    if garden_area_m2 <= 0:
        return 0.0
    # capillary delivery is rate-limited; 0.4-1.2 mm/day typical from
    # a moist earthen wick to adjacent root zone
    base_rate_mm_day = 0.8 * (laterite.capillary_rise_cm / 60.0)
    storage_factor = min(embankment_water_l / (geometry.volume_m3() * 200.0), 1.0)
    return base_rate_mm_day * storage_factor


# ----- garden layer: planting design -----

@dataclass
class GardenBed:
    name: str
    crop_water_need_mm_day: float
    root_depth_cm: float
    rainy_season_planting: bool
    dry_season_planting: bool
    notes: str = ""


SAHELIAN_GARDEN_PALETTE = [
    GardenBed("sorghum",          3.5, 90,  True,  False, "rainy season staple"),
    GardenBed("millet",           3.0, 80,  True,  False, "drought-tolerant rainy"),
    GardenBed("cowpea",           2.5, 60,  True,  False, "N-fixer, intercrop"),
    GardenBed("okra",             3.0, 50,  True,  True,  "wicking edge, both seasons"),
    GardenBed("moringa",          2.0, 200, True,  True,  "deep root, perennial"),
    GardenBed("bissap_hibiscus",  2.5, 50,  True,  False, ""),
    GardenBed("sweet_potato",     3.5, 40,  True,  True,  "shallow, near wick zone"),
    GardenBed("amaranth",         2.5, 40,  True,  True,  "leaf greens, fast cycle"),
    GardenBed("tomato_local",     4.0, 50,  False, True,  "dry-cool: Nov-Feb"),
    GardenBed("onion_shallot",    3.0, 30,  False, True,  "dry-cool window"),
]


def viable_dry_season_crops(
    capillary_supply_mm_day: float,
    supplemental_mm_day: float = 1.5,
    palette=SAHELIAN_GARDEN_PALETTE,
) -> list:
    """Crops viable through dry season given capillary supply from
    embankment plus typical supplemental input (zai pit hand-watering,
    mulched basin, small cistern allocation). Default supplemental
    1.5 mm/day reflects ~2 L/m2/day, achievable from rooftop catchment
    or stored runoff."""
    total_supply = capillary_supply_mm_day + supplemental_mm_day
    return [b for b in palette
            if b.dry_season_planting
            and b.crop_water_need_mm_day <= total_supply * 1.10]


# ----- integrated site report -----

@dataclass
class SiteReport:
    geometry: EmbankmentGeometry
    laterite: LateriteProperties
    climate: SahelianClimate
    upslope_catchment_m2: float
    design_storm_mm: float = 25.0

    def run(self) -> dict:
        runoff_l = runoff_capture_per_storm_l(
            self.geometry, self.upslope_catchment_m2, self.design_storm_mm
        )
        night_l = night_atmospheric_yield_l(self.geometry, self.laterite, nights=1)
        season_storage_l_m4 = dry_season_storage_l(
            self.geometry, self.laterite, months_into_dry=4
        )
        season_storage_l_m6 = dry_season_storage_l(
            self.geometry, self.laterite, months_into_dry=6
        )
        cap_supply_m4 = capillary_root_zone_supply_mm_day(
            self.laterite, season_storage_l_m4, self.geometry
        )
        cap_supply_m6 = capillary_root_zone_supply_mm_day(
            self.laterite, season_storage_l_m6, self.geometry
        )
        crops_m4 = viable_dry_season_crops(cap_supply_m4)
        crops_m6 = viable_dry_season_crops(cap_supply_m6)

        return {
            "embankment_volume_m3": round(self.geometry.volume_m3(), 2),
            "windward_face_m2": round(self.geometry.windward_face_area_m2(), 2),
            "leeward_face_m2": round(self.geometry.leeward_face_area_m2(), 2),
            "max_storage_L": round(
                self.geometry.volume_m3() * self.laterite.water_storage_per_m3(), 0
            ),
            "single_storm_capture_L": round(runoff_l, 0),
            "single_night_atmospheric_yield_L": round(night_l, 1),
            "storage_remaining_4mo_dry_L": round(season_storage_l_m4, 0),
            "storage_remaining_6mo_dry_L": round(season_storage_l_m6, 0),
            "capillary_supply_4mo_mm_day": round(cap_supply_m4, 2),
            "capillary_supply_6mo_mm_day": round(cap_supply_m6, 2),
            "viable_crops_4mo_dry": [c.name for c in crops_m4],
            "viable_crops_6mo_dry": [c.name for c in crops_m6],
        }


# ----- falsifiable claims -----

CLAIMS = [
    "C1: textured laterite face increases night atmospheric water uptake "
    "vs smooth face by >=30% (measurable: morning surface mass delta)",
    "C2: contour-aligned embankment intercepts >=40% of upslope runoff "
    "from a 25mm storm event (measurable: downstream flow gauge)",
    "C3: leeward garden strip receives >=0.5 mm/day capillary moisture "
    "into month 4 of dry season (measurable: TDR soil moisture probe)",
    "C4: at least 4 crop species in SAHELIAN_GARDEN_PALETTE remain viable "
    "through 4-month dry interval without irrigation (measurable: yield)",
    "C5: internal air-gap layers reduce embankment evaporative loss "
    "vs solid-fill control by >=15% (measurable: paired site mass loss)",
]


# ----- runnable example -----

if __name__ == "__main__":
    site = SiteReport(
        geometry=EmbankmentGeometry(),
        laterite=LateriteProperties(),
        climate=SahelianClimate(),
        upslope_catchment_m2=400.0,
        design_storm_mm=25.0,
    )
    report = site.run()
    print("Burkina Faso reference site - laterite embankment garden")
    print("=" * 60)
    for k, v in report.items():
        print(f"  {k}: {v}")
    print("\nFalsifiable claims:")
    for c in CLAIMS:
        print(f"  - {c}")
