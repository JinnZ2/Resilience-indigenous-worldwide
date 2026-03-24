"""Stress propagation model with hidden variables.

Refactored from Model/Hidden-variable.py into a reusable module.
Models how external stressors (climate, infrastructure failure,
human factors) propagate through indigenous community networks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from resilience.network import CommunityNetwork, NodeAttributes


@dataclass
class PropagationConfig:
    """Tunable parameters for stress propagation."""

    threshold: float = 0.6
    amplification_factor: float = 1.5
    timesteps: int = 10
    stress_cap: float = 1.0


class StressPropagator:
    """Simulate stress propagation across a CommunityNetwork."""

    def __init__(
        self,
        network: CommunityNetwork,
        config: PropagationConfig | None = None,
    ) -> None:
        self.network = network
        self.config = config or PropagationConfig()
        self.history: List[dict] = []

    def threshold_amplification(self, stress: float) -> float:
        """Non-linear amplification once stress exceeds threshold."""
        cfg = self.config
        if stress > cfg.threshold:
            return cfg.amplification_factor * (stress - cfg.threshold)
        return 0.0

    def step(self) -> None:
        """Advance the simulation by one timestep."""
        g = self.network.graph
        new_stress: dict[str, float] = {}

        for j in g.nodes:
            attrs_j = g.nodes[j]
            stress_increment = 0.0

            # Incoming stress from neighbours
            for i in g.predecessors(j):
                w = g[i][j]["weight"]
                s_i = g.nodes[i]["stress"]
                slack_i = g.nodes[i]["slack"]
                central_delay = attrs_j["centralization"]
                stress_increment += w * s_i * (1 - slack_i) * (1 + central_delay)

            # Hidden variable contributions
            h_climate = attrs_j["hidden_climate"]
            h_infra = attrs_j["hidden_infra"]
            h_community = attrs_j["hidden_community"]
            h_human = attrs_j["hidden_human"]
            resilience = attrs_j["resilience"]

            amp = self.threshold_amplification(attrs_j["stress"])

            stress_new = (
                attrs_j["stress"]
                + stress_increment
                + h_climate * (1 - resilience)
                + h_infra
                + h_community
                + amp
                + h_human * amp
            )
            new_stress[j] = min(stress_new, self.config.stress_cap)

        # Apply updated stress values
        for j, val in new_stress.items():
            g.nodes[j]["stress"] = val

    def run(self) -> pd.DataFrame:
        """Run the full simulation and return stress history as a DataFrame."""
        self.history.clear()
        for _ in range(self.config.timesteps):
            self.step()
            snapshot = {n: self.network.graph.nodes[n]["stress"] for n in self.network.nodes}
            self.history.append(snapshot)
        return pd.DataFrame(self.history)

    def reset(self, node_defaults: dict | None = None) -> None:
        """Reset all node stress values (useful for re-running scenarios)."""
        for n in self.network.nodes:
            self.network.set_node_attr(n, "stress", 0.1)
        if node_defaults:
            for name, stress in node_defaults.items():
                self.network.set_node_attr(name, "stress", stress)
        self.history.clear()


# ---------------------------------------------------------------------------
# CLI entry point: replicate original Hidden-variable.py behaviour
# ---------------------------------------------------------------------------

def _build_default_network() -> CommunityNetwork:
    """Reproduce the sample network from the original script."""
    nodes = {
        "Community_1": {
            "stress": 0.1, "slack": 0.8, "resilience": 0.9,
            "hidden_climate": 0.2, "hidden_infra": 0.1,
            "hidden_community": 0.3, "hidden_human": 0.5,
            "centralization": 0.3,
        },
        "Community_2": {
            "stress": 0.2, "slack": 0.7, "resilience": 0.8,
            "hidden_climate": 0.6, "hidden_infra": 0.2,
            "hidden_community": 0.4, "hidden_human": 0.7,
            "centralization": 0.5,
        },
        "Governance_1": {
            "stress": 0.1, "slack": 0.9, "resilience": 0.85,
            "hidden_climate": 0.4, "hidden_infra": 0.3,
            "hidden_community": 0.2, "hidden_human": 0.6,
            "centralization": 0.8,
        },
    }
    edges = {
        ("Community_1", "Governance_1"): 0.5,
        ("Community_2", "Governance_1"): 0.7,
        ("Community_1", "Community_2"): 0.3,
    }
    return CommunityNetwork.from_dict(nodes, edges)


def main() -> None:
    net = _build_default_network()
    propagator = StressPropagator(net)
    df = propagator.run()
    print(df.to_string())


if __name__ == "__main__":
    main()
