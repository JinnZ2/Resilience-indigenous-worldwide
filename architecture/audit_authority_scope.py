"""
audit_authority_scope.py

Audit-authority is itself scope-conditional. Higher tiers of government
get first right to audit a community's crisis response only within their
declared resource and time scope. If they cannot or will not exercise
that right within the declared window, the audit at the next tier down
becomes final.

## Premise

Authority without demonstrated capacity to exercise it is coercion
masquerading as governance. The same scope-audit logic applied to
regulations and corporate charters applies to *audit authority itself*.
A state government that claims final-audit authority over community
crisis response, but cannot resource the audit within 90 days, has
exited the scope of that claim. The community audit becomes the legal
record. A federal authority can override the state audit only by
exercising its own audit within its own scope window -- typically
larger, e.g. 180 days.

This protects both directions:

  - communities don't sit in legal limbo indefinitely while higher
    authorities investigate without resourcing the investigation
  - higher authorities don't get to claim legitimacy through delay
    or resource starvation; they must actually exercise audit
    capacity to retain audit authority
  - documentation rigor at the community level matters because that
    documentation may stand as the final legal record

## Linkage

Extends regulatory_scope_audit.py and corporate_charter_scope_audit.py.
The community audit records produced by those modules feed into this
tiered review structure.

License: CC0
Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict
from datetime import datetime, timedelta

# -----------------------------------------------------------
# 1. Audit tiers and their scope windows
# -----------------------------------------------------------

@dataclass
class AuditTier:
    """
    An audit authority at a given level of jurisdiction. The scope
    window is how long they have to exercise their audit before
    authority falls back to the tier below.
    """
    name: str                          # "community", "county", "state", "federal"
    level: int                         # 0=community, 1=county, 2=state, 3=federal
    scope_window_days: int             # how long this tier has to act
    resource_capacity_required: dict[str, float] = field(default_factory=dict)
    # examples: {"auditor_hours": 40, "site_visits": 2, "expert_reviews": 1}


# -----------------------------------------------------------
# 2. Audit record at a given tier
# -----------------------------------------------------------

@dataclass
class TieredAuditRecord:
    """
    An audit performed at a specific tier. May confirm, modify, or
    challenge lower-tier audits -- but only if produced within scope.
    """
    tier: AuditTier
    incident_id: str                   # community response or crisis ID
    submitted_at_iso: str              # when the tier began the audit
    completed_at_iso: str | None       # None until completed
    finding: str = ""                  # "confirms_community", "modifies", "challenges"
    rationale: str = ""
    upgrades: list[str] = field(default_factory=list)
    # specific improvements / scope-current rules proposed
    auditor_ids: list[str] = field(default_factory=list)

    def is_complete(self) -> bool:
        return self.completed_at_iso is not None

    def duration_days(self) -> float | None:
        if not self.is_complete():
            return None
        t0 = datetime.fromisoformat(self.submitted_at_iso)
        t1 = datetime.fromisoformat(self.completed_at_iso)
        return (t1 - t0).total_seconds() / 86400.0

    def within_scope_window(self) -> bool:
        dur = self.duration_days()
        if dur is None:
            return False
        return dur <= self.tier.scope_window_days


# -----------------------------------------------------------
# 3. Incident: the original community response under audit
# -----------------------------------------------------------

@dataclass
class CommunityResponseIncident:
    incident_id: str
    community_id: str
    declared_at_iso: str               # when community action was taken
    community_audit_record: dict       # the local audit trail (already exists)


# -----------------------------------------------------------
# 4. Tiered review ledger
# -----------------------------------------------------------

@dataclass
class TieredReviewLedger:
    """
    The full tiered review for a single incident. Tracks which tiers
    were eligible, which exercised their authority within scope,
    and which audit is currently final.
    """
    incident: CommunityResponseIncident
    tiers: list[AuditTier]
    records: list[TieredAuditRecord] = field(default_factory=list)

    def deadline_for(self, tier: AuditTier) -> str:
        """ISO timestamp by which this tier must complete its audit."""
        t0 = datetime.fromisoformat(self.incident.declared_at_iso)
        # tiers stack: each tier's window starts when the prior tier
        # exhausted its own window
        offset = 0
        for t in sorted(self.tiers, key=lambda x: x.level):
            if t.level < tier.level:
                offset += t.scope_window_days
        t_deadline = t0 + timedelta(days=offset + tier.scope_window_days)
        return t_deadline.isoformat()

    def tier_exercised_within_scope(self, tier_name: str) -> bool:
        for r in self.records:
            if r.tier.name == tier_name and r.is_complete() and r.within_scope_window():
                return True
        return False

    def final_audit(self, current_time_iso: str) -> dict:
        """
        Determine which audit is currently operative *and* which higher
        tiers, if any, still have open windows to override.

        Logic:
          - Find the highest-level tier that has completed an audit
            within its own scope window. That is currently operative.
          - If none has, the community baseline is operative.
          - Separately, list any higher tiers whose windows are still
            open -- they can still override, but until they do, the
            current operative audit stands.
        """
        sorted_tiers_desc = sorted(self.tiers, key=lambda t: -t.level)
        now = datetime.fromisoformat(current_time_iso)

        # find highest tier with an in-scope completed record
        operative = None
        for tier in sorted_tiers_desc:
            if tier.level == 0:
                continue
            in_scope_records = [
                r for r in self.records
                if r.tier.name == tier.name and r.is_complete()
                and r.within_scope_window()
            ]
            if in_scope_records:
                latest = max(in_scope_records,
                             key=lambda r: r.completed_at_iso or "")
                operative = {
                    "operative_tier": tier.name,
                    "rationale": f"{tier.name} exercised audit within "
                                 f"{tier.scope_window_days}-day scope window",
                    "finding": latest.finding,
                    "upgrades": latest.upgrades,
                    "completed_at": latest.completed_at_iso,
                }
                break

        if operative is None:
            operative = {
                "operative_tier": "community",
                "rationale": "no higher tier has completed audit within scope; "
                             "community audit is the operative legal record",
                "finding": "community_baseline",
                "upgrades": [],
            }

        # find higher tiers with still-open windows that could override
        pending_overrides: list[dict] = []
        operative_level_map = {
            "community": 0, "county": 1, "state": 2, "federal": 3,
        }
        op_level = operative_level_map.get(operative["operative_tier"], 0)

        for tier in sorted(self.tiers, key=lambda t: t.level):
            if tier.level <= op_level:
                continue
            # has this tier already submitted a within-scope record? if so,
            # they're already in operative or were superseded by higher
            already_completed = any(
                r.tier.name == tier.name and r.is_complete() and r.within_scope_window()
                for r in self.records
            )
            if already_completed:
                continue
            deadline = datetime.fromisoformat(self.deadline_for(tier))
            if now < deadline:
                pending_overrides.append({
                    "tier": tier.name,
                    "deadline": deadline.isoformat(),
                    "days_remaining": (deadline - now).total_seconds() / 86400.0,
                })

        return {
            **operative,
            "pending_override_windows": pending_overrides,
        }


# -----------------------------------------------------------
# 5. Falsifiable claims
# -----------------------------------------------------------

CLAIMS = [
    "Audit-authority is scope-conditional: claimed but unexercised authority does not bind.",
    "A higher tier that cannot resource an audit within its declared window forfeits override authority for that incident.",
    "Community audit is always the baseline legal record; higher tiers may upgrade only by exercising actual audit within scope.",
    "Documentation rigor at the community tier is a direct function of whether it may stand as the final record.",
    "Tiered scope windows force budgeting for actual audit capacity, not claims of it.",
    "Neither side gains by delay: communities risk weaker upgrades; higher authorities risk forfeiting override.",
]


# -----------------------------------------------------------
# 6. Demo
# -----------------------------------------------------------

if __name__ == "__main__":
    tiers = [
        AuditTier(name="community", level=0, scope_window_days=14,
                  resource_capacity_required={"auditor_hours": 8}),
        AuditTier(name="county", level=1, scope_window_days=30,
                  resource_capacity_required={"auditor_hours": 16, "site_visits": 1}),
        AuditTier(name="state", level=2, scope_window_days=90,
                  resource_capacity_required={"auditor_hours": 40, "site_visits": 2}),
        AuditTier(name="federal", level=3, scope_window_days=180,
                  resource_capacity_required={"auditor_hours": 80, "expert_reviews": 2}),
    ]

    incident = CommunityResponseIncident(
        incident_id="WINTER_STORM_2026_03_15_response",
        community_id="northern_mn_community_A",
        declared_at_iso="2026-03-16T08:00:00",
        community_audit_record={
            "action": "asset_access_food_water_blankets",
            "rationale": "no corporate response within 24h threshold",
            "proportionate": True,
        },
    )

    ledger = TieredReviewLedger(incident=incident, tiers=tiers)

    print("=" * 70)
    print("DEADLINES BY TIER")
    print("=" * 70)
    for t in tiers:
        print(f"  {t.name:10s} (level {t.level}, "
              f"window {t.scope_window_days}d) -> {ledger.deadline_for(t)}")

    # ---- Scenario A: county audits within window
    ledger.records.append(TieredAuditRecord(
        tier=tiers[1],   # county
        incident_id=incident.incident_id,
        submitted_at_iso="2026-03-20T10:00:00",
        completed_at_iso="2026-04-05T15:00:00",
        finding="confirms_community",
        rationale="community audit was proportionate and well-documented; "
                  "scope-exit determination valid",
        upgrades=["recommend county-level cache of cold-weather supplies "
                  "for future grid-failure scenarios"],
        auditor_ids=["county_emergency_mgmt_001"],
    ))

    print("\n" + "=" * 70)
    print("SCENARIO A: county completes audit within 30-day window")
    print("=" * 70)
    result = ledger.final_audit(current_time_iso="2026-04-06T00:00:00")
    for k, v in result.items():
        print(f"  {k}: {v}")

    # ---- Scenario B: county did its audit, state misses window
    print("\n" + "=" * 70)
    print("SCENARIO B: state misses 90-day window (no record submitted)")
    print("=" * 70)
    result = ledger.final_audit(current_time_iso="2026-08-01T00:00:00")
    for k, v in result.items():
        print(f"  {k}: {v}")

    # ---- Scenario C: state audits late but within their cumulative window
    ledger.records.append(TieredAuditRecord(
        tier=tiers[2],   # state
        incident_id=incident.incident_id,
        submitted_at_iso="2026-04-10T09:00:00",
        completed_at_iso="2026-07-01T17:00:00",   # ~82 days, within 90
        finding="modifies",
        rationale="confirms community response; recommends scope-current "
                  "rule for corporate-charter response thresholds in "
                  "rural-isolation scenarios",
        upgrades=[
            "MN statute amendment: codify 24h corporate response threshold for "
            "grid-failure isolation crises in unincorporated areas",
            "state cache of emergency rations at 30 county distribution points",
        ],
        auditor_ids=["state_dem_001", "state_dem_002"],
    ))

    print("\n" + "=" * 70)
    print("SCENARIO C: state completed audit within 90-day window")
    print("=" * 70)
    result = ledger.final_audit(current_time_iso="2026-07-02T00:00:00")
    for k, v in result.items():
        print(f"  {k}: {v}")

    # ---- Scenario D: federal still inside their window, no record yet
    print("\n" + "=" * 70)
    print("SCENARIO D: federal window still open, no record yet")
    print("=" * 70)
    result = ledger.final_audit(current_time_iso="2026-06-01T00:00:00")
    for k, v in result.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 70)
    print("INVERSION FLAG")
    print("=" * 70)
    print("Audit authority that cannot be exercised within scope is not")
    print("authority -- it is a claim. The framework forces higher tiers")
    print("to either resource the audit or forfeit override. Communities")
    print("do not sit in legal limbo while higher authorities investigate")
    print("without capacity to investigate. Each side's incentives align")
    print("with rigor and timeliness, not delay or coercion.")
