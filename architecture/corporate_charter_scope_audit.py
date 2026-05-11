"""
corporate_charter_scope_audit.py

Audit corporate operating privileges as scope-conditional. Any
corporation operating within a community holds an implicit charter:
extract value from this market, stabilize with this community when
crisis arrives. Failure to respond within a declared response
threshold (default 24 hours) suspends operating privileges and
activates community asset-access contingency until response is
delivered.

## Premise

A corporate charter is not a permanent grant. It is a conditional
permission to operate inside a community's territory, granted in
exchange for serving community function. When the corporation
exits the scope of that function -- most clearly during a crisis
the corporation refuses to respond to -- the charter is in scope
exit. The community's claim on the corporation's locally held
resources supersedes the corporation's disposal logic for the
duration of the crisis, subject to post-hoc audit.

This is not seizure. It is enforcement of the actual terms of
operating inside the community.

## Linkage

Builds on regulatory_scope_audit.py (scope-exit framework),
biological_response_infrastructure.py (local autonomous response),
and institutional_audit.py (premise filtering). Corporate charters
are filtered the same way regulations are; corporations carrying
'permanence', 'appearance_over_audit', 'performance_over_function'
without compensating accountability cycles are pre-existing scope
exits whose crisis-response failure is predictable.

License: CC0
Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict

# -----------------------------------------------------------
# 1. Corporate charter: the implicit / explicit operating agreement
# -----------------------------------------------------------

@dataclass
class CorporateCharter:
    """
    Operating agreement between a corporation and the community(ies)
    where it operates. The charter is conditional on the corporation
    serving its first-principle function.
    """
    corporation_id: str
    community_id: str
    function_served: str               # e.g. "food distribution and retail"
    value_extracted_categories: list[str] = field(default_factory=list)
    # examples: "land_use", "infrastructure_access", "workforce",
    #           "tax_carve_out", "regulatory_carve_out", "local_supply_chain"

    response_threshold_hours: float = 24.0
    on_site_assets: dict[str, float] = field(default_factory=dict)
    # examples: {"food_kg": 8000, "fuel_l": 50000, "trucks": 6}


# -----------------------------------------------------------
# 2. Crisis declaration: when the audit clock starts
# -----------------------------------------------------------

@dataclass
class CommunityCrisis:
    id: str
    community_id: str
    crisis_type: str                   # "food_shortage", "infrastructure_failure", ...
    declared_at_iso: str               # ISO timestamp
    needs: dict[str, float] = field(default_factory=dict)
    # examples: {"food_kg": 4500, "potable_water_l": 12000}


# -----------------------------------------------------------
# 3. Corporate response: what was done within the threshold window
# -----------------------------------------------------------

@dataclass
class CorporateResponse:
    corporation_id: str
    crisis_id: str
    delivered_within_hours: float | None    # None = no response
    resources_delivered: dict[str, float] = field(default_factory=dict)
    personnel_deployed: int = 0
    notes: str = ""

    def is_adequate(self, crisis: CommunityCrisis, threshold_hours: float,
                    delivery_fraction_required: float = 0.5) -> bool:
        """
        Adequacy: response within threshold AND delivering at least
        the required fraction of declared needs.
        """
        if self.delivered_within_hours is None:
            return False
        if self.delivered_within_hours > threshold_hours:
            return False
        if not crisis.needs:
            return self.personnel_deployed > 0 or bool(self.resources_delivered)
        for need_key, need_qty in crisis.needs.items():
            delivered = self.resources_delivered.get(need_key, 0.0)
            if delivered < delivery_fraction_required * need_qty:
                return False
        return True


# -----------------------------------------------------------
# 4. Charter audit
# -----------------------------------------------------------

@dataclass
class CharterAudit:
    charter: CorporateCharter
    crisis: CommunityCrisis
    response: CorporateResponse | None
    response_adequate: bool
    scope_exit_reasons: list[str]

    def in_scope(self) -> bool:
        return self.response_adequate and not self.scope_exit_reasons

    def summary(self) -> str:
        if self.in_scope():
            return (f"[IN SCOPE] {self.charter.corporation_id} responded "
                    f"to {self.crisis.id} adequately. Operating privileges intact.")
        return (f"[OUT OF SCOPE] {self.charter.corporation_id} failed to "
                f"meet response threshold ({self.charter.response_threshold_hours}h) "
                f"for {self.crisis.id} in community {self.crisis.community_id}. "
                f"Reasons: {self.scope_exit_reasons}. "
                f"Community asset-access contingency activated, "
                f"subject to post-hoc audit.")


def audit_charter(charter: CorporateCharter,
                  crisis: CommunityCrisis,
                  response: CorporateResponse | None) -> CharterAudit:
    reasons: list[str] = []
    if charter.community_id != crisis.community_id:
        reasons.append("charter_does_not_cover_this_community")
    if response is None:
        reasons.append("no_response")
        adequate = False
    else:
        adequate = response.is_adequate(crisis, charter.response_threshold_hours)
        if response.delivered_within_hours is None:
            reasons.append("no_response_recorded")
        elif response.delivered_within_hours > charter.response_threshold_hours:
            reasons.append(
                f"response_outside_threshold "
                f"({response.delivered_within_hours:.1f}h > "
                f"{charter.response_threshold_hours:.1f}h)"
            )
        if response is not None and crisis.needs:
            for need_key, need_qty in crisis.needs.items():
                delivered = response.resources_delivered.get(need_key, 0.0)
                if delivered < 0.5 * need_qty:
                    reasons.append(
                        f"under_delivery_{need_key}_{delivered:.0f}_of_{need_qty:.0f}"
                    )
    return CharterAudit(charter, crisis, response, adequate, reasons)


# -----------------------------------------------------------
# 5. Community asset-access contingency
# -----------------------------------------------------------

@dataclass
class CommunityAccessClaim:
    """
    What the community is claiming access to, why, and the audit trail.
    Activated only when CharterAudit returns out-of-scope.
    """
    crisis_id: str
    corporation_id: str
    assets_claimed: dict[str, float]
    rationale: str
    activated_at_iso: str
    audit_due_by_iso: str
    proportionate: bool = True
    used_for_stabilization_only: bool = True

    def serialize(self) -> dict:
        return {
            "crisis": self.crisis_id,
            "corporation": self.corporation_id,
            "assets_claimed": self.assets_claimed,
            "rationale": self.rationale,
            "activated_at": self.activated_at_iso,
            "audit_due_by": self.audit_due_by_iso,
            "proportionate": self.proportionate,
            "stabilization_only": self.used_for_stabilization_only,
        }


def proportionate_claim(crisis: CommunityCrisis,
                        on_site_assets: dict[str, float]) -> dict[str, float]:
    """
    Compute a proportionate claim: take what's needed for
    stabilization, capped by what's on site, never more than declared
    need. Surplus stays with the corporation.
    """
    claim: dict[str, float] = {}
    for need_key, need_qty in crisis.needs.items():
        available = on_site_assets.get(need_key, 0.0)
        claim[need_key] = min(need_qty, available)
    return claim


def activate_contingency(audit: CharterAudit,
                         activated_at_iso: str,
                         audit_due_by_iso: str,
                         rationale: str = "") -> CommunityAccessClaim | None:
    """
    Returns a CommunityAccessClaim only if the charter audit
    is out-of-scope. Otherwise None.
    """
    if audit.in_scope():
        return None
    claim_qty = proportionate_claim(audit.crisis, audit.charter.on_site_assets)
    return CommunityAccessClaim(
        crisis_id=audit.crisis.id,
        corporation_id=audit.charter.corporation_id,
        assets_claimed=claim_qty,
        rationale=rationale or (
            f"Corporation failed to meet {audit.charter.response_threshold_hours}h "
            f"response threshold; community asset-access activated to stabilize crisis. "
            f"Claim proportionate to declared need and limited to on-site availability."
        ),
        activated_at_iso=activated_at_iso,
        audit_due_by_iso=audit_due_by_iso,
    )


# -----------------------------------------------------------
# 6. Falsifiable claims
# -----------------------------------------------------------

CLAIMS = [
    "A corporate charter is scope-conditional; failure to respond during declared community crisis is a scope exit.",
    "Asset-access contingency activated under audit-after-action is enforcement of charter terms, not seizure.",
    "Proportionate claims limited to declared need and on-site availability are auditable and reproducible.",
    "Corporations dependent on community stability for revenue have an aligned-incentive failure when they block community self-stabilization.",
    "24-hour response threshold is a parameter, not a constant; communities may set it tighter for higher-dependency corporations.",
    "Charter audit and regulatory scope audit share the same epistemic structure: declared intent vs current scope vs current action.",
]


# -----------------------------------------------------------
# 7. Demo
# -----------------------------------------------------------

if __name__ == "__main__":
    # ---- Walmart-shaped retailer in a Northern Minnesota community
    walmart_charter = CorporateCharter(
        corporation_id="big_box_retailer_001",
        community_id="northern_mn_community_A",
        function_served="food and household goods distribution",
        value_extracted_categories=[
            "land_use", "tax_carve_out", "local_workforce",
            "infrastructure_access", "regulatory_carve_out",
        ],
        response_threshold_hours=24.0,
        on_site_assets={
            "food_kg": 8500.0,
            "potable_water_l": 4000.0,
            "fuel_l": 18000.0,
            "blankets": 320.0,
        },
    )

    # ---- Winter storm + grid failure, 36-hour isolation
    crisis = CommunityCrisis(
        id="WINTER_STORM_2026_03_15",
        community_id="northern_mn_community_A",
        crisis_type="grid_failure_with_isolation",
        declared_at_iso="2026-03-15T08:00:00",
        needs={
            "food_kg": 3200.0,
            "potable_water_l": 2400.0,
            "blankets": 180.0,
        },
    )

    # ---- Scenario A: corporation responds within window
    response_adequate = CorporateResponse(
        corporation_id="big_box_retailer_001",
        crisis_id="WINTER_STORM_2026_03_15",
        delivered_within_hours=18.0,
        resources_delivered={
            "food_kg": 2800.0,
            "potable_water_l": 2400.0,
            "blankets": 200.0,
        },
        personnel_deployed=4,
        notes="store manager opened distribution before requested",
    )

    a1 = audit_charter(walmart_charter, crisis, response_adequate)
    print("=" * 70)
    print("SCENARIO A: corporation responded adequately")
    print("=" * 70)
    print(a1.summary())
    contingency_a = activate_contingency(a1,
                                          activated_at_iso="",
                                          audit_due_by_iso="")
    print(f"Contingency activated: {contingency_a is not None}")

    # ---- Scenario B: no response within 24 hours
    response_failed = CorporateResponse(
        corporation_id="big_box_retailer_001",
        crisis_id="WINTER_STORM_2026_03_15",
        delivered_within_hours=None,
        resources_delivered={},
        personnel_deployed=0,
        notes="store locked, regional HQ unreachable",
    )

    a2 = audit_charter(walmart_charter, crisis, response_failed)
    print("\n" + "=" * 70)
    print("SCENARIO B: no response within threshold")
    print("=" * 70)
    print(a2.summary())
    claim = activate_contingency(
        a2,
        activated_at_iso="2026-03-16T08:00:00",
        audit_due_by_iso="2026-04-15T23:59:59",
        rationale="Grid failure isolated community; no corporate response "
                  "by 24-hour threshold; proportionate community claim "
                  "activated to stabilize food, water, warmth.",
    )
    print("\nCommunity asset-access claim:")
    if claim:
        for k, v in claim.serialize().items():
            print(f"  {k}: {v}")

    # ---- Scenario C: corporation responded but under-delivered
    response_partial = CorporateResponse(
        corporation_id="big_box_retailer_001",
        crisis_id="WINTER_STORM_2026_03_15",
        delivered_within_hours=20.0,
        resources_delivered={
            "food_kg": 800.0,           # well under 50% of declared need
            "potable_water_l": 600.0,
            "blankets": 50.0,
        },
        personnel_deployed=1,
        notes="single delivery, then store re-locked",
    )

    a3 = audit_charter(walmart_charter, crisis, response_partial)
    print("\n" + "=" * 70)
    print("SCENARIO C: response within window but under threshold delivery")
    print("=" * 70)
    print(a3.summary())
    claim3 = activate_contingency(
        a3,
        activated_at_iso="2026-03-16T08:30:00",
        audit_due_by_iso="2026-04-15T23:59:59",
        rationale="Partial delivery below 50% of declared community need; "
                  "contingency activated for shortfall only, not full asset claim.",
    )
    if claim3:
        # adjust the claim to only the shortfall
        shortfall = {
            k: max(0.0, v - response_partial.resources_delivered.get(k, 0.0))
            for k, v in crisis.needs.items()
        }
        claim3.assets_claimed = {
            k: min(walmart_charter.on_site_assets.get(k, 0.0), q)
            for k, q in shortfall.items()
        }
        claim3.rationale = ("Shortfall-only claim: corporation delivered some "
                            "but fell short of 50% threshold; community covers "
                            "remainder from on-site inventory.")
        print("\nShortfall-only community claim:")
        for k, v in claim3.serialize().items():
            print(f"  {k}: {v}")

    print("\n" + "=" * 70)
    print("INVERSION FLAG")
    print("=" * 70)
    print("Corporations depend on community stability for customers, workforce,")
    print("and supply-chain continuity. Blocking community self-stabilization")
    print("during crisis sabotages the corporation's own market. The audit")
    print("framework restores aligned incentives: respond and your charter")
    print("strengthens; fail to respond and the community uses your on-site")
    print("resources for the duration of the crisis, under post-hoc audit.")
