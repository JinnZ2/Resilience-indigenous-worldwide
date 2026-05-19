"""
distributed_node_economy.py
============================
CC0. stdlib only. Falsifiable.

Models economies where geographic/cultural fragmentation is treated as
STRUCTURAL FEATURE rather than vulnerability. Each node operates
semi-autonomously, matched to its local constraint set. Inter-node
trade happens through direct exchange, with central coordination
limited to standards and dispute resolution.

Core inversion: fragmentation = distributed resilience.
Centralization converts distributed resilience into monocultural
vulnerability through single-point-of-failure architecture.

Falsifiable claim: distributed-node economies show higher cascade
resistance than centralized economies when stressed by external
shocks (price collapse, supply chain failure, political disruption).

Author: Kavik (JinnZ2)
License: CC0
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------
# NODE AND NETWORK STRUCTURES
# ---------------------------------------------------------------------

@dataclass
class GeographicNode:
    """A semi-autonomous economic node defined by geography/culture."""
    name: str
    terrain: str                          # altitude, climate, water availability
    natural_resources: list               # what the geography produces
    natural_energy: list                  # solar, wind, geothermal, gravity, hydro
    indigenous_knowledge: list            # generational adaptations to this terrain
    carrying_capacity: dict               # water, food, population limits
    production_specialties: list = field(default_factory=list)
    surplus_potential: list = field(default_factory=list)
    deficit_needs: list = field(default_factory=list)


@dataclass
class InterNodeRelation:
    """Trade relationship between two nodes."""
    node_a: str
    node_b: str
    a_provides: list                      # what flows from A to B
    b_provides: list                      # what flows from B to A
    exchange_basis: str                   # "direct_barter", "regional_credit", "mixed"
    distance: float                       # km
    transport_cost_relative: float        # 0-1, lower is cheaper
    trust_level: str                      # "high", "developing", "low"


@dataclass
class DistributedEconomy:
    """A full network of nodes with inter-node relations."""
    name: str
    nodes: list
    relations: list
    coordination_layer: str               # "minimal", "standards_only", "active_governance"
    external_interface: str               # how it interacts with global economy
    resilience_features: list = field(default_factory=list)


# ---------------------------------------------------------------------
# BOLIVIA EXAMPLE: distributed node geometry
# ---------------------------------------------------------------------

ALTIPLANO_NODE = GeographicNode(
    name="Altiplano (high plateau)",
    terrain="3500-4500m elevation, cold, dry, large salt flats",
    natural_resources=["lithium brines", "quinoa", "llama/alpaca", "salt"],
    natural_energy=["solar (high UV)", "wind (consistent)", "gravity (altitude differential)"],
    indigenous_knowledge=[
        "altitude agriculture (Aymara, Quechua)",
        "camelid husbandry",
        "salt extraction and trade",
        "water conservation in arid conditions",
    ],
    carrying_capacity={
        "water_recharge_rate_low": True,
        "agricultural_limit": "modest, altitude-restricted crops",
        "lithium_extraction_limit": "water-bounded",
    },
    production_specialties=["lithium products", "quinoa", "camelid fiber", "salt"],
    surplus_potential=["solar electricity", "lithium battery storage", "salt"],
    deficit_needs=["tropical fruits", "wood", "lowland crops", "fish"],
)

YUNGAS_NODE = GeographicNode(
    name="Yungas (cloud forest)",
    terrain="1000-2500m, subtropical, high rainfall",
    natural_resources=["coca", "coffee", "citrus", "timber", "medicinal plants"],
    natural_energy=["hydro (abundant water)", "biomass"],
    indigenous_knowledge=[
        "traditional cultivation of multiple crops",
        "medicinal plant systems",
        "forest management",
    ],
    carrying_capacity={
        "water_abundant": True,
        "agricultural_limit": "high, diverse crop range",
    },
    production_specialties=["coffee", "fruits", "medicinal plants", "timber"],
    surplus_potential=["food crops", "hydroelectric power", "wood"],
    deficit_needs=["minerals", "lithium products", "altitude-grown grains"],
)

AMAZON_NODE = GeographicNode(
    name="Bolivian Amazon",
    terrain="tropical lowland, high biodiversity",
    natural_resources=["timber", "rubber", "Brazil nuts", "biodiversity", "river fish"],
    natural_energy=["biomass", "river hydro"],
    indigenous_knowledge=[
        "forest pharmacology",
        "river navigation and fishing",
        "agroforestry systems",
    ],
    carrying_capacity={
        "biodiversity_high": True,
        "extraction_sensitivity": "very high (cannot tolerate industrial scale)",
    },
    production_specialties=["nuts", "fish", "sustainable timber", "medicinals"],
    surplus_potential=["food", "specialty agriculture"],
    deficit_needs=["minerals", "manufactured goods", "lithium products"],
)

VALLES_NODE = GeographicNode(
    name="Valles (inter-Andean valleys)",
    terrain="1500-2800m, temperate, moderate rainfall",
    natural_resources=["maize", "wheat", "potatoes", "fruit", "livestock"],
    natural_energy=["small hydro", "solar", "biomass"],
    indigenous_knowledge=[
        "diverse agricultural systems",
        "terracing",
        "livestock-crop integration",
    ],
    carrying_capacity={
        "water_moderate": True,
        "agricultural_limit": "high, broad crop range",
    },
    production_specialties=["grains", "potatoes", "dairy", "fruit"],
    surplus_potential=["staple foods", "livestock products"],
    deficit_needs=["lithium products", "tropical goods", "minerals"],
)

BOLIVIA_DISTRIBUTED = DistributedEconomy(
    name="Bolivia Distributed Node Model",
    nodes=[ALTIPLANO_NODE, YUNGAS_NODE, AMAZON_NODE, VALLES_NODE],
    relations=[
        InterNodeRelation(
            node_a="Altiplano", node_b="Yungas",
            a_provides=["lithium products", "salt", "camelid fiber"],
            b_provides=["coffee", "fruits", "medicinal plants"],
            exchange_basis="direct_barter",
            distance=200, transport_cost_relative=0.3,
            trust_level="high (historical trade routes)",
        ),
        InterNodeRelation(
            node_a="Altiplano", node_b="Valles",
            a_provides=["lithium batteries", "salt", "quinoa"],
            b_provides=["grains", "potatoes", "fruit", "dairy"],
            exchange_basis="direct_barter",
            distance=300, transport_cost_relative=0.4,
            trust_level="high",
        ),
        InterNodeRelation(
            node_a="Yungas", node_b="Amazon",
            a_provides=["coffee", "altitude crops"],
            b_provides=["nuts", "fish", "tropical goods"],
            exchange_basis="direct_barter",
            distance=400, transport_cost_relative=0.5,
            trust_level="developing",
        ),
    ],
    coordination_layer="minimal (standards for measure; dispute resolution councils)",
    external_interface="limited; only surplus beyond local needs traded externally",
    resilience_features=[
        "no single-point-of-failure",
        "each node has independent energy production",
        "each node has independent food production",
        "if external market collapses, internal trade continues",
        "if one node fails, others continue",
        "geographic isolation prevents single regulatory capture",
    ],
)


# ---------------------------------------------------------------------
# RESILIENCE METRICS
# ---------------------------------------------------------------------

def cascade_resistance_score(economy: DistributedEconomy) -> dict:
    """
    Calculates cascade resistance based on:
    - node count (more = more redundancy)
    - node autonomy (more independent each is, more resilient)
    - inter-node trade diversity (more pairs = more paths)
    - dependence on external systems (less = more resilient)
    """
    node_count = len(economy.nodes)
    relation_count = len(economy.relations)
    max_possible_relations = (node_count * (node_count - 1)) // 2
    relation_density = relation_count / max_possible_relations if max_possible_relations > 0 else 0

    autonomy_factors = []
    for node in economy.nodes:
        has_food = any("food" in s.lower() or "crop" in s.lower() or "grain" in s.lower()
                       for s in node.production_specialties)
        has_energy = len(node.natural_energy) > 0
        has_water = node.carrying_capacity.get("water_abundant", False) or \
                    node.carrying_capacity.get("water_moderate", False)
        autonomy_factors.append((has_food, has_energy, has_water))

    autonomy_score = sum(sum(f) for f in autonomy_factors) / (len(autonomy_factors) * 3) \
                     if autonomy_factors else 0

    return {
        "node_count": node_count,
        "relation_density": round(relation_density, 2),
        "autonomy_score": round(autonomy_score, 2),
        "cascade_resistance_indicator": round(
            (node_count * 0.3) + (relation_density * 0.3) + (autonomy_score * 0.4), 2
        ),
        "interpretation": "higher = more cascade resistant",
    }


# ---------------------------------------------------------------------
# CENTRALIZED vs DISTRIBUTED COMPARISON
# ---------------------------------------------------------------------

def compare_geometries(centralized: dict, distributed: DistributedEconomy) -> dict:
    """
    Compares centralized economy (specified as dict) against distributed.

    centralized format:
        {
            "name": str,
            "single_resource_dependence": bool,
            "external_currency_required": bool,
            "central_authority": bool,
            "regional_autonomy": bool,
        }
    """
    return {
        "centralized_vulnerability": {
            "single_point_failure": centralized.get("single_resource_dependence", True),
            "external_currency_lock": centralized.get("external_currency_required", True),
            "central_authority_capture_risk": centralized.get("central_authority", True),
            "no_regional_autonomy": not centralized.get("regional_autonomy", False),
        },
        "distributed_resilience": {
            "node_count": len(distributed.nodes),
            "trade_paths": len(distributed.relations),
            "autonomy_features": distributed.resilience_features,
        },
        "prediction": (
            "under external shock (price collapse, supply disruption), "
            "distributed economy continues to function via internal trade; "
            "centralized economy experiences cascade failure"
        ),
    }


# ---------------------------------------------------------------------
# IMPLEMENTATION PRINCIPLES
# ---------------------------------------------------------------------

IMPLEMENTATION_PRINCIPLES = {
    "geography_first": "design nodes around what the terrain actually produces, not what external markets demand",
    "local_knowledge_first": "indigenous and place-based knowledge is the starting point, not the optimization target",
    "minimal_coordination": "shared standards and dispute resolution only; not active management",
    "trade_through_surplus": "only what's beyond local needs leaves the node",
    "energy_per_node": "each node generates and stores its own electricity",
    "food_per_node": "each node aims for food self-sufficiency",
    "water_per_node": "each node manages its own water within carrying capacity",
    "exit_optional": "any node can disengage from network without external permission",
}


# ---------------------------------------------------------------------
# FALSIFIABLE PREDICTIONS
# ---------------------------------------------------------------------

FALSIFIABLE_PREDICTIONS = [
    {
        "claim": "distributed-node economies survive external shocks (commodity price collapse, supply chain failure) with measurably less population displacement and food insecurity than centralized economies",
        "test": "compare matched cases: countries with strong regional autonomy vs centralized states during 2008, 2020, 2022 shocks",
        "evidence_required": "displacement and food insecurity metrics by political-economic structure",
        "falsified_if": "centralized economies show equal or better outcomes under shock",
    },
    {
        "claim": "fragmented geography produces more resilient outcomes than unified geography when each region is permitted to specialize to local conditions",
        "test": "compare Switzerland (fragmented, autonomous cantons) vs France (centralized) on resilience metrics",
        "evidence_required": "crisis-response data over multiple events",
        "falsified_if": "centralized France shows superior resilience",
    },
    {
        "claim": "central coordination limited to standards and dispute resolution produces better outcomes than active management",
        "test": "compare distributed-governance regions with active vs minimal coordination",
        "evidence_required": "outcome metrics across both types",
        "falsified_if": "active management shows superior outcomes",
    },
]


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("DISTRIBUTED NODE ECONOMY MODEL")
    print("=" * 60)
    print(f"\nExample: {BOLIVIA_DISTRIBUTED.name}")
    print(f"Nodes: {len(BOLIVIA_DISTRIBUTED.nodes)}")
    print(f"Trade relations: {len(BOLIVIA_DISTRIBUTED.relations)}")

    resistance = cascade_resistance_score(BOLIVIA_DISTRIBUTED)
    print(f"\nCascade resistance: {resistance['cascade_resistance_indicator']}")
    for key, val in resistance.items():
        print(f"  {key}: {val}")

    print(f"\nImplementation principles: {len(IMPLEMENTATION_PRINCIPLES)}")
    print(f"Falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
