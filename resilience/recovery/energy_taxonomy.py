#!/usr/bin/env python3
"""
energy_taxonomy.py -- Classification of all energy interactions.

A first-principles taxonomy for evaluating any energy capture idea.
Most "new energy ideas" are not new sources -- they are new ways of
intercepting transfer before it degrades into thermal/diffusive loss.

Four-layer classification:
  A. Sources (true energy origin)
     - Nuclear (strong/weak interaction)
     - Radiative (stellar input)
     - Gravitational cycles (external forcing: tides, rain)

  B. Storage (energy held for later use)
     - Gravitational (mgh)
     - Chemical (bond energy)
     - Thermal (sensible + latent heat)
     - Elastic (strain energy)
     - Phase change (latent heat boundary)

  C. Transfer / Structuring (energy in motion)
     - Electromagnetic (charge, field, radiation)
     - Mechanical (stress, pressure, velocity)
     - Fluid dynamic (pressure fields, Coriolis)
     - Harmonic (resonance, oscillatory coupling)
     - Diffusive (concentration gradients)

  D. Loss / Dissipation (energy becoming unrecoverable)
     - Thermalization (random microscopic motion)
     - Diffusion (concentration equalization)
     - Turbulence (chaotic flow)

The practical filter for any energy idea:
  1. Which interaction carries the energy?
  2. Is this source, storage, or transfer?
  3. Am I intercepting before dissipation?
  4. Or trying to recover already-degraded energy?

Capture pathways (almost all reduce to one of):
  - delta_Mechanical -> Electrical (piezo, vibration, pressure)
  - delta_Thermal -> Electrical/Mechanical (Seebeck, expansion)
  - delta_Radiative -> Electrical/Thermal (solar, IR)
  - delta_Chemical -> Electrical/Thermal (combustion, bio)
  - delta_Field -> Electrical (electrostatic, magnetic gradients)

Special interaction types:
  - Harmonic: lock into resonance, amplify, couple out.
    Narrow bandwidth, detunes under variable load.
  - Gravitational: storage/mediator, not source.
    Requires pre-existing energy to lift mass.
  - Coriolis: directional bias in rotating frames.
    Shapes trajectories, not a primary source.

References
----------
- Feynman, R. (1964). The Feynman Lectures on Physics, Vol. I, Ch. 4:
  Conservation of Energy.
- Bejan, A. (2016). Advanced Engineering Thermodynamics, 4th ed. Wiley.
- Odum, H. T. (1971). Environment, Power, and Society. Wiley.
  (energy hierarchy and transformity)

Usage
-----
    python3 energy_taxonomy.py --demo
    python3 energy_taxonomy.py --classify "piezoelectric floor tiles"
    python3 energy_taxonomy.py --json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------
# Fundamental Interactions
# ---------------------------

class FundamentalForce(Enum):
    """The four fundamental interactions."""
    STRONG = "strong"
    WEAK = "weak"
    ELECTROMAGNETIC = "electromagnetic"
    GRAVITATIONAL = "gravitational"


# ---------------------------
# Energy Layer
# ---------------------------

class EnergyLayer(Enum):
    """Where energy sits in the source -> loss pipeline."""
    SOURCE = "source"              # true origin
    STORAGE = "storage"            # held for later
    TRANSFER = "transfer"          # in motion between systems
    DISSIPATION = "dissipation"    # becoming unrecoverable


# ---------------------------
# Interaction Type
# ---------------------------

class InteractionType(Enum):
    """Physical interaction types (fundamental + emergent)."""
    # Fundamental
    NUCLEAR_STRONG = "nuclear_strong"
    NUCLEAR_WEAK = "nuclear_weak"
    ELECTROMAGNETIC = "electromagnetic"
    GRAVITATIONAL = "gravitational"

    # Emergent / macroscopic
    THERMAL = "thermal"
    MECHANICAL = "mechanical"
    CHEMICAL = "chemical"
    RADIATIVE = "radiative"
    FLUID_DYNAMIC = "fluid_dynamic"
    HARMONIC = "harmonic"
    ELASTIC = "elastic"
    PHASE_CHANGE = "phase_change"
    DIFFUSIVE = "diffusive"
    MAGNETIC = "magnetic"
    ELECTROSTATIC = "electrostatic"
    CORIOLIS = "coriolis"


# ---------------------------
# Capture Pathway
# ---------------------------

class CapturePathway(Enum):
    """How gradients become usable energy."""
    MECHANICAL_TO_ELECTRICAL = "dMech_to_Elec"     # piezo, vibration
    THERMAL_TO_ELECTRICAL = "dTherm_to_Elec"       # Seebeck
    THERMAL_TO_MECHANICAL = "dTherm_to_Mech"       # expansion, steam
    RADIATIVE_TO_ELECTRICAL = "dRad_to_Elec"       # PV
    RADIATIVE_TO_THERMAL = "dRad_to_Therm"         # solar thermal
    CHEMICAL_TO_ELECTRICAL = "dChem_to_Elec"       # fuel cell
    CHEMICAL_TO_THERMAL = "dChem_to_Therm"         # combustion
    FIELD_TO_ELECTRICAL = "dField_to_Elec"         # electrostatic, magnetic


# ---------------------------
# Interaction Registry
# ---------------------------

@dataclass
class InteractionEntry:
    """A classified energy interaction."""
    name: str
    interaction: InteractionType
    layer: EnergyLayer
    gradient: str                  # what gradient drives it
    origin: str                    # underlying fundamental force
    density: str                   # low, medium, high
    harvestable: bool
    capture_pathway: Optional[CapturePathway]
    constraints: List[str]
    use_when: str
    notes: str = ""


TAXONOMY: List[InteractionEntry] = [
    # === SOURCES ===
    InteractionEntry(
        "Nuclear Fission/Fusion", InteractionType.NUCLEAR_STRONG,
        EnergyLayer.SOURCE, "binding energy (nuclear potential)",
        "strong", "very_high", True, None,
        ["requires regime shift (fission/fusion)", "radiation management"],
        "When density matters and infrastructure exists",
        "High-density stored energy reservoir",
    ),
    InteractionEntry(
        "Radioactive Decay", InteractionType.NUCLEAR_WEAK,
        EnergyLayer.SOURCE, "instability -> decay pathways",
        "weak", "low", True, None,
        ["low power density", "long timescale", "material availability"],
        "Autonomous low-rate release (RTGs, medical)",
        "High persistence, low power density",
    ),
    InteractionEntry(
        "Solar Radiation", InteractionType.RADIATIVE,
        EnergyLayer.SOURCE, "photon flux from stellar fusion",
        "electromagnetic", "medium", True, CapturePathway.RADIATIVE_TO_ELECTRICAL,
        ["intermittent", "area-dependent", "Shockley-Queisser limit"],
        "When area is available and intermittency is manageable",
    ),

    # === STORAGE ===
    InteractionEntry(
        "Gravitational Potential", InteractionType.GRAVITATIONAL,
        EnergyLayer.STORAGE, "E = mgh",
        "gravitational", "low", True, CapturePathway.MECHANICAL_TO_ELECTRICAL,
        ["requires pre-existing energy to lift", "or natural cycle (rain, tides)"],
        "When vertical movement or flow already exists, or need buffering",
        "Storage/mediator, not a primary source",
    ),
    InteractionEntry(
        "Chemical Bonds", InteractionType.CHEMICAL,
        EnergyLayer.STORAGE, "chemical potential (delta_mu)",
        "electromagnetic", "medium", True, CapturePathway.CHEMICAL_TO_ELECTRICAL,
        ["release rate control", "material availability"],
        "When controllable release is needed",
        "Electron configurations (EM origin)",
    ),
    InteractionEntry(
        "Thermal Mass", InteractionType.THERMAL,
        EnergyLayer.STORAGE, "temperature gradient (nabla_T)",
        "electromagnetic", "medium", True, CapturePathway.THERMAL_TO_ELECTRICAL,
        ["degrades over time", "Carnot-limited conversion"],
        "When gradients exist or can be created",
        "Degraded energy field (high entropy), still harvestable if gradients exist",
    ),
    InteractionEntry(
        "Elastic Strain", InteractionType.ELASTIC,
        EnergyLayer.STORAGE, "deformation field",
        "electromagnetic", "medium", True, CapturePathway.MECHANICAL_TO_ELECTRICAL,
        ["short duration", "material fatigue"],
        "Short-term storage + fast release",
    ),
    InteractionEntry(
        "Phase Change (Latent Heat)", InteractionType.PHASE_CHANGE,
        EnergyLayer.STORAGE, "latent heat boundary",
        "electromagnetic", "high", True, CapturePathway.THERMAL_TO_MECHANICAL,
        ["narrow temperature window", "material selection"],
        "High-density thermal buffering at specific temperatures",
    ),

    # === TRANSFER ===
    InteractionEntry(
        "Electromagnetic Transfer", InteractionType.ELECTROMAGNETIC,
        EnergyLayer.TRANSFER, "charge, field, radiation (delta_V, delta_E)",
        "electromagnetic", "high", True, CapturePathway.FIELD_TO_ELECTRICAL,
        ["coupling losses", "impedance matching"],
        "Primary transfer + conversion domain",
    ),
    InteractionEntry(
        "Mechanical Transfer", InteractionType.MECHANICAL,
        EnergyLayer.TRANSFER, "stress, pressure, velocity (nabla_P, nabla_v)",
        "electromagnetic", "high", True, CapturePathway.MECHANICAL_TO_ELECTRICAL,
        ["friction losses", "material limits"],
        "Structured, low-entropy transfer -- highly harvestable",
    ),
    InteractionEntry(
        "Fluid Dynamic", InteractionType.FLUID_DYNAMIC,
        EnergyLayer.TRANSFER, "pressure and velocity fields",
        "mechanical + gravitational", "medium", False, None,
        ["turbulence", "viscous losses"],
        "Transport + distribution layer (shapes access, not a source)",
    ),
    InteractionEntry(
        "Harmonic / Oscillatory", InteractionType.HARMONIC,
        EnergyLayer.TRANSFER, "resonance condition, Q factor, phase",
        "electromagnetic", "medium", True, CapturePathway.MECHANICAL_TO_ELECTRICAL,
        ["narrow bandwidth", "detunes under variable load"],
        "When frequency is stable or can be tuned (structures, rotating systems)",
        "Lock into resonance -> amplify -> couple out",
    ),
    InteractionEntry(
        "Coriolis", InteractionType.CORIOLIS,
        EnergyLayer.TRANSFER, "F = -2m(Omega x v)",
        "gravitational + mechanical", "very_low", False, None,
        ["small magnitude unless large scale or high velocity"],
        "Redirect flows, induce asymmetry, separate phases (not generation)",
        "Directional bias in rotating frames -- shapes trajectories, not a source",
    ),
    InteractionEntry(
        "Diffusive (Mass Transport)", InteractionType.DIFFUSIVE,
        EnergyLayer.TRANSFER, "concentration gradient (nabla_C)",
        "electromagnetic", "low", True, CapturePathway.CHEMICAL_TO_ELECTRICAL,
        ["slow", "often a loss channel unless intercepted"],
        "When concentration differences exist (osmotic power, salinity gradient)",
    ),

    # === DISSIPATION ===
    InteractionEntry(
        "Thermalization", InteractionType.THERMAL,
        EnergyLayer.DISSIPATION, "random microscopic motion",
        "electromagnetic", "n/a", False, None,
        ["maximum entropy", "no gradient remaining"],
        "This IS the loss -- intercept before it reaches this state",
    ),
    InteractionEntry(
        "Turbulent Dissipation", InteractionType.FLUID_DYNAMIC,
        EnergyLayer.DISSIPATION, "chaotic flow -> heat",
        "mechanical", "n/a", False, None,
        ["irrecoverable once thermalized"],
        "Shape turbulence spectrum before dissipation (see structured_noise.py)",
    ),
]


# ---------------------------
# Classifier
# ---------------------------

def classify_idea(description: str) -> Dict[str, Any]:
    """
    Classify an energy capture idea against the taxonomy.

    Matches keywords in the description to known interaction types
    and returns the classification with the practical filter questions.
    """
    desc_lower = description.lower()

    # Keyword matching for interaction types
    keyword_map = {
        "piezo": [InteractionType.MECHANICAL, CapturePathway.MECHANICAL_TO_ELECTRICAL],
        "vibrat": [InteractionType.HARMONIC, CapturePathway.MECHANICAL_TO_ELECTRICAL],
        "solar": [InteractionType.RADIATIVE, CapturePathway.RADIATIVE_TO_ELECTRICAL],
        "photovoltaic": [InteractionType.RADIATIVE, CapturePathway.RADIATIVE_TO_ELECTRICAL],
        "pv": [InteractionType.RADIATIVE, CapturePathway.RADIATIVE_TO_ELECTRICAL],
        "wind": [InteractionType.FLUID_DYNAMIC, CapturePathway.MECHANICAL_TO_ELECTRICAL],
        "thermal": [InteractionType.THERMAL, CapturePathway.THERMAL_TO_ELECTRICAL],
        "seebeck": [InteractionType.THERMAL, CapturePathway.THERMAL_TO_ELECTRICAL],
        "thermoelectric": [InteractionType.THERMAL, CapturePathway.THERMAL_TO_ELECTRICAL],
        "steam": [InteractionType.THERMAL, CapturePathway.THERMAL_TO_MECHANICAL],
        "biogas": [InteractionType.CHEMICAL, CapturePathway.CHEMICAL_TO_THERMAL],
        "fuel cell": [InteractionType.CHEMICAL, CapturePathway.CHEMICAL_TO_ELECTRICAL],
        "combustion": [InteractionType.CHEMICAL, CapturePathway.CHEMICAL_TO_THERMAL],
        "gravity": [InteractionType.GRAVITATIONAL, CapturePathway.MECHANICAL_TO_ELECTRICAL],
        "hydro": [InteractionType.GRAVITATIONAL, CapturePathway.MECHANICAL_TO_ELECTRICAL],
        "tidal": [InteractionType.GRAVITATIONAL, CapturePathway.MECHANICAL_TO_ELECTRICAL],
        "nuclear": [InteractionType.NUCLEAR_STRONG, None],
        "magnetic": [InteractionType.MAGNETIC, CapturePathway.FIELD_TO_ELECTRICAL],
        "electrostatic": [InteractionType.ELECTROSTATIC, CapturePathway.FIELD_TO_ELECTRICAL],
        "osmot": [InteractionType.DIFFUSIVE, CapturePathway.CHEMICAL_TO_ELECTRICAL],
        "salinity": [InteractionType.DIFFUSIVE, CapturePathway.CHEMICAL_TO_ELECTRICAL],
        "phase change": [InteractionType.PHASE_CHANGE, CapturePathway.THERMAL_TO_MECHANICAL],
        "elastic": [InteractionType.ELASTIC, CapturePathway.MECHANICAL_TO_ELECTRICAL],
        "spring": [InteractionType.ELASTIC, CapturePathway.MECHANICAL_TO_ELECTRICAL],
        "resonan": [InteractionType.HARMONIC, CapturePathway.MECHANICAL_TO_ELECTRICAL],
    }

    matched_interactions = []
    matched_pathways = []

    for keyword, (itype, pathway) in keyword_map.items():
        if keyword in desc_lower:
            matched_interactions.append(itype)
            if pathway:
                matched_pathways.append(pathway)

    # Find matching taxonomy entries
    matched_entries = []
    for entry in TAXONOMY:
        if entry.interaction in matched_interactions:
            matched_entries.append(entry)

    # Determine layer
    layers = list(set(e.layer.value for e in matched_entries)) if matched_entries else ["unknown"]

    # Practical filter
    is_source = EnergyLayer.SOURCE.value in layers
    is_storage = EnergyLayer.STORAGE.value in layers
    is_transfer = EnergyLayer.TRANSFER.value in layers
    is_dissipation = EnergyLayer.DISSIPATION.value in layers

    if is_source:
        assessment = "True energy source involved. Highest potential."
    elif is_storage and not is_dissipation:
        assessment = "Tapping stored energy. Viable if replenishment exists."
    elif is_transfer:
        assessment = "Intercepting energy in transfer. Good -- catch it before dissipation."
    elif is_dissipation and not (is_source or is_storage or is_transfer):
        assessment = "Attempting to recover already-degraded energy. Low yield expected."
    elif is_dissipation:
        assessment = "Mixed layers. Some recovery from degraded energy -- focus on the source/transfer components."
    else:
        assessment = "Could not classify. Check which physical interaction carries the energy."

    return {
        "description": description,
        "matched_interactions": [i.value for i in set(matched_interactions)],
        "capture_pathways": [p.value for p in set(matched_pathways)],
        "energy_layers": layers,
        "assessment": assessment,
        "practical_filter": {
            "q1_which_interaction": [i.value for i in set(matched_interactions)] or ["unknown"],
            "q2_source_storage_or_transfer": layers,
            "q3_intercepting_before_dissipation": is_transfer or is_storage,
            "q4_recovering_degraded_energy": is_dissipation,
        },
        "matched_entries": [
            {"name": e.name, "layer": e.layer.value, "constraints": e.constraints,
             "use_when": e.use_when}
            for e in matched_entries
        ],
    }


# ---------------------------
# Output
# ---------------------------

def print_taxonomy():
    """Print the complete taxonomy."""
    print("=" * 70)
    print("  ENERGY INTERACTION TAXONOMY")
    print("  Most new ideas are not new sources --")
    print("  they are new ways to intercept transfer before dissipation.")
    print("=" * 70)

    current_layer = None
    for entry in TAXONOMY:
        if entry.layer != current_layer:
            current_layer = entry.layer
            print(f"\n{'=' * 50}")
            print(f"  {current_layer.value.upper()}")
            print(f"{'=' * 50}")

        print(f"\n  {entry.name}")
        print(f"    Interaction: {entry.interaction.value}")
        print(f"    Gradient: {entry.gradient}")
        print(f"    Origin: {entry.origin}")
        print(f"    Density: {entry.density}")
        print(f"    Harvestable: {'yes' if entry.harvestable else 'no'}")
        if entry.capture_pathway:
            print(f"    Capture: {entry.capture_pathway.value}")
        print(f"    Use when: {entry.use_when}")
        if entry.constraints:
            print(f"    Constraints: {'; '.join(entry.constraints)}")
        if entry.notes:
            print(f"    Notes: {entry.notes}")

    print(f"\n{'=' * 70}")
    print(f"  CAPTURE PATHWAYS (almost all reduce to one of):")
    print(f"{'=' * 70}")
    for cp in CapturePathway:
        print(f"  {cp.value}")

    print(f"\n{'=' * 70}")
    print(f"  PRACTICAL FILTER (for any energy idea):")
    print(f"{'=' * 70}")
    print(f"  1. Which interaction is actually carrying the energy?")
    print(f"  2. Is this a source, storage, or transfer layer?")
    print(f"  3. Am I intercepting before dissipation?")
    print(f"  4. Or am I trying to recover already degraded energy?")
    print()


def run_demo(as_json: bool = False):
    """Run demonstration with example classifications."""
    examples = [
        "piezoelectric floor tiles in a train station",
        "solar thermal sand battery for night heating",
        "biogas from human waste driving a Seebeck generator",
        "gravity storage in abandoned mine shaft",
        "harvesting waste heat from server room with thermoelectric",
        "tidal barrage with osmotic salinity gradient backup",
        "recovering thermal energy from ambient air",
    ]

    results = [classify_idea(ex) for ex in examples]

    if as_json:
        output = {
            "taxonomy_size": len(TAXONOMY),
            "capture_pathways": [cp.value for cp in CapturePathway],
            "classifications": results,
        }
        print(json.dumps(output, indent=2))
        return

    print_taxonomy()

    print(f"\n{'=' * 70}")
    print(f"  EXAMPLE CLASSIFICATIONS")
    print(f"{'=' * 70}")

    for r in results:
        print(f"\n  Idea: \"{r['description']}\"")
        print(f"    Interactions: {', '.join(r['matched_interactions'])}")
        print(f"    Pathways: {', '.join(r['capture_pathways'])}")
        print(f"    Layer: {', '.join(r['energy_layers'])}")
        print(f"    Assessment: {r['assessment']}")
        pf = r["practical_filter"]
        intercept = "YES" if pf["q3_intercepting_before_dissipation"] else "NO"
        degraded = "YES" if pf["q4_recovering_degraded_energy"] else "NO"
        print(f"    Intercepting before dissipation: {intercept}")
        print(f"    Recovering degraded energy: {degraded}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Energy Interaction Taxonomy -- classify any energy capture "
            "idea against first-principles physics. Sources vs storage "
            "vs transfer vs dissipation."
        ),
    )
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--classify", type=str, help="Classify a specific energy idea")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.classify:
        result = classify_idea(args.classify)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n  Idea: \"{result['description']}\"")
            print(f"  Interactions: {', '.join(result['matched_interactions'])}")
            print(f"  Pathways: {', '.join(result['capture_pathways'])}")
            print(f"  Layer: {', '.join(result['energy_layers'])}")
            print(f"  Assessment: {result['assessment']}")
    elif args.demo or args.json:
        run_demo(as_json=args.json)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
