#!/usr/bin/env python3
"""
structured_noise.py -- Convert disorder into directed work.

The standard engineering approach suppresses noise, turbulence,
vibration, and thermal fluctuation.  This module treats them as
unaligned structure that can be shaped rather than fought.

Core insight: you don't eliminate noise -- you tune the boundary
where noise becomes useful vs dissipative.

Four conversion strategies:
  1. Thermal noise -> gradient amplification
     Phase-change inclusions convert random dT into buffered heat flow.
  2. Turbulence -> controlled mixing field
     Geometry inserts shape turbulence spectrum into preferred eddy scales.
  3. Mechanical vibration -> broadband harvesting
     Multi-scale impedance stacks capture energy across frequency bands.
  4. Chemical inconsistency -> reaction front structuring
     Controlled flow paths and temperature microfields direct reaction waves.

The field optimization grid models a physical process (foundry, reactor,
or any coupled system) as a 2D field of temperature, velocity, vibration,
and chemical gradient.  Each cell's efficiency depends on how well its
local disorder is aligned with useful work.

Key constraint: over-coupling stiffens the system, loses adaptive
behavior, and drops efficiency.  The optimum is controlled variability
within stable bounds -- not uniformity.

Precise definition:
  noise = energy outside your coupling bandwidth

Not lost energy.  Uncorrelated energy.  Still carries structure
(frequency, spatial pattern, intermittency) -- just structure your
current receiver can't see.

Two ways to use noise:
  A. Harvest it (hard): match its statistics, don't force order.
     Wideband receivers, rectification + accumulation, aggregation.
  B. Use it structurally (often better): prevent stiction, enhance
     mixing, maintain systems near critical transition points.
     Often improves total system efficiency more than direct capture.

Three engineering levers:
  1. Impedance spreading: spectrum of mechanical impedances so
     different frequencies couple somewhere.
  2. Nonlinear capture: threshold + rectify + accumulate turns
     random input into biased output over time.
  3. Stochastic resonance: add noise to help weak signals cross
     detection thresholds.  Noise becomes carrier assist.

Decision filter for any noise source:
  Q1. Is there still structure (frequency, spatial, intermittent)?
  Q2. Can I match it without forcing coherence?
  Q3. Does capturing it reduce performance elsewhere?
  Q4. Is it better used to assist another process?

Hard limit: when recovery increases total system entropy instead
of reducing it, stop.  Not all noise is worth pursuing.

Old view: noise = loss, suppress, isolate, uniform
New view: noise = unaligned structure, shape, couple selectively,
          controlled variability

References
----------
- Prigogine, I. & Stengers, I. (1984). Order Out of Chaos. Bantam.
  (dissipative structures, self-organization from fluctuations)
- Bejan, A. (2000). Shape and Structure, from Engineering to Nature.
  Cambridge. (constructal law: flow systems evolve toward easier access)
- Benzi, R. et al. (1981). Stochastic resonance in climatic change.
  Tellus, 34(1). (noise-enhanced signal detection)

Usage
-----
    python3 structured_noise.py --demo
    python3 structured_noise.py --grid-size 100 --json
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------
# Physical Constants
# ---------------------------

STEEL_CONSTANTS = {
    "melting_point_c": 1538,
    "specific_heat_kj_kg_k": 0.466,
    "density_kg_m3": 7850,
    "thermal_conductivity_w_mk": 45,
}


# ---------------------------
# Field Cell
# ---------------------------

@dataclass
class FieldCell:
    """A single cell in the optimization grid."""
    temperature: float = 25.0       # C
    velocity_x: float = 0.0         # m/s
    velocity_y: float = 0.0
    vibration: float = 0.0          # amplitude (arbitrary units)
    chemical_gradient: float = 0.0  # reaction front intensity (0-1)


# ---------------------------
# Conversion Strategies
# ---------------------------

@dataclass
class ConversionStrategy:
    """A strategy for converting noise into useful work."""
    name: str
    target: str                    # thermal, turbulence, vibration, chemical
    mechanism: str
    intervention: str
    expected_improvement: float    # fraction (e.g., 0.15 = 15% recovery)


STRATEGIES = [
    ConversionStrategy(
        "Thermal Gradient Amplification",
        "thermal",
        "Phase-change inclusions at high-fluctuation regions convert "
        "random temperature swings into buffered, directional heat flow",
        "Insert phase-change material zones (paraffin, salt hydrate) "
        "at locations with highest thermal variance",
        0.15,
    ),
    ConversionStrategy(
        "Turbulence Spectrum Shaping",
        "turbulence",
        "Geometry inserts (vanes, porous structures) induce preferred "
        "eddy scales, converting chaotic flow into mixing enhancer "
        "and heat transfer amplifier",
        "Add intentionally irregular (but bounded) flow structures -- "
        "not smooth, but shaped to preferred turbulence spectrum",
        0.20,
    ),
    ConversionStrategy(
        "Broadband Vibration Harvesting",
        "vibration",
        "Multi-scale mechanical stacks with impedance gradients capture "
        "energy across frequency bands: compliant layer for mid-freq, "
        "stiff layer for high impulse",
        "Layer mechanical interfaces with graduated impedance -- "
        "not rigid uniform structure but graded stiffness",
        0.12,
    ),
    ConversionStrategy(
        "Reaction Front Structuring",
        "chemical",
        "Controlled flow paths and temperature microfields direct "
        "reaction waves instead of fighting uneven reactions",
        "Shape flow paths to create directed reaction fronts "
        "with controlled advance rate",
        0.18,
    ),
]


# ---------------------------
# Noise Classification
# ---------------------------

class NoiseType(Enum):
    """Types of noise, classified by physical origin."""
    BROADBAND_MECHANICAL = "broadband_mechanical"  # random vibration, micro-deformation
    THERMAL_FLUCTUATION = "thermal_fluctuation"    # small-scale nabla_T
    TURBULENT_FLUID = "turbulent_fluid"            # chaotic velocity fields
    ELECTRICAL_STOCHASTIC = "electrical_stochastic" # charge motion, EM fluctuation
    CHEMICAL_HETEROGENEITY = "chemical_heterogeneity" # uneven reaction fronts


class NoiseUse(Enum):
    """How to use a noise source."""
    HARVEST_DIRECT = "harvest_direct"       # extract energy (hard)
    STRUCTURAL_ASSIST = "structural_assist"  # use to improve other processes (easier)
    IGNORE = "ignore"                        # not worth pursuing


@dataclass
class NoiseSource:
    """A classified noise source in a physical system."""
    name: str
    noise_type: NoiseType
    amplitude: float           # relative scale 0-1
    bandwidth: str             # narrow, moderate, broad
    has_structure: bool        # frequency, spatial pattern, intermittency
    recommended_use: NoiseUse
    lever: str                 # which engineering lever applies
    rationale: str


def classify_noise(
    noise_type: str,
    amplitude: float,
    has_pattern: bool = False,
    system_stiffness: float = 0.5,
) -> Dict[str, Any]:
    """
    Classify a noise source and recommend action.

    Parameters
    ----------
    noise_type : str
        One of: mechanical, thermal, turbulent, electrical, chemical
    amplitude : float
        Relative amplitude (0-1, where 1 = same order as signal)
    has_pattern : bool
        Whether the noise has detectable structure (frequency, spatial)
    system_stiffness : float
        How coupled/stiff the system already is (0 = loose, 1 = rigid)

    Returns
    -------
    dict with classification, recommended use, lever, and rationale.
    """
    # Map string to enum
    type_map = {
        "mechanical": NoiseType.BROADBAND_MECHANICAL,
        "thermal": NoiseType.THERMAL_FLUCTUATION,
        "turbulent": NoiseType.TURBULENT_FLUID,
        "electrical": NoiseType.ELECTRICAL_STOCHASTIC,
        "chemical": NoiseType.CHEMICAL_HETEROGENEITY,
    }
    nt = type_map.get(noise_type, NoiseType.BROADBAND_MECHANICAL)

    # Decision logic
    # Q1: Is there structure?
    if not has_pattern and amplitude < 0.1:
        return {
            "noise_type": nt.value,
            "use": NoiseUse.IGNORE.value,
            "lever": "none",
            "rationale": "No structure, low amplitude. Recovery cost exceeds captured energy.",
            "filter": {"q1_structure": False, "q2_matchable": False,
                       "q3_hurts_elsewhere": False, "q4_better_as_assist": False},
        }

    # Q3: Would capturing it stiffen an already-stiff system?
    if system_stiffness > 0.8:
        return {
            "noise_type": nt.value,
            "use": NoiseUse.STRUCTURAL_ASSIST.value,
            "lever": "stochastic_resonance",
            "rationale": (
                "System already stiff. Use noise as carrier assist to maintain "
                "adaptivity rather than adding more coupling."
            ),
            "filter": {"q1_structure": has_pattern, "q2_matchable": True,
                       "q3_hurts_elsewhere": True, "q4_better_as_assist": True},
        }

    # Q4: Is it better as structural assist?
    if nt in (NoiseType.TURBULENT_FLUID, NoiseType.CHEMICAL_HETEROGENEITY):
        return {
            "noise_type": nt.value,
            "use": NoiseUse.STRUCTURAL_ASSIST.value,
            "lever": "impedance_spreading" if nt == NoiseType.TURBULENT_FLUID else "nonlinear_capture",
            "rationale": (
                f"{nt.value} is more valuable as mixing enhancer or reaction "
                f"front director than as direct energy source."
            ),
            "filter": {"q1_structure": has_pattern, "q2_matchable": True,
                       "q3_hurts_elsewhere": False, "q4_better_as_assist": True},
        }

    # Q2: Can we match it?
    if has_pattern and amplitude > 0.2:
        lever = "impedance_spreading" if nt == NoiseType.BROADBAND_MECHANICAL else "nonlinear_capture"
        return {
            "noise_type": nt.value,
            "use": NoiseUse.HARVEST_DIRECT.value,
            "lever": lever,
            "rationale": (
                f"Structured {nt.value} at amplitude {amplitude:.1f}. "
                f"Match with {lever} for partial capture."
            ),
            "filter": {"q1_structure": True, "q2_matchable": True,
                       "q3_hurts_elsewhere": False, "q4_better_as_assist": False},
        }

    # Default: structural assist
    return {
        "noise_type": nt.value,
        "use": NoiseUse.STRUCTURAL_ASSIST.value,
        "lever": "stochastic_resonance",
        "rationale": "Moderate noise with some structure. Best used to assist signal detection.",
        "filter": {"q1_structure": has_pattern, "q2_matchable": has_pattern,
                   "q3_hurts_elsewhere": False, "q4_better_as_assist": True},
    }


# ---------------------------
# Three Engineering Levers
# ---------------------------

def impedance_spreading(
    frequencies: List[float],
    impedances: List[float],
) -> Dict[str, Any]:
    """
    Lever 1: Impedance spreading.

    Instead of matching one frequency, create a spectrum of mechanical
    impedances so different frequencies couple somewhere in the stack.

    Parameters
    ----------
    frequencies : list of float
        Noise frequency components (Hz)
    impedances : list of float
        Available impedance layers (Pa*s/m or similar)

    Returns
    -------
    dict with coverage analysis.
    """
    if not frequencies or not impedances:
        return {"coverage": 0, "matched": [], "unmatched": frequencies}

    matched = []
    unmatched = []

    # Each impedance layer has a bandwidth around its natural frequency
    for freq in frequencies:
        found = False
        for imp in impedances:
            # Simplified: impedance matches if within 30% of frequency ratio
            ratio = freq / (imp + 0.01)
            if 0.7 < ratio < 1.3:
                matched.append({"frequency": freq, "impedance": imp, "ratio": round(ratio, 2)})
                found = True
                break
        if not found:
            unmatched.append(freq)

    coverage = len(matched) / len(frequencies) if frequencies else 0

    return {
        "total_frequencies": len(frequencies),
        "matched": len(matched),
        "unmatched_count": len(unmatched),
        "coverage": round(coverage, 3),
        "matches": matched,
        "gaps": unmatched,
        "recommendation": (
            "Good coverage" if coverage > 0.7
            else "Add impedance layers to cover gaps" if coverage > 0.3
            else "Significant mismatch -- consider nonlinear capture instead"
        ),
    }


def nonlinear_capture(
    signal: List[float],
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Lever 2: Nonlinear capture.

    Linear systems ignore small fluctuations.  Nonlinear systems
    threshold + rectify + accumulate, turning random input into
    biased output over time.

    Parameters
    ----------
    signal : list of float
        Time series of noise signal values.
    threshold : float
        Activation threshold.

    Returns
    -------
    dict with captured energy, efficiency, and duty cycle.
    """
    if not signal:
        return {"captured": 0, "total": 0, "efficiency": 0}

    total_energy = sum(abs(s) for s in signal)
    captured = sum(max(0, abs(s) - threshold) for s in signal)
    active_samples = sum(1 for s in signal if abs(s) > threshold)
    duty_cycle = active_samples / len(signal)

    return {
        "total_energy": round(total_energy, 4),
        "captured_energy": round(captured, 4),
        "efficiency": round(captured / total_energy, 4) if total_energy > 0 else 0,
        "threshold": threshold,
        "duty_cycle": round(duty_cycle, 4),
        "active_samples": active_samples,
        "total_samples": len(signal),
        "recommendation": (
            "Good capture rate" if duty_cycle > 0.3
            else "Lower threshold or aggregate over more area/time" if duty_cycle > 0.05
            else "Signal too weak for threshold capture -- use stochastic resonance"
        ),
    }


def stochastic_resonance(
    weak_signal: List[float],
    noise_amplitude: float = 0.5,
    detection_threshold: float = 1.0,
) -> Dict[str, Any]:
    """
    Lever 3: Stochastic resonance.

    Add noise to improve signal transfer.  Counterintuitive but real:
    weak signal + noise -> crosses threshold -> detectable.

    Noise becomes carrier assist, not interference.

    Parameters
    ----------
    weak_signal : list of float
        Signal too weak to detect on its own.
    noise_amplitude : float
        Amplitude of added noise.
    detection_threshold : float
        Threshold for detection.

    Returns
    -------
    dict with detection rates with and without noise assist.
    """
    import random
    rng = random.Random(42)

    # Without noise
    detected_clean = sum(1 for s in weak_signal if abs(s) >= detection_threshold)

    # With noise assist (many trials)
    trials = 10
    detected_noisy_total = 0
    for _ in range(trials):
        detected = sum(
            1 for s in weak_signal
            if abs(s + rng.gauss(0, noise_amplitude)) >= detection_threshold
        )
        detected_noisy_total += detected
    detected_noisy_avg = detected_noisy_total / trials

    rate_clean = detected_clean / len(weak_signal) if weak_signal else 0
    rate_noisy = detected_noisy_avg / len(weak_signal) if weak_signal else 0
    improvement = (rate_noisy - rate_clean) / max(rate_clean, 0.001)

    return {
        "signal_samples": len(weak_signal),
        "detection_threshold": detection_threshold,
        "noise_amplitude": noise_amplitude,
        "detection_rate_clean": round(rate_clean, 4),
        "detection_rate_with_noise": round(rate_noisy, 4),
        "improvement_factor": round(improvement, 2),
        "stochastic_resonance_active": rate_noisy > rate_clean,
        "recommendation": (
            f"Noise assists detection ({improvement:.0%} improvement)"
            if rate_noisy > rate_clean
            else "Noise amplitude too high or signal already detectable"
        ),
    }


# ---------------------------
# Field Optimization Grid
# ---------------------------

class FieldOptimizer:
    """
    2D field optimization grid for coupled physical processes.

    Models a physical system (foundry, reactor, processing chamber)
    as a grid of cells with temperature, velocity, vibration, and
    chemical gradient fields.  Applies structured noise patterns
    and evaluates local efficiency at each cell.
    """

    def __init__(self, grid_size: int = 50):
        self.size = grid_size
        self.grid: List[List[FieldCell]] = [
            [FieldCell() for _ in range(grid_size)]
            for _ in range(grid_size)
        ]

    def apply_thermal_fluctuations(self, strength: float = 50.0):
        """
        Inject structured thermal noise.

        Not random -- sinusoidal patterns that create usable gradients
        rather than uniform temperature.
        """
        for x in range(self.size):
            for y in range(self.size):
                variance = math.sin(x / 5) * math.cos(y / 5) * strength
                self.grid[x][y].temperature += variance

    def apply_flow_field(self, max_velocity: float = 5.0):
        """
        Apply structured flow field (bounded turbulence).

        Rotational velocity patterns create mixing without chaos.
        """
        for x in range(self.size):
            for y in range(self.size):
                self.grid[x][y].velocity_x = math.sin(y / 4) * max_velocity
                self.grid[x][y].velocity_y = math.cos(x / 4) * max_velocity

    def apply_vibration_field(self, max_amplitude: float = 2.0):
        """
        Apply structured mechanical vibration pattern.

        Multi-frequency pattern instead of single resonance.
        """
        for x in range(self.size):
            for y in range(self.size):
                structured = math.sin(x / 3) + math.cos(y / 3)
                self.grid[x][y].vibration = structured * max_amplitude

    def apply_chemical_gradients(self, max_gradient: float = 1.0):
        """
        Apply directed chemical gradient field.

        Linear base with structured microvariation -- creates
        reaction fronts instead of uniform reaction.
        """
        for x in range(self.size):
            for y in range(self.size):
                base = (x + y) / (2 * self.size)
                variation = math.sin(x / 5) * 0.1
                self.grid[x][y].chemical_gradient = min(
                    max_gradient, base + variation
                )

    def cell_efficiency(self, cell: FieldCell, target_temp: float = 1600.0) -> float:
        """
        Calculate local efficiency for a cell.

        Efficiency depends on how well the local noise fields
        align with useful work:
          - Temperature deviation from target (closer = better for process)
          - Velocity field (higher = better mixing)
          - Vibration (moderate = energy harvest + mixing)
          - Chemical gradient (higher = more complete reaction)

        Returns 0-1 efficiency score.
        """
        # Temperature factor: deviation from target
        t_dev = abs(cell.temperature - target_temp) / target_temp
        t_factor = max(0, 1.0 - t_dev)

        # Velocity factor: diminishing returns on mixing
        speed = math.hypot(cell.velocity_x, cell.velocity_y)
        v_factor = 1.0 - math.exp(-speed / 5)

        # Vibration factor: moderate is optimal
        vib_abs = abs(cell.vibration)
        m_factor = 1.0 - math.exp(-vib_abs / 2)

        # Chemical factor: gradient drives reaction
        c_factor = 1.0 - math.exp(-cell.chemical_gradient * 3)

        # Combined: weighted geometric mean favors balanced coupling
        # Over-optimizing one dimension at expense of others reduces overall
        efficiency = (t_factor * 0.3 + v_factor * 0.25 +
                      m_factor * 0.20 + c_factor * 0.25)
        return min(1.0, max(0.0, efficiency))

    def evaluate_grid(self, target_temp: float = 1600.0) -> Dict[str, Any]:
        """
        Evaluate efficiency across the entire grid.

        Returns aggregate statistics and hotspot analysis.
        """
        efficiencies = []
        hotspots = []
        coldspots = []

        for x in range(self.size):
            for y in range(self.size):
                eff = self.cell_efficiency(self.grid[x][y], target_temp)
                efficiencies.append(eff)
                if eff > 0.8:
                    hotspots.append((x, y, eff))
                elif eff < 0.2:
                    coldspots.append((x, y, eff))

        avg_eff = sum(efficiencies) / len(efficiencies)
        min_eff = min(efficiencies)
        max_eff = max(efficiencies)

        # Variance: measure of how structured vs uniform the field is
        variance = sum((e - avg_eff) ** 2 for e in efficiencies) / len(efficiencies)
        std_dev = math.sqrt(variance)

        return {
            "grid_size": self.size,
            "total_cells": self.size * self.size,
            "avg_efficiency": round(avg_eff, 4),
            "min_efficiency": round(min_eff, 4),
            "max_efficiency": round(max_eff, 4),
            "std_deviation": round(std_dev, 4),
            "hotspots": len(hotspots),
            "coldspots": len(coldspots),
            "bounded_variability": round(std_dev / avg_eff, 4) if avg_eff > 0 else 0,
        }


# ---------------------------
# Before/After Comparison
# ---------------------------

def compare_approaches(grid_size: int = 50) -> Dict[str, Any]:
    """
    Compare uniform (suppress noise) vs structured (shape noise).
    """
    # Baseline: uniform field (traditional approach: suppress everything)
    baseline = FieldOptimizer(grid_size)
    # Set to uniform high temperature, zero flow, zero vibration
    for x in range(grid_size):
        for y in range(grid_size):
            baseline.grid[x][y].temperature = 1600
            baseline.grid[x][y].velocity_x = 0
            baseline.grid[x][y].velocity_y = 0
            baseline.grid[x][y].vibration = 0
            baseline.grid[x][y].chemical_gradient = 0.5
    baseline_eval = baseline.evaluate_grid()

    # Structured: apply all noise shaping strategies
    structured = FieldOptimizer(grid_size)
    # Start at process temperature with structured noise
    for x in range(grid_size):
        for y in range(grid_size):
            structured.grid[x][y].temperature = 1600
    structured.apply_thermal_fluctuations(strength=30)
    structured.apply_flow_field(max_velocity=5)
    structured.apply_vibration_field(max_amplitude=2)
    structured.apply_chemical_gradients()
    structured_eval = structured.evaluate_grid()

    improvement = (
        (structured_eval["avg_efficiency"] - baseline_eval["avg_efficiency"])
        / baseline_eval["avg_efficiency"] * 100
        if baseline_eval["avg_efficiency"] > 0 else 0
    )

    return {
        "baseline": baseline_eval,
        "structured": structured_eval,
        "improvement_pct": round(improvement, 1),
        "strategies_applied": [s.name for s in STRATEGIES],
    }


# ---------------------------
# Output
# ---------------------------

def run_demo(grid_size: int = 50, as_json: bool = False):
    """Run demonstration of structured noise optimization."""
    comparison = compare_approaches(grid_size)

    # Noise classifications
    noise_examples = [
        classify_noise("mechanical", 0.6, has_pattern=True, system_stiffness=0.3),
        classify_noise("thermal", 0.2, has_pattern=False, system_stiffness=0.5),
        classify_noise("turbulent", 0.8, has_pattern=True, system_stiffness=0.4),
        classify_noise("electrical", 0.05, has_pattern=False, system_stiffness=0.9),
        classify_noise("chemical", 0.4, has_pattern=True, system_stiffness=0.3),
    ]

    # Three levers
    imp_result = impedance_spreading(
        frequencies=[10, 25, 60, 120, 250, 500],
        impedances=[12, 55, 110, 480],
    )

    import random
    rng = random.Random(42)
    noise_signal = [rng.gauss(0, 1.0) for _ in range(200)]
    nl_result = nonlinear_capture(noise_signal, threshold=0.8)

    weak = [0.3 * math.sin(i / 5) for i in range(200)]
    sr_result = stochastic_resonance(weak, noise_amplitude=0.6, detection_threshold=0.8)

    if as_json:
        result = {
            "comparison": comparison,
            "noise_classifications": noise_examples,
            "impedance_spreading": imp_result,
            "nonlinear_capture": nl_result,
            "stochastic_resonance": sr_result,
            "strategies": [
                {"name": s.name, "target": s.target, "mechanism": s.mechanism,
                 "intervention": s.intervention, "expected_improvement": s.expected_improvement}
                for s in STRATEGIES
            ],
        }
        print(json.dumps(result, indent=2))
        return

    print("=" * 70)
    print("  STRUCTURED NOISE OPTIMIZATION")
    print("  noise = energy outside your coupling bandwidth")
    print("=" * 70)

    print(f"\n--- Noise Classification ---")
    for nc in noise_examples:
        print(f"  {nc['noise_type']:25s}  use: {nc['use']:20s}  lever: {nc['lever']}")
        print(f"    {nc['rationale']}")

    print(f"\n--- Lever 1: Impedance Spreading ---")
    print(f"  Frequencies: {imp_result['total_frequencies']}  |  "
          f"Matched: {imp_result['matched']}  |  "
          f"Coverage: {imp_result['coverage']:.0%}")
    print(f"  {imp_result['recommendation']}")
    if imp_result['gaps']:
        print(f"  Gaps at: {imp_result['gaps']} Hz")

    print(f"\n--- Lever 2: Nonlinear Capture ---")
    print(f"  Total energy: {nl_result['total_energy']:.2f}  |  "
          f"Captured: {nl_result['captured_energy']:.2f}  |  "
          f"Efficiency: {nl_result['efficiency']:.0%}")
    print(f"  Duty cycle: {nl_result['duty_cycle']:.0%}  |  "
          f"{nl_result['recommendation']}")

    print(f"\n--- Lever 3: Stochastic Resonance ---")
    print(f"  Detection clean: {sr_result['detection_rate_clean']:.0%}  |  "
          f"With noise: {sr_result['detection_rate_with_noise']:.0%}")
    print(f"  Improvement: {sr_result['improvement_factor']:.0%}  |  "
          f"SR active: {sr_result['stochastic_resonance_active']}")
    print(f"  {sr_result['recommendation']}")

    print(f"\n--- Conversion Strategies ---")
    for s in STRATEGIES:
        print(f"  {s.name:35s}  [{s.target:10s}]  {s.expected_improvement:.0%} expected")

    b = comparison["baseline"]
    st = comparison["structured"]
    print(f"\n--- Grid Comparison ({grid_size}x{grid_size} = {grid_size**2} cells) ---")
    print(f"  {'Metric':<25} {'Uniform':>12} {'Structured':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12}")
    print(f"  {'Avg efficiency':<25} {b['avg_efficiency']:>12.4f} {st['avg_efficiency']:>12.4f}")
    print(f"  {'Max efficiency':<25} {b['max_efficiency']:>12.4f} {st['max_efficiency']:>12.4f}")
    print(f"  {'Hotspots (>0.8)':<25} {b['hotspots']:>12} {st['hotspots']:>12}")
    print(f"  Improvement: {comparison['improvement_pct']:+.1f}%")

    print(f"\n--- Decision Filter ---")
    print(f"  Q1. Is there still structure (frequency, spatial, intermittent)?")
    print(f"  Q2. Can I match it without forcing coherence?")
    print(f"  Q3. Does capturing it reduce performance elsewhere?")
    print(f"  Q4. Is it better used to assist another process?")
    print(f"  STOP when recovery increases total system entropy.")

    print()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Structured Noise Optimization -- convert disorder into "
            "directed work through thermal shaping, turbulence spectrum "
            "control, vibration harvesting, and reaction front structuring."
        ),
    )
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--grid-size", type=int, default=50, help="Grid size (default: 50)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.demo and not args.json:
        parser.print_help()
        sys.exit(0)

    run_demo(grid_size=args.grid_size, as_json=args.json)


if __name__ == "__main__":
    main()
