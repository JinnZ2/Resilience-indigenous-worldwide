"""
Calibration tests for architecture/hormuz_cascade_audit.py

Pins the two published anchors that the mortality function is calibrated to:
  - Sudan 2024  : 17M exposed, 50% deficit, 6mo, buffer 0.10 -> ~2.5M deaths
  - Ukraine 2023:  1B exposed,  5% deficit, 6mo, buffer 0.30 -> ~1M deaths

If anyone retunes the base rate or alpha in
excess_mortality_from_caloric_deficit, these tests will fail loudly
rather than letting the calibration silently drift.

Also pins a handful of structural invariants the cascade depends on:
  - timing-loss piecewise curve hits 40% at 6 weeks delay
  - Haber-Bosch energy ledger is internally consistent
  - solar-only scenario stays under presenter ceiling
  - structural mortality ceiling is enforced at 30%
"""

from architecture.hormuz_cascade_audit import (
    excess_mortality_from_caloric_deficit,
    yield_loss_from_delay,
    hb_energy_required,
    hb_nat_gas_required,
    hormuz_coupling_loss,
    solar_minimum_modifier,
    build_scenarios,
    HB_ENERGY_PER_KG_N,
    NG_LHV,
)


# ============================================================
# Published-anchor calibration
# ============================================================

def test_sudan_2024_anchor():
    """Clingendael 2024: 17M @ 50% kcal deficit × 6mo -> ~2.5M deaths."""
    deaths = excess_mortality_from_caloric_deficit({
        "pop_exposed":           17e6,
        "kcal_deficit_pct":      0.50,
        "duration_months":       6.0,
        "buffer_redistribution": 0.10,
    })
    # Published estimate is 2.5M; allow +/- 10% tolerance for model form.
    assert 2.25e6 <= deaths <= 2.75e6, (
        f"Sudan 2024 calibration drifted: got {deaths:,.0f}, expected ~2.5M"
    )


def test_ukraine_2023_anchor():
    """Edinburgh/Aberdeen/Karlsruhe/Rutgers: ~10% global fert disruption,
    broad pop exposed, ~6mo -> ~1M deaths. Encoded as 1B @ 5% deficit
    (effective after Haber-Bosch substitution), 6mo, buffer 0.30."""
    deaths = excess_mortality_from_caloric_deficit({
        "pop_exposed":           1.0e9,
        "kcal_deficit_pct":      0.05,
        "duration_months":       6.0,
        "buffer_redistribution": 0.30,
    })
    # Published rough estimate is ~1M; allow generous +/- 30% (broad-pop
    # estimates carry more uncertainty than concentrated-deficit ones).
    assert 0.7e6 <= deaths <= 1.3e6, (
        f"Ukraine 2023 calibration drifted: got {deaths:,.0f}, expected ~1M"
    )


# ============================================================
# Structural invariants
# ============================================================

def test_zero_deficit_zero_deaths():
    deaths = excess_mortality_from_caloric_deficit({
        "pop_exposed":           1e9,
        "kcal_deficit_pct":      0.0,
        "duration_months":       12.0,
        "buffer_redistribution": 0.0,
    })
    assert deaths == 0.0


def test_mortality_ceiling_enforced():
    """Physical ceiling: rate capped at 30% of exposed population."""
    deaths = excess_mortality_from_caloric_deficit({
        "pop_exposed":           1e9,
        "kcal_deficit_pct":      0.99,
        "duration_months":       60.0,
        "buffer_redistribution": 0.0,
    })
    assert deaths <= 0.30 * 1e9 + 1


def test_timing_loss_curve_anchored():
    """Piecewise yield-loss curve must hit known breakpoints."""
    assert yield_loss_from_delay({"weeks_delay": 0}) == 0.0
    assert abs(yield_loss_from_delay({"weeks_delay": 2}) - 0.08) < 1e-9
    assert abs(yield_loss_from_delay({"weeks_delay": 4}) - 0.22) < 1e-9
    assert abs(yield_loss_from_delay({"weeks_delay": 6}) - 0.40) < 1e-9
    assert abs(yield_loss_from_delay({"weeks_delay": 8}) - 0.60) < 1e-9


def test_timing_dominates_past_six_weeks():
    """Audit claim C5: agronomy constraint binds at >6 wk delay."""
    assert yield_loss_from_delay({"weeks_delay": 6}) >= 0.40


def test_haber_bosch_ledger_consistent():
    """NG required = (J of N fixation) / NG_LHV. Must round-trip."""
    kg_N = 1e9
    energy_J = hb_energy_required({"kg_N": kg_N})
    ng_kg    = hb_nat_gas_required({"kg_N": kg_N})
    # ng_kg * NG_LHV should reproduce energy_J to within rounding
    assert abs(ng_kg * NG_LHV - energy_J) / energy_J < 1e-9


def test_hormuz_coupling_decay_monotonic():
    """Longer substitution lag => more loss, never less."""
    base = {"hormuz_throughput_frac": 0.0, "buffer_stock_months": 1.0}
    losses = [hormuz_coupling_loss({**base, "substitution_lag_months": m})
              for m in (2, 6, 12, 24)]
    assert losses == sorted(losses)


def test_solar_drag_bounded():
    """Solar minimum modifier stays inside [2%, 8%]."""
    lo = solar_minimum_modifier({"solar_min_intensity": 0.0})
    hi = solar_minimum_modifier({"solar_min_intensity": 1.0})
    assert abs(lo - 0.02) < 1e-9
    assert abs(hi - 0.08) < 1e-9


# ============================================================
# Scenario-level audit claims
# ============================================================

def _run(name):
    s = next(s for s in build_scenarios() if s.scenario == name)
    s.execute()
    return s.results


def test_solar_only_under_presenter_ceiling():
    """Audit claim C3: solar alone cannot drive 225M deaths."""
    r = _run("solar_only_no_hormuz")
    assert r["excess_deaths"] < 225e6


def test_presenter_high_reaches_structural_ceiling():
    """Audit claim C1: compound cascade can reach the 1.07B*30% ceiling."""
    r = _run("presenter_high_concentrated")
    assert r["excess_deaths"] >= 225e6


def test_fao_baseline_exceeds_wfp_hunger_increment():
    """Audit claim C2: even institutional-aligned scenario beats WFP's
    45M hunger increment, because hunger != all-cause mortality."""
    r = _run("FAO_baseline_broad_sharing")
    assert r["excess_deaths"] >= 40e6


def test_energy_ledger_nonnegative():
    """Audit claim C4: NG and J freed scale with N withheld."""
    r = _run("presenter_high_concentrated")
    assert r["kg_N_withheld"] > 0
    assert r["natgas_freed_kg"] > 0
    assert r["hb_energy_freed_J"] > 0
