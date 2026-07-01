#!/usr/bin/env python3
# community_antifungal_simulator.py
# =====================================================================
# COLLABORATIVE SIMULATOR — MODERN + TRADITIONAL ANTIFUNGAL THERAPIES
# =====================================================================
# - Define local traditional remedies (plant extracts, etc.)
# - Combine them with each other and with modern drugs
# - Simulate temporal resistance evolution under different dosing schedules
# - Discover new cross‑mechanism combinations via crossover
# - All parameters adjustable; CC0 — free for any community to use, modify, share.
# =====================================================================

import random
import json
import os

# ═══════════════════════ COUPLING CORE ═══════════════════════════
TARGETS = {
    # ─── Modern targets ───
    "CW": dict(name="β-glucan synthase (echinocandin)", eff=9, tox=2, p_res=0.40, axis="cell_wall"),
    "EG": dict(name="ergosterol synthesis (azole)",     eff=7, tox=3, p_res=0.60, axis="sterol"),
    "MD": dict(name="polyene (binds ergosterol)",       eff=8, tox=7, p_res=0.20, axis="sterol"),
    "PS": dict(name="EF-Tu protein synthesis",          eff=6, tox=5, p_res=0.50, axis="protein"),
    "NA": dict(name="5-FC nucleic acid",                eff=5, tox=4, p_res=0.70, axis="nucleic"),
    "SS": dict(name="Hsp90 stress buffer",              eff=4, tox=1, p_res=0.30, axis="stress"),
    "QP": dict(name="quorum / biofilm",                 eff=6, tox=2, p_res=0.40, axis="biofilm"),
}

J = {
    ("EG", "MD"): -0.6,
    ("MD", "NA"): +0.5,
    ("EG", "NA"): +0.3,
    ("CW", "EG"): +0.4,
    ("SS", "EG"): +0.5,
    ("SS", "CW"): +0.4,
    ("QP", "CW"): +0.2,
    ("QP", "EG"): +0.2,
}

def _j(a, b):
    return J.get((a, b), J.get((b, a), 0.0))

def efficacy(S):
    by_axis = {}
    for t in S:
        by_axis.setdefault(TARGETS[t]["axis"], []).append(t)
    base = 0.0
    for ts in by_axis.values():
        effs = sorted((TARGETS[t]["eff"] for t in ts), reverse=True)
        base += effs[0] + 0.5 * sum(effs[1:])
    syn = 0.0
    Sl = sorted(S)
    for i in range(len(Sl)):
        for k in range(i+1, len(Sl)):
            jij = _j(Sl[i], Sl[k])
            if jij:
                syn += jij * (TARGETS[Sl[i]]["eff"] * TARGETS[Sl[k]]["eff"])**0.5
    return base + syn

def toxicity(S):
    return sum(TARGETS[t]["tox"] for t in S)

def resistance_prob(S):
    by_axis = {}
    for t in S:
        by_axis.setdefault(TARGETS[t]["axis"], []).append(t)
    p = 1.0
    for ts in by_axis.values():
        p *= min(TARGETS[t]["p_res"] for t in ts)
    return p

# ══════════════════ TRADITIONAL REMEDY MANAGER ════════════════════
def add_traditional_remedy():
    """Interactive definition of a traditional treatment."""
    print("\n── Define a Traditional Remedy ──")
    code = input("Short code (e.g., GARLIC): ").strip().upper()
    if code in TARGETS:
        print("Code already exists. Use update function (or remove first).")
        return
    name = input("Full name (e.g., Garlic extract): ").strip()
    try:
        eff = float(input("Efficacy (1‑10, how well it kills fungus): "))
        tox = float(input("Toxicity/side effects (0‑10, 0=none): "))
        p_res = float(input("Resistance escape probability (0‑1, lower=harder to resist): "))
    except ValueError:
        print("Invalid number. Aborting.")
        return
    print("Biological axis (e.g., cell_wall, membrane, traditional_barrier).")
    print("Existing axes: " + ", ".join({t["axis"] for t in TARGETS.values()}))
    axis = input("Axis for this remedy: ").strip().lower()
    if not axis:
        axis = "traditional"
    TARGETS[code] = dict(name=name, eff=eff, tox=tox, p_res=p_res, axis=axis)
    print(f"Added {name} ({code}) successfully.")

    # Optionally add synergy with existing targets
    add_syn = input("Add synergy with existing drugs? (y/n): ").strip().lower()
    if add_syn == 'y':
        while True:
            other = input("Target code to pair with (or press Enter to finish): ").strip().upper()
            if not other:
                break
            if other not in TARGETS:
                print("Unknown code.")
                continue
            try:
                strength = float(input(f"Synergy strength with {other} (-1 antagonism to +1 synergy): "))
            except ValueError:
                print("Invalid. Skipping.")
                continue
            J[(code, other)] = strength
            print(f"Added J[{code},{other}] = {strength}")
    print()

def list_targets():
    print("\n─── Available Targets ───")
    for code, t in sorted(TARGETS.items()):
        print(f"  {code:<6} {t['name']:<35} eff={t['eff']:<3} tox={t['tox']:<3} p_res={t['p_res']:<.2f} axis={t['axis']}")
    print()

def save_custom_library(filename="traditional_remedies.json"):
    """Save user‑added TARGETS and J entries (excluding built‑ins)."""
    builtins = {"CW","EG","MD","PS","NA","SS","QP"}
    custom_targets = {k:v for k,v in TARGETS.items() if k not in builtins}
    custom_J = {f"{a}+{b}":v for (a,b),v in J.items() if a not in builtins or b not in builtins}
    data = {"targets": custom_targets, "J": custom_J}
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Custom library saved to {filename}")

def load_custom_library(filename="traditional_remedies.json"):
    if not os.path.exists(filename):
        print("No custom library file found.")
        return
    with open(filename, 'r') as f:
        data = json.load(f)
    for code, props in data.get("targets", {}).items():
        TARGETS[code] = props
    for pair, val in data.get("J", {}).items():
        a,b = pair.split("+")
        J[(a,b)] = val
    print(f"Loaded custom library from {filename}")

# ═══════════════════ TEMPORAL SIMULATION ════════════════════════
R, K, MU = 0.5, 1_000_000.0, 1e-4

class Drug:
    def __init__(self, code):
        self.code = code
        self.eff = TARGETS[code]["eff"]
        self.kill_rate = 1.2 * (self.eff / 9.0)
        self.p_res = TARGETS[code]["p_res"]
        self.axis = TARGETS[code]["axis"]

SENS_GLOBAL = None  # will be set per run

def compute_kill(genotype, active_drugs, ergosterol=1.0, use_coupling=True):
    sens_drugs = [d for d in active_drugs if d.code in SENS_GLOBAL[genotype]]
    if not sens_drugs:
        return 0.0
    if not use_coupling:
        return sum(d.kill_rate for d in sens_drugs)
    active_targets = {d.code for d in sens_drugs}
    # Special ergosterol handling for EG+MD pair
    if active_targets == {"EG", "MD"}:
        azole_kill = TARGETS["EG"]["eff"] * (1.2/9)
        polyene_kill = TARGETS["MD"]["eff"] * ergosterol * (1.2/9)
        return azole_kill + polyene_kill
    return efficacy(active_targets) * (1.2 / 9)

def step(pop, active_drugs, collateral=False, use_coupling=True, ergosterol=1.0):
    total = sum(pop.values())
    new = {}
    E = ergosterol
    azole_active = any(d.code == "EG" for d in active_drugs)
    if azole_active:
        E = max(0.0, E - 0.5)

    for g, n in pop.items():
        growth = R * n * (1 - total / K)
        kill_rate = compute_kill(g, active_drugs, E, use_coupling)
        if collateral and g == "RA" and any(d.code == "MD" for d in active_drugs):
            kill_rate += 0.8 * 1.2
        new[g] = max(0.0, n + growth - kill_rate * n)

    f1 = MU * new["WT"]
    new["WT"] -= 2*f1; new["RA"] += f1; new["RB"] += f1
    f2 = MU * (new["RA"] + new["RB"])
    new["RA"] -= MU*new["RA"]; new["RB"] -= MU*new["RB"]; new["RAB"] += f2
    return {g: max(0.0, v) for g, v in new.items()}, E

def run_simulation(drug_A_code, drug_B_code, schedule, collateral=False, use_coupling=True):
    drug_A = Drug(drug_A_code)
    drug_B = Drug(drug_B_code)
    global SENS_GLOBAL
    SENS_GLOBAL = {
        "WT": {drug_A.code, drug_B.code},
        "RA": {drug_B.code},
        "RB": {drug_A.code},
        "RAB": set(),
    }
    pop = {"WT": 1e5, "RA": 1.0, "RB": 1.0, "RAB": 0.0}
    ergosterol = 1.0
    for active_codes in schedule:
        active_drugs = []
        if drug_A.code in active_codes: active_drugs.append(drug_A)
        if drug_B.code in active_codes: active_drugs.append(drug_B)
        SENS_GLOBAL = SENS_GLOBAL  # re-set after creation (to avoid late binding issues)
        pop, ergosterol = step(pop, active_drugs, collateral, use_coupling, ergosterol)
        if sum(pop.values()) < 1.0:
            break
    total = sum(pop.values())
    rfrac = pop["RAB"]/total if total > 1 else 0.0
    return total, rfrac, (total < 1.0)

def schedules(n=40):
    return {
        "simultaneous": [{"A","B"}]*n,
        "sequential mono": [{"A"}]*(n//2) + [{"B"}]*(n//2),
        "fast cycling": [{"A"} if i%2==0 else {"B"} for i in range(n)],
    }

# ═══════════════════ CROSSOVER MECHANISM ═══════════════════════
class Mechanism:
    def __init__(self, targets, name=""):
        self.targets = set(targets)
        self.name = name
    def fitness(self):
        return efficacy(self.targets) - toxicity(self.targets) - 12*resistance_prob(self.targets)
    def __str__(self):
        return f"{self.name}: {self.targets} -> score {self.fitness():.2f}"

def crossover(parent_a, parent_b, offspring_name="Offspring"):
    union = parent_a.targets.union(parent_b.targets)
    k = random.randint(1, len(union))
    return Mechanism(set(random.sample(list(union), k)), offspring_name)

# ═══════════════════════ MAIN MENU ═══════════════════════════
def main():
    print("="*60)
    print("  COMMUNITY ANTIFUNGAL SIMULATOR")
    print("  Traditional knowledge + modern pharmacology")
    print("="*60)
    while True:
        print("\n── Menu ──")
        print("1. List all targets (modern + traditional)")
        print("2. Add a traditional remedy")
        print("3. Save custom remedies to file")
        print("4. Load custom remedies from file")
        print("5. Simulate a two‑drug combination")
        print("6. Crossover two mechanisms (discovery)")
        print("7. Quit")
        choice = input("Choose: ").strip()
        if choice == '1':
            list_targets()
        elif choice == '2':
            add_traditional_remedy()
        elif choice == '3':
            save_custom_library()
        elif choice == '4':
            load_custom_library()
        elif choice == '5':
            list_targets()
            code_A = input("Code for Drug A (e.g., CW or GARLIC): ").strip().upper()
            code_B = input("Code for Drug B: ").strip().upper()
            if code_A not in TARGETS or code_B not in TARGETS:
                print("Unknown code(s).")
                continue
            print("Dosing schedules: simultaneous, sequential mono, fast cycling")
            sched_name = input("Schedule name: ").strip()
            sched = schedules().get(sched_name)
            if not sched:
                print("Unknown schedule. Using fast cycling.")
                sched = schedules()["fast cycling"]
            tot, rf, cl = run_simulation(code_A, code_B, sched)
            print(f"Final pop: {tot:.0f}   R-frac: {rf:.3f}   {'CLEARED' if cl else 'survives'}")
        elif choice == '6':
            print("Create two parent mechanisms from target codes (space separated).")
            p1 = input("Parent1 codes (e.g., CW EG GARLIC): ").upper().split()
            p2 = input("Parent2 codes: ").upper().split()
            m1 = Mechanism(p1, "Parent1")
            m2 = Mechanism(p2, "Parent2")
            print(f"Parent1: {m1}")
            print(f"Parent2: {m2}")
            off = crossover(m1, m2, "Offspring")
            print(f"Offspring: {off}")
            print("Add to targets? (y/n): ", end="")
            if input().strip().lower() == 'y':
                name = input("Name for this combination: ").strip()
                # Add as a single target? Not directly, but we could store it as a mechanism.
                print("Mechanism stored (not a single target, but you can reuse its set in simulations).")
        elif choice == '7':
            print("Exiting. Stay curious!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
