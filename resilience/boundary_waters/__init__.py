"""Boundary Waters (BWCA) sulfide-mine cascade model.

Ported from JinnZ2/earth-systems-physics/boundary_waters (CC0).
Models a 500-year cascade from acid rock drainage through hydrology,
ecology, community displacement, port economics, and international
treaty liability under the Boundary Waters Treaty of 1909.

Indigenous focus: 1854 Treaty ceded territory, Bois Forte, Grand
Portage, and Fond du Lac Bands of Lake Superior Chippewa, and the
manoomin (wild rice) harvest protected under usufructuary rights.
"""

from resilience.boundary_waters.cascade import run_cascade, summarize
from resilience.boundary_waters.export import export_all

__all__ = ["run_cascade", "summarize", "export_all"]
