#!/usr/bin/env python3
# combined_antifungal_simulator.py
# Merges:
#  - mechanism crossing (crossover of target sets)
#  - temporal dosing & resistance evolution
#  - coupling topology (non-additive efficacy, axis orthogonality, sequence‑dependent antagonism)
# CC0. stdlib only.

import random
import math

# ─── COUPLING TOPOLOGY DATA (from antifungal_coupling_core.py) ───
TARGETS = {
    "CW": dict(name="β-glucan synthase (echinocandin)", eff=9, tox=2, p_res=0.40, axis="cell_wall"),
    "EG": dict(name="ergosterol synthesis (azole)",     eff=7, tox=3, p_res=0.60, axis="sterol"),
    "MD": dict(name="polyene (binds ergosterol)",       eff=8, tox=7, p_res=0.20, axis="sterol"),
    "PS": dict(name="EF-Tu protein synthesis",          eff=6, tox=5, p_res=0.50, axis="protein"),
    "NA": dict(name="5-FC nucleic acid",                eff=5, tox=4, p_res=0.70, axis="nucleic"),
    "SS": dict(name="Hsp90 stress buffer",              eff=4, tox=1, p_res=0.30, axis="stress"),
    "QP": dict(name="quorum / biofilm",                 eff=6, tox=2, p_res=0.40, axis="biofilm"),
}

# Signed pairwise efficacy coupling (synergy/antagonism)
J = {
    ("EG", "MD"): -0.6,   # azole depletes ergosterol -> antagonizes polyene
    ("MD", "NA"): +0.5,   # membrane damage boosts 5-FC uptake
    ("EG", "NA"): +0.3,
    ("CW", "EG"): +0.4,   # echinocandin + azole
    ("SS", "EG"): +0.5,   # Hsp90 inhibition potentiates azole
    ("SS", "CW"): +0.4,
    ("QP", "CW"): +0.2, ("QP", "EG"): +0.2,
}

def _j(a, b):
    return J.get((a, b), J.get((b, a), 0.0))

def efficacy(S):
    """Non‑additive efficacy using axis redundancy discount + synergy terms."""
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
        for k in range(i + 1, len(Sl)):
            jij = _j(Sl[i], Sl[k])
            if jij:
                syn += jij * (TARGETS[Sl[i]]["eff"] * TARGETS[Sl[k]]["eff"]) ** 0.5
    return base + syn

def toxicity(S):
    return sum(TARGETS[t]["tox"] for t in S)

def resistance_prob(S):
    """Axis‑orthogonality resistance suppression: multiply minima across axes."""
    by_axis = {}
    for t in S:
        by_axis.setdefault(TARGETS[t]["axis"], []).append(t)
    p = 1.0
    for ts in by_axis.values():
        p *= min(TARGETS[t]["p_res"] for t in ts)
    return p

# ─── TEMPORAL SIMULATION ENGINE ───
R, K, MU = 0.5, 1_000_000.0, 1e-4   # growth rate, carrying capacity, base mutation rate

class Drug:
    """Represents a single drug with a target from TARGETS, scaled kill rate."""
    def __init__(self, code):
        self.code = code
        self.eff = TARGETS[code]["eff"]
        # scale so that an eff=9 target gives kill rate ≈ 1.2 as in original model
        self.kill_rate = 1.2 * (self.eff / 9.0)
        self.p_res = TARGETS[code]["p_res"]   # escape probability (used for mutation scaling)
        self.axis = TARGETS[code]["axis"]

def compute_kill(genotype, active_drugs, ergosterol=1.0, use_coupling=False):
    """
    Kill rate for a given genotype and set of active drugs.
    If use_coupling=True, kill = efficacy(active_set_for_genotype) scaled;
    otherwise, additive sum of individual drug kills (like original).
    """
    # Which drugs can still kill this genotype?
    sens_drugs = [d for d in active_drugs if d.code in SENS[genotype]]
    if not sens_drugs:
        return 0.0

    if not use_coupling:
        # Original additive kill
        return sum(d.kill_rate for d in sens_drugs)

    # Coupling‑based kill: use efficacy of the set of targets the genotype is sensitive to
    active_targets = {d.code for d in sens_drugs}

    # Special handling for ergosterol-dependent pair (EG + MD)
    # If exactly EG (azole) and MD (polyene) are in the active_targets, use ergosterol pool
    if active_targets == {"EG", "MD"}:
        # Ergotsterol pool influences polyene kill; azole depletes it.
        # Azole kill = 7 * constant (independent of E for simplicity)
        # Polyene kill = 8 * E
        # This matches the polyene_azole() logic but inside one time step
        kill = 0.0
        # Note: order within the step is simultaneous, but we approximate by:
        # azole acts, then polyene acts on the remaining E.
        # We'll assume both are present; azole reduces E first, then polyene hits.
        # (A more precise model would require stateful steps, but this captures the antagonism.)
        azole_kill = TARGETS["EG"]["eff"] * (1.2/9)  # scaled
        polyene_kill = TARGETS["MD"]["eff"] * ergosterol * (1.2/9)
        kill = azole_kill + polyene_kill
        # Also deplete ergosterol for future steps? We'll handle that in step()
        return kill

    # General case: use efficacy() but scale back to kill rate.
    # efficacy() returns a number ~ sum of effs + synergies. We need a scaling factor.
    # We'll use the same base scaling: kill = efficacy(active_targets) * (1.2/9)
    return efficacy(active_targets) * (1.2 / 9)


def step(pop, active_drugs, collateral=False, use_coupling=True, ergosterol=1.0):
    """
    Advance population one time step.
    ergosterol is a state variable passed in; returns new pop and updated ergosterol.
    """
    total = sum(pop.values())
    new = {}
    E = ergosterol

    # Determine if EG or MD are active for ergosterol dynamics
    azole_active = any(d.code == "EG" for d in active_drugs)
    polyene_active = any(d.code == "MD" for d in active_drugs)

    # If azole is active, deplete ergosterol
    if azole_active:
        E = max(0.0, E - 0.5)  # simple decay per step

    for g, n in pop.items():
        growth = R * n * (1 - total / K)

        kill_rate = compute_kill(g, active_drugs, ergosterol=E, use_coupling=use_coupling)
        # Apply extra collateral sensitivity if requested (e.g., RA hypersensitive to B)
        if collateral and g == "RA":
            # if drug B (MD/polyene) is active, extra kill
            if any(d.code == "MD" for d in active_drugs):
                kill_rate += 0.8 * 1.2  # extra kill as in original

        kill = kill_rate * n
        new[g] = max(0.0, n + growth - kill)

    # Mutation flux (same as original but scaled by per-drug resistance probability)
    # For each drug, we add a mutation rate proportional to p_res.
    # To keep it simple, we use a fixed MU but optionally modify based on p_res later.
    f1 = MU * new["WT"]
    new["WT"] -= 2 * f1
    new["RA"] += f1
    new["RB"] += f1

    f2 = MU * (new["RA"] + new["RB"])
    new["RA"] -= MU * new["RA"]
    new["RB"] -= MU * new["RB"]
    new["RAB"] += f2

    return {g: max(0.0, v) for g, v in new.items()}, E


def run_simulation(drug_A_code, drug_B_code, schedule, collateral=False, use_coupling=True):
    """Run temporal evolution for a two-drug combination."""
    drug_A = Drug(drug_A_code)
    drug_B = Drug(drug_B_code)
    # Map genotype -> set of drug codes it is sensitive to
    SENS = {
        "WT": {drug_A.code, drug_B.code},
        "RA": {drug_B.code},   # resistant to A
        "RB": {drug_A.code},   # resistant to B
        "RAB": set(),
    }
    # Wrap SENS in a global-ish for compute_kill (quick and dirty)
    global SENS_GLOBAL
    SENS_GLOBAL = SENS

    pop = {"WT": 1e5, "RA": 1.0, "RB": 1.0, "RAB": 0.0}
    ergosterol = 1.0
    for step_no, active_codes in enumerate(schedule):
        # Convert active drug codes to Drug objects
        active_drugs = []
        if drug_A.code in active_codes:
            active_drugs.append(drug_A)
        if drug_B.code in active_codes:
            active_drugs.append(drug_B)
        # create a mutable SENS dict accessible by compute_kill
        SENS_GLOBAL = SENS
        pop, ergosterol = step(pop, active_drugs, collateral, use_coupling, ergosterol)
        # early termination if cleared
        if sum(pop.values()) < 1.0:
            break

    total = sum(pop.values())
    rfrac = pop["RAB"] / total if total > 1 else 0.0
    cleared = total < 1.0
    return total, rfrac, cleared


# Helper schedules
def schedules(n=40):
    return {
        "simultaneous": [{"A", "B"}] * n,
        "sequential mono": [{"A"}] * (n // 2) + [{"B"}] * (n // 2),
        "fast cycling": [{"A"} if i % 2 == 0 else {"B"} for i in range(n)],
    }

# ─── CROSSOVER MECHANICS (kept from original for library generation) ───
class Mechanism:
    def __init__(self, targets, name=""):
        self.targets = set(targets)
        self.name = name or "Unnamed"

    def fitness(self):
        return efficacy(self.targets) - toxicity(self.targets) - 12 * resistance_prob(self.targets)

    def __str__(self):
        return f"{self.name}: {self.targets} -> score {self.fitness():.2f}"


def crossover(parent_a, parent_b, offspring_name="Offspring"):
    union = parent_a.targets.union(parent_b.targets)
    k = random.randint(1, len(union))
    offspring_targets = set(random.sample(list(union), k))
    return Mechanism(offspring_targets, offspring_name)


# ─── MAIN DEMO ───
if __name__ == "__main__":
    print("=" * 70)
    print("  COMBINED ANTIFUNGAL SIMULATOR")
    print("  Coupling topology + temporal resistance evolution + crossover")
    print("=" * 70)

    # 1. Show how different drug pairs perform under various schedules
    test_pairs = [
        ("CW", "EG", "echinocandin + azole"),
        ("EG", "MD", "azole + polyene"),
    ]
    for code_A, code_B, label in test_pairs:
        print(f"\n>>> Drug pair: {label} (A={code_A}, B={code_B})")
        print(f"{'Schedule':<20} {'Final pop':>10} {'R-frac':>8}  Outcome (coupling on)")
        for sched_name, sched in schedules().items():
            # Use coupling=True
            tot, rf, cl = run_simulation(code_A, code_B, sched, collateral=False, use_coupling=True)
            print(f"{sched_name:<20} {tot:>10.0f} {rf:>8.3f}  {'CLEARED' if cl else 'survives'}")

    # 2. Show sequence‑dependent kill explicitly for azole+polyene with ergosterol
    print("\n\n>>> Sequence-dependent antagonism (non-commutative):")
    # Quick simulation of one step with ergosterol depletion order
    # We'll just use the polyene_azole() style
    def polyene_azole(order):
        E = 1.0
        kill = 0.0
        for drug in order:
            if drug == "polyene":
                kill += 8.0 * E
            elif drug == "azole":
                kill += 7.0
                E *= 0.3
        return kill

    ab = polyene_azole(["azole", "polyene"])
    ba = polyene_azole(["polyene", "azole"])
    print(f"  azole → polyene : kill = {ab:.1f}")
    print(f"  polyene → azole : kill = {ba:.1f}")
    print("  J[azole→polyene] ≠ J[polyene→azole] → non-commutative matrix")

    # 3. Crossover demo: generate a few mechanisms and evaluate them
    print("\n\n>>> Crossover discovery (coupling score):")
    m1 = Mechanism({"CW", "EG"}, "Parent1")
    m2 = Mechanism({"MD", "NA"}, "Parent2")
    print(m1)
    print(m2)
    offspring = crossover(m1, m2, "Offspring1")
    print(offspring)
    print("(You can cross any sets; the fitness uses efficacy/toxicity/resistance from coupling model.)")
