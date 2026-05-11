"""
Layer engines. Each returns a state dict given upstream forcing.
Pure functions. No hidden state. Deterministic + stochastic paths separated.
"""

from math import exp

from resilience.boundary_waters.constants import (
    AS_PER_TONNE_MG,
    BOIS_FORTE_ENROLLMENT,
    BOREAL_FOREST_ACRES_CORRIDOR,
    BREACH_LIABILITY_USD_ANNUAL,
    BWCA_RESERVOIR_CAPACITY_KM3,
    DOWNSTREAM_USERS_RELIANT,
    DULUTH_PORT_JOBS,
    FOND_DU_LAC_ENROLLMENT,
    GRAND_PORTAGE_ENROLLMENT,
    HG_PER_TONNE_MG,
    IJC_TRIGGER_DAYS,
    INTL_BOUNDARY_FLUX_FRAC,
    KAWISHIWI_DISCHARGE_M3_S,
    LAKE_TROUT_HG_BAF,
    LOON_HG_LETHAL_PPM,
    LUMBER_JOBS_CORRIDOR,
    MANOOMIN_ACRES_AT_RISK,
    MEAN_LAKE_RESIDENCE_YR,
    MINE_JOBS_DIRECT,
    MINE_JOB_DURATION_YR,
    MINE_START_YEAR,
    PB_PER_TONNE_MG,
    PEAT_HG_METHYLATION_RATE,
    RESIDENTS_WITHIN_20KM,
    SULFATE_LETHAL_MG_L,
    SULFATE_PER_TONNE_ORE_KG,
    SULFATE_TOXIC_MG_L,
    TOURISM_JOBS_CURRENT,
    TREATY_SULFATE_BREACH_MG_L,
    WELL_DEPENDENT_FRAC,
)


# ═════════════════════════════════════════════════════════════
# L0 — CHEMISTRY ENGINE
# ═════════════════════════════════════════════════════════════

def chemistry_layer(year, mine_active, cumulative_waste_tonnes):
    """
    Acid + metal generation from exposed sulfide rock.
    Post-closure drainage persists via microbial catalysis.
    """
    if not mine_active and cumulative_waste_tonnes == 0:
        return _zero_chem()

    # Acid rock drainage scales with cumulative exposed surface
    # Declines slowly post-closure (half-life ~200 yr observed)
    exposure_factor = 1.0 if mine_active else exp(-(year - MINE_START_YEAR - MINE_JOB_DURATION_YR) / 290.0)

    sulfate_kg_yr = cumulative_waste_tonnes * SULFATE_PER_TONNE_ORE_KG * 0.04 * exposure_factor
    hg_mg_yr      = cumulative_waste_tonnes * HG_PER_TONNE_MG * 0.08 * exposure_factor
    pb_mg_yr      = cumulative_waste_tonnes * PB_PER_TONNE_MG * 0.06 * exposure_factor
    as_mg_yr      = cumulative_waste_tonnes * AS_PER_TONNE_MG * 0.07 * exposure_factor

    return {
        "sulfate_kg_yr": sulfate_kg_yr,
        "hg_mg_yr":      hg_mg_yr,
        "pb_mg_yr":      pb_mg_yr,
        "as_mg_yr":      as_mg_yr,
        "exposure":      exposure_factor,
    }


def _zero_chem():
    return {"sulfate_kg_yr": 0, "hg_mg_yr": 0, "pb_mg_yr": 0, "as_mg_yr": 0, "exposure": 0}


# ═════════════════════════════════════════════════════════════
# L1 — HYDROLOGY ENGINE
# ═════════════════════════════════════════════════════════════

def hydrology_layer(chem, year_since_start):
    """
    Vollenweider-style mass balance: dC/dt = (L - k*C)/V
    Steady-state C* = L/(k*V), where k = 1/tau (residence time).
    Load L (kg/yr) -> concentration in receiving lake chain.
    Empirical ceiling: AMD plumes observed at 100-3000 mg/L SO4.
    """
    annual_flow_m3 = KAWISHIWI_DISCHARGE_M3_S * 3600 * 24 * 365  # ~7.6e8 m3/yr

    # Receiving lake volume (Birch/South Kawishiwi chain ~ 0.3 km3)
    receiving_vol_m3 = 3.0e8

    # Steady-state: flush rate = 1/residence_time
    flush_rate_yr = 1.0 / MEAN_LAKE_RESIDENCE_YR

    # Concentration (kg/m3 -> mg/L via *1000)
    load_kg_yr = chem["sulfate_kg_yr"]
    steady_state_mg_l = (load_kg_yr / (flush_rate_yr * receiving_vol_m3)) * 1000 / 1000

    # Approach to steady state: 1 - exp(-t/tau)
    approach = 1 - exp(-year_since_start / MEAN_LAKE_RESIDENCE_YR) if year_since_start > 0 else 0
    sulfate_mg_l = steady_state_mg_l * approach

    # Empirical ceiling from observed AMD sites (Berkeley Pit ~8000, typical 200-2000)
    sulfate_mg_l = min(sulfate_mg_l, 4000.0)

    hg_load_mg_yr = chem["hg_mg_yr"]
    hg_ss_ng_l = (hg_load_mg_yr * 1e6) / (flush_rate_yr * receiving_vol_m3 * 1000)
    hg_conc_ng_l = min(hg_ss_ng_l * approach, 80.0)   # cap at observed AMD max
    methyl_hg_ng_l = hg_conc_ng_l * PEAT_HG_METHYLATION_RATE

    crosses_border_mg_l = sulfate_mg_l * INTL_BOUNDARY_FLUX_FRAC

    return {
        "sulfate_mg_l":        sulfate_mg_l,
        "hg_ng_l":             hg_conc_ng_l,
        "methyl_hg_ng_l":      methyl_hg_ng_l,
        "canada_sulfate_mg_l": crosses_border_mg_l,
        "manoomin_breach":     sulfate_mg_l > SULFATE_TOXIC_MG_L,
        "manoomin_lethal":     sulfate_mg_l > SULFATE_LETHAL_MG_L,
    }


# ═════════════════════════════════════════════════════════════
# L2 — ECOLOGY ENGINE
# ═════════════════════════════════════════════════════════════

def ecology_layer(hydro, year_since_start):
    """
    Wild rice, lake trout, loons, boreal forest, amphibians.
    Thresholds are fish-kill class, not 'slight stress'.
    """
    manoomin_loss_frac = min(1.0, max(0, (hydro["sulfate_mg_l"] - 5) / (SULFATE_LETHAL_MG_L - 5)))
    manoomin_acres_lost = MANOOMIN_ACRES_AT_RISK * manoomin_loss_frac

    lake_trout_hg_ppm = hydro["methyl_hg_ng_l"] * LAKE_TROUT_HG_BAF / 1e9 * 1e6 / 1000
    loon_mortality_frac = min(1.0, lake_trout_hg_ppm / LOON_HG_LETHAL_PPM)

    # Boreal forest downstream acidification (peatland die-off)
    forest_loss_frac = min(0.4, hydro["sulfate_mg_l"] / 200.0)
    forest_acres_lost = BOREAL_FOREST_ACRES_CORRIDOR * forest_loss_frac

    amphibian_collapse = hydro["sulfate_mg_l"] > 30

    return {
        "manoomin_acres_lost":  manoomin_acres_lost,
        "lake_trout_hg_ppm":    lake_trout_hg_ppm,
        "loon_mortality_frac":  loon_mortality_frac,
        "forest_acres_lost":    forest_acres_lost,
        "amphibian_collapse":   amphibian_collapse,
    }


# ═════════════════════════════════════════════════════════════
# L3 — COMMUNITY / LABOR ENGINE
# ═════════════════════════════════════════════════════════════

def community_layer(hydro, ecol, mine_active, year_since_start):
    """
    Well contamination, forced migration, labor displacement.
    Mine jobs vs. destroyed tourism/lumber/sovereignty jobs.
    """
    # Well contamination follows water table + substrate
    well_contamination_frac = min(1.0, hydro["sulfate_mg_l"] / 40.0) if year_since_start > 2 else 0
    wells_contaminated = int(RESIDENTS_WITHIN_20KM * WELL_DEPENDENT_FRAC * well_contamination_frac)

    # Forced migration trigger: well failure + no municipal alt
    migration_pressure = well_contamination_frac * 0.7 + ecol["manoomin_acres_lost"]/MANOOMIN_ACRES_AT_RISK * 0.3
    forced_migrants = int(RESIDENTS_WITHIN_20KM * min(0.65, migration_pressure))

    # Treaty-protected harvesters (Bois Forte, Grand Portage, Fond du Lac)
    # Manoomin loss = usufructuary rights violation under 1854 Treaty
    treaty_harvesters_displaced = int(
        (BOIS_FORTE_ENROLLMENT + GRAND_PORTAGE_ENROLLMENT + FOND_DU_LAC_ENROLLMENT)
        * ecol["manoomin_acres_lost"] / MANOOMIN_ACRES_AT_RISK
    )

    # Jobs ledger
    mine_jobs = MINE_JOBS_DIRECT if mine_active else 0
    tourism_loss_frac = min(1.0, hydro["sulfate_mg_l"] / 15.0)
    tourism_jobs_lost = int(TOURISM_JOBS_CURRENT * tourism_loss_frac)

    lumber_loss_frac = min(0.6, ecol["forest_acres_lost"] / BOREAL_FOREST_ACRES_CORRIDOR)
    lumber_jobs_lost = int(LUMBER_JOBS_CORRIDOR * lumber_loss_frac)

    net_jobs = mine_jobs - tourism_jobs_lost - lumber_jobs_lost

    return {
        "wells_contaminated":         wells_contaminated,
        "forced_migrants":            forced_migrants,
        "treaty_harvesters_displaced": treaty_harvesters_displaced,
        "mine_jobs":                  mine_jobs,
        "tourism_jobs_lost":          tourism_jobs_lost,
        "lumber_jobs_lost":           lumber_jobs_lost,
        "net_jobs":                   net_jobs,
    }


# ═════════════════════════════════════════════════════════════
# L4 — PORT / RESERVOIR ENGINE
# ═════════════════════════════════════════════════════════════

def port_layer(hydro, ecol, year_since_start):
    """
    Lake Superior pollution transit (~200 yr residence).
    Reservoir capacity loss from sedimentation + contamination.
    Duluth-Superior port function at risk if Hg advisories cascade.
    """
    # Contaminant fraction reaching Lake Superior via St. Louis R. tributary
    # (separate pathway from Rainy, but tailings dust + runoff)
    lake_superior_hg_loading = hydro["hg_ng_l"] * 0.12

    # Reservoir function degradation (drinking/industrial water for
    # downstream ports and 680k basin residents)
    reservoir_usability_frac = max(0, 1.0 - hydro["sulfate_mg_l"] / 100.0)
    reservoir_km3_lost = BWCA_RESERVOIR_CAPACITY_KM3 * (1 - reservoir_usability_frac)

    # Port labor cascade: tourism collapse + fish advisories + water quality
    # spills into Duluth service economy
    port_impact_frac = min(0.3, year_since_start / 100.0 * ecol["loon_mortality_frac"])
    port_jobs_at_risk = int(DULUTH_PORT_JOBS * port_impact_frac)

    # Downstream water users losing safe intake
    users_losing_safe_water = int(DOWNSTREAM_USERS_RELIANT * (1 - reservoir_usability_frac))

    return {
        "lake_superior_hg_loading":   lake_superior_hg_loading,
        "reservoir_km3_lost":         reservoir_km3_lost,
        "port_jobs_at_risk":          port_jobs_at_risk,
        "users_losing_safe_water":    users_losing_safe_water,
    }


# ═════════════════════════════════════════════════════════════
# L5 — INTERNATIONAL LAW ENGINE
# ═════════════════════════════════════════════════════════════

def intl_law_layer(hydro, year_since_start, breach_days_accumulated):
    """
    Boundary Waters Treaty 1909, Art. IV.
    Trail Smelter (1941) customary intl law precedent.
    """
    daily_breach = hydro["canada_sulfate_mg_l"] > TREATY_SULFATE_BREACH_MG_L
    new_breach_days = 365 if daily_breach else 0
    total_breach_days = breach_days_accumulated + new_breach_days

    ijc_referral_triggered = total_breach_days > IJC_TRIGGER_DAYS
    trail_smelter_liability = total_breach_days > 365 * 2  # sustained 2-yr harm

    liability_npv_usd = BREACH_LIABILITY_USD_ANNUAL * max(0, (total_breach_days / 365) - 1)

    return {
        "canada_sulfate_breach":      daily_breach,
        "total_breach_days":          total_breach_days,
        "ijc_referral_triggered":     ijc_referral_triggered,
        "trail_smelter_liability":    trail_smelter_liability,
        "liability_npv_usd":          liability_npv_usd,
    }
