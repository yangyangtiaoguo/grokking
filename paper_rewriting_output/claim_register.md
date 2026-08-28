# Claim Register

> Authoritative wording locked from `refine-logs/CLAIMS_FROM_RESULTS.md` (two independent audit rounds). Manuscript prose must match this register; any drift toward stronger language is a defect, not a style choice.

| Claim | Locked Wording (use verbatim or close paraphrase) | Forbidden Overclaim | Evidence Row(s) |
|---|---|---|---|
| C1 | Empirical finite-budget phase diagram with two failure boundaries and a two-regime (kinetic boundary layer / deep-trap interior) structure; n=12 exposure-matched replication rules out an n=10-specific artifact under the tested protocol. | "phase transition," "proven asymptotic," "rules out finite-size effects in general" | E-C1-01 to E-C1-05 |
| C2 | Among the tested interventions, only full-support uniform injection achieves complete rescue; dose transition is sharp, bracketed between 0.391% and 0.781%. | "full support is necessary," "the critical dose is exactly 1/128" | E-C2-01 to E-C2-03 |
| C3 | Critical-slowing-like behavior / increasing failure probability near the boundary, established via 15-seed censoring-fraction curves. | "critical slowing down" (unqualified), "proven divergence," "critical exponent" | E-C3-01, E-C3-02 |
| C4 | Held-out predictive test validates the single-scale model class; E_c and 2^-alpha remain statistically indistinguishable out-of-sample. | "E_c is the governing law," "we identified the boundary's exact functional form" | E-C4-01 to E-C4-03 |
| C5 | Local directional robustness within the tested perturbation range (width/lr/depth), confirmed via pre-specified (timestamped) predictions. SGD+momentum result shows "not optimizer-invariant," not "SGD is worse" (untuned). | "preregistered" (use "pre-specified" / "timestamped pre-data specification"), "SGD is a worse optimizer for grokking" | E-C5-01, E-C5-02 |
| C6 | Transfers to a second arithmetic task (modular addition) under exposure-matched controls. Third task (Dyck-1) is a deliberately harder out-of-domain stress test that qualifies rather than confirms the transfer claim; cross-task comparison is qualitative replication of ranking direction, not a controlled numeric-exposure comparison. | "universal coverage mechanism," "task-general," claiming Dyck-1 "replicated the injection ranking" without noting the weaker magnitude | E-C6-01 to E-C6-04 |

## Positive framing directive (per user's 2026-08-28 instruction, style_profile.md)

Every claim above is stated as a positive, evidence-backed finding — the "forbidden overclaim" column exists to prevent drift upward, not to invite hedged downward restatement. Do not append disclaimers beyond the locked wording (e.g., do not add "though this is based on limited seeds" after C3's censoring-curve statement — the seed count is already reported once in Methods).
