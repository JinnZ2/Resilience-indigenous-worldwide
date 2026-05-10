"""
regulatory_scope_audit.py

Audit regulations against their declared scope. Surface when a rule
is being applied outside the conditions it was designed for, so
communities can respond to actual constraints without violating the
regulation's original good-faith intent.

## Premise

Every regulation was written for a specific operating envelope --
a thermal range, a population density, a substrate stability, an
infrastructure assumption. When real conditions exit that envelope,
the regulation is *outside its scope*. Continuing to enforce it
inverts its original purpose and produces the harm it was meant
to prevent.

## The framework

For each regulation, record:

  - its first-principle intent (what harm it was meant to prevent)
  - its declared or inferred scope (when those conditions hold)
  - the current actual conditions

If actual conditions are outside scope, the regulation is flagged
as expired *for that situation*. The intent is preserved; the
specific rule is suspended pending an updated rule that addresses
the new conditions.

This protects communities legally and ethically: they are honoring
the regulation's first-principle intent while exiting its expired
letter. Central authority retains the audit role -- it validates
afterward whether the local response served the intent. If yes,
the action stands. If no, central authority must produce a better
rule that fits the new conditions.

## Linkage

Pairs with biological_response_infrastructure.py (local autonomous
response) and constraint_filter_architecture.py (premise filtering).
The scope-audit is the legal-epistemic instrument that lets the
biological mode operate without being blocked by expired permission
regimes.

License: CC0
Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict

# -----------------------------------------------------------
# 1. Scope variable: a condition the regulation depends on
# -----------------------------------------------------------

@dataclass
class ScopeVar:
    """
    A single condition the regulation was designed for.
    e.g. 'population_density', range (0, 5000) per km^2.
    """
    name: str
    valid_range: tuple[float, float]
    units: str = ""

    def in_range(self, value: float) -> bool:
        return self.valid_range[0] <= value <= self.valid_range[1]


# -----------------------------------------------------------
# 2. Regulation: a rule with declared intent and scope
# -----------------------------------------------------------

@dataclass
class Regulation:
    """
    A regulation with its first-principle intent and the scope
    variables under which it was designed to operate.
    """
    id: str
    title: str
    jurisdiction: str
    year_enacted: int
    first_principle_intent: str           # what harm it was meant to prevent
    scope: list[ScopeVar] = field(default_factory=list)
    enforcement_text: str = ""            # the literal rule

    def in_scope(self, conditions: dict[str, float]) -> bool:
        for var in self.scope:
            if var.name not in conditions:
                return False
            if not var.in_range(conditions[var.name]):
                return False
        return True

    def scope_exit_signature(self, conditions: dict[str, float]) -> list[dict]:
        """Which variables have exited scope, by how much."""
        exits = []
        for var in self.scope:
            if var.name not in conditions:
                exits.append({"variable": var.name, "reason": "not_measured"})
                continue
            v = conditions[var.name]
            if not var.in_range(v):
                low, high = var.valid_range
                exits.append({
                    "variable": var.name,
                    "current_value": v,
                    "valid_range": (low, high),
                    "units": var.units,
                    "deviation": (v - high) if v > high else (v - low),
                })
        return exits


# -----------------------------------------------------------
# 3. Situation: actual local conditions a community is facing
# -----------------------------------------------------------

@dataclass
class Situation:
    id: str
    location: str
    description: str
    conditions: dict[str, float]
    declared_at: str = ""                 # ISO date string, optional


# -----------------------------------------------------------
# 4. Scope audit result
# -----------------------------------------------------------

@dataclass
class ScopeAudit:
    regulation: Regulation
    situation: Situation
    in_scope: bool
    scope_exits: list[dict]
    intent_still_applicable: bool         # is the harm-prevention purpose still relevant?

    def summary(self) -> str:
        if self.in_scope:
            return (f"[IN SCOPE] {self.regulation.id} applies normally "
                    f"to {self.situation.location}.")
        if not self.intent_still_applicable:
            return (f"[OUT OF SCOPE -- INTENT EXPIRED] {self.regulation.id} "
                    f"does not apply; the harm it was designed to prevent "
                    f"is not present in {self.situation.location}.")
        return (f"[OUT OF SCOPE -- INTENT PRESERVED] {self.regulation.id} "
                f"is outside its operating envelope at {self.situation.location}. "
                f"Local response should preserve the first-principle intent: "
                f"'{self.regulation.first_principle_intent}'. "
                f"Audit-after central authority retains validation right.")

    def deviations_human_readable(self) -> str:
        lines = []
        for ex in self.scope_exits:
            if "current_value" in ex:
                lines.append(
                    f"  {ex['variable']} = {ex['current_value']:.2f} {ex.get('units','')} "
                    f"(valid {ex['valid_range'][0]:.2f}-{ex['valid_range'][1]:.2f})"
                )
            else:
                lines.append(f"  {ex['variable']}: {ex['reason']}")
        return "\n".join(lines)


# -----------------------------------------------------------
# 5. Audit operations
# -----------------------------------------------------------

def audit(reg: Regulation, sit: Situation,
          intent_check: callable = None) -> ScopeAudit:
    """
    Run a scope audit. `intent_check` is an optional function
    that returns whether the original harm-prevention intent
    still applies under the current situation.
    """
    in_scope = reg.in_scope(sit.conditions)
    exits = reg.scope_exit_signature(sit.conditions)
    intent_applicable = True if intent_check is None else intent_check(reg, sit)
    return ScopeAudit(reg, sit, in_scope, exits, intent_applicable)


def audit_many(regs: list[Regulation], sit: Situation) -> list[ScopeAudit]:
    return [audit(r, sit) for r in regs]


# -----------------------------------------------------------
# 6. Local response permit: the constructive output of the audit
# -----------------------------------------------------------

@dataclass
class LocalResponseRecord:
    """
    What the community did, on what basis, with what timing.
    This is the post-hoc audit trail central authority reviews.
    """
    situation_id: str
    regulations_evaluated: list[str]
    out_of_scope_regulations: list[str]
    intent_preserved: list[str]
    action_taken: str
    rationale: str
    responder: str
    timestamp: str
    post_hoc_audit_due_by: str = ""

    def serialize(self) -> dict:
        return {
            "situation": self.situation_id,
            "regulations_evaluated": self.regulations_evaluated,
            "out_of_scope": self.out_of_scope_regulations,
            "intent_preserved": self.intent_preserved,
            "action": self.action_taken,
            "rationale": self.rationale,
            "responder": self.responder,
            "timestamp": self.timestamp,
            "audit_due_by": self.post_hoc_audit_due_by,
        }


def build_response_record(sit: Situation, audits: list[ScopeAudit],
                          action: str, rationale: str,
                          responder: str, timestamp: str,
                          audit_due_by: str = "") -> LocalResponseRecord:
    evaluated = [a.regulation.id for a in audits]
    oos = [a.regulation.id for a in audits if not a.in_scope]
    preserved = [a.regulation.first_principle_intent for a in audits
                 if not a.in_scope and a.intent_still_applicable]
    return LocalResponseRecord(
        situation_id=sit.id,
        regulations_evaluated=evaluated,
        out_of_scope_regulations=oos,
        intent_preserved=preserved,
        action_taken=action,
        rationale=rationale,
        responder=responder,
        timestamp=timestamp,
        post_hoc_audit_due_by=audit_due_by,
    )


# -----------------------------------------------------------
# 7. Falsifiable claims
# -----------------------------------------------------------

CLAIMS = [
    "A regulation outside its declared scope cannot serve its original intent; enforcing it inverts the intent.",
    "Communities preserving first-principle intent while exiting expired letter act inside the regulation's purpose, not against it.",
    "Post-hoc audit preserves accountability; pre-permitting blocks response without improving outcome.",
    "Scope-audit results are reproducible: same regulation, same situation, same conditions yield same finding.",
    "Burden of proof shifts to central authority to produce a scope-current rule when the legacy rule has exited scope.",
    "Imposed helplessness collapses when communities have an auditable instrument for distinguishing in-scope from out-of-scope regulation.",
]


# -----------------------------------------------------------
# 8. Demo
# -----------------------------------------------------------

if __name__ == "__main__":
    # ---- Example regulation 1: a centralized septic permit rule
    septic_rule = Regulation(
        id="MN_7080_subpart_X_legacy",
        title="Centralized municipal sewer connection requirement",
        jurisdiction="Minnesota -- urban density tier",
        year_enacted=1985,
        first_principle_intent="prevent groundwater contamination from improper "
                               "human waste disposal in high-density populations",
        scope=[
            ScopeVar("population_density_per_km2", (2000.0, 20000.0)),
            ScopeVar("groundwater_depth_m", (1.0, 30.0), units="m"),
            ScopeVar("lot_size_ha", (0.0, 0.2), units="ha"),
            ScopeVar("annual_rainfall_mm", (400.0, 1200.0), units="mm"),
        ],
        enforcement_text="All dwellings within municipal boundary must connect "
                         "to centralized sewer.",
    )

    # ---- Example regulation 2: a bridge permit rule from a high-budget era
    bridge_permit_rule = Regulation(
        id="STATE_BRIDGE_PERMIT_LEGACY",
        title="State-issued bridge construction permit",
        jurisdiction="State DOT, post-Interstate era",
        year_enacted=1972,
        first_principle_intent="ensure load-bearing safety on permanent "
                               "high-traffic vehicular bridges",
        scope=[
            ScopeVar("expected_daily_vehicles", (500.0, 50000.0)),
            ScopeVar("span_meters", (15.0, 500.0), units="m"),
            ScopeVar("design_life_years", (50.0, 100.0), units="yr"),
            ScopeVar("budget_usd_million", (1.0, 200.0), units="M USD"),
        ],
        enforcement_text="No bridge may be constructed without state DOT permit "
                         "and licensed engineer of record.",
    )

    # ---- Situation A: rural homestead, low density
    homestead = Situation(
        id="SIT_HOMESTEAD_2025",
        location="Grand Lake Township, St. Louis County, MN",
        description="Two-acre homestead, no municipal sewer access, well water, "
                    "composting toilet + graywater system proposed",
        conditions={
            "population_density_per_km2": 4.0,
            "groundwater_depth_m": 8.0,
            "lot_size_ha": 0.8,
            "annual_rainfall_mm": 720.0,
        },
    )

    # ---- Situation B: washed-out rural footbridge, community needs crossing
    footbridge = Situation(
        id="SIT_FOOTBRIDGE_2025",
        location="rural creek crossing serving 14 households",
        description="Seasonal creek washed out single-lane footbridge; "
                    "community-built 6-meter pedestrian crossing proposed",
        conditions={
            "expected_daily_vehicles": 0.0,        # foot traffic, not vehicular
            "span_meters": 6.0,
            "design_life_years": 20.0,
            "budget_usd_million": 0.004,
        },
    )

    # ---- Audits
    print("=" * 70)
    print("AUDIT 1: composting toilet on rural homestead")
    print("=" * 70)
    a1 = audit(septic_rule, homestead)
    print(a1.summary())
    print("\nScope exits:")
    print(a1.deviations_human_readable())
    print(f"\nFirst-principle intent: {septic_rule.first_principle_intent}")
    print(f"Intent still applicable: {a1.intent_still_applicable}")
    print("  (Yes -- preventing groundwater contamination is always relevant;")
    print("   but the specific rule was scoped for urban density, not 4 people / km^2.")
    print("   A scope-current rule for this density would specify safe composting")
    print("   distance from well, graywater filter setup, etc.)")

    record1 = build_response_record(
        sit=homestead, audits=[a1],
        action="install_composting_toilet_and_graywater_per_MN_7080_7083",
        rationale="centralized sewer rule outside scope at 4 pop/km^2; "
                  "groundwater protection intent preserved via composting design "
                  "with safe well separation, per substrate-current rules 7080/7083",
        responder="property_owner",
        timestamp="2025-06-15T10:00:00",
        audit_due_by="2025-09-15",
    )
    print("\nResponse record:")
    for k, v in record1.serialize().items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 70)
    print("AUDIT 2: community footbridge after washout")
    print("=" * 70)
    a2 = audit(bridge_permit_rule, footbridge)
    print(a2.summary())
    print("\nScope exits:")
    print(a2.deviations_human_readable())
    print(f"\nFirst-principle intent: {bridge_permit_rule.first_principle_intent}")
    print("  (The state DOT permit was scoped for vehicular bridges with major")
    print("   load and 50+ year design life. A 6m pedestrian crossing serving")
    print("   14 households at zero vehicle load is outside that envelope.")
    print("   Load-bearing-safety intent preserved via competent local construction")
    print("   and post-hoc inspection.)")

    record2 = build_response_record(
        sit=footbridge, audits=[a2],
        action="community_pedestrian_crossing_built_with_local_materials",
        rationale="state vehicular-bridge permit outside scope (0 vehicles, 6m span); "
                  "load-bearing safety preserved via standard timber-truss design "
                  "and immediate community inspection cycle",
        responder="community_council",
        timestamp="2025-06-20T08:30:00",
        audit_due_by="2025-08-20",
    )
    print("\nResponse record:")
    for k, v in record2.serialize().items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 70)
    print("INVERSION FLAG")
    print("=" * 70)
    print("Both regulations, if enforced literally in these situations, would")
    print("produce the harm they were designed to prevent:")
    print("  - septic rule: forcing centralized sewer where none exists delays")
    print("    sanitation, increasing risk of improvised disposal and contamination")
    print("  - bridge rule: blocking community crossing isolates households,")
    print("    impedes emergency access, creates the access-failure the safety")
    print("    framework was meant to address")
    print("\nThe scope audit surfaces this inversion. Communities act inside")
    print("the original intent; central authority audits afterward.")
