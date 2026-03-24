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
