# human_food_grain_monitor.py  v2
# repo: precursor-detection / resilience   CC0   stdlib only   phone-buildable   dataclass-first
# architecture: fetch-on-wifi -> JSON cache -> read offline on road
#
# CONTRACT (differential-frame-core): every noun is dX/dt under scope.
#
# v2 CHANGE (flaw caught in field): v1 scored each grain on a scalar flow_score -> implied a single
# winner. WRONG. there is no best grain. each crop is a PROBABILITY FIELD with a peak over a
# condition space (heat / water / season / soil). a location is a point + a year-to-year SWING.
# resilience is NOT a top score -- it is:
#     COVERAGE   : does some crop's field sit over this cell's conditions?
#     REDUNDANCY : how many crops cover it, so one failure doesn't zero the cell?
#     PORTFOLIO  : the crop SET that covers the whole gradient with backups.
# the commodity complex forced ONE crop onto EVERY cell via fixtures (irrigate desert, fertilize
# depleted soil, ship across the gradient) and called the uniformity efficiency. the flow model
# reads the gradient first and lets geography assign the crop.

import json, os, math
from dataclasses import dataclass, field, asdict

CACHE = os.path.expanduser("~/grain_cache.json")
AXES = ("heat", "water", "season", "soil")   # all 0..1. season=length. soil=fertility.

# ======================================================================
# PART A -- HUMAN-FOOD BUFFER (retained from v1; this part was correct)
# tracks the human-direct calorie cushion SEPARATE from the fuel/feed mass, on dX/dt not level.
# ======================================================================
@dataclass
class Commodity:
    name: str; production: float; ending_stocks: float
    human_direct: float; feed: float; fuel: float; export: float
    @property
    def total_use(self): return self.human_direct + self.feed + self.fuel + self.export
    @property
    def human_stocks_to_use(self): return self.ending_stocks / self.human_direct if self.human_direct else 0.0
    @property
    def total_stocks_to_use(self): return self.ending_stocks / self.total_use if self.total_use else 0.0
    @property
    def human_fraction(self): return self.human_direct / self.total_use if self.total_use else 0.0

def buffer_dxdt(series):
    if len(series) < 2: return 0.0
    (t0, x0), (t1, x1) = series[-2], series[-1]
    return (x1 - x0) / (t1 - t0) if t1 != t0 else 0.0

def trip(series, floor=0.12, max_drawdown=-0.02):
    level = series[-1][1] if series else 0.0
    rate = buffer_dxdt(series)
    return {"human_stocks_to_use": round(level,3), "drawdown_rate": round(rate,4),
            "level_trip": level < floor, "rate_trip": rate < max_drawdown,
            "state": ("DEFICIT_APPROACH" if (level<floor and rate<max_drawdown)
                      else "THINNING" if rate<max_drawdown
                      else "LOW_BUT_STABLE" if level<floor else "OK")}

# ======================================================================
# PART B -- CROPS AS PROBABILITY FIELDS OVER A CONDITION GRADIENT (the refactor)
# ======================================================================
@dataclass
class Crop:
    name: str
    ideal: dict          # peak location in condition space
    tolerance: float     # breadth of the field (gaussian sigma). broad=generalist, narrow=specialist
    human_direct: float  # 0..1 feeds people directly (not the fuel/feed complex)
    seed_saveable: float # 0..1 landrace vs fixture-dependent hybrid
    yield_cost: float    # 0..1 peak-yield given up vs irrigated wheat (honest counterweight)
    needs_fixture: bool = False   # True = real tolerance collapses without irrigation/Haber-Bosch

def fit(crop, cond):
    d2 = sum((crop.ideal[k] - cond[k])**2 for k in AXES)
    return math.exp(-d2 / (2 * crop.tolerance**2))

@dataclass
class Envelope:                 # a geographic/condition cell
    name: str
    center: dict
    swing: float = 0.12         # year-to-year variability radius -> drives redundancy NEED

def sample_swing(env):
    pts = [dict(env.center)]
    for k in AXES:
        for s in (+env.swing, -env.swing):
            p = dict(env.center); p[k] = min(1.0, max(0.0, p[k] + s)); pts.append(p)
    return pts

def portfolio(env, crops, fit_floor=0.5, inputs_available=False):
    pts = sample_swing(env)
    scored = []
    for c in crops:
        f_center = fit(c, env.center)
        f_worst = min(fit(c, p) for p in pts)      # must hold under variability, not just at center
        if c.needs_fixture and not inputs_available:
            f_center *= 0.3; f_worst *= 0.3        # fixture crop without its fixture = tolerance collapses
        scored.append((c.name, round(f_center,2), round(f_worst,2), c.human_direct, c.yield_cost))
    covered = [s for s in scored if s[2] >= fit_floor]
    covered.sort(key=lambda s: -s[1])
    human_covered = [s for s in covered if s[3] >= 0.7]
    return {"cell": env.name, "covered": bool(covered),
            "redundancy": len(covered), "human_food_redundancy": len(human_covered),
            "portfolio": [s[0] for s in covered],
            "best": covered[0][0] if covered else None,
            "yield_cost_of_best": covered[0][4] if covered else None,
            "gap": not bool(human_covered)}

CROPS = [
    Crop("pearl_millet",  {"heat":0.90,"water":0.15,"season":0.40,"soil":0.20}, 0.30, 1.00, 0.85, 0.45),
    Crop("sorghum",       {"heat":0.85,"water":0.25,"season":0.50,"soil":0.35}, 0.32, 0.70, 0.70, 0.30),
    Crop("fonio",         {"heat":0.85,"water":0.20,"season":0.15,"soil":0.15}, 0.28, 1.00, 0.90, 0.55),
    Crop("finger_millet", {"heat":0.70,"water":0.40,"season":0.30,"soil":0.30}, 0.28, 1.00, 0.90, 0.45),
    Crop("teff",          {"heat":0.60,"water":0.40,"season":0.25,"soil":0.40}, 0.26, 1.00, 0.85, 0.50),
    Crop("quinoa",        {"heat":0.35,"water":0.30,"season":0.50,"soil":0.40}, 0.28, 1.00, 0.85, 0.45),
    Crop("barley",        {"heat":0.35,"water":0.45,"season":0.35,"soil":0.50}, 0.34, 0.80, 0.75, 0.20),
    Crop("oats",          {"heat":0.35,"water":0.60,"season":0.45,"soil":0.55}, 0.28, 0.90, 0.75, 0.35),
    Crop("rye",           {"heat":0.25,"water":0.40,"season":0.40,"soil":0.30}, 0.34, 0.85, 0.80, 0.30),
    Crop("wild_rice",     {"heat":0.35,"water":0.90,"season":0.40,"soil":0.40}, 0.20, 1.00, 0.90, 0.40),
    Crop("rice_paddy",    {"heat":0.72,"water":0.92,"season":0.70,"soil":0.50}, 0.22, 1.00, 0.50, 0.10),
    Crop("wheat_industrial",{"heat":0.50,"water":0.50,"season":0.70,"soil":0.70},0.22,0.80,0.40,0.00, needs_fixture=True),
    Crop("corn_industrial", {"heat":0.65,"water":0.65,"season":0.75,"soil":0.80},0.20,0.10,0.20,0.00, needs_fixture=True),
]

ENVELOPES = [
    Envelope("sahel_hot_arid",      {"heat":0.90,"water":0.15,"season":0.35,"soil":0.20}, 0.16),
    Envelope("ethiopian_highland",  {"heat":0.60,"water":0.40,"season":0.30,"soil":0.40}, 0.12),
    Envelope("andean_altiplano",    {"heat":0.32,"water":0.30,"season":0.50,"soil":0.40}, 0.12),
    Envelope("northern_mn_wetland", {"heat":0.35,"water":0.85,"season":0.35,"soil":0.40}, 0.16),
    Envelope("temperate_cool_wet",  {"heat":0.40,"water":0.60,"season":0.50,"soil":0.55}, 0.12),
    Envelope("monsoon_paddy",       {"heat":0.75,"water":0.90,"season":0.70,"soil":0.50}, 0.10),
]

def write_cache(commodities, series):
    with open(CACHE,"w") as f: json.dump({"commodities":[asdict(c) for c in commodities],"series":series}, f)
def read_cache():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else None
def sim_fallback():
    return [Commodity("wheat",1.048,0.762,0.85,0.12,0.0,0.40),
            Commodity("corn",15.0,2.13,1.40,6.1,5.6,3.0)], [(0,1.05),(1,0.98),(2,0.93),(3,0.90)]

def run(inputs_available=False):
    data = read_cache()
    if data:
        commodities=[Commodity(**c) for c in data["commodities"]]; series=[tuple(p) for p in data["series"]]
    else:
        commodities, series = sim_fallback()
    print("=== A: HUMAN-FOOD vs ENGINE/LIVESTOCK BUFFER ===")
    for c in commodities:
        print(f'{c.name:6} human_frac={c.human_fraction:.2f}  human_S/U={c.human_stocks_to_use:.2f}  '
              f'total_S/U={c.total_stocks_to_use:.2f}  (total masks {c.total_stocks_to_use-c.human_stocks_to_use:+.2f})')
    print("  wheat human-buffer dX/dt:", trip(series))
    print("\n=== B: PORTFOLIO BY ENVELOPE  (coverage + redundancy, NOT a rank) ===")
    print(f'    inputs_available={inputs_available}  (fixtures collapse when False)')
    for env in ENVELOPES:
        r = portfolio(env, CROPS, inputs_available=inputs_available)
        flag = "  <-- GAP: no human-food crop survives swing" if r["gap"] else ""
        print(f'\n{r["cell"]}: redundancy={r["redundancy"]} human_redundancy={r["human_food_redundancy"]}{flag}')
        print(f'    portfolio: {r["portfolio"]}')
        print(f'    best={r["best"]} (yield_cost={r["yield_cost_of_best"]})')

if __name__ == "__main__":
    run(inputs_available=False)
