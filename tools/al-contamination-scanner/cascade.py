"""
cascade.py  --  CC0

The simulation engine. Monte Carlo over plausible recycled-aluminium batch
compositions, routed through each region's vulnerability channel, scored per
product class, aggregated to an exposure_weighted_risk_index (EWRI).

stdlib only. Deterministic given a seed. No narrative output -- it emits a
data structure. The caller renders.

METHODOLOGY RULE (carried from prior work):
  if a claim is refuted by data, update the claim -- do NOT modify the
  simulation to support the hypothesis. The batch model below is sampled from
  published scrap carryover ranges, not tuned to produce hotspots.
"""

import random
from dataclasses import dataclass, field

from contaminants import (
    CONTAMINANTS, PRODUCT_CLASSES, FOOD_CAN, ELECTRICAL, MEDICAL, STRUCTURAL,
    injury_severity, conductivity_iacs, active_injury_vectors,
)
from regions import REGIONS, exposure_multiplier


# ---------------------------------------------------------------------------
# BATCH SAMPLING
# ---------------------------------------------------------------------------

def sample_batch(rng, recycled_fraction):
    """
    Draw one plausible alloy composition.

    recycled_fraction blends primary-level and scrap-carryover ranges:
      comp = (1-f)*primary + f*U(scrap_low, scrap_high)
    Pb and Cd are sampled with a heavy upper tail because the danger is the
    rare-but-severe contaminated batch (painted/soldered scrap), not the median.
    """
    comp = {}
    for sym, c in CONTAMINANTS.items():
        lo, hi = c.scrap_carryover
        if sym in ("Pb", "Cd"):
            # heavy-tailed: most batches near low end, occasional spike
            u = rng.random() ** 3          # bias toward 0
            scrap = lo + (hi - lo) * u
            # 1-in-12 chance of a bad-stock spike toward the high end
            if rng.random() < 1 / 12:
                scrap = lo + (hi - lo) * (0.6 + 0.4 * rng.random())
        else:
            scrap = rng.uniform(lo, hi)
        comp[sym] = (1.0 - recycled_fraction) * c.primary_level + recycled_fraction * scrap
    return comp


# ---------------------------------------------------------------------------
# SCORING
# ---------------------------------------------------------------------------

@dataclass
class RegionResult:
    key: str
    name: str
    ewri: float                       # exposure-weighted risk index (mean)
    ewri_p95: float                   # 95th percentile (the bad-batch tail)
    per_product: dict                 # {product_class: mean severity}
    dominant_vector: dict             # {product_class: top contaminant symbol}
    mean_iacs: float                  # mean conductivity of sampled batches
    multiplier: float                 # region exposure multiplier


def run_region(rng, region, n_batches):
    per_product_acc = {pc: 0.0 for pc in PRODUCT_CLASSES}
    vector_counts = {pc: {} for pc in PRODUCT_CLASSES}
    iacs_acc = 0.0
    ewri_samples = []

    mult = exposure_multiplier(region)

    for _ in range(n_batches):
        comp = sample_batch(rng, region.recycled_fraction)
        iacs_acc += conductivity_iacs(comp)

        batch_ewri = 0.0
        for pc in PRODUCT_CLASSES:
            sev = injury_severity(comp, pc)
            per_product_acc[pc] += sev
            # weight by how much the region relies on this product
            reliance = region.product_reliance.get(pc, 0.0)
            batch_ewri += sev * reliance
            # track dominant vector
            vecs = active_injury_vectors(comp, pc)
            if vecs:
                top = vecs[0][0]
                vector_counts[pc][top] = vector_counts[pc].get(top, 0) + 1
        # apply the regional channel multiplier
        ewri_samples.append(batch_ewri * mult)

    ewri_samples.sort()
    n = len(ewri_samples)
    mean_ewri = sum(ewri_samples) / n
    p95 = ewri_samples[min(n - 1, int(0.95 * n))]

    per_product = {pc: per_product_acc[pc] / n_batches for pc in PRODUCT_CLASSES}
    dominant = {}
    for pc in PRODUCT_CLASSES:
        if vector_counts[pc]:
            dominant[pc] = max(vector_counts[pc].items(), key=lambda kv: kv[1])[0]
        else:
            dominant[pc] = "-"

    return RegionResult(
        key=region.key, name=region.name,
        ewri=mean_ewri, ewri_p95=p95,
        per_product=per_product, dominant_vector=dominant,
        mean_iacs=iacs_acc / n_batches, multiplier=mult,
    )


def run_scan(n_batches=20000, seed=1, regions=None):
    """
    Full hotspot scan across all regions.
    Returns list[RegionResult] sorted worst-first by mean EWRI.
    """
    rng = random.Random(seed)
    regions = regions or REGIONS
    results = [run_region(rng, r, n_batches) for r in regions.values()]
    results.sort(key=lambda r: r.ewri, reverse=True)
    return results
