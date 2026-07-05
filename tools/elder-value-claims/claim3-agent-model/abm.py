# abm.py  --  CC0
# Claim 3: Elder survival advantage — agent-based model.
# stdlib only. No external dependencies.
#
# Two groups run in parallel for N generations:
#   Group A: elders (age >= elder_threshold) are kept, transmit knowledge.
#   Group B: elders discarded at elder_threshold; no knowledge transfer.
# Environmental shocks test whether accumulated knowledge reduces mortality.

import random, json, math, sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).parent
RESULTS_DIR = HERE / "results"

# ---------------------------------------------------------------------------
# CONFIGURATION  (mirrors config.yaml; loaded below if PyYAML present)
# ---------------------------------------------------------------------------

CFG = {
    "n_generations": 1000,
    "population_size": 200,
    "n_runs": 30,
    "rng_seed": 42,
    "max_age": 80,
    "reproductive_age_min": 15,
    "reproductive_age_max": 45,
    "elder_threshold": 55,
    "base_fertility": 0.04,
    "base_mortality": 0.015,
    "knowledge_half_life": 12,
    "elder_transmission_rate": 0.30,
    "knowledge_survival_bonus": 0.60,
    "initial_knowledge": 1.0,
    "shock_probability": 0.05,
    "shock_severity": 0.40,
    "elder_survival_weight_a": 1.0,
    "elder_survival_weight_b": 0.0,
    "survival_threshold_advantage": 0.30,
}


# ---------------------------------------------------------------------------
# AGENT
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    age: float
    knowledge: float


# ---------------------------------------------------------------------------
# GROUP SIMULATION
# ---------------------------------------------------------------------------

def init_population(n, cfg, rng):
    return [Agent(age=rng.uniform(0, cfg["max_age"] * 0.6),
                  knowledge=cfg["initial_knowledge"]) for _ in range(n)]


def step(agents, cfg, elder_weight, transfer_active, rng):
    new_agents = []
    # knowledge decay
    decay = math.exp(-1 / cfg["knowledge_half_life"])

    for a in agents:
        a.age += 1
        a.knowledge *= decay

    # elder transmission
    elders = [a for a in agents if a.age >= cfg["elder_threshold"]]
    young = [a for a in agents if a.age < cfg["elder_threshold"]]

    if transfer_active and elders and young:
        for a in young:
            if rng.random() < cfg["elder_transmission_rate"]:
                donor = rng.choice(elders)
                a.knowledge = min(1.0, a.knowledge + donor.knowledge * 0.5)

    # group knowledge (mean)
    group_k = sum(a.knowledge for a in agents) / max(len(agents), 1)

    # environmental shock
    shock = rng.random() < cfg["shock_probability"]
    survivors = []
    for a in agents:
        # base mortality
        mort = cfg["base_mortality"]
        # elder discard
        if a.age >= cfg["elder_threshold"] and elder_weight == 0.0:
            mort = 1.0  # discarded
        # shock mortality (reduced by group knowledge)
        if shock:
            shock_mort = cfg["shock_severity"] * (1.0 - group_k * cfg["knowledge_survival_bonus"])
            mort = 1.0 - (1.0 - mort) * (1.0 - shock_mort)
        if rng.random() > mort:
            survivors.append(a)

    # reproduction
    reproductors = [a for a in survivors
                    if cfg["reproductive_age_min"] <= a.age <= cfg["reproductive_age_max"]]
    for a in reproductors:
        if rng.random() < cfg["base_fertility"]:
            child_k = a.knowledge * 0.3  # partial inheritance
            survivors.append(Agent(age=0, knowledge=child_k))

    return survivors


def run_group(elder_weight, transfer_active, cfg, rng):
    agents = init_population(cfg["population_size"], cfg, rng)
    for gen in range(cfg["n_generations"]):
        agents = step(agents, cfg, elder_weight, transfer_active, rng)
        if not agents:
            return 0  # extinct
    return len(agents)


# ---------------------------------------------------------------------------
# RUNNER
# ---------------------------------------------------------------------------

def run(verbose=False):
    cfg = CFG
    results_a, results_b = [], []

    for run_i in range(cfg["n_runs"]):
        rng = random.Random(cfg["rng_seed"] + run_i)
        rng_b = random.Random(cfg["rng_seed"] + run_i + 10000)

        pop_a = run_group(cfg["elder_survival_weight_a"], True, cfg, rng)
        pop_b = run_group(cfg["elder_survival_weight_b"], False, cfg, rng_b)

        results_a.append(pop_a)
        results_b.append(pop_b)
        if verbose:
            print(f"run {run_i+1:02d}  A={pop_a:4d}  B={pop_b:4d}")

    mean_a = sum(results_a) / len(results_a)
    mean_b = sum(results_b) / len(results_b)
    advantage = (mean_a - mean_b) / max(mean_b, 1)
    extinct_a = results_a.count(0)
    extinct_b = results_b.count(0)

    supported = advantage >= cfg["survival_threshold_advantage"]

    verdict = {
        "claim": "3-elder-survival-advantage",
        "n_runs": cfg["n_runs"],
        "n_generations": cfg["n_generations"],
        "mean_final_pop_A_elders_valued": round(mean_a, 1),
        "mean_final_pop_B_elders_discarded": round(mean_b, 1),
        "survival_advantage_ratio": round(advantage, 3),
        "threshold": cfg["survival_threshold_advantage"],
        "extinct_runs_A": extinct_a,
        "extinct_runs_B": extinct_b,
        "supported": supported,
        "notes": "advantage = (mean_A - mean_B) / mean_B. Positive = elders-valued group survives better.",
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "raw_results.json").write_text(
        json.dumps({"group_a": results_a, "group_b": results_b}, indent=2))
    (RESULTS_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    return verdict


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    run(verbose=verbose)
