"""The shared law across biological, cognitive, and institutional domains.

The pattern is hormetic and substrate-general. For a given capacity
axis and a given stressor along that axis:

  - zero stress      => atrophy along the axis (the capacity is not built)
  - bounded stress   => capacity gain along the axis, peaking near an
                        organism- or domain-specific optimum dose
  - excessive stress => damage, potentially irreversible

The audit's claim is that this law applies across substrates -- bone,
muscle, immune system, cognitive faculty, social network, community
infrastructure -- and that institutional measurement which tests only
at the unstressed baseline cannot see the capacity that constraint
built. Equivalently: protected populations are not the natural
reference; they are the structurally atrophied tail of the dose curve.
"""

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass
class HormeticCurve:
    name: str
    optimal_dose: float
    sensitivity: float
    injury_threshold: float
    atrophy_floor: float = -0.2

    def response(self, dose: float) -> float:
        if dose <= 0:
            return self.atrophy_floor
        if dose <= self.optimal_dose:
            return self.atrophy_floor + (1.0 - self.atrophy_floor) * (dose / self.optimal_dose)
        if dose <= self.injury_threshold:
            span = self.injury_threshold - self.optimal_dose
            return 1.0 - (dose - self.optimal_dose) / span
        overshoot = dose - self.injury_threshold
        return max(-1.0, -overshoot / self.sensitivity)


DOMAINS = {
    "bone (Wolff's law)":            HormeticCurve("bone",      1.0, 0.7, 3.0),
    "muscle (supercompensation)":    HormeticCurve("muscle",    0.8, 0.6, 2.5),
    "immune (vaccination/exposure)": HormeticCurve("immune",    0.3, 0.4, 2.0),
    "cognition (constraint)":        HormeticCurve("cognition", 0.6, 0.5, 2.0),
    "social network (mutual aid)":   HormeticCurve("social",    0.7, 0.6, 2.5),
    "community infrastructure":      HormeticCurve("infra",     0.5, 0.5, 2.5),
    "plant (drought priming)":       HormeticCurve("plant",     0.5, 0.4, 2.2),
}


def domain_sweep(name: str, doses: Iterable[float]) -> List[Tuple[float, float]]:
    curve = DOMAINS[name]
    return [(d, curve.response(d)) for d in doses]


def shared_law_summary() -> str:
    return (
        "Across substrates the same triangular hormetic shape holds:\n"
        "  - zero stress along an axis  =>  atrophy along that axis\n"
        "  - bounded stress at optimum  =>  capacity gain\n"
        "  - stress above tolerance     =>  damage, sometimes irreversible\n"
        "Measurement at the unstressed baseline therefore systematically\n"
        "under-reports capacity in populations exposed to bounded stress\n"
        "and over-reports capacity in populations protected from it."
    )


def print_curve(name: str, dose_max: float = None, n: int = 21):
    curve = DOMAINS[name]
    if dose_max is None:
        dose_max = curve.injury_threshold + 0.5
    step = dose_max / (n - 1)
    print(f"\n  {name}")
    print(f"    optimum dose {curve.optimal_dose:.2f}   injury threshold {curve.injury_threshold:.2f}")
    print(f"    {'dose':>6}  {'response':>8}  bar")
    for i in range(n):
        d = i * step
        r = curve.response(d)
        bar_list = [" "] * 51
        bar_list[25] = "|"
        bar_pos = int(round((r + 1.0) * 25))
        bar_pos = max(0, min(50, bar_pos))
        bar_list[bar_pos] = "*"
        bar = "".join(bar_list)
        print(f"    {d:6.2f}  {r:+8.2f}  {bar}")


def equivalent_doses_for_capacity(target_capacity: float) -> List[Tuple[str, float, float]]:
    """For each domain, find the two doses that hit a given capacity level."""
    rows = []
    for name, curve in DOMAINS.items():
        if target_capacity > 1.0 or target_capacity < curve.atrophy_floor:
            continue
        # Rising arm: dose where response == target on [0, optimal]
        lo = (target_capacity - curve.atrophy_floor) * curve.optimal_dose / (1.0 - curve.atrophy_floor)
        # Falling arm: dose where response == target on [optimal, injury]
        if target_capacity >= 0:
            hi = curve.optimal_dose + (1.0 - target_capacity) * (curve.injury_threshold - curve.optimal_dose)
        else:
            hi = curve.injury_threshold + (-target_capacity) * curve.sensitivity
        rows.append((name, lo, hi))
    return rows


if __name__ == "__main__":
    print("CROSS-DOMAIN PATTERN  --  the shared law")
    print("=" * 76)
    print(shared_law_summary())
    print()

    print("Domain hormetic parameters:")
    print("-" * 76)
    print(f"  {'domain':38s}  {'optimum':>8}  {'injury>':>8}  {'atrophy':>8}")
    for name, curve in DOMAINS.items():
        print(f"  {name:38s}  {curve.optimal_dose:>8.2f}  {curve.injury_threshold:>8.2f}  {curve.atrophy_floor:>+8.2f}")

    print()
    print("Sample curve: cognition under constraint")
    print("-" * 76)
    print_curve("cognition (constraint)", dose_max=2.5, n=13)

    print()
    print("Sample curve: bone under loading")
    print("-" * 76)
    print_curve("bone (Wolff's law)", dose_max=3.5, n=13)

    print()
    print("Doses producing capacity = 0.50 in each domain:")
    print("-" * 76)
    print(f"  {'domain':38s}  {'low-dose':>8}  {'high-dose':>9}")
    for name, lo, hi in equivalent_doses_for_capacity(0.50):
        print(f"  {name:38s}  {lo:>8.2f}  {hi:>9.2f}")
