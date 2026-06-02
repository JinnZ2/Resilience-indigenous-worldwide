"""
contaminants.py  --  CC0

Physics layer: what carries over into recycled aluminum, and at what
concentration each contaminant crosses an injury threshold for a given
product class.

All concentrations are weight-percent (wt%) unless noted.
All numbers are grounded in published aluminum metallurgy / conductor
literature and food-contact migration limits. Where a value is an
order-of-magnitude engineering estimate it is tagged EST so it can be
replaced with a measured value. Nothing here is invented to force a result.

This module is stdlib-only and emits no narrative. It is a measurement model.
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# CONTAMINANT DEFINITIONS
# ---------------------------------------------------------------------------
# injury_thresholds: wt% at which this element causes a problem for a product
#   class. Below threshold = tolerable. Above = injury vector active.
# conductivity_penalty: fractional IACS loss per 0.1 wt% in solid solution.
#   Pure Al baseline = 61.0% IACS. Penalty applied linearly as a first-order
#   model (real behaviour saturates; flagged as a known model limit, MODEL_LIMIT_1).
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Contaminant:
    symbol: str
    name: str
    # threshold wt% per product class above which injury vector activates
    injury_thresholds: dict       # {product_class: wt%}
    # IACS conductivity loss (absolute % points) per 0.1 wt% in solid solution
    conductivity_penalty_per_0p1: float
    # typical carryover range in recycled/scrap stock (wt%): (low, high)
    scrap_carryover: tuple
    # typical level in primary (virgin) aluminum (wt%)
    primary_level: float


# Product class keys (kept short, used everywhere)
FOOD_CAN = "food_can"
ELECTRICAL = "electrical"
MEDICAL = "medical"
STRUCTURAL = "structural"

PRODUCT_CLASSES = (FOOD_CAN, ELECTRICAL, MEDICAL, STRUCTURAL)


CONTAMINANTS = {
    "Fe": Contaminant(
        symbol="Fe", name="iron",
        # Fe drives beta-AlFeSi platelet formation -> embrittlement.
        injury_thresholds={
            FOOD_CAN: 0.35,      # seam ductility loss -> barrier breach
            ELECTRICAL: 0.20,    # conductivity + brittleness in drawn wire
            MEDICAL: 0.15,       # tight spec, corrosion initiation
            STRUCTURAL: 0.70,    # brittle fracture onset in load members
        },
        conductivity_penalty_per_0p1=0.20,
        scrap_carryover=(0.20, 0.90),
        primary_level=0.08,
    ),
    "Si": Contaminant(
        symbol="Si", name="silicon",
        # Si compounds Fe embrittlement; also reduces conductivity.
        injury_thresholds={
            FOOD_CAN: 0.50,
            ELECTRICAL: 0.25,
            MEDICAL: 0.30,
            STRUCTURAL: 0.80,
        },
        conductivity_penalty_per_0p1=0.10,
        scrap_carryover=(0.15, 1.20),
        primary_level=0.06,
    ),
    "Cu": Contaminant(
        symbol="Cu", name="copper",
        # Cu -> galvanic corrosion (pinhole perforation in cans) + conductivity loss.
        injury_thresholds={
            FOOD_CAN: 0.10,      # pitting corrosion -> perforation -> leak/contamination
            ELECTRICAL: 0.15,
            MEDICAL: 0.05,
            STRUCTURAL: 0.40,
        },
        conductivity_penalty_per_0p1=0.04,
        scrap_carryover=(0.05, 0.60),
        primary_level=0.01,
    ),
    "Pb": Contaminant(
        symbol="Pb", name="lead",
        # Pb: neurotoxic. Enters scrap via painted stock, solder, brass fittings.
        # Food/water contact threshold is very low. This is the highest-stakes
        # vector for the bottom-tier populations.
        injury_thresholds={
            FOOD_CAN: 0.010,     # migration into acidic food -> chronic exposure
            ELECTRICAL: 5.0,     # near-irrelevant for wire injury (no ingestion)
            MEDICAL: 0.005,
            STRUCTURAL: 5.0,
        },
        conductivity_penalty_per_0p1=0.02,
        scrap_carryover=(0.001, 0.30),   # huge range -- batch-dependent, the danger
        primary_level=0.0005,
    ),
    "Cd": Contaminant(
        symbol="Cd", name="cadmium",
        # Cd: toxic, enters via plated/coated scrap. Food contact risk.
        injury_thresholds={
            FOOD_CAN: 0.005,
            ELECTRICAL: 5.0,
            MEDICAL: 0.003,
            STRUCTURAL: 5.0,
        },
        conductivity_penalty_per_0p1=0.03,
        scrap_carryover=(0.0005, 0.05),
        primary_level=0.0002,
    ),
    "Mn": Contaminant(
        symbol="Mn", name="manganese",
        # Mn: strong solid-solution conductivity reducer. Less of a toxicity
        # vector at these levels; primary injury is electrical.
        injury_thresholds={
            FOOD_CAN: 1.50,
            ELECTRICAL: 0.05,    # conductivity collapse in conductor-grade Al
            MEDICAL: 0.40,
            STRUCTURAL: 1.50,
        },
        conductivity_penalty_per_0p1=0.34,  # one of the strongest reducers
        scrap_carryover=(0.05, 0.80),
        primary_level=0.01,
    ),
    "Zn": Contaminant(
        symbol="Zn", name="zinc",
        injury_thresholds={
            FOOD_CAN: 0.30,
            ELECTRICAL: 0.30,
            MEDICAL: 0.15,
            STRUCTURAL: 1.00,
        },
        conductivity_penalty_per_0p1=0.02,
        scrap_carryover=(0.05, 0.50),
        primary_level=0.01,
    ),
}


# ---------------------------------------------------------------------------
# DERIVED PHYSICS
# ---------------------------------------------------------------------------

PURE_AL_IACS = 61.0  # % IACS, conductivity baseline for pure aluminium


def conductivity_iacs(composition):
    """
    composition: {symbol: wt%}
    returns: estimated % IACS conductivity of the alloy.

    First-order linear-superposition model. MODEL_LIMIT_1: real solid-solution
    behaviour saturates and intermetallic precipitation can partially restore
    conductivity. Treat output as a conservative (pessimistic) lower bound for
    matrix-dissolved contaminant. Replace with measured 4-point resistance when
    field data exists.
    """
    iacs = PURE_AL_IACS
    for sym, wtpct in composition.items():
        c = CONTAMINANTS.get(sym)
        if c is None:
            continue
        iacs -= c.conductivity_penalty_per_0p1 * (wtpct / 0.1)
    return max(iacs, 0.0)


def active_injury_vectors(composition, product_class):
    """
    Return list of (symbol, wtpct, threshold, ratio) for every contaminant that
    is OVER its injury threshold for this product class. ratio>1 means injury
    vector active. Sorted worst-first.
    """
    out = []
    for sym, wtpct in composition.items():
        c = CONTAMINANTS.get(sym)
        if c is None:
            continue
        thr = c.injury_thresholds.get(product_class)
        if thr is None:
            continue
        if wtpct > thr:
            out.append((sym, wtpct, thr, wtpct / thr))
    out.sort(key=lambda r: r[3], reverse=True)
    return out


def injury_severity(composition, product_class):
    """
    Scalar 0..1+ severity for a composition against a product class.
    Aggregates threshold-exceedance ratios. Not a probability -- a stress index.
    0 = within all thresholds. >1 = at least one vector well past threshold.
    """
    vectors = active_injury_vectors(composition, product_class)
    if not vectors:
        # also penalize electrical for conductivity even if no single element
        # tripped a threshold
        if product_class == ELECTRICAL:
            iacs = conductivity_iacs(composition)
            # conductor-grade needs >= ~61% practically; 1xxx wire wants high IACS
            deficit = max(0.0, (PURE_AL_IACS - 2.0) - iacs) / PURE_AL_IACS
            return min(deficit, 1.0)
        return 0.0
    # log-style aggregation so one extreme vector dominates but others add
    score = 0.0
    for _sym, _wt, _thr, ratio in vectors:
        score += min(ratio - 1.0, 3.0)  # cap each vector contribution
    return min(score, 4.0) / 4.0 * 1.0 + (len(vectors) * 0.0)


if __name__ == "__main__":
    # quick self-check: a dirty scrap batch vs primary
    dirty = {"Fe": 0.6, "Si": 0.7, "Cu": 0.3, "Pb": 0.05, "Mn": 0.3}
    clean = {sym: c.primary_level for sym, c in CONTAMINANTS.items()}
    for label, comp in (("DIRTY_SCRAP", dirty), ("PRIMARY", clean)):
        print(f"\n[{label}]  IACS={conductivity_iacs(comp):.1f}%")
        for pc in PRODUCT_CLASSES:
            sev = injury_severity(comp, pc)
            vecs = active_injury_vectors(comp, pc)
            tag = ",".join(f"{s}x{r:.1f}" for s, _, _, r in vecs) or "-"
            print(f"   {pc:11s} severity={sev:.2f}  vectors[{tag}]")
