"""
regions.py  --  CC0

Regional vulnerability layer. Each region is a load-routing profile, not a
judgement. The variables are the ones that decide WHO absorbs a contaminated
batch first:

  import_dependency : fraction of aluminium goods imported as finished product
                      (high = no leverage over upstream batch quality)
  qc_capacity       : 0..1 local ability to detect contamination before use
                      (low = contamination passes silently into use)
  price_pressure    : 0..1 forced acceptance of lowest-grade material
                      (high = sorted into worst batches)
  buffer            : 0..1 ability to absorb a failure without injury
                      (low = no slack; failure -> direct harm)
  product_reliance  : {product_class: weight} how much daily survival depends
                      on each product class

These are first-pass values. Every one is meant to be overwritten by a local
operator with ground truth. Provenance is tracked: source tag per region.
"""

from dataclasses import dataclass, field
from contaminants import FOOD_CAN, ELECTRICAL, MEDICAL, STRUCTURAL


@dataclass
class Region:
    key: str
    name: str
    import_dependency: float      # 0..1
    qc_capacity: float            # 0..1  (higher = better detection)
    price_pressure: float         # 0..1
    buffer: float                 # 0..1  (higher = more slack)
    product_reliance: dict        # {product_class: weight 0..1}
    recycled_fraction: float      # 0..1  expected recycled content in supply
    source: str = "EST_first_pass"   # provenance tag


# ---------------------------------------------------------------------------
# REGION SET  (the zones Kavik flagged)
# ---------------------------------------------------------------------------
# Values are deliberately conservative first-pass estimates. Replace via
# regions_local.json overlay (see run_hotspot_scan.py) when field data lands.

REGIONS = {
    "africa_subsaharan": Region(
        key="africa_subsaharan", name="Sub-Saharan Africa",
        import_dependency=0.85, qc_capacity=0.15, price_pressure=0.90,
        buffer=0.10, recycled_fraction=0.55,
        product_reliance={FOOD_CAN: 0.8, ELECTRICAL: 0.7, MEDICAL: 0.9, STRUCTURAL: 0.4},
    ),
    "india": Region(
        key="india", name="India",
        import_dependency=0.45, qc_capacity=0.35, price_pressure=0.80,
        buffer=0.25, recycled_fraction=0.60,
        product_reliance={FOOD_CAN: 0.7, ELECTRICAL: 0.8, MEDICAL: 0.7, STRUCTURAL: 0.6},
    ),
    "south_america": Region(
        key="south_america", name="South America",
        import_dependency=0.55, qc_capacity=0.35, price_pressure=0.70,
        buffer=0.30, recycled_fraction=0.50,
        product_reliance={FOOD_CAN: 0.8, ELECTRICAL: 0.6, MEDICAL: 0.6, STRUCTURAL: 0.5},
    ),
    "cuba": Region(
        key="cuba", name="Cuba",
        import_dependency=0.75, qc_capacity=0.20, price_pressure=0.95,
        buffer=0.08, recycled_fraction=0.85,   # embargo -> forced recycled use
        product_reliance={FOOD_CAN: 0.9, ELECTRICAL: 0.8, MEDICAL: 0.95, STRUCTURAL: 0.5},
    ),
    "puerto_rico": Region(
        key="puerto_rico", name="Puerto Rico",
        import_dependency=0.90, qc_capacity=0.30, price_pressure=0.80,
        buffer=0.15, recycled_fraction=0.55,
        product_reliance={FOOD_CAN: 0.85, ELECTRICAL: 0.7, MEDICAL: 0.8, STRUCTURAL: 0.5},
    ),
    "us_inner_city": Region(
        key="us_inner_city", name="US Inner-City Poor",
        import_dependency=0.60, qc_capacity=0.40, price_pressure=0.75,
        buffer=0.18, recycled_fraction=0.45,
        product_reliance={FOOD_CAN: 0.85, ELECTRICAL: 0.6, MEDICAL: 0.5, STRUCTURAL: 0.4},
    ),
    "us_rural_poor": Region(
        key="us_rural_poor", name="US Rural Poor",
        import_dependency=0.55, qc_capacity=0.35, price_pressure=0.70,
        buffer=0.20, recycled_fraction=0.45,
        product_reliance={FOOD_CAN: 0.8, ELECTRICAL: 0.7, MEDICAL: 0.45, STRUCTURAL: 0.5},
    ),
}


def exposure_multiplier(region: Region):
    """
    Region-level amplifier on raw injury severity. Combines the load-routing
    variables into a single multiplier >= 0. This is the channel that turns
    a contaminated batch into a human-injury event.

    geometry:
      worse detection (low qc) -> contamination passes  -> amplify
      higher price pressure    -> worse batch accepted   -> amplify
      lower buffer             -> no slack to absorb      -> amplify
      higher import dependency -> no upstream leverage    -> amplify
    """
    detection_gap = 1.0 - region.qc_capacity
    no_slack = 1.0 - region.buffer
    # multiplicative -- these stack, they do not average
    m = (
        (0.5 + detection_gap)
        * (0.5 + region.price_pressure)
        * (0.5 + no_slack)
        * (0.5 + region.import_dependency)
    )
    return m
