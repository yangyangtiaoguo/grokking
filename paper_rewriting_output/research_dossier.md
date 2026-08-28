# Research Dossier

## 1. Venue Requirements

This paper targets an ICLR-tier top ML conference, positioned in the **empirical/mechanistic science-of-deep-learning track** (the category that includes grokking phenomenology, double descent, scaling laws, and training-dynamics studies), not the learning-theory track. Concretely this means:

- **No closed-form proof expected.** Reviewers in this track evaluate whether the empirical claims are well-supported by controlled experiments, not whether a theorem is proved. This paper's explicit self-scoping ("empirical study, not closed-form theory" — see Abstract in `PAPER_SKELETON.md`) matches the track's norms rather than fighting them.
- **Reproducibility expectations.** Top-tier ML venues generally expect: code/data availability statements, exact hyperparameters, number of seeds per condition, and (increasingly, post-2023) explicit uncertainty quantification for any claimed trend. This paper's `Compute Accounting` and `Preregistration Protocol` subsections (already in the skeleton) anticipate this.
- **Page limits.** Typical top-tier ML conference main-paper limits are in the 8-10 page range plus unlimited appendix/supplementary material. Given this paper's six-claim structure plus a three-task generalization check, the appendix will need to carry most of the raw data tables (already planned: Appendix B/C in the skeleton).
- **Broader-impact / limitations statement.** Increasingly required as a dedicated section, not folded into Discussion. The skeleton's Limitations list is already non-defensive and specific (small scale, few seeds/cell, no closed-form law, Dyck-1 flagged for future work) — this is the right shape.

I do not have verified knowledge of the exact 2027 ICLR reproducibility-checklist wording; the above is general knowledge of the pattern top ML venues have followed in recent years, not a specific verified citation.

## 2. Review Criteria

For a phenomenology-style empirical paper (grokking, double descent, and similar training-dynamics work), reviewers at top ML venues typically weigh:

- **Soundness of the experimental design over sheer scale.** Papers in this genre (e.g., the original grokking paper, Omnigrok) got traction from clean, controlled small-scale experiments with clear ablations, not from parameter count. This paper's small scale (n≤12, d≤128) is a legitimate design choice for this genre as long as the paper is explicit that it doesn't claim results at larger scale — which the skeleton already does.
- **Whether negative/null results are handled honestly.** A recurring failure mode reviewers flag is a paper that quietly drops an experiment that didn't support the main narrative. This paper's `p_star` rejection (C4), the SGD "not confirmed as decisively worse without matched tuning" caveat (C5), and the Dyck-1 exploratory framing (C6) are exactly the kind of honest negative-result handling that tends to read well to careful reviewers — reviewers who catch a paper hiding an inconvenient result tend to react far more negatively than reviewers who see an honestly-scoped partial result.
- **Statistical rigor proportional to claim strength.** A claim like C3 (kinetics) that was previously flagged by an internal audit for insufficient seed count and has since been strengthened to 15 seeds with censoring-aware analysis is the right level of rigor for the strength of claim being made (partial support for "critical-slowing-like behavior," not "proven divergence").
- **Novelty relative to the most recent, most similar prior work** — here specifically Zhao (ACL 2026 Findings), the paper whose open problem this work directly answers. Reviewers will expect the paper to be crisp about exactly what Zhao's paper left open and exactly what this paper adds (continuous skew axis + boundary structure + rescue-dose characterization + cross-task check), not vague novelty claims.

## 3. Accepted Paper Patterns

Papers in the grokking/training-dynamics empirical genre that have been well received tend to share these patterns:

- **Lead with the phenomenon, not the mechanism speculation.** Show the empirical pattern (phase diagram, dose-response curve) clearly before offering mechanistic interpretation, and clearly separate "what we measured" from "what we think it means."
- **Use deliberately small, interpretable settings** (toy arithmetic tasks, small transformers) rather than trying to demonstrate the phenomenon at scale — this genre earns credibility through cleanliness of the controlled experiment, not through scale.
- **Explicit ablation/control tables that isolate one variable at a time** — this paper's `same_dist` / `rare_short` / `uniform` triplet in C2 is exactly this pattern: each control isolates one candidate explanation (more samples? rarity? full coverage?) rather than bundling everything into one comparison.
- **A "we predicted X, we got not-X, here's the corrected picture" narrative arc when applicable** — reviewers generally respond well to papers that show their own hypothesis was refined or partially wrong by the data, as long as the correction is presented as a finding (not buried). This paper's Discussion section explicitly reports that the original proposal predicted the wrong direction for the phase boundary and that this was corrected by data — this is a genre-appropriate move, not a weakness, PROVIDED it's framed as "here's what we learned," not apologetically.
- **Limitations placed prominently, not as a token final paragraph.** The genre increasingly rewards specific, falsifiable limitations statements over generic "future work" boilerplate.

## 4. Constraints for This Paper

Given the two rounds of independent audit already locked into `CLAIMS_FROM_RESULTS.md`, the paper's framing must respect these hard constraints:

1. **Do not re-inflate "empirical finite-budget phase diagram" back into "phase transition."** The audit was explicit that this distinction matters — a reviewer who catches the paper using stronger language than the evidence supports in one place, after being careful everywhere else, will discount the whole paper's rigor.
2. **C3 (kinetics) must stay at "critical-slowing-like behavior," not "proven divergence."** This claim was REJECTED in the first audit round and only reached "partial" after substantial additional evidence (15-seed censoring curves). It is the most fragile claim in the paper and should be presented with commensurate caution — likely positioned as a secondary finding supporting C1's two-regime structure, not as an equal-weight standalone contribution (the skeleton already reflects this by merging C1+C3).
3. **C4 must not be oversold as "we found the law."** The audit explicitly found E_c and 2^-alpha statistically indistinguishable out-of-sample. The honest framing (already in the skeleton) is "family discrimination without unique resolution" — this should be kept as a secondary analysis, not a headline contribution.
4. **C6/Dyck-1 must not read as "we proved a universal mechanism."** The skeleton already frames Dyck-1 as a deliberately harder out-of-domain stress test that qualifies rather than confirms the transfer claim — this framing must survive into the final prose, especially in the Abstract and Introduction where scope-creep is most likely to slip in during drafting.
5. **The "8/8 pre-specified directional predictions confirmed" claim (C5)** should be reported with the exact provenance caveat already negotiated in the skeleton's review process: these are timestamped pre-data specifications (verified via file timestamps), not formally registered predictions in an external registry — the paper should use "pre-specified" rather than "preregistered" throughout, per the third review round's finding.

These constraints are not obstacles to publishability — they are what makes the paper's claims defensible under adversarial review. A paper that stays inside them is a stronger, not weaker, submission than one that reaches for a more dramatic framing.
