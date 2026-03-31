#!/usr/bin/env python3
"""
perimeter_defense.py -- Autonomous perimeter monitoring and response.

Detection and deterrent logic for autonomous sites.  Models threat
classification, distance-scaled response, camera hardening for extreme
cold, and remote status reporting for operators away from site.

Core components:
  - ThreatClassifier: categorizes detections by type (human, predator,
    wildlife, vehicle, unknown) and threat level.
  - DeterrentController: maps threat types to deterrent responses
    (sonic, electric mesh, strobe, alert) with distance-scaled intensity.
  - CameraHardening: specifications for cold-climate camera housings
    that survive -40C without brittle failure.
  - RemoteStatus: aggregates site health into a single coherence
    check for operators on the road.

Design principles:
  - Energy-proportional response: close threats get high-power deterrent,
    distant threats get monitoring only.
  - Species-specific deterrents minimize energy waste and avoid
    harming non-threats.
  - Camera housings use salvaged PVC pipe with resistor heating,
    activated only below -20C.
  - Detection logic is framework-agnostic: works with any object
    detection backend (YOLO, MobileNet, manual classification).

References
----------
- Smith, M. E. et al. (2000). Effectiveness of predator deterrents
  for wolves. Wildlife Society Bulletin, 28(4), 937-943.
- Breck, S. W. et al. (2002). Non-lethal deterrent techniques for bears.
  USDA Wildlife Services Technical Report.
- IEEE 802.11 (WiFi) and MQTT for low-overhead sensor networking.

Usage
-----
    python3 perimeter_defense.py --demo
    python3 perimeter_defense.py --demo --json

Note: actual camera/sensor hardware integration requires opencv-python
and/or torch for ML detection.  This module provides the decision logic
layer that runs on any Python installation.
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------
# Threat Classification
# ---------------------------

class ThreatType(Enum):
    HUMAN_UNKNOWN = "human_unknown"
    HUMAN_KNOWN = "human_known"
    PREDATOR_BEAR = "bear"
    PREDATOR_WOLF = "wolf"
    PREDATOR_COUGAR = "cougar"
    WILDLIFE_DEER = "deer"
    WILDLIFE_OTHER = "wildlife_other"
    VEHICLE = "vehicle"
    UNKNOWN = "unknown"


class ThreatLevel(Enum):
    CRITICAL = "critical"      # immediate physical danger
    HIGH = "high"              # probable threat, active response
    MODERATE = "moderate"      # monitor closely
    LOW = "low"                # log only
    NONE = "none"              # known-safe


THREAT_LEVELS = {
    ThreatType.HUMAN_UNKNOWN: ThreatLevel.HIGH,
    ThreatType.HUMAN_KNOWN: ThreatLevel.NONE,
    ThreatType.PREDATOR_BEAR: ThreatLevel.HIGH,
    ThreatType.PREDATOR_WOLF: ThreatLevel.HIGH,
    ThreatType.PREDATOR_COUGAR: ThreatLevel.CRITICAL,
    ThreatType.WILDLIFE_DEER: ThreatLevel.LOW,
    ThreatType.WILDLIFE_OTHER: ThreatLevel.LOW,
    ThreatType.VEHICLE: ThreatLevel.MODERATE,
    ThreatType.UNKNOWN: ThreatLevel.MODERATE,
}


@dataclass
class Detection:
    """A single detection event from any sensor source."""
    label: str                    # raw label from detector
    confidence: float             # 0-1
    distance_meters: float        # estimated distance
    camera_id: str = ""
    timestamp: float = 0.0       # unix timestamp

    def threat_type(self) -> ThreatType:
        """Map detection label to threat type."""
        label_lower = self.label.lower()
        mapping = {
            "person": ThreatType.HUMAN_UNKNOWN,
            "human": ThreatType.HUMAN_UNKNOWN,
            "bear": ThreatType.PREDATOR_BEAR,
            "wolf": ThreatType.PREDATOR_WOLF,
            "cougar": ThreatType.PREDATOR_COUGAR,
            "mountain_lion": ThreatType.PREDATOR_COUGAR,
            "deer": ThreatType.WILDLIFE_DEER,
            "moose": ThreatType.WILDLIFE_OTHER,
            "car": ThreatType.VEHICLE,
            "truck": ThreatType.VEHICLE,
        }
        for key, ttype in mapping.items():
            if key in label_lower:
                return ttype
        return ThreatType.UNKNOWN


class ThreatClassifier:
    """Classify detections into threat levels with confidence filtering."""

    def __init__(self, min_confidence: float = 0.70):
        self.min_confidence = min_confidence
        self.known_humans: List[str] = []  # IDs of known-safe humans

    def classify(self, detection: Detection) -> Dict[str, Any]:
        """Classify a single detection."""
        if detection.confidence < self.min_confidence:
            return {
                "threat_type": "below_threshold",
                "threat_level": "none",
                "action": "log",
                "confidence": detection.confidence,
                "note": f"Confidence {detection.confidence:.0%} below "
                        f"minimum {self.min_confidence:.0%}",
            }

        ttype = detection.threat_type()
        level = THREAT_LEVELS.get(ttype, ThreatLevel.MODERATE)

        return {
            "threat_type": ttype.value,
            "threat_level": level.value,
            "confidence": detection.confidence,
            "distance_meters": detection.distance_meters,
            "camera_id": detection.camera_id,
        }


# ---------------------------
# Deterrent Controller
# ---------------------------

@dataclass
class DeterrentAction:
    """A deterrent response specification."""
    name: str
    type: str              # sonic, electric, strobe, alert
    max_power_watts: float
    effective_range_meters: float
    description: str


DEFAULT_DETERRENTS = {
    ThreatType.PREDATOR_WOLF: DeterrentAction(
        "high_freq_sonic", "sonic", 50, 100,
        "High-frequency sonic deterrent. Wolves avoid 15-25 kHz range.",
    ),
    ThreatType.PREDATOR_BEAR: DeterrentAction(
        "electric_mesh_pulse", "electric", 200, 5,
        "Capacitive discharge mesh pulse. Single 12V ignition coil burst.",
    ),
    ThreatType.PREDATOR_COUGAR: DeterrentAction(
        "overhead_strobe", "strobe", 30, 50,
        "Overhead strobe light. Cougars avoid sudden bright light.",
    ),
    ThreatType.HUMAN_UNKNOWN: DeterrentAction(
        "pack_protocol_alert", "alert", 5, 0,
        "Alert sent to operator. Flood lights activated. Audio warning.",
    ),
}


class DeterrentController:
    """
    Map threats to deterrent responses with distance-scaled intensity.

    Close threats get full power.  Distant threats get monitoring only.
    Species-specific deterrents minimize energy waste.
    """

    def __init__(
        self,
        deterrents: Optional[Dict[ThreatType, DeterrentAction]] = None,
        close_range_meters: float = 5.0,
        monitoring_range_meters: float = 50.0,
    ):
        self.deterrents = deterrents or DEFAULT_DETERRENTS
        self.close_range = close_range_meters
        self.monitoring_range = monitoring_range_meters

    def respond(self, detection: Detection) -> Dict[str, Any]:
        """Determine response for a detection."""
        ttype = detection.threat_type()
        level = THREAT_LEVELS.get(ttype, ThreatLevel.LOW)

        if level in (ThreatLevel.LOW, ThreatLevel.NONE):
            return {
                "action": "log",
                "threat_type": ttype.value,
                "distance": detection.distance_meters,
                "note": f"Non-threat ({ttype.value}). Logging for archive.",
            }

        deterrent = self.deterrents.get(ttype)
        if not deterrent:
            return {
                "action": "alert",
                "threat_type": ttype.value,
                "distance": detection.distance_meters,
                "note": "No specific deterrent configured. Alerting operator.",
            }

        # Distance-scaled intensity
        if detection.distance_meters <= self.close_range:
            intensity_pct = 100
        elif detection.distance_meters <= self.monitoring_range:
            # Linear scale from 100% at close to 30% at monitoring range
            ratio = (detection.distance_meters - self.close_range) / (
                self.monitoring_range - self.close_range
            )
            intensity_pct = int(100 - 70 * ratio)
        else:
            intensity_pct = 0

        if intensity_pct <= 0:
            return {
                "action": "monitor",
                "threat_type": ttype.value,
                "distance": detection.distance_meters,
                "deterrent": deterrent.name,
                "note": "Beyond effective range. Monitoring only.",
            }

        power_watts = deterrent.max_power_watts * intensity_pct / 100

        return {
            "action": "deploy",
            "threat_type": ttype.value,
            "deterrent": deterrent.name,
            "deterrent_type": deterrent.type,
            "distance_meters": detection.distance_meters,
            "intensity_pct": intensity_pct,
            "power_watts": round(power_watts, 1),
            "description": deterrent.description,
        }


# ---------------------------
# Camera Hardening
# ---------------------------

CAMERA_HARDENING_SPEC = {
    "housing": "Salvaged heavy-duty PVC pipe section with glass lens cap",
    "lens_cap": "Recycled glass jar lid, sealed with silicone gasket",
    "heating": {
        "element": "5W resistor near lens",
        "activation_temp_c": -20,
        "purpose": "Prevent frost buildup on lens",
        "power_watts": 5,
    },
    "mounting": "Geometric angle overlapping adjacent camera field of view",
    "cable_entry": "Silicone-sealed PVC conduit with drip loop",
    "operating_range_c": (-40, 50),
    "notes": [
        "Standard camera plastic becomes brittle below -20C",
        "PVC pipe sections from plumbing salvage are impact-resistant",
        "Drip loop prevents condensation from wicking into housing",
        "Overlapping fields eliminate blind spots for perimeter coverage",
    ],
}


# ---------------------------
# Remote Status
# ---------------------------

@dataclass
class SubsystemHealth:
    """Health reading from one subsystem."""
    name: str
    health: float       # 0-1
    last_alert: str = ""


class RemoteStatus:
    """
    Aggregate site status for remote operators.

    Produces a single coherence check suitable for mobile display:
    green (all clear), yellow (degraded), red (action needed).
    """

    def __init__(self):
        self.subsystems: List[SubsystemHealth] = []
        self.recent_events: List[Dict[str, Any]] = []

    def update_subsystem(self, name: str, health: float, alert: str = ""):
        """Update or add a subsystem health reading."""
        for sub in self.subsystems:
            if sub.name == name:
                sub.health = health
                sub.last_alert = alert
                return
        self.subsystems.append(SubsystemHealth(name, health, alert))

    def add_event(self, event: Dict[str, Any]):
        """Log a perimeter event for the remote operator."""
        self.recent_events.append(event)
        # Keep last 50 events
        if len(self.recent_events) > 50:
            self.recent_events = self.recent_events[-50:]

    def summary(self) -> Dict[str, Any]:
        """Generate remote status summary."""
        if not self.subsystems:
            return {"coherence": "unknown", "color": "grey"}

        avg_health = sum(s.health for s in self.subsystems) / len(self.subsystems)
        min_health = min(s.health for s in self.subsystems)
        alerts = [s for s in self.subsystems if s.last_alert]

        if min_health > 0.80:
            color = "green"
            coherence = "nominal"
        elif min_health > 0.50:
            color = "yellow"
            coherence = "degraded"
        else:
            color = "red"
            coherence = "action_required"

        # Recent threat events
        threat_events = [
            e for e in self.recent_events[-10:]
            if e.get("action") in ("deploy", "alert")
        ]

        return {
            "coherence": coherence,
            "color": color,
            "avg_health": round(avg_health, 3),
            "min_health": round(min_health, 3),
            "subsystems": {
                s.name: {"health": s.health, "alert": s.last_alert}
                for s in self.subsystems
            },
            "active_alerts": len(alerts),
            "recent_threats": len(threat_events),
            "recent_events": threat_events,
        }


# ---------------------------
# Demo / CLI
# ---------------------------

def run_demo(as_json: bool = False) -> Dict[str, Any]:
    """Run demonstration of perimeter defense system."""
    results: Dict[str, Any] = {}

    classifier = ThreatClassifier(min_confidence=0.70)
    controller = DeterrentController()

    # Simulate detection events
    detections = [
        Detection("bear", 0.92, 3.0, "cam_north"),
        Detection("wolf", 0.85, 25.0, "cam_east"),
        Detection("deer", 0.95, 15.0, "cam_south"),
        Detection("person", 0.78, 40.0, "cam_west"),
        Detection("unknown", 0.55, 30.0, "cam_north"),
        Detection("cougar", 0.88, 8.0, "cam_east"),
        Detection("truck", 0.91, 100.0, "cam_south"),
    ]

    classifications = []
    responses = []
    for det in detections:
        c = classifier.classify(det)
        r = controller.respond(det)
        classifications.append(c)
        responses.append(r)

    results["detections"] = [
        {
            "label": d.label,
            "confidence": d.confidence,
            "distance": d.distance_meters,
            "camera": d.camera_id,
            "classification": c,
            "response": r,
        }
        for d, c, r in zip(detections, classifications, responses)
    ]

    # Camera hardening
    results["camera_hardening"] = CAMERA_HARDENING_SPEC

    # Remote status
    remote = RemoteStatus()
    remote.update_subsystem("power", 0.95)
    remote.update_subsystem("water", 0.82)
    remote.update_subsystem("thermal", 0.90)
    remote.update_subsystem("perimeter", 0.75, "bear detected cam_north")
    remote.update_subsystem("biogas", 0.88)
    for r in responses:
        remote.add_event(r)
    results["remote_status"] = remote.summary()

    if as_json:
        print(json.dumps(results, indent=2))
        return results

    print("=" * 60)
    print("PERIMETER DEFENSE -- Autonomous Detection and Response")
    print("=" * 60)

    for entry in results["detections"]:
        d = entry
        c = d["classification"]
        r = d["response"]
        print(f"\n  [{d['camera']:10s}] {d['label']:8s}  "
              f"conf={d['confidence']:.0%}  dist={d['distance']:.0f}m")
        print(f"    Threat: {c.get('threat_type', 'n/a'):15s}  "
              f"Level: {c.get('threat_level', 'n/a')}")
        print(f"    Action: {r['action']}", end="")
        if r.get("deterrent"):
            print(f"  ->  {r['deterrent']} at {r.get('intensity_pct', 0)}% "
                  f"({r.get('power_watts', 0)}W)")
        else:
            print(f"  ({r.get('note', '')})")

    print(f"\n--- Camera Hardening ---")
    spec = results["camera_hardening"]
    print(f"  Housing: {spec['housing']}")
    print(f"  Heating: {spec['heating']['element']} "
          f"(activates at {spec['heating']['activation_temp_c']}C)")
    print(f"  Range: {spec['operating_range_c'][0]}C to {spec['operating_range_c'][1]}C")

    rs = results["remote_status"]
    print(f"\n--- Remote Status [{rs['color'].upper()}] ---")
    print(f"  Coherence: {rs['coherence']}  |  "
          f"Avg health: {rs['avg_health']}  |  Min: {rs['min_health']}")
    for name, sub in rs["subsystems"].items():
        indicator = "OK" if sub["health"] > 0.80 else "!!"
        print(f"    [{indicator}] {name:15s}  {sub['health']:.2f}  "
              f"{sub['alert'] if sub['alert'] else ''}")
    print(f"  Recent threats: {rs['recent_threats']}")

    print()
    return results


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Perimeter defense -- threat classification, distance-scaled "
            "deterrent response, camera hardening for extreme cold, and "
            "remote status reporting for autonomous sites."
        ),
    )
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        sys.exit(0)

    run_demo(as_json=args.json)


if __name__ == "__main__":
    main()
