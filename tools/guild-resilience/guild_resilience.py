# guild_resilience.py  v1
# repo: precursor-detection / resilience   CC0   stdlib only   phone-buildable
#
# Models a placed guild – a multi‑species food web – as a single resilient unit.
# Each species is a narrow specialist.  Guild resilience is the union of their
# probability fields over the micro‑gradient of a watershed.
#
# CONTRACT: A guild covers a condition space if, for every year-to-year swing
# point (hypercube corners), at least one member of the guild fits with
# probability ≥ fit_floor.  Redundancy is how many members clear that floor
# at the hardest swing point.

import itertools, math
from dataclasses import dataclass, field

AXES = ("heat", "water", "season", "soil")   # 0..1, all dimensionless

# ----------------------------------------------------------------------
# Species – a single food plant within a guild
# ----------------------------------------------------------------------
@dataclass
class Species:
    name: str
    ideal: dict          # peak location in condition space (0..1)
    tolerance: float     # breadth of the gaussian field (sigma)
    calorie_contribution: float = 0.1   # fraction of diet it can provide (rough)

def fit(species, cond):
    """Gaussian probability that the species thrives at this condition."""
    d2 = sum((species.ideal[k] - cond[k])**2 for k in AXES)
    return math.exp(-d2 / (2 * species.tolerance**2))

# ----------------------------------------------------------------------
# Guild – a placed multi‑species community
# ----------------------------------------------------------------------
@dataclass
class Guild:
    name: str
    home: dict            # centre of the watershed/garden/field area
    swing: float          # year‑to‑year variability radius
    members: list         # list of Species that live together here
    culture_note: str = ""

def guild_cover(guild, cond):
    """Maximum fit among all guild members at this condition."""
    return max(fit(sp, cond) for sp in guild.members)

def guild_portfolio(guild, fit_floor=0.5, diagonal_samples=True):
    """Generate swing points, evaluate coverage & redundancy."""
    pts = sample_swing(guild.home, guild.swing, diagonal_samples)
    worst_cover = min(guild_cover(guild, p) for p in pts)
    worst_member_fits = [fit(sp, pts[0]) for sp in guild.members]  # placeholder
    # actually we want, for the hardest point, which members still fit
    hardest_pt = max(pts, key=lambda p: -guild_cover(guild, p))  # point with worst max fit
    worst_fit_values = [fit(sp, hardest_pt) for sp in guild.members]
    covered_members = sum(1 for f in worst_fit_values if f >= fit_floor)
    return {
        "guild": guild.name,
        "covered": worst_cover >= fit_floor,
        "redundancy_at_hardest_point": covered_members,
        "worst_case_max_fit": round(worst_cover, 3),
        "culture_note": guild.culture_note,
    }

def sample_swing(center, swing, diagonal_samples=True):
    """Corner points of the swing hypercube (or single‑axis deviations)."""
    N = len(AXES)
    if not diagonal_samples:
        pts = [dict(center)]
        for k in AXES:
            for s in (+swing, -swing):
                p = dict(center); p[k] = min(1.0, max(0.0, p[k] + s)); pts.append(p)
        return pts
    pts = []
    for bits in itertools.product([0,1], repeat=N):
        p = {}
        for i, axis in enumerate(AXES):
            sign = +swing if bits[i] else -swing
            val = center[axis] + sign
            p[axis] = min(1.0, max(0.0, val))
        pts.append(p)
    return pts

# ======================================================================
# GUILD LIBRARY – communities from around the world
# ======================================================================
# Species ideals are "home" ± small offsets that represent micro‑niches
# within the watershed/garden.  Tolerances are typically narrow (0.15–0.25)
# because these are un‑domesticated or landrace specialists.
#
# Format: (name, {heat, water, season, soil}, tolerance, calorie_contribution)

# --- 1. Ojibwe wild rice guild (northern Minnesota wetlands) ---
ojibwe_home = {"heat":0.35, "water":0.85, "season":0.35, "soil":0.40}
ojibwe_members = [
    Species("wild_rice",      {"heat":0.35,"water":0.90,"season":0.40,"soil":0.40}, 0.20, 0.25),
    Species("cattail",        {"heat":0.35,"water":0.95,"season":0.45,"soil":0.35}, 0.22, 0.15),
    Species("arrowhead_wapato",{"heat":0.34,"water":0.92,"season":0.42,"soil":0.38}, 0.20, 0.15),
    Species("wild_celery",    {"heat":0.33,"water":0.88,"season":0.38,"soil":0.42}, 0.18, 0.10),
    Species("cranberry",      {"heat":0.32,"water":0.80,"season":0.30,"soil":0.20}, 0.18, 0.05),
    Species("wild_onion",     {"heat":0.36,"water":0.70,"season":0.32,"soil":0.45}, 0.22, 0.05),
    Species("dock",           {"heat":0.37,"water":0.75,"season":0.35,"soil":0.50}, 0.25, 0.10),
    Species("sumac",          {"heat":0.40,"water":0.55,"season":0.40,"soil":0.30}, 0.25, 0.05),
]

# --- 2. Haudenosaunee Three Sisters (Northeast temperate) ---
three_sisters_home = {"heat":0.55, "water":0.65, "season":0.60, "soil":0.75}
three_sisters_members = [
    Species("corn_flint",     {"heat":0.58,"water":0.60,"season":0.65,"soil":0.80}, 0.22, 0.30),
    Species("beans_climbing", {"heat":0.55,"water":0.65,"season":0.60,"soil":0.75}, 0.25, 0.25),
    Species("squash_winter",  {"heat":0.52,"water":0.55,"season":0.55,"soil":0.70}, 0.28, 0.20),
    Species("sunflower",      {"heat":0.56,"water":0.50,"season":0.62,"soil":0.65}, 0.22, 0.10),
    Species("jerusalem_artichoke", {"heat":0.54,"water":0.60,"season":0.55,"soil":0.60}, 0.26, 0.10),
    Species("amaranth",       {"heat":0.57,"water":0.45,"season":0.50,"soil":0.55}, 0.24, 0.05),
]

# --- 3. Milpa (Mesoamerican polyculture) ---
milpa_home = {"heat":0.75, "water":0.65, "season":0.80, "soil":0.60}
milpa_members = [
    Species("corn_dent",      {"heat":0.76,"water":0.60,"season":0.82,"soil":0.65}, 0.22, 0.30),
    Species("beans_common",   {"heat":0.74,"water":0.65,"season":0.78,"soil":0.60}, 0.25, 0.20),
    Species("squash_pepo",    {"heat":0.73,"water":0.55,"season":0.76,"soil":0.55}, 0.28, 0.20),
    Species("chili_pepper",   {"heat":0.78,"water":0.50,"season":0.85,"soil":0.50}, 0.20, 0.05),
    Species("amaranth_grain", {"heat":0.77,"water":0.45,"season":0.70,"soil":0.45}, 0.24, 0.10),
    Species("epazote",        {"heat":0.75,"water":0.55,"season":0.82,"soil":0.55}, 0.22, 0.05),
    Species("chia",           {"heat":0.74,"water":0.40,"season":0.65,"soil":0.40}, 0.20, 0.05),
]

# --- 4. Andean terraces (quinoa, potatoes, oca) ---
andean_home = {"heat":0.35, "water":0.40, "season":0.50, "soil":0.45}
andean_members = [
    Species("quinoa",        {"heat":0.35,"water":0.30,"season":0.50,"soil":0.40}, 0.28, 0.25),
    Species("potato_native", {"heat":0.32,"water":0.45,"season":0.45,"soil":0.50}, 0.22, 0.30),
    Species("oca",           {"heat":0.33,"water":0.40,"season":0.48,"soil":0.45}, 0.24, 0.15),
    Species("tarwi_lupin",   {"heat":0.34,"water":0.35,"season":0.52,"soil":0.40}, 0.22, 0.10),
    Species("maca",          {"heat":0.30,"water":0.30,"season":0.35,"soil":0.35}, 0.18, 0.05),
]

# --- 5. Sahelian intercropped grains (pearl millet, sorghum, cowpea) ---
sahel_home = {"heat":0.90, "water":0.20, "season":0.40, "soil":0.25}
sahel_members = [
    Species("pearl_millet",  {"heat":0.90,"water":0.15,"season":0.40,"soil":0.20}, 0.30, 0.35),
    Species("sorghum",       {"heat":0.88,"water":0.25,"season":0.45,"soil":0.30}, 0.28, 0.25),
    Species("cowpea",        {"heat":0.87,"water":0.22,"season":0.38,"soil":0.28}, 0.22, 0.15),
    Species("bambara_groundnut", {"heat":0.86,"water":0.20,"season":0.42,"soil":0.22}, 0.20, 0.10),
    Species("sesame",        {"heat":0.89,"water":0.18,"season":0.35,"soil":0.25}, 0.24, 0.05),
]

# --- 6. East African highland banana/coffee system ---
eafrican_highland_home = {"heat":0.65, "water":0.75, "season":0.80, "soil":0.70}
eafr_highland_members = [
    Species("banana_east_african", {"heat":0.66,"water":0.78,"season":0.82,"soil":0.75}, 0.22, 0.30),
    Species("enset",        {"heat":0.64,"water":0.70,"season":0.78,"soil":0.72}, 0.20, 0.25),
    Species("coffee_arabica", {"heat":0.62,"water":0.72,"season":0.80,"soil":0.65}, 0.18, 0.00), # cash/food edge
    Species("yam",           {"heat":0.67,"water":0.76,"season":0.85,"soil":0.68}, 0.25, 0.15),
    Species("pigeon_pea",    {"heat":0.65,"water":0.65,"season":0.75,"soil":0.60}, 0.24, 0.10),
]

# --- 7. Asian rice‑fish‑duck paddy guild ---
riceland_home = {"heat":0.75, "water":0.92, "season":0.75, "soil":0.55}
riceland_members = [
    Species("rice_paddy",   {"heat":0.72,"water":0.92,"season":0.70,"soil":0.50}, 0.22, 0.35),
    Species("azolla_fern",  {"heat":0.74,"water":0.95,"season":0.78,"soil":0.55}, 0.20, 0.05),  # feed/fix nitrogen
    Species("carp",         {"heat":0.73,"water":0.90,"season":0.72,"soil":0.55}, 0.20, 0.15),  # fish
    Species("duck",         {"heat":0.75,"water":0.85,"season":0.74,"soil":0.55}, 0.22, 0.10),  # animal protein
    Species("water_spinach",{"heat":0.76,"water":0.88,"season":0.80,"soil":0.60}, 0.18, 0.05),
]

# --- 8. Mediterranean polyculture (olive, grape, grain, legumes) ---
med_home = {"heat":0.55, "water":0.35, "season":0.70, "soil":0.45}
med_members = [
    Species("olive",        {"heat":0.58,"water":0.25,"season":0.72,"soil":0.40}, 0.22, 0.15),
    Species("grape_vine",   {"heat":0.56,"water":0.30,"season":0.70,"soil":0.38}, 0.20, 0.10),
    Species("durum_wheat",  {"heat":0.54,"water":0.35,"season":0.68,"soil":0.50}, 0.25, 0.30),
    Species("chickpea",     {"heat":0.55,"water":0.28,"season":0.65,"soil":0.42}, 0.22, 0.15),
    Species("lentil",       {"heat":0.53,"water":0.32,"season":0.60,"soil":0.45}, 0.22, 0.15),
    Species("fig",          {"heat":0.57,"water":0.35,"season":0.72,"soil":0.40}, 0.24, 0.05),
]

# --- 9. Southeast Asian homegarden (multi‑storey) ---
seasian_home = {"heat":0.82, "water":0.85, "season":0.90, "soil":0.65}
seasian_members = [
    Species("coconut",     {"heat":0.82,"water":0.80,"season":0.92,"soil":0.60}, 0.22, 0.10),
    Species("breadfruit",  {"heat":0.80,"water":0.78,"season":0.90,"soil":0.65}, 0.24, 0.15),
    Species("taro",        {"heat":0.80,"water":0.90,"season":0.88,"soil":0.70}, 0.20, 0.20),
    Species("yam_dioscorea",{"heat":0.81,"water":0.82,"season":0.86,"soil":0.68}, 0.22, 0.15),
    Species("banana",      {"heat":0.83,"water":0.84,"season":0.92,"soil":0.72}, 0.25, 0.15),
    Species("papaya",      {"heat":0.84,"water":0.75,"season":0.94,"soil":0.60}, 0.22, 0.05),
    Species("sweet_potato", {"heat":0.79,"water":0.72,"season":0.85,"soil":0.55}, 0.24, 0.10),
]

# --- 10. Amazonian terra preta agroforestry ---
amazon_home = {"heat":0.85, "water":0.80, "season":0.90, "soil":0.90}  # rich black earth
amazon_members = [
    Species("manioc",       {"heat":0.85,"water":0.75,"season":0.90,"soil":0.85}, 0.22, 0.30),
    Species("peach_palm",   {"heat":0.84,"water":0.82,"season":0.92,"soil":0.90}, 0.24, 0.15),
    Species("cupuacu",      {"heat":0.83,"water":0.85,"season":0.88,"soil":0.88}, 0.20, 0.05),
    Species("acai",         {"heat":0.86,"water":0.90,"season":0.92,"soil":0.85}, 0.22, 0.05),
    Species("pineapple",    {"heat":0.87,"water":0.70,"season":0.85,"soil":0.80}, 0.25, 0.05),
    Species("cashew",       {"heat":0.84,"water":0.65,"season":0.88,"soil":0.75}, 0.24, 0.05),
]

# --- 11. Tibetan barley‑pea‑buckwheat rotation ---
tibetan_home = {"heat":0.22, "water":0.35, "season":0.25, "soil":0.30}
tibetan_members = [
    Species("hulless_barley", {"heat":0.22,"water":0.32,"season":0.25,"soil":0.30}, 0.24, 0.35),
    Species("pea_field",      {"heat":0.20,"water":0.35,"season":0.22,"soil":0.32}, 0.22, 0.20),
    Species("buckwheat",      {"heat":0.21,"water":0.33,"season":0.20,"soil":0.28}, 0.22, 0.15),
    Species("mustard_greens", {"heat":0.23,"water":0.36,"season":0.18,"soil":0.35}, 0.20, 0.10),
]

# --- 12. Pacific Northwest Coast salal‑camas‑wapato ---
pnw_home = {"heat":0.30, "water":0.80, "season":0.40, "soil":0.55}
pnw_members = [
    Species("camas",         {"heat":0.31,"water":0.65,"season":0.38,"soil":0.55}, 0.22, 0.25),
    Species("salal",         {"heat":0.29,"water":0.82,"season":0.42,"soil":0.50}, 0.18, 0.05),
    Species("wapato",        {"heat":0.32,"water":0.88,"season":0.40,"soil":0.52}, 0.20, 0.15),
    Species("salmonberry",   {"heat":0.30,"water":0.85,"season":0.45,"soil":0.60}, 0.20, 0.05),
    Species("silverweed",    {"heat":0.31,"water":0.78,"season":0.38,"soil":0.53}, 0.22, 0.10),
]

# --- 13. Kalahari mongongo‑marula‑melon gather‑tend system ---
kalahari_home = {"heat":0.88, "water":0.15, "season":0.45, "soil":0.15}
kalahari_members = [
    Species("mongongo",     {"heat":0.88,"water":0.12,"season":0.45,"soil":0.15}, 0.18, 0.20),
    Species("marula",       {"heat":0.87,"water":0.18,"season":0.48,"soil":0.18}, 0.22, 0.15),
    Species("tsamma_melon", {"heat":0.89,"water":0.10,"season":0.40,"soil":0.12}, 0.16, 0.10),
    Species("gemsbok_cucumber", {"heat":0.86,"water":0.14,"season":0.42,"soil":0.14}, 0.18, 0.10),
]

# --- 14. Australian Aboriginal yam‑daisy‑grass seed guild ---
austral_home = {"heat":0.70, "water":0.25, "season":0.50, "soil":0.20}
austral_members = [
    Species("murnong_yam_daisy", {"heat":0.70,"water":0.28,"season":0.48,"soil":0.22}, 0.20, 0.20),
    Species("bush_tomato",   {"heat":0.72,"water":0.20,"season":0.52,"soil":0.18}, 0.18, 0.10),
    Species("native_millet", {"heat":0.71,"water":0.22,"season":0.45,"soil":0.18}, 0.22, 0.25),
    Species("quandong",      {"heat":0.69,"water":0.24,"season":0.50,"soil":0.20}, 0.22, 0.05),
]

# --- 15. Sámi cloudberry‑angelica‑reindeer‑lichen mountain mire ---
sami_home = {"heat":0.12, "water":0.65, "season":0.15, "soil":0.15}
sami_members = [
    Species("cloudberry",   {"heat":0.12,"water":0.70,"season":0.14,"soil":0.12}, 0.15, 0.15),
    Species("angelica",     {"heat":0.11,"water":0.65,"season":0.16,"soil":0.18}, 0.16, 0.10),
    Species("reindeer_lichen", {"heat":0.10,"water":0.55,"season":0.10,"soil":0.10}, 0.18, 0.05),  # indirectly via reindeer
    Species("bilberry",     {"heat":0.13,"water":0.60,"season":0.15,"soil":0.15}, 0.16, 0.10),
]

# --- 16. Polynesian atoll breadfruit‑pandanus‑giant swamp taro ---
atoll_home = {"heat":0.85, "water":0.65, "season":0.90, "soil":0.20}  # coral sand
atoll_members = [
    Species("breadfruit",       {"heat":0.85,"water":0.62,"season":0.92,"soil":0.22}, 0.24, 0.25),
    Species("pandanus",         {"heat":0.84,"water":0.60,"season":0.88,"soil":0.18}, 0.22, 0.10),
    Species("giant_swamp_taro", {"heat":0.86,"water":0.78,"season":0.90,"soil":0.25}, 0.20, 0.15),
    Species("coconut",          {"heat":0.87,"water":0.55,"season":0.95,"soil":0.20}, 0.22, 0.15),
]

# --- 17. Korean jangdokdae (soybean‑pepper‑perilla multi‑strata) ---
korean_home = {"heat":0.52, "water":0.70, "season":0.60, "soil":0.65}
korean_members = [
    Species("soybean",      {"heat":0.52,"water":0.65,"season":0.58,"soil":0.70}, 0.22, 0.25),
    Species("chili_pepper", {"heat":0.54,"water":0.60,"season":0.62,"soil":0.60}, 0.20, 0.05),
    Species("perilla",      {"heat":0.51,"water":0.68,"season":0.60,"soil":0.65}, 0.22, 0.10),
    Species("garlic",       {"heat":0.50,"water":0.62,"season":0.50,"soil":0.68}, 0.20, 0.05),
    Species("mung_bean",    {"heat":0.53,"water":0.63,"season":0.55,"soil":0.60}, 0.24, 0.10),
]

# --- 18. Ethiopian enset‑coffee‑khat agroforest ---
ethiopian_home = {"heat":0.62, "water":0.72, "season":0.75, "soil":0.65}
ethiopian_members = [
    Species("enset",        {"heat":0.62,"water":0.70,"season":0.78,"soil":0.68}, 0.20, 0.30),
    Species("coffee_arabica", {"heat":0.60,"water":0.75,"season":0.76,"soil":0.62}, 0.18, 0.00),
    Species("khat",         {"heat":0.64,"water":0.65,"season":0.80,"soil":0.60}, 0.22, 0.05),
    Species("cabbage_tree", {"heat":0.61,"water":0.72,"season":0.74,"soil":0.66}, 0.24, 0.10),
    Species("teff",         {"heat":0.60,"water":0.62,"season":0.55,"soil":0.55}, 0.22, 0.15),
]

# ----------------------------------------------------------------------
# GUILD COLLECTION
# ----------------------------------------------------------------------
GUILDS = [
    Guild("Ojibwe Wild Rice Guild",        ojibwe_home, 0.16, ojibwe_members, "Northern Minnesota wetlands – tended, not domesticated"),
    Guild("Haudenosaunee Three Sisters",   three_sisters_home, 0.12, three_sisters_members, "Northeast temperate polyculture"),
    Guild("Milpa Mesoamerica",             milpa_home, 0.14, milpa_members, "Mesoamerican corn‑bean‑squash with multiple companions"),
    Guild("Andean Terraces",               andean_home, 0.12, andean_members, "High‑altitude quinoa‑potato‑oca rotation"),
    Guild("Sahel Intercrop",               sahel_home, 0.18, sahel_members, "Sahelian dryland grains and legumes"),
    Guild("E.African Highland Food Forest", eafrican_highland_home, 0.12, eafr_highland_members, "Banana‑enset‑coffee multi‑storey"),
    Guild("Asian Rice‑Fish‑Duck",           riceland_home, 0.10, riceland_members, "Integrated paddy guild with aquatic life"),
    Guild("Mediterranean Polyculture",      med_home, 0.14, med_members, "Olive‑grape‑grain‑legume mosaic"),
    Guild("SE Asian Homegarden",            seasian_home, 0.10, seasian_members, "Multi‑storey coconut‑breadfruit‑taro"),
    Guild("Amazon Terra Preta",             amazon_home, 0.10, amazon_members, "Manioc‑peach palm‑cupuaçu on black earth"),
    Guild("Tibetan Barley‑Pea Rotation",    tibetan_home, 0.12, tibetan_members, "High‑cold dryland mixed grains"),
    Guild("PNW Coast Salal‑Camas",         pnw_home, 0.14, pnw_members, "Pacific Northwest root & berry guild"),
    Guild("Kalahari Mongongo‑Marula",       kalahari_home, 0.20, kalahari_members, "Desert edge gather‑tend system"),
    Guild("Australian Aboriginal Yam‑Daisy", austral_home, 0.18, austral_members, "Murnong yam daisy & native millet"),
    Guild("Sámi Mountain Mire",             sami_home, 0.12, sami_members, "Sub‑Arctic berry‑angelica‑reindeer lichen"),
    Guild("Polynesian Atoll Breadfruit",    atoll_home, 0.12, atoll_members, "Coral atoll agroforest with giant swamp taro"),
    Guild("Korean Jangdokdae",             korean_home, 0.12, korean_members, "Soy‑pepper‑perilla kitchen garden"),
    Guild("Ethiopian Enset‑Coffee",         ethiopian_home, 0.12, ethiopian_members, "Enset‑coffee‑khat highland system"),
]

# ----------------------------------------------------------------------
# EVALUATION
# ----------------------------------------------------------------------
def evaluate_all_guilds(fit_floor=0.5, diagonal_samples=True):
    print("GUILD RESILIENCE SCAN")
    print(f"fit_floor={fit_floor}, diagonal_samples={diagonal_samples}\n")
    for g in GUILDS:
        res = guild_portfolio(g, fit_floor, diagonal_samples)
        status = "COVERS" if res["covered"] else "GAP"
        print(f"{g.name:35s} | {status:6s} | worst max fit={res['worst_case_max_fit']:.3f} | redundancy={res['redundancy_at_hardest_point']}")
        if res["culture_note"]:
            print(f"  ↳ {res['culture_note']}")

if __name__ == "__main__":
    evaluate_all_guilds(fit_floor=0.5, diagonal_samples=True)
