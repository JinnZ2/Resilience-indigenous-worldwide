"""
field_test.py  --  CC0

Field-deployable decision protocol. Three escalating tests, cheapest first.
Routes a measured sample to a GO / CAUTION / STOP verdict per product class.
No instrument required for tier 1.

  TIER 1  spot test (ferric-chloride / visual)   ~ $0, minutes
          coarse: flags heavy contamination only
  TIER 2  DC conductivity (4-point or cheap meter on wire) ~ $50
          conductivity proxy for total solute load (electrical class)
  TIER 3  XRF (handheld)                          ~ $1.5-3k
          quantitative per-element wt% -> full injury vector readout

The protocol is constraint-primary: it tells the operator the cheapest test
that resolves the decision, and escalates only when the cheap test is
ambiguous. Emergency-class logic (food/medical) escalates faster than
structural because the injury vector is ingestion/implantation.
"""

from contaminants import (
    PRODUCT_CLASSES, FOOD_CAN, ELECTRICAL, MEDICAL, STRUCTURAL,
    injury_severity, conductivity_iacs, active_injury_vectors, CONTAMINANTS,
)

GO = "GO"
CAUTION = "CAUTION"
STOP = "STOP"


# product classes where injury vector is ingestion/implantation -> low tolerance
INGESTION_CLASSES = (FOOD_CAN, MEDICAL)


def tier1_spot_test_guidance(product_class):
    """
    Return the cheapest field check + what a positive result means.
    Pure text protocol, no instrument.
    """
    base = [
        "Visual: bright uniform silver = lower risk. Grey/mottled/dark oxide,",
        "  visible inclusions, or solder/paint residue = HIGH carryover risk.",
        "Magnet test: aluminium is non-magnetic. ANY magnetic pull = steel/Fe",
        "  contamination in the melt -> embrittlement vector active.",
    ]
    if product_class in INGESTION_CLASSES:
        base += [
            "Acid spot (vinegar, 10 min on inner surface): darkening/pitting =",
            "  reactive contaminant (Cu/Pb) -> DO NOT use for food/medical.",
        ]
    return base


def verdict_from_xrf(composition, product_class):
    """
    TIER 3 quantitative verdict. composition = {symbol: wt%} from XRF.
    Returns (verdict, severity, active_vectors).
    """
    sev = injury_severity(composition, product_class)
    vecs = active_injury_vectors(composition, product_class)

    # ingestion classes: any active toxic vector (Pb/Cd/Cu) = STOP
    toxic = {"Pb", "Cd", "Cu"}
    if product_class in INGESTION_CLASSES:
        if any(s in toxic for s, *_ in vecs):
            return STOP, sev, vecs
        if sev > 0.25:
            return STOP, sev, vecs
        if sev > 0.05:
            return CAUTION, sev, vecs
        return GO, sev, vecs

    if product_class == ELECTRICAL:
        iacs = conductivity_iacs(composition)
        if iacs < 55.0 or sev > 0.5:
            return STOP, sev, vecs
        if iacs < 58.5 or sev > 0.15:
            return CAUTION, sev, vecs
        return GO, sev, vecs

    # structural
    if sev > 0.6:
        return STOP, sev, vecs
    if sev > 0.25:
        return CAUTION, sev, vecs
    return GO, sev, vecs


def verdict_from_conductivity(iacs, product_class):
    """
    TIER 2: conductivity-only verdict. Only decisive for ELECTRICAL.
    For other classes, conductivity is a weak proxy -> recommend escalation.
    """
    if product_class == ELECTRICAL:
        if iacs < 55.0:
            return STOP, "conductivity below conductor-grade floor"
        if iacs < 58.5:
            return CAUTION, "conductivity reduced -- derate ampacity or escalate"
        return GO, "conductivity within conductor grade"
    return CAUTION, "conductivity is weak proxy for this class -- escalate to XRF"


def protocol(product_class):
    """
    Emit the full escalating protocol for a product class as a data structure.
    """
    return {
        "product_class": product_class,
        "ingestion_risk": product_class in INGESTION_CLASSES,
        "tier1_spot": tier1_spot_test_guidance(product_class),
        "tier2_conductivity_decisive": product_class == ELECTRICAL,
        "tier3_required_for_ingestion": product_class in INGESTION_CLASSES,
        "escalation_rule": (
            "ingestion classes: tier1 fail -> STOP. tier1 pass -> still require "
            "tier3 XRF before food/medical use (Pb/Cd invisible to tier1)."
            if product_class in INGESTION_CLASSES else
            "tier1 fail -> escalate. electrical: tier2 decisive. "
            "structural: tier3 if load-bearing."
        ),
    }


if __name__ == "__main__":
    dirty = {"Fe": 0.6, "Si": 0.7, "Cu": 0.3, "Pb": 0.05, "Mn": 0.3, "Cd": 0.01, "Zn": 0.2}
    for pc in PRODUCT_CLASSES:
        v, sev, vecs = verdict_from_xrf(dirty, pc)
        tag = ",".join(f"{s}x{r:.1f}" for s, _, _, r in vecs) or "-"
        print(f"{pc:11s} -> {v:7s}  severity={sev:.2f}  [{tag}]")
