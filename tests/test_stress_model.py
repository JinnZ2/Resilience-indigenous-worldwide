"""Tests for the stress propagation model."""

from resilience.network import CommunityNetwork, NodeAttributes
from resilience.stress_model import PropagationConfig, StressPropagator


def _simple_network() -> CommunityNetwork:
    net = CommunityNetwork()
    net.add_node("A", NodeAttributes(stress=0.1, slack=0.8, resilience=0.9))
    net.add_node("B", NodeAttributes(stress=0.2, slack=0.7, resilience=0.8))
    net.add_edge("A", "B", weight=0.5)
    return net


def test_propagation_increases_stress():
    net = _simple_network()
    prop = StressPropagator(net, PropagationConfig(timesteps=5))
    df = prop.run()
    assert df["B"].iloc[-1] > df["B"].iloc[0], "Stress should increase over time"


def test_stress_capped_at_one():
    net = _simple_network()
    prop = StressPropagator(net, PropagationConfig(timesteps=50))
    df = prop.run()
    assert df.max().max() <= 1.0, "Stress should never exceed 1.0"


def test_history_length_matches_timesteps():
    net = _simple_network()
    cfg = PropagationConfig(timesteps=7)
    prop = StressPropagator(net, cfg)
    df = prop.run()
    assert len(df) == 7


def test_reset_clears_history():
    net = _simple_network()
    prop = StressPropagator(net)
    prop.run()
    prop.reset()
    assert len(prop.history) == 0


def test_threshold_amplification_below_threshold():
    net = _simple_network()
    prop = StressPropagator(net, PropagationConfig(threshold=0.6))
    assert prop.threshold_amplification(0.3) == 0.0


def test_threshold_amplification_above_threshold():
    net = _simple_network()
    prop = StressPropagator(net, PropagationConfig(threshold=0.6, amplification_factor=1.5))
    result = prop.threshold_amplification(0.8)
    assert abs(result - 0.3) < 1e-9
