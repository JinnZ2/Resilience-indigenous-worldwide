# Resilience Indigenous Worldwide

## Project Overview

Legal research and computational modeling repository supporting indigenous communities
facing resource extraction, military intervention, and corporate colonization. Covers
multi-jurisdictional legal analysis (US, EU, international), financial risk assessment,
and network stress modeling.

## Repository Structure

```
docs/                        # Legal analysis and strategy documents
  greenland/                 # Greenland-specific analysis
  venezuela/                 # Venezuela-specific analysis
  strategy/                  # Cross-cutting legal and media strategies
resilience/                  # Python package for computational modeling
  __init__.py
  network.py                 # Network graph and node definitions
  stress_model.py            # Stress propagation and hidden variable model
  risk_matrix.py             # Legal/financial risk scoring
  visualization.py           # Plotting and report generation
  data/                      # Default datasets and configurations
```

## Development

### Python Setup

```bash
pip install -r requirements.txt
```

### Running the Stress Model

```bash
python -m resilience.stress_model
```

### Running Tests

```bash
python -m pytest tests/
```

## Conventions

- **Python files**: lowercase with underscores (`stress_model.py`)
- **Markdown docs**: lowercase with hyphens (`conflict-of-interest.md`)
- **Directories**: lowercase, no spaces (`docs/greenland/`)
- **Python style**: PEP 8, type hints on public functions
- **Imports**: stdlib first, then third-party, then local

## Key Dependencies

- `numpy` - numerical computation
- `pandas` - data manipulation
- `networkx` - graph modeling
- `matplotlib` - visualization

## Legal Domains Covered

- SEC Regulation S-K disclosure requirements
- EU Corporate Sustainability Due Diligence Directive (CSDDD)
- Bilateral Investment Treaties (BIT) and ISDS challenges
- Rome Statute / International Criminal Court
- UN Declaration on the Rights of Indigenous Peoples (UNDRIP)
- Free, Prior, and Informed Consent (FPIC)


Review this repository against its CLAUDE.md and produce REVIEW.md.
Focus on:

1. **Structural consistency with CLAUDE.md:**
   - Does the repo layout match the documented structure (docs/, resilience/, data/)?
   - Are Python naming conventions (lowercase_underscore) and Markdown conventions (lowercase-hyphens) followed everywhere?
   - Are imports ordered stdlib → third-party → local, as per the convention?
   - Do all public functions in the resilience package have type hints?

2. **README & discoverability:**
   - Does the README concisely explain the project’s purpose (legal research + computational modeling for indigenous communities)?
   - Missing: CITATION.cff, KEYWORDS.txt, repository topics, license badge, "Why This Matters" urgency statement. Provide ready-to-paste snippets for each.
   - Is there a clear one-liner import example for the resilience package?
   - Does the README list the legal domains covered and link to key strategy documents?

3. **Obvious inconsistencies:**
   - Broken links between docs and code, especially references to datasets or strategy files.
   - Duplicate or conflicting legal analyses across different jurisdiction folders (greenland/ vs venezuela/ vs strategy/).
   - Missing tests for the computational modules (network, stress_model, risk_matrix, visualization).

4. **Documentation gaps:**
   - Does each legal domain directory (greenland/, venezuela/) have at least a summary README or index?
   - Is the stress model’s methodology (hidden variables, propagation logic) clearly explained in the module docstring or a companion doc?
   - Are the risk scoring criteria and financial risk metrics documented?

5. **Repository topics suggestion:** 
   Propose topics like: `indigenous-rights`, `legal-research`, `resource-extraction`, `fpic`, `undrip`, `network-stress`, `corporate-accountability`, `isds`, `esg`, `human-rights`.

Keep sections concise. Output the full REVIEW.md.
