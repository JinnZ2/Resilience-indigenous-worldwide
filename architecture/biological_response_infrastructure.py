"""
biological_response_infrastructure.py

Distributed infrastructure with local constraint sensing and immediate
response, modeled on biological immune / metabolic systems. Central
authority validates *after* the fact, never blocks response *before*
the fact.

## Premise

Cells do not ask permission to respond to tissue damage. An immune
system that waited for central authorization would be a dead immune
system. Biological resilience is maximally distributed decision-making
with immediate local feedback and *post hoc* audit, not pre-emptive
permitting.

Current regulatory infrastructure inverts this: communities must
request central approval before responding to local constraints
(washed-out creek, failed septic, lost grid power). By the time
approval arrives, the local system has degraded -- same pathology
as a finger waiting for brain authorization while infection
propagates.

This module models the inversion. Nodes sense local damage, respond
within a response-latency window, log the response, and central
audit reviews afterward. The metric: does the network survive
versus does it die waiting.

## Linkage

Extends institutional_audit.py and constraint_filter_architecture.py.
The regulatory premises that block distributed response
(`permission_before_response`, `centralized_authority_assumed`)
are added to the filter set.

License: CC0
Stdlib only.
"""

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Callable
import math

# -----------------------------------------------------------
# 1. Node: a local infrastructure cell with sensing and response capacity
# -----------------------------------------------------------

@dataclass
class Node:
    """
    A local infrastructure cell. Has constraint sensors, response
    capacity, and a connection list to neighbors. Decisions are
    local; central audit is post hoc.
    """
    id: str
    function: str                       # "water", "power", "transit", etc.
    capacity: float = 1.0               # current load-bearing fraction (1.0 = healthy)
    damage_threshold: float = 0.3       # below this, node is failing
    response_latency_steps: int = 1     # how fast it can react
    neighbors: list[str] = field(default_factory=list)
    autonomous: bool = True             # can it respond without central approval?
    last_response_step: int = -1
    audit_log: list[dict] = field(default_factory=list)

    def sense_damage(self) -> float:
        """Return damage level. 0 = healthy, 1 = fully failed."""
        return max(0.0, 1.0 - self.capacity)

    def can_respond(self, current_step: int) -> bool:
        if not self.autonomous:
            return False
        return (current_step - self.last_response_step) >= self.response_latency_steps

    def respond(self, current_step: int, repair_rate: float = 0.3) -> dict:
        """Local immediate response. Logs the event for later audit."""
        damage = self.sense_damage()
        gain = min(damage, repair_rate)
        self.capacity += gain
        self.last_response_step = current_step
        event = {
            "step": current_step,
            "node": self.id,
            "damage_sensed": damage,
            "repair_applied": gain,
            "post_capacity": self.capacity,
        }
        self.audit_log.append(event)
        return event


# -----------------------------------------------------------
# 2. Network: collection of nodes with mesh topology
# -----------------------------------------------------------

@dataclass
class Network:
    name: str
    nodes: dict[str, Node]
    central_authority_latency_steps: int = 30
    central_authority_required: bool = False

    def neighbors_of(self, node_id: str) -> list[Node]:
        n = self.nodes[node_id]
        return [self.nodes[nid] for nid in n.neighbors if nid in self.nodes]

    def total_capacity(self) -> float:
        return sum(n.capacity for n in self.nodes.values())

    def healthy_fraction(self) -> float:
        n_healthy = sum(1 for n in self.nodes.values()
                        if n.sense_damage() < n.damage_threshold)
        return n_healthy / len(self.nodes) if self.nodes else 0.0

    def has_collapsed(self) -> bool:
        """Network is collapsed if more than half the nodes have failed."""
        return self.healthy_fraction() < 0.5


# -----------------------------------------------------------
# 3. Damage events: external shocks distributed across the network
# -----------------------------------------------------------

@dataclass
class DamageEvent:
    step: int
    target_nodes: list[str]
    severity: float                  # capacity reduction per node

    def apply(self, net: Network) -> None:
        for nid in self.target_nodes:
            if nid in net.nodes:
                net.nodes[nid].capacity = max(0.0,
                                              net.nodes[nid].capacity - self.severity)


# -----------------------------------------------------------
# 4. Two response regimes
# -----------------------------------------------------------

def step_biological(net: Network, current_step: int,
                    repair_rate: float = 0.3) -> list[dict]:
    """
    Each node senses local damage and responds immediately if able.
    No central approval gate. Biological mode.
    """
    events = []
    for node in net.nodes.values():
        if node.sense_damage() > 0.05 and node.can_respond(current_step):
            events.append(node.respond(current_step, repair_rate))
    return events


def step_permission_required(net: Network, current_step: int,
                             repair_rate: float = 0.3,
                             pending: dict | None = None) -> tuple[list[dict], dict]:
    """
    Nodes must request central permission. Repairs only occur after
    central_authority_latency_steps have elapsed. Permitting mode.
    """
    pending = pending if pending is not None else {}
    events = []

    # collect new requests
    for node in net.nodes.values():
        if node.sense_damage() > 0.05 and node.id not in pending:
            pending[node.id] = current_step    # request submitted at this step

    # service pending requests when latency elapses
    ready_ids = [
        nid for nid, submitted in list(pending.items())
        if (current_step - submitted) >= net.central_authority_latency_steps
    ]
    for nid in ready_ids:
        node = net.nodes.get(nid)
        if node and node.sense_damage() > 0.05:
            ev = node.respond(current_step, repair_rate)
            ev["permit_wait_steps"] = current_step - pending[nid]
            events.append(ev)
        pending.pop(nid, None)
    return events, pending


# -----------------------------------------------------------
# 5. Damage propagation (untended damage spreads to neighbors)
# -----------------------------------------------------------

def propagate_damage(net: Network, spread_rate: float = 0.05) -> None:
    """
    Damaged nodes degrade their neighbors a little each step. Sepsis
    analog: untended local failure spreads to adjacent tissue.
    """
    updates = {}
    for node in net.nodes.values():
        if node.sense_damage() > node.damage_threshold:
            for nb in net.neighbors_of(node.id):
                updates[nb.id] = updates.get(nb.id, 0.0) + spread_rate
    for nid, dec in updates.items():
        net.nodes[nid].capacity = max(0.0, net.nodes[nid].capacity - dec)


# -----------------------------------------------------------
# 6. Simulation harness
# -----------------------------------------------------------

def simulate(net: Network,
             damage_schedule: list[DamageEvent],
             steps: int,
             repair_rate: float = 0.3,
             spread_rate: float = 0.05) -> dict:
    schedule_by_step = defaultdict(list)
    for ev in damage_schedule:
        schedule_by_step[ev.step].append(ev)

    history = []
    pending: dict[str, int] = {}
    collapsed_at = None

    for step in range(1, steps + 1):
        # apply scheduled damage
        for ev in schedule_by_step.get(step, []):
            ev.apply(net)

        # respond (mode chosen by network configuration)
        if net.central_authority_required:
            _, pending = step_permission_required(net, step, repair_rate, pending)
        else:
            step_biological(net, step, repair_rate)

        # untended damage spreads
        propagate_damage(net, spread_rate)

        # record
        history.append({
            "step": step,
            "total_capacity": net.total_capacity(),
            "healthy_fraction": net.healthy_fraction(),
        })
        if net.has_collapsed() and collapsed_at is None:
            collapsed_at = step

    return {
        "network": net.name,
        "mode": "permission_required" if net.central_authority_required else "biological",
        "steps": steps,
        "final_capacity": net.total_capacity(),
        "final_healthy_fraction": net.healthy_fraction(),
        "collapsed_at": collapsed_at,
        "history": history,
    }


# -----------------------------------------------------------
# 7. Network builders
# -----------------------------------------------------------

def mesh_network(name: str, n_nodes: int, function: str = "water",
                 central_required: bool = False,
                 central_latency: int = 30) -> Network:
    """
    Build a mesh: each node connects to its 4 nearest neighbors
    on a sqrt(n) x sqrt(n) lattice. Biology-like local adjacency.
    """
    side = int(math.sqrt(n_nodes))
    nodes: dict[str, Node] = {}
    for i in range(side):
        for j in range(side):
            nid = f"{function}_{i}_{j}"
            neighbors = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < side and 0 <= nj < side:
                    neighbors.append(f"{function}_{ni}_{nj}")
            nodes[nid] = Node(id=nid, function=function, neighbors=neighbors,
                              autonomous=not central_required)
    return Network(name=name, nodes=nodes,
                   central_authority_required=central_required,
                   central_authority_latency_steps=central_latency)


# -----------------------------------------------------------
# 8. Falsifiable claims
# -----------------------------------------------------------

CLAIMS = [
    "Local-response networks survive damage shocks that permission-gated networks do not.",
    "Damage propagation rate exceeds central-authority latency in distributed shocks; the math is not subjective.",
    "Audit-after preserves accountability without blocking response; pre-permitting blocks response without improving outcome.",
    "Mesh topology with autonomous nodes is a biological-immune analog; the resilience properties transfer.",
    "Regulations enforcing centralized authority over local response carry the same premise failure as legacy building codes.",
    "Communities with composting toilets, mesh networking, distributed power are biological-mode infrastructure.",
    "The cost of a permission system exceeds the cost of post-hoc audit by a factor proportional to network size and shock frequency.",
]


# -----------------------------------------------------------
# 9. Demo: identical shock applied to two identical networks
# -----------------------------------------------------------

if __name__ == "__main__":
    n_nodes = 64
    steps = 120

    # identical shock schedule for both networks
    shocks = [
        DamageEvent(step=10, target_nodes=["water_0_0", "water_1_0", "water_2_0"], severity=0.6),
        DamageEvent(step=25, target_nodes=["water_3_3", "water_4_4"], severity=0.7),
        DamageEvent(step=50, target_nodes=["water_5_5", "water_6_6", "water_7_7"], severity=0.5),
        DamageEvent(step=75, target_nodes=["water_1_4", "water_2_5"], severity=0.6),
        DamageEvent(step=95, target_nodes=["water_4_1", "water_5_2", "water_6_3"], severity=0.7),
    ]

    bio_net = mesh_network("biological_mesh", n_nodes, central_required=False)
    perm_net = mesh_network("permission_required", n_nodes, central_required=True,
                            central_latency=30)

    bio_result = simulate(bio_net, shocks, steps)
    perm_result = simulate(perm_net, shocks, steps)

    print("=" * 70)
    print("BIOLOGICAL MODE (local autonomous response)")
    print("=" * 70)
    print(f"  final_capacity       = {bio_result['final_capacity']:.2f}")
    print(f"  final_healthy_frac   = {bio_result['final_healthy_fraction']:.2f}")
    print(f"  collapsed_at         = {bio_result['collapsed_at']}")

    print("\n" + "=" * 70)
    print("PERMISSION-REQUIRED MODE (central authority latency = 30 steps)")
    print("=" * 70)
    print(f"  final_capacity       = {perm_result['final_capacity']:.2f}")
    print(f"  final_healthy_frac   = {perm_result['final_healthy_fraction']:.2f}")
    print(f"  collapsed_at         = {perm_result['collapsed_at']}")

    print("\n" + "=" * 70)
    print("THERMODYNAMIC DELTA")
    print("=" * 70)
    delta_cap = bio_result["final_capacity"] - perm_result["final_capacity"]
    delta_health = bio_result["final_healthy_fraction"] - perm_result["final_healthy_fraction"]
    print(f"  capacity advantage of biological mode: {delta_cap:+.2f}")
    print(f"  health advantage of biological mode:   {delta_health:+.2%}")
    if perm_result["collapsed_at"] and not bio_result["collapsed_at"]:
        print(f"  permission network collapsed at step {perm_result['collapsed_at']};"
              f" biological network survived all {steps} steps")
