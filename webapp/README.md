# Community Asset Mapper

React component for mapping and sharing community resources, skills,
knowledge, and mutual support.  The human-facing layer of the resilience
toolkit -- while the Python modules compute system designs, this lets
a community see and contribute what they actually have.

## Categories

| Category | What it covers |
|----------|---------------|
| **Skills & Abilities** | Repair, teaching, trade skills, crafts |
| **Knowledge & Wisdom** | Traditional medicine, elder knowledge, oral history |
| **Tools & Equipment** | Shared tools, workshop access, lending libraries |
| **Care & Support** | Childcare circles, elder care, emergency mutual aid |
| **Community Building** | Gatherings, organizing, conflict resolution |
| **Local Industry** | Machine shops, woodworking, manufacturing capacity |
| **Natural Resources** | Water sources, clay deposits, timber, stone, soil |

Industry and natural resources have additional fields (production
capacity, estimated quantity, access considerations).

## Setup

Requires React 18+ and Tailwind CSS. Uses `lucide-react` for icons.

```bash
npm install react lucide-react
```

Drop `CommunityAssetMapper.jsx` into any React project with Tailwind
configured.

```jsx
import CommunityAssetMapper from './CommunityAssetMapper';

function App() {
  return <CommunityAssetMapper />;
}
```

## How it connects to the Python toolkit

The Python modules in `resilience/recovery/` model what a community
*could* build.  This component maps what a community *already has*.

When planning a geometric city or recovery base:
1. Run the asset mapper to inventory existing community resources
2. Feed the inventory into the Python system builders to identify gaps
3. Use the gap analysis to prioritize which systems to build first

Example: if the asset mapper shows the community has a machine shop
(industry) and clay deposits (natural resources) but no water source,
the geometric city builder would prioritize the water system.

## Offline use

The component runs entirely client-side with no backend.  Asset data
persists in React state (add localStorage or IndexedDB for persistence).
Works on any device with a browser -- no internet needed after initial load.
