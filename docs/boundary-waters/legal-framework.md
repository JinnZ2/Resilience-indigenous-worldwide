# Legal Framework — Boundary Waters Sulfide Mine

The cascade model is grounded in a stack of treaties, statutes, and
customary international law. Each layer of the model maps to a
specific legal trigger.

## 1854 Treaty with the Chippewa (10 Stat. 1109)

- Ceded the Arrowhead region (including the mine footprint) to the
  United States.
- Article 11 reserved to the signatory Bands the right to **hunt, fish,
  and gather** on the ceded lands until otherwise ordered by the
  President — a reservation that has never been abrogated.
- The 1854 Treaty Authority (Bois Forte, Grand Portage, and Fond du
  Lac) administers off-reservation rights.
- Destruction of the *resource* destroys the *right*. Precedent:
  *Minnesota v. Mille Lacs Band*, 526 U.S. 172 (1999).

Model coupling: `community_layer → treaty_harvesters_displaced`.

## Boundary Waters Treaty of 1909 (U.S.–U.K./Canada)

- **Article IV**: "boundary waters … shall not be polluted on either
  side to the injury of health or property on the other."
- Creates the International Joint Commission (IJC) as the forum for
  cross-border water disputes.
- The mine's watershed flows **north across the border** into Quetico
  and the Rainy–Lake of the Woods system — every kilogram of sulfate
  is a direct Article IV question.

Model coupling: `intl_law_layer → canada_sulfate_breach` when the
border concentration exceeds 10 mg/L (set at the manoomin threshold
because the same rice beds grow on the Canadian side).

## Trail Smelter Arbitration (U.S. v. Canada, 1941)

- Canonical customary-international-law precedent: "no State has the
  right to use or permit the use of its territory in such a manner as
  to cause injury by fumes in or to the territory of another."
- Liability was assessed and damages paid. The rule is now cited as
  *sic utere tuo ut alienum non laedas* (use your own so as not to
  injure another) and is arguably *jus cogens* for transboundary
  pollution.
- The model's `liability_npv_usd` uses Trail Smelter's damage-NPV
  framework: breach years × annualized liability.

Model coupling: `intl_law_layer → trail_smelter_liability` after two
sustained years of breach.

## UNDRIP & Free, Prior, and Informed Consent (FPIC)

- UN Declaration on the Rights of Indigenous Peoples, Articles 10,
  19, 29, 32: no relocation, no legislative or administrative measure,
  and no project affecting lands or resources without FPIC.
- The U.S. endorsed UNDRIP in 2010. Article 29(2) specifically
  prohibits storage or disposal of hazardous materials on indigenous
  lands without FPIC — tailings storage facilities are the textbook
  case.

FPIC has never been sought from the 1854 Treaty Bands for this mine.
That is a standing violation regardless of whether permitting
proceeds.

## SEC Regulation S-K (17 C.F.R. § 229)

Same machinery as the Venezuela/ERI strategy in this repo:

- **Item 101** — description of business; must disclose material
  environmental constraints.
- **Item 103** — legal proceedings; treaty litigation and
  tribal-rights suits are reportable.
- **Item 105** — risk factors; tailings-failure liability NPV
  ($1.08 T in the model) is material to any reasonable investor.
- **Item 303 (MD&A)** — known trends and uncertainties; the 290-year
  post-closure ARD half-life is a known trend.

Antofagasta trades on the London Stock Exchange (LON: ANTO) and
discloses under UK CA 2006; institutional U.S. holders trigger SEC
disclosure on the holder side.

## EU Corporate Sustainability Due Diligence Directive (CSDDD)

- Duty of care extends across the entire value chain, including
  upstream suppliers and downstream financial counterparties.
- Applies to Antofagasta indirectly via EU-listed ETFs, EU-based
  banks financing the project, and EU insurance underwriters.
- The CSDDD creates a private right of action for affected
  communities — the 1854 Treaty Authority has standing under the
  "adversely affected stakeholder" clause.

## Antiquities Act & NEPA

- The 2023 Public Land Order 7917 withdrew 225,378 acres from mineral
  entry for 20 years following a full NEPA Environmental Assessment
  (USFS, 2022).
- Reversal via the Congressional Review Act triggers a duty to
  supplement the NEPA record — and every data point in the cascade
  model is EA-responsive.

## Summary — legal layer to model layer

| Legal instrument | Model layer | Trigger metric |
|------------------|-------------|----------------|
| 1854 Treaty, Art. 11 | `community` | `treaty_harvesters_displaced` |
| MN Rule 7050.0224 | `hydrology` / `ecology` | `sulfate_mg_l > 10` |
| Boundary Waters Treaty 1909, Art. IV | `intl_law` | `canada_sulfate_breach` |
| Trail Smelter precedent | `intl_law` | `liability_npv_usd` |
| UNDRIP Art. 29 + FPIC | All layers (standing) | Lack of consent documented |
| SEC Reg S-K Item 105 | `port` + `intl_law` | Peak NPV + port jobs at risk |
| EU CSDDD | Cross-cutting | Value-chain exposure |
