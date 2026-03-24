"""Visualization utilities for stress propagation and risk analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from resilience.network import CommunityNetwork


def plot_stress_history(
    df: pd.DataFrame,
    title: str = "Stress Propagation Over Time",
    output_path: Optional[Path] = None,
) -> None:
    """Line plot of stress levels per node over simulation timesteps."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for col in df.columns:
        ax.plot(df.index, df[col], marker="o", label=col)
    ax.set_xlabel("Timestep")
    ax.set_ylabel("Stress Level")
    ax.set_title(title)
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(True, alpha=0.3)
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def plot_risk_breakdown(
    scores: dict,
    title: str = "Risk Score by Category",
    output_path: Optional[Path] = None,
) -> None:
    """Horizontal bar chart of risk category scores."""
    labels = [k.value if hasattr(k, "value") else str(k) for k in scores]
    values = list(scores.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#d32f2f" if v >= 0.5 else "#ff9800" if v >= 0.25 else "#4caf50" for v in values]
    ax.barh(labels, values, color=colors)
    ax.set_xlabel("Risk Score")
    ax.set_title(title)
    ax.set_xlim(0, 1.0)
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def plot_network(
    network: CommunityNetwork,
    title: str = "Community Network",
    output_path: Optional[Path] = None,
) -> None:
    """Visualize the community network graph with stress-based coloring."""
    import networkx as nx

    g = network.graph
    stress_vals = [g.nodes[n].get("stress", 0) for n in g.nodes]

    fig, ax = plt.subplots(figsize=(8, 6))
    pos = nx.spring_layout(g, seed=42)
    nx.draw_networkx(
        g,
        pos,
        ax=ax,
        node_color=stress_vals,
        cmap=plt.cm.YlOrRd,
        vmin=0,
        vmax=1,
        node_size=800,
        font_size=9,
        edge_color="#999999",
        width=2,
    )
    sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=plt.Normalize(0, 1))
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label="Stress Level")
    ax.set_title(title)
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)
