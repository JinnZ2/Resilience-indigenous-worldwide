"""
monte_carlo_resilience_sim.py

Stochastic comparison of two response architectures under randomized
crisis scenarios:

  A) Distributed framework: local autonomous response with scope-audit
     governance (the modules in this metrology stack).
  B) Centralized system: permission-gated response, no local agency.

## Methodology

Run N iterations. Each iteration samples a crisis (type, severity,
timing) and community/system parameters (initial morale, local
capacity, central capacity, response latency, etc). Both architectures
face the same sampled crisis with their respective response logic.
Measure outcomes: survival rate, infrastructure preservation, social
cohesion, cascade failures, trust, cost, recovery time.

## Falsifiability

The result is reproducible: same random seed -> same outcomes. Change
the parameter distributions, the response logic, or the scoring
functions and rerun. If the distributed framework's advantage
disappears under your modifications, that's the data point -- you've
found a regime where it doesn't help, or where the model assumptions
were doing the work.

## Limitations (named explicitly)

  - audit integrity assumed (real-world capture not modeled)
  - community willingness assumed (learned helplessness baseline only)
  - no external prohibition (state suppression of local response unmodeled)
  - communication infrastructure assumed intact
  - small-community dynamics; city-scale not validated

License: CC0
Stdlib only.
"""

import random
import statistics
import math
from dataclasses import dataclass, field
from collections import Counter

# -----------------------------------------------------------
# 1. Crisis types and severity sampling
# -----------------------------------------------------------

CRISIS_TYPES = [
    "weather_grid_failure",
    "economic_shock",
    "supply_chain_break",
    "corporate_withdrawal",
    "infrastructure_failure",
    "public_health_event",
    "regulatory_collapse",
]


@dataclass
class Crisis:
    crisis_type: str
    severity: float          # 0.0 = trivial, 1.0 = catastrophic
    duration_days: float
    overlapping_crises: int  # how many other crises co-occur


def sample_crisis(rng: random.Random) -> Crisis:
    return Crisis(
        crisis_type=rng.choice(CRISIS_TYPES),
        severity=max(0.0, min(1.0, rng.betavariate(2.0, 3.0))),
        duration_days=rng.uniform(1.0, 45.0),
        overlapping_crises=rng.choices(
            [0, 1, 2, 3], weights=[0.55, 0.25, 0.15, 0.05])[0],
    )


# -----------------------------------------------------------
# 2. Community / system parameter sampling
# -----------------------------------------------------------

@dataclass
class Community:
    morale: float              # 0..1
    local_capacity: float      # 0..1 (skills, supplies, leadership)
    cohesion: float            # 0..1 baseline social bonds
    audit_transparency: float  # 0..1 (how rigorously can locals document)


@dataclass
class CentralAuthority:
    response_latency_days: float
    capacity: float            # 0..1
    geographic_reach: float    # fraction of communities reachable in window


def sample_community(rng: random.Random) -> Community:
    return Community(
        morale=rng.betavariate(5.0, 3.0),
        local_capacity=rng.betavariate(3.0, 3.0),
        cohesion=rng.betavariate(4.0, 3.0),
        audit_transparency=rng.betavariate(3.0, 2.5),
    )


def sample_central(rng: random.Random) -> CentralAuthority:
    return CentralAuthority(
        response_latency_days=rng.uniform(3.0, 30.0),
        capacity=rng.betavariate(2.5, 2.5),
        geographic_reach=rng.betavariate(2.0, 3.0),
    )


# -----------------------------------------------------------
# 3. Outcome model
# -----------------------------------------------------------

@dataclass
class Outcome:
    survival: float            # fraction of community functional post-crisis
    infrastructure_intact: float
    cohesion_post: float
    cascade_failures: int
    trust_post: float          # 0..1 institutional trust
    recovery_days: float
    cost_usd: float


def run_distributed(crisis: Crisis, community: Community,
                    rng: random.Random) -> Outcome:
    """
    Distributed framework: communities respond immediately using local
    capacity + cohesion + transparency. Audit is post-hoc.
    """
    effective_response = (
        0.55 * community.local_capacity
        + 0.30 * community.cohesion
        + 0.15 * community.audit_transparency
    )
    severity_load = crisis.severity * (1.0 + 0.25 * crisis.overlapping_crises)
    survival = max(0.0, min(1.0,
        1.0 - severity_load * (1.0 - effective_response) - rng.gauss(0, 0.05)
    ))
    infrastructure = max(0.0, min(1.0,
        1.0 - 0.85 * severity_load * (1.0 - effective_response * 0.9)
        - rng.gauss(0, 0.06)
    ))
    cohesion_post = max(0.0, min(1.0,
        community.cohesion + 0.15 * effective_response - 0.3 * severity_load
        + rng.gauss(0, 0.05)
    ))
    # cascades: local response usually contains them
    cascade_p = max(0.0, min(1.0,
        0.35 * severity_load - 0.6 * effective_response))
    cascade_failures = sum(1 for _ in range(4) if rng.random() < cascade_p)

    trust_post = max(0.0, min(1.0,
        0.45 + 0.45 * effective_response - 0.25 * severity_load
        + rng.gauss(0, 0.05)
    ))
    recovery = max(1.0,
        crisis.duration_days * 0.4 * (1.0 + severity_load)
        * (1.0 - 0.55 * effective_response)
        + rng.gauss(0, 4.0)
    )
    cost = max(0.0,
        180_000.0 + 600_000.0 * severity_load * (1.0 - 0.55 * effective_response)
        + rng.gauss(0, 80_000.0)
    )
    return Outcome(survival, infrastructure, cohesion_post,
                   cascade_failures, trust_post, recovery, cost)


def run_centralized(crisis: Crisis, central: CentralAuthority,
                    community: Community, rng: random.Random) -> Outcome:
    """
    Centralized: response delayed by latency. Locals forbidden to act.
    Damage propagates while waiting. Reach matters because central
    can't be everywhere at once.
    """
    # how much damage propagates before central arrives
    propagation_window = central.response_latency_days / 30.0  # normalize
    severity_load = crisis.severity * (1.0 + 0.25 * crisis.overlapping_crises)
    # community sits in helplessness during the wait
    helplessness_decay = 0.6 * propagation_window  # morale erodes

    effective_response = (
        central.capacity * central.geographic_reach
        * max(0.0, 1.0 - 0.5 * propagation_window)
    )

    survival = max(0.0, min(1.0,
        1.0 - severity_load * (1.0 - effective_response)
        - 0.25 * propagation_window
        - rng.gauss(0, 0.07)
    ))
    infrastructure = max(0.0, min(1.0,
        1.0 - severity_load * (1.0 - effective_response * 0.7)
        - 0.20 * propagation_window
        - rng.gauss(0, 0.08)
    ))
    cohesion_post = max(0.0, min(1.0,
        community.cohesion - 0.35 * severity_load
        - 0.25 * helplessness_decay
        + rng.gauss(0, 0.06)
    ))
    cascade_p = max(0.0, min(1.0,
        0.55 * severity_load + 0.30 * propagation_window
        - 0.35 * effective_response))
    cascade_failures = sum(1 for _ in range(5) if rng.random() < cascade_p)

    trust_post = max(0.0, min(1.0,
        0.35 - 0.45 * propagation_window + 0.30 * effective_response
        - 0.20 * severity_load + rng.gauss(0, 0.06)
    ))
    recovery = max(1.0,
        crisis.duration_days * 1.4 * (1.0 + severity_load)
        * (1.0 - 0.30 * effective_response)
        + central.response_latency_days * 1.6
        + rng.gauss(0, 12.0)
    )
    cost = max(0.0,
        900_000.0 + 1_800_000.0 * severity_load * (1.0 - 0.30 * effective_response)
        + 60_000.0 * central.response_latency_days
        + rng.gauss(0, 200_000.0)
    )
    return Outcome(survival, infrastructure, cohesion_post,
                   cascade_failures, trust_post, recovery, cost)


# -----------------------------------------------------------
# 4. Simulation driver
# -----------------------------------------------------------

@dataclass
class SimResults:
    distributed: list[Outcome] = field(default_factory=list)
    centralized: list[Outcome] = field(default_factory=list)


def simulate(n_iterations: int, seed: int = 42) -> SimResults:
    rng = random.Random(seed)
    results = SimResults()
    for _ in range(n_iterations):
        crisis = sample_crisis(rng)
        community = sample_community(rng)
        central = sample_central(rng)
        # both architectures face the same crisis & community
        d_out = run_distributed(crisis, community,
                                random.Random(rng.random()))
        c_out = run_centralized(crisis, central, community,
                                random.Random(rng.random()))
        results.distributed.append(d_out)
        results.centralized.append(c_out)
    return results


# -----------------------------------------------------------
# 5. Outcome aggregation and comparison
# -----------------------------------------------------------

def summarize(outcomes: list[Outcome]) -> dict:
    survivals = [o.survival for o in outcomes]
    infra = [o.infrastructure_intact for o in outcomes]
    cohesion = [o.cohesion_post for o in outcomes]
    cascades = [o.cascade_failures for o in outcomes]
    trust = [o.trust_post for o in outcomes]
    recovery = [o.recovery_days for o in outcomes]
    cost = [o.cost_usd for o in outcomes]
    return {
        "survival_mean": statistics.mean(survivals),
        "survival_median": statistics.median(survivals),
        "survival_std": statistics.stdev(survivals) if len(survivals) > 1 else 0,
        "infra_mean": statistics.mean(infra),
        "cohesion_mean": statistics.mean(cohesion),
        "cascade_mean": statistics.mean(cascades),
        "cascade_zero_rate": sum(1 for c in cascades if c == 0) / len(cascades),
        "trust_mean": statistics.mean(trust),
        "recovery_mean_days": statistics.mean(recovery),
        "recovery_median_days": statistics.median(recovery),
        "cost_mean_usd": statistics.mean(cost),
        "cost_median_usd": statistics.median(cost),
        "p05_survival": sorted(survivals)[max(0, int(0.05 * len(survivals)) - 1)],
    }


def compare(results: SimResults) -> dict:
    d = summarize(results.distributed)
    c = summarize(results.centralized)
    delta = {
        "survival_delta_pct_points": (d["survival_mean"] - c["survival_mean"]) * 100,
        "infra_delta_pct_points": (d["infra_mean"] - c["infra_mean"]) * 100,
        "cohesion_delta_pct_points": (d["cohesion_mean"] - c["cohesion_mean"]) * 100,
        "cascade_delta": d["cascade_mean"] - c["cascade_mean"],
        "trust_delta_pct_points": (d["trust_mean"] - c["trust_mean"]) * 100,
        "recovery_speedup_days": c["recovery_mean_days"] - d["recovery_mean_days"],
        "cost_savings_usd": c["cost_mean_usd"] - d["cost_mean_usd"],
    }
    return {"distributed": d, "centralized": c, "delta": delta}


# -----------------------------------------------------------
# 6. Sensitivity test: which variables move outcomes?
# -----------------------------------------------------------

def correlate(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


# -----------------------------------------------------------
# 7. Falsifiable claims
# -----------------------------------------------------------

CLAIMS = [
    "Distributed framework survival rate exceeds centralized by >15 percentage points across stochastic crisis distributions.",
    "Zero-cascade rate is materially higher under distributed response (>2x centralized).",
    "Recovery time and cost are bounded under distributed; unbounded tails appear under centralized.",
    "Trust recovery is faster under distributed because communities see their action validated post-hoc.",
    "Tail-risk worst 5% of distributed outcomes still beats median centralized outcomes on multiple axes.",
    "Sensitivity differs: distributed depends most on local capacity; centralized depends most on response latency.",
    "Results are reproducible: same seed yields same outcomes; the framework is falsifiable, not rhetorical.",
]


# -----------------------------------------------------------
# 8. Demo run
# -----------------------------------------------------------

if __name__ == "__main__":
    N = 5000
    print(f"Running Monte Carlo: {N} iterations, seed=42, stdlib only")
    print()
    results = simulate(n_iterations=N, seed=42)
    comp = compare(results)

    print("=" * 70)
    print("DISTRIBUTED FRAMEWORK")
    print("=" * 70)
    for k, v in comp["distributed"].items():
        if "cost" in k:
            print(f"  {k:30s} = ${v:>14,.0f}")
        elif "days" in k:
            print(f"  {k:30s} = {v:>9.2f}")
        else:
            print(f"  {k:30s} = {v:>9.4f}")

    print("\n" + "=" * 70)
    print("CENTRALIZED SYSTEM")
    print("=" * 70)
    for k, v in comp["centralized"].items():
        if "cost" in k:
            print(f"  {k:30s} = ${v:>14,.0f}")
        elif "days" in k:
            print(f"  {k:30s} = {v:>9.2f}")
        else:
            print(f"  {k:30s} = {v:>9.4f}")

    print("\n" + "=" * 70)
    print("DELTA (distributed - centralized)")
    print("=" * 70)
    for k, v in comp["delta"].items():
        if "usd" in k:
            print(f"  {k:30s} = ${v:>+14,.0f}")
        else:
            print(f"  {k:30s} = {v:>+9.2f}")

    # sensitivity: correlate community.local_capacity with survival
    # (need to re-sample to get the parameter alongside outcomes)
    print("\n" + "=" * 70)
    print("SENSITIVITY (correlations across runs)")
    print("=" * 70)
    rng = random.Random(42)
    capacity_samples, survival_samples = [], []
    latency_samples, cent_survival_samples = [], []
    for _ in range(N):
        crisis = sample_crisis(rng)
        community = sample_community(rng)
        central = sample_central(rng)
        d_out = run_distributed(crisis, community, random.Random(rng.random()))
        c_out = run_centralized(crisis, central, community, random.Random(rng.random()))
        capacity_samples.append(community.local_capacity)
        survival_samples.append(d_out.survival)
        latency_samples.append(central.response_latency_days)
        cent_survival_samples.append(c_out.survival)

    print(f"  distributed: local_capacity vs survival    r = "
          f"{correlate(capacity_samples, survival_samples):+.3f}")
    print(f"  centralized: response_latency vs survival  r = "
          f"{correlate(latency_samples, cent_survival_samples):+.3f}")
    print()
    print("Reproducibility: rerun with same seed for identical results.")
    print("Modify parameter distributions or response functions to test")
    print("regimes where the distributed advantage may diminish.")
