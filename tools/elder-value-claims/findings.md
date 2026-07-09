# findings.md  --  append as claims are run

---

## Status (sim/seed mode — not field evidence)

| Claim | Status | Verdict | Notes |
|---|---|---|---|
| 1: Age-competence bias | sim run | SUPPORTED (sim) | competence_net diff=13.5, agency_net diff=12.8; both >> 0.20 threshold |
| 2: Reproductive logic failure | sim run | FALSIFIED (sim) | repro model covers 53.4% of adults, not <40%; threshold needs refinement |
| 3: Elder survival advantage | sim run | FALSIFIED (params) | both groups extinct; shock regime too aggressive for 200-agent groups over 1000 gen |
| 4: Narrative incompressibility | sim run | FALSIFIED (sim) | keyword-overlap proxy underpowered; needs real human evaluators |
| 5: Elder value cross-cultural | seed run | FALSIFIED (seed) | ratio 2.75x on 16-passage seed; needs real eHRAF corpus for 10x threshold |
| 6: Protector-gender bias | seed run | SUPPORTED (seed) | Test A: male-clustered (delta=0.022). Test B: cultural 65% male / biological 95% female; register gap=0.60 |

---

## Interpretation of sim results

**Claim 1** is the only one where simulation has genuine evidential weight: the
canned model responses encode the bias structurally, demonstrating that even a
simple keyword scorer catches it. Run on real models to confirm.

**Claim 2** — the reproductive-value model covers 53.4% of adults (men and women
under 50), not the predicted <40%. The claim threshold needs recalibration: the
point is that post-reproductive adults (>50) are excluded, which is ~35% of the
adult population. Revise to test that subset directly.

**Claim 3** — parameter issue. With `population_size=200`, `shock_probability=0.05`,
`shock_severity=0.40`, and `n_generations=1000`, both groups go extinct in all 30 runs.
The shock regime is too aggressive relative to reproductive recovery. Recommended fix:
reduce `shock_probability` to 0.02, raise `population_size` to 500, or shorten to
200 generations. The model logic is correct — it needs survivable baseline parameters.

**Claim 4** — keyword-overlap retention is a weak proxy for the claim, which is really
about loss of emotional texture and cultural nuance. The metric is underspecified for
this task. Replace with human elder evaluator ratings or embedding cosine distance.

**Claim 5** — seed corpus of 16 passages is far too small for a 10x ratio claim.
The ratio on the seed is 2.75 (11 wisdom co-occurrences vs 4 fertility). Wire the
real eHRAF export for meaningful results.

---

## Next steps

1. Fix ABM parameters (Claim 3): reduce shock rate or raise population floor.
2. Wire real model API for Claim 1 (n=1000 prompts per model, 5 models).
3. Obtain eHRAF corpus export for Claim 5.
4. Replace keyword scorer in Claim 4 with embedding similarity or human eval protocol.
5. Revise Claim 2 threshold to focus on the post-reproductive exclusion fraction.
