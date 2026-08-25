# State of the Climate in 2025 (BAMS)

**Source:** *State of the Climate in 2025.* Bulletin of the American Meteorological Society (BAMS), 36th annual State of the Climate report, American Meteorological Society. ~625 scientists across ~60 countries. Publication date August 2025 per the summary this file was compiled from; the report's standard release for a given climate year is usually mid-to-late summer of the following year — anyone citing this doc should confirm the actual issue date against BAMS directly.

## The structural finding

**2025 was the warmest year on record with no El Niño present.** Near-neutral to weak-La-Niña conditions prevailed in the eastern Pacific. The 2023-2024 records were partly fuelled by a strong El Niño; removing that assist and still landing top-3 shifts the reading. The trend line itself is now sufficient to hit these levels without an ENSO push.

## Numbers (falsifiable, source-cited above)

| Axis | 2025 value | Baseline / comparison |
|------|------------|----------------------|
| CO₂ | 425.6 ppm | +53% above pre-industrial (~278 ppm) |
| Methane | 1,935.7 ppb | +166% above pre-industrial |
| Nitrous oxide | 338.9 ppb | +26% above pre-industrial |
| Fossil-fuel CO₂ emissions | 10.3 PgC/yr | >3× the 1960s rate |
| Global temperature rank | top 3 warmest | in ~175-year record |
| Global temperature rank *without El Niño* | warmest on record | — |
| Ocean heat content (0-2000 m) | record high | — |
| Global mean sea level | +111.2 mm above 1993 baseline | 14th consecutive record year |
| Sea-level components | +1.6 mm/yr thermal expansion, +2.0 mm/yr ice melt | — |
| Sea surface temperature | 3rd highest | in 172-year record |
| Ocean surface hit by ≥1 marine heatwave | 87% | — |
| Arctic warming rate | ~3× global average | 2nd-warmest year in 126-year Arctic record |
| Arctic max sea ice extent | lowest on record | in 47-year satellite record; min extent 11th lowest |
| Multi-year ice (>4 yr) area, Sept 2025 | 95,000 km² | vs ~1,500,000 km² in the 1980s |
| Tundra greenness | 3rd-highest on record | warming + precipitation increase |
| Antarctic annual mean temp | warmest since 1979 | — |
| Antarctic sea ice max/min extent | 3rd and 4th lowest | ~decade-long below-average trend |
| Reference glacier mass balance | > -1 m water equivalent | 4th straight year at this loss; 38 consecutive years of loss |
| Share of all glacier loss since 1976 | ~41% in the last decade | — |
| Named tropical cyclones (global) | 97 | vs 87 (1991-2020 average) |
| Category 5 tropical cyclones | 5 | 3 in the North Atlantic (tied 2nd most for that basin) |
| Recent warmth streak | 2015-2025 | the 11 warmest years on record |

## Regional peaks

- **Europe:** warmest year on record.
- **Russia, China, South Korea, Argentina:** each their 2nd-warmest year.
- **Antarctic Peninsula:** surface melt approached record levels in early January.

## Notable events

- **Hurricane Melissa (N Atlantic):** 190 mph, 892 hPa — one of the strongest Atlantic hurricanes on record. Cat 5 landfall in Jamaica. 95 fatalities, >$12.2B damage.
- **Tropical Cyclone Zelia (Australia):** Cat 5 at sea, Cat 4 landfall in Western Australia. Marble Bar flood heights ~2 m above previous records.

## Cross-references in this repo

- `materials/earth_mandala.py` uses synthetic proxies on the same five axes (ΔT, ice, ocean heat, CO₂, biodiversity). The 2025 warmest-without-El-Niño finding directly contradicts the script's framing of the 2026 "Godzilla El Niño" as the trajectory peak — the trend line is doing the work without the ENSO assist. Biodiversity is not covered in this BAMS summary and remains unanchored.
- `constraint_resilience_audit/warning_time_audit.py` models proxy-lag under nonlinear coupling. Attributing warmth to ENSO state is the exact proxy this report retires: through 2024 it looked "reasonable" (warmth co-occurred with El Niño); in 2025 the proxy failed while the truth kept rising.
- `constraint_resilience_audit/institutional_framing.py` — baselines here matter: 1993 for sea level, 1991-2020 for cyclones, ~278 ppm for pre-industrial CO₂, 1979 for Antarctic. Different baseline choices produce different "record" thresholds.

*Refute a claim by correcting the source citation, not by softening this table.*

CC0. Copy, fork, repost.
