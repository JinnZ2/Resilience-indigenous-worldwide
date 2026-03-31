#!/usr/bin/env python3
"""
human_body_alerts.py — Human biological sensing as a threat-detection framework.

Purpose
-------
Models the human body as an array of biological sensors that detect
environmental threats.  Provides a generic, pluggable architecture:
register sensors and interpretation rules, then run detection against
reported environmental conditions or symptoms.

Core abstractions:
  * BiologicalSensor  — a sensing capability (organ system, sensitivity, etc.)
  * SymptomRule        — maps a symptom to possible environmental causes
  * ThreatCondition    — maps an environmental metric to sensor activation
  * SensorRegistry     — catalogue of available sensors
  * HumanGeometricCoupling — detection engine (threat matrix + symptom lookup)

The built-in demo populates a small set of example sensors, threat
conditions, and symptom rules, then runs detection against sample
environmental data.

References
----------
* Goldstein, E.B. (2021). Sensation and Perception (11th ed.). Cengage.
* Craig, A.D. (2003). "Interoception: the sense of the physiological
  condition of the body." Current Opinion in Neurobiology, 13(4), 500-505.
* Prigogine, I. & Stengers, I. (1984). Order Out of Chaos. Bantam.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable


# ------------------
# Biological Sensor
# ------------------

@dataclass
class BiologicalSensor:
    """A biological sensing capability."""
    name: str
    organ_system: str
    what_it_detects: List[str]
    sensitivity_range: str
    calibration_signals: List[str]   # symptoms indicating activation
    reliability: float               # 0-1
    tags: Dict[str, str] = field(default_factory=dict)


# ------------------
# Symptom Rule
# ------------------

@dataclass
class SymptomRule:
    """Maps a symptom to possible environmental causes."""
    symptom: str
    possible_causes: List[str]
    sensor: str                      # which sensor produces this symptom


# ------------------
# Threat Condition
# ------------------

@dataclass
class ThreatCondition:
    """
    Maps an environmental condition key to sensors that activate.
    Used in detect_threat_matrix().
    """
    condition_key: str               # e.g. "infrasound", "chemical"
    threshold: float                 # minimum value to trigger
    sensor_name: str
    symptom: str
    interpretation: str
    confidence_scale: float = 0.7    # multiplied by condition value


# ------------------
# Sensor Registry
# ------------------

class SensorRegistry:
    """Registry of biological sensors. Populate via register()."""

    def __init__(self):
        self.sensors: Dict[str, BiologicalSensor] = {}

    def register(self, sensor: BiologicalSensor):
        self.sensors[sensor.name] = sensor

    def all(self) -> List[BiologicalSensor]:
        return list(self.sensors.values())

    def by_organ(self, organ_keyword: str) -> List[BiologicalSensor]:
        return [
            s for s in self.sensors.values()
            if organ_keyword.lower() in s.organ_system.lower()
        ]


# ------------------
# Human Geometric Coupling
# ------------------

class HumanGeometricCoupling:
    """
    Maps environmental conditions -> biological detections.
    Pluggable via ThreatCondition and SymptomRule registries.
    """

    def __init__(self):
        self.threat_conditions: List[ThreatCondition] = []
        self.symptom_rules: List[SymptomRule] = []

    def add_threat_condition(self, condition: ThreatCondition):
        self.threat_conditions.append(condition)

    def add_symptom_rule(self, rule: SymptomRule):
        self.symptom_rules.append(rule)

    def detect_threat_matrix(
        self, environmental_conditions: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Given environmental condition values, return which sensors
        activate and what they indicate.
        """
        detections = []

        for tc in self.threat_conditions:
            value = environmental_conditions.get(tc.condition_key, 0)
            if value >= tc.threshold:
                detections.append({
                    "sensor": tc.sensor_name,
                    "symptom": tc.symptom,
                    "interpretation": tc.interpretation,
                    "confidence": tc.confidence_scale * min(1.0, value),
                })

        # Integrated threat (multiple sensors activating)
        if len(detections) > 2:
            avg_conf = sum(d["confidence"] for d in detections) / len(detections)
            detections.append({
                "sensor": "integrated",
                "symptom": "Multiple signals -- heightened awareness",
                "interpretation": "Multiple environmental signals indicate threat",
                "confidence": min(1.0, avg_conf * 1.2),
            })

        overall = (
            sum(d["confidence"] for d in detections) / len(detections)
            if detections else 0
        )

        return {
            "detections": detections,
            "overall_threat_level": min(1.0, overall),
            "sensors_activated": list(set(d["sensor"] for d in detections)),
        }

    def interpret_symptoms(
        self, symptoms: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Given reported symptoms, return possible environmental causes.
        """
        results = []
        for symptom in symptoms:
            matching = [r for r in self.symptom_rules if r.symptom == symptom]
            for rule in matching:
                results.append({
                    "symptom": rule.symptom,
                    "possible_causes": rule.possible_causes,
                    "sensor": rule.sensor,
                })
        return results


# ------------------------------------------------------------------
# Demo data — a small illustrative sensor / rule / condition set
# ------------------------------------------------------------------

def build_demo() -> tuple:
    """Build and return a populated (SensorRegistry, HumanGeometricCoupling)."""

    registry = SensorRegistry()

    registry.register(BiologicalSensor(
        name="vestibular",
        organ_system="inner ear / vestibular",
        what_it_detects=["infrasound", "pressure changes", "acceleration"],
        sensitivity_range="0.1 – 20 Hz vibration; sub-Pascal pressure deltas",
        calibration_signals=["dizziness", "nausea", "spatial disorientation"],
        reliability=0.85,
        tags={"modality": "mechanoreception"},
    ))

    registry.register(BiologicalSensor(
        name="chemosensory",
        organ_system="olfactory / vomeronasal",
        what_it_detects=["volatile organic compounds", "pheromones", "toxins"],
        sensitivity_range="parts-per-billion for select odorants",
        calibration_signals=["headache", "nausea", "irritation"],
        reliability=0.75,
        tags={"modality": "chemoreception"},
    ))

    registry.register(BiologicalSensor(
        name="electromagnetic",
        organ_system="retina / skin / magnetite deposits",
        what_it_detects=["visible light", "UV", "EMF fluctuations"],
        sensitivity_range="380 – 740 nm (visible); subtle DC field shifts",
        calibration_signals=["visual disturbance", "skin tingling", "fatigue"],
        reliability=0.60,
        tags={"modality": "photoreception / magnetoreception"},
    ))

    registry.register(BiologicalSensor(
        name="interoceptive",
        organ_system="autonomic nervous system / gut-brain axis",
        what_it_detects=["social threat", "deception cues", "stress hormones"],
        sensitivity_range="millisecond autonomic shifts",
        calibration_signals=["gut feeling", "anxiety", "heart-rate change"],
        reliability=0.70,
        tags={"modality": "interoception"},
    ))

    coupling = HumanGeometricCoupling()

    coupling.add_threat_condition(ThreatCondition(
        condition_key="infrasound",
        threshold=0.3,
        sensor_name="vestibular",
        symptom="dizziness",
        interpretation="Low-frequency acoustic energy detected",
        confidence_scale=0.8,
    ))

    coupling.add_threat_condition(ThreatCondition(
        condition_key="chemical",
        threshold=0.2,
        sensor_name="chemosensory",
        symptom="headache",
        interpretation="Airborne chemical exposure detected",
        confidence_scale=0.75,
    ))

    coupling.add_threat_condition(ThreatCondition(
        condition_key="emf",
        threshold=0.4,
        sensor_name="electromagnetic",
        symptom="fatigue",
        interpretation="Anomalous electromagnetic field detected",
        confidence_scale=0.6,
    ))

    coupling.add_threat_condition(ThreatCondition(
        condition_key="social_threat",
        threshold=0.5,
        sensor_name="interoceptive",
        symptom="anxiety",
        interpretation="Social / deception threat detected",
        confidence_scale=0.7,
    ))

    coupling.add_symptom_rule(SymptomRule(
        symptom="dizziness",
        possible_causes=["infrasound exposure", "pressure change", "vestibular disruption"],
        sensor="vestibular",
    ))

    coupling.add_symptom_rule(SymptomRule(
        symptom="headache",
        possible_causes=["chemical exposure", "VOCs", "carbon monoxide"],
        sensor="chemosensory",
    ))

    coupling.add_symptom_rule(SymptomRule(
        symptom="anxiety",
        possible_causes=["social threat", "deception detected", "autonomic stress response"],
        sensor="interoceptive",
    ))

    return registry, coupling


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def _print_human(registry: SensorRegistry, result: Dict[str, Any],
                 symptom_result: List[Dict[str, Any]]) -> None:
    """Pretty-print results for human consumption."""

    print("=" * 60)
    print("  Human Body Alert System — Demo Run")
    print("=" * 60)

    print("\nRegistered sensors:")
    for s in registry.all():
        print(f"  [{s.name}] {s.organ_system}  (reliability {s.reliability:.0%})")
        print(f"      detects: {', '.join(s.what_it_detects)}")

    print("\n--- Threat Matrix ---")
    print(f"  Overall threat level: {result['overall_threat_level']:.2f}")
    print(f"  Sensors activated:    {result['sensors_activated']}")
    for d in result["detections"]:
        print(f"    • {d['sensor']:15s}  {d['symptom']:30s}  "
              f"confidence={d['confidence']:.2f}")
        print(f"      {d['interpretation']}")

    if symptom_result:
        print("\n--- Symptom Interpretation ---")
        for entry in symptom_result:
            print(f"    {entry['symptom']}  (sensor: {entry['sensor']})")
            for cause in entry["possible_causes"]:
                print(f"      - {cause}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Human biological sensing as a threat-detection framework. "
            "Models the body as an array of sensors and runs detection "
            "against sample environmental conditions."
        ),
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Emit results as JSON instead of human-readable text",
    )
    parser.add_argument(
        "--conditions", type=str, default=None,
        help=(
            'Environmental conditions as a JSON object, e.g. '
            '\'{"infrasound": 0.6, "chemical": 0.5}\'. '
            "If omitted a built-in demo set is used."
        ),
    )
    parser.add_argument(
        "--symptoms", type=str, nargs="*", default=None,
        help=(
            "Symptoms to interpret, e.g. --symptoms dizziness headache. "
            "If omitted a built-in demo set is used."
        ),
    )
    args = parser.parse_args()

    registry, coupling = build_demo()

    # Environmental conditions
    if args.conditions is not None:
        try:
            env_conditions = json.loads(args.conditions)
        except json.JSONDecodeError as exc:
            print(f"Error: --conditions is not valid JSON: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        env_conditions = {
            "infrasound": 0.6,
            "chemical": 0.5,
            "emf": 0.3,
            "social_threat": 0.8,
        }

    # Symptoms
    symptoms = args.symptoms if args.symptoms is not None else [
        "dizziness", "headache", "anxiety",
    ]

    threat_result = coupling.detect_threat_matrix(env_conditions)
    symptom_result = coupling.interpret_symptoms(symptoms)

    if args.json_output:
        output = {
            "sensors": [
                {
                    "name": s.name,
                    "organ_system": s.organ_system,
                    "what_it_detects": s.what_it_detects,
                    "sensitivity_range": s.sensitivity_range,
                    "calibration_signals": s.calibration_signals,
                    "reliability": s.reliability,
                    "tags": s.tags,
                }
                for s in registry.all()
            ],
            "environmental_conditions": env_conditions,
            "threat_matrix": threat_result,
            "symptom_interpretation": symptom_result,
        }
        json.dump(output, sys.stdout, indent=2)
        print()
    else:
        _print_human(registry, threat_result, symptom_result)


if __name__ == "__main__":
    main()
