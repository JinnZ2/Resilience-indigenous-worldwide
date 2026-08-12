"""Tests for resilience.network — CommunityNetwork and NodeAttributes."""

import pytest

from resilience.network import CommunityNetwork, NodeAttributes


def test_node_attributes_defaults():
    attrs = NodeAttributes()
    assert 0.0 <= attrs.stress <= 1.0
    assert 0.0 <= attrs.resilience <= 1.0


def test_node_attributes_to_dict():
    attrs = NodeAttributes(stress=0.5, slack=0.6)
    d = attrs.to_dict()
    assert d["stress"] == 0.5
    assert d["slack"] == 0.6
    assert "hidden_climate" in d


def test_add_and_retrieve_node():
    net = CommunityNetwork()
    net.add_node("Bois Forte")
    assert "Bois Forte" in net.nodes
    attr = net.get_node_attr("Bois Forte")
    assert "stress" in attr


def test_add_node_custom_attrs():
    net = CommunityNetwork()
    net.add_node("Grand Portage", NodeAttributes(stress=0.8, resilience=0.4))
    attr = net.get_node_attr("Grand Portage")
    assert attr["stress"] == 0.8
    assert attr["resilience"] == 0.4


def test_add_edge_and_weight():
    net = CommunityNetwork()
    net.add_node("A")
    net.add_node("B")
    net.add_edge("A", "B", weight=0.7)
    assert ("A", "B") in net.edges
    assert net.edge_weight("A", "B") == pytest.approx(0.7)


def test_set_node_attr():
    net = CommunityNetwork()
    net.add_node("C")
    net.set_node_attr("C", "stress", 0.99)
    assert net.get_node_attr("C")["stress"] == pytest.approx(0.99)


def test_from_dict_roundtrip():
    nodes = {
        "Fond du Lac": {"stress": 0.3, "slack": 0.7, "resilience": 0.8,
                        "centralization": 0.2, "hidden_climate": 0.1,
                        "hidden_infra": 0.1, "hidden_community": 0.2,
                        "hidden_human": 0.4},
    }
    edges = {("Fond du Lac", "Fond du Lac"): 0.0}
    net = CommunityNetwork.from_dict(nodes, edges)
    assert "Fond du Lac" in net.nodes
    assert net.get_node_attr("Fond du Lac")["stress"] == pytest.approx(0.3)


def test_empty_network():
    net = CommunityNetwork()
    assert net.nodes == []
    assert net.edges == []


def test_multiple_edges():
    net = CommunityNetwork()
    for name in ["X", "Y", "Z"]:
        net.add_node(name)
    net.add_edge("X", "Y", 0.3)
    net.add_edge("Y", "Z", 0.6)
    net.add_edge("X", "Z", 0.9)
    assert len(net.edges) == 3
