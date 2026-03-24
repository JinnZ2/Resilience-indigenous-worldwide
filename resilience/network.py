"""Network graph definitions for community resilience modeling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import networkx as nx


@dataclass
class NodeAttributes:
    """Attributes for a single community or governance node."""

    stress: float = 0.1
    slack: float = 0.8
    resilience: float = 0.9
    centralization: float = 0.3
    hidden_climate: float = 0.2
    hidden_infra: float = 0.1
    hidden_community: float = 0.3
    hidden_human: float = 0.5

    def to_dict(self) -> dict:
        return {
            "stress": self.stress,
            "slack": self.slack,
            "resilience": self.resilience,
            "centralization": self.centralization,
            "hidden_climate": self.hidden_climate,
            "hidden_infra": self.hidden_infra,
            "hidden_community": self.hidden_community,
            "hidden_human": self.hidden_human,
        }


class CommunityNetwork:
    """Graph-based representation of community and governance nodes.

    Wraps a networkx DiGraph with convenience methods for adding
    communities, governance structures, and weighted edges.
    """

    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def add_node(self, name: str, attrs: NodeAttributes | None = None) -> None:
        """Add a community or governance node."""
        attrs = attrs or NodeAttributes()
        self.graph.add_node(name, **attrs.to_dict())

    def add_edge(self, source: str, target: str, weight: float = 0.5) -> None:
        """Add a weighted directed edge between nodes."""
        self.graph.add_edge(source, target, weight=weight)

    def get_node_attr(self, name: str) -> dict:
        """Return attribute dict for a node."""
        return dict(self.graph.nodes[name])

    def set_node_attr(self, name: str, key: str, value: float) -> None:
        """Update a single attribute on a node."""
        self.graph.nodes[name][key] = value

    @property
    def nodes(self) -> List[str]:
        return list(self.graph.nodes)

    @property
    def edges(self) -> List[Tuple[str, str]]:
        return list(self.graph.edges)

    def edge_weight(self, source: str, target: str) -> float:
        return self.graph[source][target]["weight"]

    @classmethod
    def from_dict(
        cls,
        nodes: Dict[str, dict],
        edges: Dict[Tuple[str, str], float],
    ) -> "CommunityNetwork":
        """Build a network from the legacy dict format used in Hidden-variable.py."""
        net = cls()
        for name, attrs in nodes.items():
            net.graph.add_node(name, **attrs)
        for (src, tgt), w in edges.items():
            net.add_edge(src, tgt, weight=w)
        return net
