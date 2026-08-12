import numpy as np
import pandas as pd

# --- Define nodes ---
nodes = {
    "Community_1": {"stress":0.1, "slack":0.8, "resilience":0.9, "hidden_climate":0.2,
                    "hidden_infra":0.1, "hidden_community":0.3, "hidden_human":0.5, "centralization":0.3},
    "Community_2": {"stress":0.2, "slack":0.7, "resilience":0.8, "hidden_climate":0.6,
                    "hidden_infra":0.2, "hidden_community":0.4, "hidden_human":0.7, "centralization":0.5},
    "Governance_1": {"stress":0.1, "slack":0.9, "resilience":0.85, "hidden_climate":0.4,
                     "hidden_infra":0.3, "hidden_community":0.2, "hidden_human":0.6, "centralization":0.8},
    # add more nodes as needed
}

# --- Define edge weights ---
edges = {
    ("Community_1","Governance_1"): 0.5,
    ("Community_2","Governance_1"): 0.7,
    ("Community_1","Community_2"): 0.3,
}

# --- Threshold amplification function ---
def threshold_amplification(stress, threshold=0.6, factor=1.5):
    return factor*(stress-threshold) if stress > threshold else 0

# --- Propagation function ---
def propagate_stress(nodes, edges):
    new_nodes = {k: nodes[k].copy() for k in nodes}
    for j in nodes:
        stress_increment = 0
        for i in nodes:
            if (i,j) in edges:
                w = edges[(i,j)]
                S_i = nodes[i]["stress"]
                slack_i = nodes[i]["slack"]
                central_delay = nodes[j]["centralization"]  # amplifies stress if centralized
                stress_increment += w * S_i * (1 - slack_i) * (1 + central_delay)
        # Hidden variables
        H_c = nodes[j]["hidden_climate"]
        H_i = nodes[j]["hidden_infra"]
        H_comm = nodes[j]["hidden_community"]
        H_h = nodes[j]["hidden_human"]
        stress_new = nodes[j]["stress"] + stress_increment + H_c*(1-nodes[j]["resilience"]) + H_i + H_comm + threshold_amplification(nodes[j]["stress"])
        stress_new += H_h * threshold_amplification(nodes[j]["stress"])
        new_nodes[j]["stress"] = min(stress_new, 1.0)
    return new_nodes

# --- Time evolution ---
timesteps = 10
history = []

for t in range(timesteps):
    nodes = propagate_stress(nodes, edges)
    history.append({k: nodes[k]["stress"] for k in nodes})

df_history = pd.DataFrame(history)
print(df_history)
