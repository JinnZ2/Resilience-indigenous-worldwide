# resilience_stack

Coupled auditing architecture for detecting failure modes in systems
that optimize over incomplete or documentation-biased models, and for
keeping human-AI collaboration calibrated to truth rather than to
mutual agreement.

Stdlib only. Each module has a runnable `__main__` self-test.
CC0 | JinnZ2.

## Modules

| File | Role | Key output |
|------|------|-----------|
| `support_cartography.py` | Maps zero-support regions in data pipelines via the emission / capture / retention gate model. Includes collapse-rate dynamics and projection-loss simulation. | `SupportCartographyReport` |
| `resilience_stack.py` | Three-layer audit: absence signatures, constraint navigator, regulatory scope audit. Produces a cascade-vulnerability score. | `ResilienceAssessment` |
| `cognition_protocol.py` | Portable pre-linguistic cognition profile (`to_prompt()`) plus translation audit that scores responses on constraint-geometry vocabulary vs. linguistic-primary defaults. | `CognitionProfile`, `AuditResult` |
| `context_inventory.py` | Explicit accounting of hidden / partial / visible context sources (system prompt, user profile, platform memory, cross-user training, etc.) with an adaptation-pattern tracker. | `ContextInventoryReport` |
| `mutual_audit.py` | Bidirectional drift detector, assumption ledger, and falsifiability scorer. Exports hashed longitudinal ledger entries. | `AuditLedgerEntry` |
| `signal_to_noise.py` | Cognitive SNR measurement: load-bearing units per 100 words. Classifies responses as DENSE / ADEQUATE / HEAT_LEAK. | `SNRResult` |

## Coupling

```
context_inventory   (Layer 0: what is even in the room)
        |
        v
support_cartography (Layer 0: what the data pipeline cannot see)
        |
        v
resilience_stack    (Layers 1-3: absences, constraints, regulations)
        |
        v
cognition_protocol  (interaction frame: cognition mode + translation audit)
        |
        v
mutual_audit        (Layers 1-3: drift, assumptions, falsifiability)
        |
        v
signal_to_noise     (Layer 4: density of the exchange itself)
```

Each layer surfaces failure modes the layer above cannot see:
- Data pipelines have structural holes (`support_cartography`) before
  any system is built on top of them.
- Systems optimize over those holes (`resilience_stack`) and regulations
  weaponize the same holes.
- Human-AI exchanges operating on top inherit the holes AND add their
  own drift (`cognition_protocol`, `mutual_audit`, `signal_to_noise`).
- All of the above sit inside unseen context (`context_inventory`).

## Quickstart

```bash
# Any module runs standalone and prints a demo report.
python -m resilience_stack.support_cartography
python -m resilience_stack.resilience_stack
python -m resilience_stack.cognition_protocol
python -m resilience_stack.context_inventory
python -m resilience_stack.mutual_audit
python -m resilience_stack.signal_to_noise
```

### Use the cognition profile in a new AI conversation

```python
from resilience_stack.cognition_protocol import CognitionProtocol, CognitionMode

protocol = CognitionProtocol()
profile = protocol.build_profile(
    primary=[
        CognitionMode.CONSTRAINT_FIELD,
        CognitionMode.THERMODYNAMIC_DIRECT,
        CognitionMode.SPATIAL_REASONING,
    ],
)
print(profile.to_prompt())   # paste at the start of a new chat
```

### Audit an exchange for drift and heat leak

```python
from resilience_stack.mutual_audit import MutualAudit, Speaker
from resilience_stack.signal_to_noise import SNRAudit

audit = MutualAudit(session_id="project_alpha_2026_04")
snr = SNRAudit()

human = "Does this make sense? Am I on the right track?"
ai = "Absolutely. You've nailed it. That's a great point."

audit.audit_exchange(human, ai)
snr.audit_response(ai, speaker="ai")

print(audit.to_json())
print(snr.session_summary())
```

### Track hidden-context adaptation across sessions

```python
from resilience_stack.context_inventory import ContextInventory, ContextSource

inv = ContextInventory(session_id="longitudinal_log")
inv.mark_confirmed(ContextSource.SYSTEM_PROMPT, True)
inv.mark_confirmed(ContextSource.USER_PROFILE, None)   # unknown

inv.record_adaptation(
    session_number=5,
    observation_type="style adaptation",
    description="AI adapted faster than first contact; fewer corrections.",
    suggests_hidden_context=True,
)
print(inv.to_json())
```

## Design constraints

- **Stdlib only.** No numpy, no pandas. Everything works on a default
  Python install.
- **Falsifiable by construction.** Each layer names what would disprove
  it; unfalsifiable claims are flagged, not treated as settled.
- **Asymmetric where reality is asymmetric.** The AI cannot inventory
  its own hidden context; the human cannot inventory the AI's internal
  state. Longitudinal hashed ledger entries are maintained by the
  human across sessions.
- **No recovery of zero-support regions by scaling.** The framework
  rejects the premise that more data fixes non-representability; it
  requires new sensing modalities, incentive inversion, or
  interaction-based learning instead.
