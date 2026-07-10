# Ancient Persia -- Consolidated Resilience Toolkit

A single-file toolkit consolidating 11 analysis and modeling modules for
indigenous resilience work. Named for the Persian tradition of engineering
systems that endure -- qanats still flow after 3,000 years.

Source: [JinnZ2/Inversion](https://github.com/JinnZ2/Inversion/tree/main/scripts)

---

## What's Inside

### Detecting Threats

**Contamination Detector** -- Quantitative text analysis that catches
institutional capture and epistemic degradation. Measures lexical diversity
(MATTR), hedging ratios, source diversity, argument density, and circular
reasoning. Use it to analyze reports, proposals, or policy documents before
trusting them.

```bash
python3 -c "from resilience.ancient_persia import analyze; r = analyze('your text here'); print(r.composite_score, r.risk_level)"
```

**Validation Framework** -- Multi-epistemological claim validation.
Tests claims against information entropy, falsifiability (Popper),
internal consistency, and citation quality. Cross-domain scoring flags
whether a claim holds up under physics, biology, systems dynamics, and
empirical observation simultaneously.

---

### Modeling Resource Flows

**Resource Flow Dynamics** -- Models the tension between accumulation
and circulation. Tracks circulating resource (C), hoarded resource (H),
and system responsiveness (R). Single-pool ODE model for one community;
multi-agent networked model for regions with designated "hoarder" agents
(extractive corporations, occupying forces). Detects collapse when
throughput drops below 20% of peak.

```bash
python3 -m resilience.ancient_persia --mode network --agents 30 --hoarders 0,1,2
```

**Dependency Audit** -- Maps hidden subsidies, true costs, and systemic
vulnerabilities across all dependencies (water, energy, food, knowledge).
Scores each dependency by source type (commons vs. private monopoly),
degradation rate, and substitution feasibility. Outputs a vulnerability
index and sovereignty score with actionable recommendations.

---

### Assessing Risk

**Operational Risk Monitor** -- Weighted multi-criteria risk scoring
with price divergence detection (catches input substitution), field
observation analysis, and redline threshold checking. Batch-audit
multiple entities at once, sorted by risk score.

**Risk Matrix** (from parent package) -- Complements operational risk
with legal and financial risk scoring specific to indigenous contexts
(SEC, CSDDD, BIT/ISDS, ICC).

---

### Building Without Supply Chains

**Zero-Infrastructure Alerts** -- Build threat detection networks from
environmental signals that need no electricity, internet, or supply chains.
Registers signals (bird alarm calls, ground vibrations, water turbidity),
assembles them into alert systems, detects coupling synergies, and
computes network integrity scores.

**Desert Sand Energy Coupling** -- Multi-physics energy harvesting from
environmental substrates. Registers coupling techniques (piezoelectric,
triboelectric, thermoelectric, pyroelectric, acoustic), detects synergies,
and weaves them into integrated energy systems scored on power density,
efficiency, and scalability.

**Geometric Desalination** -- Models water infrastructure as a vector
space. Each dimension (energy input, water output, brine management,
mineral extraction, ecological restoration, community ownership) is a
vector. Practices are composed into systems scored by coupling density
and geometric potential. Includes traditional methods (solar stills,
fog harvesting) alongside engineering approaches.

---

### Sustaining Land and Materials

**Mineral Mulch** -- Stone-mulch microclimate simulation. Models daily
thermal cycles, pH buffering, biological activity, multi-year mineral
decay, thermal shock propagation, cumulative stress/recovery, and frost
protection. All parameters configurable -- works for any climate.

```bash
python3 -m resilience.ancient_persia daily --soil-ph 4.5 --albedo 0.4
python3 -m resilience.ancient_persia mineral --years 20
python3 -m resilience.ancient_persia frost --diameters 4 8 12 16
```

**Salvage Reclamation** -- Material recovery accounting. When components
fail, they decompose into recoverable materials and reusable parts that
feed the next build. Tracks effective salvage (gated by available tools),
innovation potential (value vs. reprocessing cost), and workshop
sovereignty score.

---

### Understanding Organizations

**Organizational Topology** -- Compares hierarchy, distributed, and
embedded-rule (bee-like) organizational structures under identical
conditions. Measures convergence speed, energy expenditure, perturbation
resilience, and failure tolerance. Useful for understanding why
centralized colonial structures fail where distributed indigenous
governance succeeds.

```bash
python3 -m resilience.ancient_persia --compare --agents 128 --perturbation-at 50 --failure-at 75
```

---

## Design Principles

- **Zero external dependencies** -- uses only Python standard library
- **Offline capable** -- no internet, API, or cloud needed
- **Physics-grounded** -- thermodynamic constraints, not assumptions
- **Configurable** -- all parameters adjustable via CLI or code
- **Dual output** -- human-readable terminal output or JSON for pipelines
- **Single file** -- copy one file, get 11 tools

## How the Modules Connect

```
  Contamination Detector ──> flags bad reports
  Validation Framework   ──> tests claims in those reports
          │
          v
  Dependency Audit ──> maps what the community actually depends on
  Operational Risk ──> scores current danger levels
          │
          v
  Resource Flow Dynamics ──> models extraction vs. circulation
  Organizational Topology ──> models governance alternatives
          │
          v
  Zero-Infrastructure Alerts ──> build detection without power
  Desert Sand Energy Coupling ──> build energy from substrate
  Geometric Desalination ──> build water systems
  Mineral Mulch ──> protect and restore soil
  Salvage Reclamation ──> recover materials from wreckage
```

## Related

See also [`resilience/recovery/`](recovery/) for 9 additional standalone
modules focused specifically on war-torn and post-conflict recovery,
organized by phase (immediate survival, short-term recovery, long-term
rebuilding).
