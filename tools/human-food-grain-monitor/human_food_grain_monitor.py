# human_food_grain_monitor.py
# repo: precursor-detection / resilience    CC0    stdlib only    phone-buildable    dataclass-first
# architecture: fetch-on-wifi -> JSON cache -> read offline on road (same as thermal_to_ir / firms_fetch)
#
# CONTRACT (differential-frame-core): every noun is dX/dt under scope.
# This tool refuses two noun-traps the news/USDA headline commits:
#   TRAP 1 (sink-blind): counts total bushels as "supply". but fuel + feed mass is a buffer for
#                        ENGINES and LIVESTOCK, not people. so it monitors the HUMAN-FOOD calorie
#                        buffer SEPARATELY. abundance in bushels != abundance in human calories.
#   TRAP 2 (level-blind): watches the price/stock LEVEL (a noun). the signal is dStocks/dt — the
#                         RATE the cushion is consumed. the drawdown leads the price spike.
#
# It also scores each grain on the FLOW vs STATIC axis (flow_static_axis.py) so the resilient
# substitution set (millet / fonio / oats / sorghum / teff) is visible, not just the fragile complex.

import json, os
from dataclasses import dataclass, field, asdict

CACHE = os.path.expanduser("~/grain_cache.json")

# ----------------------------------------------------------------------
# one commodity's supply/use, split by SINK. units: million bushels OR Mt — keep consistent per run.
# the only split that matters: does the calorie reach a HUMAN MOUTH directly, or an engine/animal/port.
# ----------------------------------------------------------------------
@dataclass
class Commodity:
    name: str
    production: float
    ending_stocks: float
    human_direct: float        # food/seed/industrial that feeds people (cereal, flour, HFCS, etc.)
    feed: float                # livestock — lossy (~90% calorie loss before human)
    fuel: float                # ethanol/biofuel — oil-coupled, zero human calorie
    export: float              # leaves the domestic human pool

    @property
    def total_use(self):
        return self.human_direct + self.feed + self.fuel + self.export

    @property
    def human_stocks_to_use(self):
        # buffer measured ONLY against human-direct demand. the people-cushion.
        return self.ending_stocks / self.human_direct if self.human_direct else 0.0

    @property
    def total_stocks_to_use(self):
        return self.ending_stocks / self.total_use if self.total_use else 0.0

    @property
    def human_fraction(self):
        return self.human_direct / self.total_use if self.total_use else 0.0

# ----------------------------------------------------------------------
# buffer drawdown. feed a TIME SERIES of human_stocks_to_use -> get dX/dt (the leading signal).
# threshold trip fires on the RATE, not the level. negative slope = cushion being spent.
# ----------------------------------------------------------------------
def buffer_dxdt(series):
    # series: list[(period, human_stocks_to_use)] in time order
    if len(series) < 2:
        return 0.0
    (t0, x0), (t1, x1) = series[-2], series[-1]
    return (x1 - x0) / (t1 - t0) if t1 != t0 else 0.0

def trip(series, floor=0.12, max_drawdown=-0.02):
    # floor: human stocks-to-use below this = thin cushion (≈ <6 weeks human supply territory)
    # max_drawdown: dX/dt more negative than this = spending the cushion fast
    level = series[-1][1] if series else 0.0
    rate = buffer_dxdt(series)
    return {
        "human_stocks_to_use": round(level, 3),
        "drawdown_rate": round(rate, 4),
        "level_trip": level < floor,
        "rate_trip": rate < max_drawdown,
        "state": ("DEFICIT_APPROACH" if (level < floor and rate < max_drawdown)
                  else "THINNING" if rate < max_drawdown
                  else "LOW_BUT_STABLE" if level < floor
                  else "OK"),
    }

# ----------------------------------------------------------------------
# FLOW vs STATIC crop axis. 1.0 = pure flow (locally regenerable, low-input, climate-hardy).
# higher = better resilience for a least-buffer node, NOT higher peak yield.
# ----------------------------------------------------------------------
@dataclass
class Grain:
    name: str
    low_water: float           # 0..1  (C4 / drought-tolerant -> high)
    low_external_N: float      # 0..1  (independent of Haber-Bosch -> high)
    short_season: float        # 0..1  (fits erratic windows -> high)
    seed_saveable: float       # 0..1  (landrace, not hybrid/patented -> high)
    human_direct: float        # 0..1  (eaten by people, not fuel/feed complex -> high)
    trade_decoupled: float     # 0..1  (not priced off oil/global commodity -> high)
    peak_yield_penalty: float  # 0..1  the COST: how much peak yield given up vs irrigated wheat

    @property
    def flow_score(self):
        dims = [self.low_water, self.low_external_N, self.short_season,
                self.seed_saveable, self.human_direct, self.trade_decoupled]
        return round(sum(dims) / len(dims), 2)

GRAINS = [
    #     name              water  N     seas   seed  human  decoup  yield_penalty
    Grain("fonio",          0.95, 0.90, 0.95, 0.90, 1.00, 0.95, 0.55),
    Grain("pearl_millet",   0.95, 0.85, 0.85, 0.85, 1.00, 0.90, 0.45),
    Grain("finger_millet",  0.85, 0.85, 0.80, 0.90, 1.00, 0.90, 0.45),
    Grain("sorghum",        0.90, 0.75, 0.70, 0.70, 0.70, 0.50, 0.30),  # also feed/fuel -> human lower
    Grain("teff",           0.80, 0.80, 0.85, 0.85, 1.00, 0.90, 0.50),
    Grain("oats",           0.55, 0.70, 0.70, 0.75, 0.90, 0.75, 0.35),
    Grain("wheat_industrial",0.30,0.20, 0.40, 0.40, 0.80, 0.30, 0.00),  # the fixture baseline
    Grain("corn_industrial", 0.25,0.15, 0.45, 0.20, 0.10, 0.10, 0.00),  # fuel/feed, not human
    Grain("rice_paddy",      0.10,0.40, 0.45, 0.60, 1.00, 0.50, 0.10),
]

# ----------------------------------------------------------------------
# offline cache layer. fetch_and_cache() runs at home on wifi (you wire the USDA PSD / FAOSTAT
# pull here). read_cache() runs on the road. sim_fallback() if no cache + no net (graceful).
# ----------------------------------------------------------------------
def write_cache(commodities, series):
    with open(CACHE, "w") as f:
        json.dump({"commodities": [asdict(c) for c in commodities], "series": series}, f)

def read_cache():
    if not os.path.exists(CACHE):
        return None
    with open(CACHE) as f:
        return json.load(f)

def sim_fallback():
    # field-data rule: if real data refutes these, UPDATE the data — never retune to look calm.
    wheat = Commodity("wheat", production=1.048, ending_stocks=0.762,
                      human_direct=0.85, feed=0.12, fuel=0.0, export=0.40)
    corn  = Commodity("corn", production=15.0, ending_stocks=2.13,
                      human_direct=1.40, feed=6.1, fuel=5.6, export=3.0)
    # human-food stocks-to-use series for wheat, last 4 periods (illustrative, declining):
    wheat_series = [(0, 1.05), (1, 0.98), (2, 0.93), (3, 0.90)]
    return [wheat, corn], wheat_series

def run():
    data = read_cache()
    if data:
        commodities = [Commodity(**c) for c in data["commodities"]]
        series = [tuple(p) for p in data["series"]]
    else:
        commodities, series = sim_fallback()

    print("=== HUMAN-FOOD vs ENGINE/LIVESTOCK BUFFER ===")
    for c in commodities:
        print(f'{c.name:8} human_frac={c.human_fraction:.2f}  '
              f'human_S/U={c.human_stocks_to_use:.2f}  total_S/U={c.total_stocks_to_use:.2f}  '
              f'(total hides {(c.total_stocks_to_use - c.human_stocks_to_use):+.2f} of cushion)')

    print("\n=== WHEAT HUMAN-FOOD BUFFER dX/dt (the leading signal) ===")
    print(trip(series))

    print("\n=== GRAIN FLOW-vs-STATIC AXIS (resilience, not peak yield) ===")
    for g in sorted(GRAINS, key=lambda x: x.flow_score, reverse=True):
        kind = "FLOW " if g.flow_score >= 0.6 else "static"
        print(f'{g.name:17} flow={g.flow_score}  {kind}  yield_cost={g.peak_yield_penalty:.2f}')

if __name__ == "__main__":
    run()
