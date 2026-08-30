# Reviewer-Aware Audit

Objection Register populated from an independent full-manuscript review (external
reviewer, sophnet.com `gpt-5.6-sol`, complete `main.tex` supplied, overall score
61/100, Major Revision). This substitutes for `structured_review.py`'s three
placeholder personas — the sophnet reviewer's findings map onto the same three
axes (Methods & Reproducibility, Contribution, Structure & Clarity) and are used
directly here rather than filling the templates with self-review.

## 1. Reviewer Value Map

| Reviewer criterion | What reviewers/editors want | Our manuscript evidence | Current weakness (pre-fix) | Revision action |
|---|---|---|---|---|
| Novelty | A continuous, mechanism-isolated axis that goes beyond Zhao's single qualitative comparison. | Contribution bullets (Introduction); Table~\ref{tab:relatedwork} vs. 4 nearest prior works. | Delta from Zhao was implicit rather than stated as a single sentence. | Introduction's second paragraph states the delta directly: continuous $\alpha$ axis + mechanism-isolated rescue vs. Zhao's 2-point comparison. |
| Significance | Evidence that the rescue mechanism is real and not an artifact of one task. | Modular-addition replication (\S4.4.2) and Dyck-1 stress test (\S4.4.3) under exposure-matched controls. | Modular addition originally read as "replication" though only 3/5 seeds reached the full threshold; risked overclaiming. | \S4.4.2 states the 3/5 seed count explicitly; Discussion frames Dyck-1 as qualifying, not confirming, transfer. |
| Technical soundness | Every stated protocol detail must be internally consistent and match the code that produced the numbers. | \S3 Setup now specifies architecture, optimizer, LR, batch size, init scale, dropout/clipping, and evaluation procedure (verified against `campaign_lib.py`/`task_ar.py`). | Original draft omitted LR, batch size, optimizer coefficients, init scale, dropout/clipping, and decoding procedure; a batch-denominator ambiguity (k of 128 replaced vs. added) was unresolved. | Added explicit hyperparameter sentence to \S3.1 (verified against `campaign_lib.py::run_cell`); added the "replaces $k$ of 128 slots, not adds $k$ extra" clarification to \S4.2 (verified against the same function's `rng.choice` batch construction). |
| Evidence sufficiency | Held-out predictions and robustness claims fully accounted for; no silent gaps between "8 pre-specified" and "N shown". | Table~\ref{tab:heldout} (family-discrimination) and Table~\ref{tab:robustness} (directional predictions). | 8 held-out $\alpha$ values were pre-specified but only 5 appeared in the table, with no explanation for the missing 3. | Verified against `results/m9_densify.json`: at $\alpha=1.7,1.9$ every tested $\lambda$ is above the $0.9$ threshold, and at $\alpha=2.65$ every tested $\lambda$ is below it, so the ceiling is not interpolable at those 3 points. \S4.3 and Table~\ref{tab:heldout}'s caption now state this explicitly rather than silently showing 5 of 8. |
| Clarity | Central quantitative claims (deep-trap non-escape, $n=12$ replication, per-cell seed density) each need a table/figure, not just prose assertion. | Figure~\ref{fig:phasediagram} (with Appendix~A seed-count table), Table~\ref{tab:gridconvergence}, Figure~\ref{fig:dyckboundary}/\ref{fig:dycktrajectory} with Appendix~B data tables. | Reviewer noted the $n=12$ replication, $10^6$-step deep-trap evidence, and Dyck-1 rescue numbers were asserted in prose without a backing table, and "Appendix C" was cited but absent from the manuscript. | Added Appendix~A (per-$\alpha$ seed-count table for the phase diagram) and Appendix~B (full Dyck-1 boundary grid + rescue-ranking table); both are the tables the missing appendix references pointed to. |
| Venue fit | Empirical/finite-budget framing throughout, not borrowed statistical-mechanics language implying an equilibrium quantity that was never measured. | \S3.4 Exposure-matching protocol; Introduction contribution bullet 1. | Both used "thermodynamics" to describe finite-budget training dynamics, which a Methods reviewer reads as an unearned physics claim. | Replaced "thermodynamics" with "failure structure" in both locations; no equilibrium/statistical-mechanical quantity is claimed anywhere in the manuscript. |

## 2. Reviewer Objection Register

| Likely objection | Where triggered | Severity | What the reviewer may say | Preemptive fix | Status |
|---|---|---|---|---|---|
| LARGECOUNTER/task hyperparameters underspecified for reproduction | \S3.1 Setup | CRITICAL | "I cannot reproduce this without LR, batch size, optimizer betas, init scale, and the evaluation procedure." | Added explicit sentence specifying AdamW $\beta=(0.9,0.999)$, no dropout/clipping, LR $10^{-3}$ cosine schedule, batch 128, init scale $10\times$ (LARGECOUNTER/Dyck-1) vs. default (modular addition), and teacher-forced full-span accuracy as the evaluation metric — all verified directly against `campaign_lib.py`/`task_ar.py`/`task_modadd.py`. | FIXED |
| Dyck-1 enumeration internally inconsistent (1430 vs. 16,796) and no negative-example handling described | \S3.5 Second and third tasks | CRITICAL | "L=8 gives 1430 paths, L=10 gives 16,796 — which is it? And a recognition task needs negatives." | Confirmed via `task_dyck1.py`/`dyck_campaign.py` that only $L=10$ (16,796, $C_{10}$) was used in the formal campaign; removed the conflicting "1430" mention. Added the deterministic-position masking rule (verified against the code's `if d==0 or remaining==d` logic) explaining why forced-token scoring makes explicit negative examples unnecessary. | FIXED |
| Boundary/ceiling claim extrapolates beyond the stated $\lambda$ range | \S4.1 Failure Map, Figure~\ref{fig:phasediagram} | MAJOR | "Figure 1 says $\lambda\in[0.05,0.5]$ but the $\alpha=1.5$ ceiling's CI sits entirely above 0.5." | Verified against `stats_appendix.json`: $\alpha\le1.5$ was probed up to $\lambda=1.0$. \S4.1's caption/prose now state the extended probe range explicitly rather than only the narrower default grid. | FIXED |
| Batch-injection denominator ambiguous ($k/128$ vs. $k/129$) | \S4.2 Coverage Intervention | MAJOR | "Is the dose $k$ added to a 128-batch or one of 128 slots replaced?" | Verified against `campaign_lib.py::run_cell`'s `rng.choice(..., size=batch-k) + rng.choice(..., size=k)` construction (fixed total of 128); \S4.2 now states explicitly that $k$ replaces, not adds to, 128 slots. | FIXED |
| "Full-support coverage" overclaims what the controls isolate, since $P_\alpha$ already has full support | \S4.2 Coverage Intervention, Introduction | MAJOR | "The skewed distribution already has full support; your controls vary breadth of the injected slot's sampling, not presence/absence of support." | Reworded \S4.2, the Introduction, and the Discussion to describe the controls as varying "breadth of the injected examples' exposure across the state space" rather than "full-support coverage" being introduced by the intervention. | FIXED |
| "Thermodynamics" language unearned for a finite-budget empirical study | Introduction contribution bullet 1, \S3.4 | MINOR | "No equilibrium/statistical-mechanical quantity is actually measured here." | Replaced both instances with "failure structure". | FIXED |
| Held-out point accounting gap (8 pre-specified, only 5 shown) | \S4.3 Boundary Candidate Summary, Table~\ref{tab:heldout} | MAJOR | "What happened to the other 3 of 8 pre-specified points?" | Verified against `results/m9_densify.json` + `results/m10_predictions.json`: the 3 missing points ($\alpha=1.7,1.9,2.65$) have their entire tested $\lambda$ grid on one side of the $0.9$ threshold, so no ceiling is interpolable there. \S4.3 and the table caption now state this explicitly. | FIXED |
| Central quantitative results (per-cell seed density, Dyck-1 full grid/rescue data) asserted without a backing table; "Appendix C" cited but absent | \S4.1, \S4.4.3 | MAJOR | "Appendix C is cited but there is no appendix in the submitted manuscript." | Added `\appendix` with Appendix~A (per-$\alpha$ seed-count table, phase diagram) and Appendix~B (full Dyck-1 boundary grid + injection-ranking table); updated in-text `Appendix~A`/`Appendix~B` references to match. | FIXED |
| No code/data availability statement | End of manuscript | MAJOR | "Where is the code/data that produced these numbers?" | Added a "Code and data availability" statement before the appendix, describing the retained timestamped JSON logs and scripts. | FIXED |
| Terminology drift between Trap/Crush verdict labels and "trapped"/"starved" prose language | \S3.3 Verdict rule, \S4.2 | MINOR | "Trap/Crush and trapped/starved aren't obviously the same two things." | \S4.2 now explicitly maps \textsc{Trap} to "trapped on the head" and \textsc{Crush} to "starved of any learnable signal" at first use. | FIXED |
| Modular-addition "replication" claim reads stronger than 3/5-seed evidence | \S4.4.2 | MINOR (already scoped correctly) | "Only 3 of 5 seeds reach the generalization threshold — is this really a replication?" | \S4.4.2 already states the 3/5 count explicitly and the Introduction frames it as "transfer," not "replication"; no further change needed. | NO_CHANGE_NEEDED |
| Statistical-test formalization for "statistically indistinguishable" (E_c vs. $2^{-\alpha}$) and formal significance tests elsewhere | \S4.3, \S4.1 | MINOR | "What test establishes 'statistically indistinguishable'? A CI-overlap eyeball is not a formal test." | Scoped out for future work per the user's explicit instruction to leave some findings (formal significance testing beyond bootstrap CIs and pre-specified thresholds) for a follow-up rather than retrofitting new statistical machinery into this submission. | OPEN (scoped to future work, by design) |

## 3. Editorial Fit Map

- **Venue fit:** ICLR-tier ML conference, empirical grokking/generalization track. The paper's scope (finite-budget empirical phase diagram + mechanism-isolating rescue controls + cross-task transfer test) matches the venue's appetite for rigorously-scoped empirical characterization papers, and explicitly avoids the stronger asymptotic/statistical-mechanics claims that would put it in a physics-of-learning track instead.
- **Editor-facing value:** A continuous-axis, mechanism-isolated answer to an open question (Zhao 2026) left as a single qualitative comparison, replicated across two problem sizes and two additional tasks under exposure-matched controls — a concrete, falsifiable extension an editor can defend to the board as advancing a specific open question rather than a broad survey.
- **Desk-reject risks:**
  - Missing hyperparameters/reproducibility details — RESOLVED (added to \S3.1).
  - Internal numeric inconsistency (Dyck-1 enumeration, boundary $\lambda$-range) — RESOLVED (both traced to source data and corrected).
  - Cited-but-missing appendix — RESOLVED (Appendix~A/B added).
  - No code/data availability statement — RESOLVED (statement added).
  - Overlap with prior work — not a risk; Table~\ref{tab:relatedwork} explicitly differentiates against the 4 nearest works along 6 axes.

## Round 5 addendum (post-revision independent re-review)

A fresh independent review of the round-4-revised manuscript (same external reviewer,
sophnet.com `gpt-5.6-sol`) scored it 58/100, Major Revision — lower than round 4's 61,
because it surfaced one genuine CRITICAL defect the round-4 fix pass had missed, plus
several MAJOR findings. Each was verified against the actual experiment code
(`task_ar.py`, `task_modadd.py`, `task_dyck1.py`, `m8_dose_response.py`,
`m11_factorial.py`, `m4_fits.py`) before any text was changed — some reviewer claims
were confirmed true, at least one was found to be factually wrong against the code
(module-addition zero-injection baseline), and one additivity-test miscount in the
robustness table was independently caught and fixed during verification (depth=3
was not actually confirmed against baseline).

| Finding | Severity | Verification | Resolution |
|---|---|---|---|
| LARGECOUNTER task construction contradicted itself: prose said "model generates the full sequence bin(0)#bin(1)#...#bin(2^n-1)" but the skew protocol samples individual states $x$, and evaluation referred to a "2n-bit target span" | CRITICAL | Confirmed against `task_ar.py::make_sequences`: each training example is a single transition $x\to x+1$, input includes $\mathrm{bin}(x)$ explicitly, loss masked to the $n$ target bits only. The manuscript's "no external input reveals the counter" framing was incompatible with the actual code. | \S3.1 rewritten to describe the transition-based construction precisely, remove the "full sequence"/"$2n$-bit span" language, and state that $A_{\mathrm{unif}}$/$A_{\mathrm{hi}}$ average per-transition accuracy over all $2^n$ states. |
| Dyck-1 "recognition" mislabeled: only valid paths are used and scoring happens at grammar-forced positions, not on arbitrary accept/reject strings | MAJOR | Confirmed against `task_dyck1.py`: no invalid-string examples exist anywhere in the pipeline. | Renamed the task throughout to "Dyck-1 forced-position prediction"; \S3.5 states precisely what is forced vs. free and why no negative examples are used. |
| Sub-$1/128$ doses in the dose-response curve had no stated implementation | MAJOR | Confirmed against `m8_dose_response.py::DOSE_CELLS`: $k=1$ is held fixed and batch size is varied (1024/512/256/128), with step count scaled inversely to hold total sample count fixed. | \S4.2 now states the exact batch/step schedule and the resulting $p$ values for every plotted dose. |
| "Breadth of exposure is what matters" still read as isolating breadth independently of entropy/state-composition confounds | MAJOR | Agreed as a genuine scope gap — the three controls vary uniform vs. one targeted set, not breadth alone; this would need new factorial controls (entropy-matched, cardinality-matched) to fully decompose, which is out of scope for this revision per the user's explicit instruction to avoid over-correcting into new experiments. | \S4.2 narrowed to "among these three tested distributions, uniform full-state injection is the one that rescues," with an explicit note that entropy/state-composition are confounded with breadth in this comparison. |
| Modular-addition section claimed no zero-injection baseline exists | MAJOR | **Reviewer was factually wrong**: `m12_modadd_targeted.json` contains a $k=0$ baseline (mean $0.413$, 0/3 generalizing) that had simply not been written into the prose. | \S4.4.2 now reports the baseline explicitly; "replication" reworded to "ranking direction reproduces... we read this as ranking transfer rather than a matched-magnitude replication," since uniform injection here only reaches 3/5 vs. LARGECOUNTER's 8/8. |
| Family-discrimination candidates: only 2 of 5 formulas given, no fitting objective stated, "statistically indistinguishable" unquantified | MAJOR | Verified against `m4_fits.py`: 5 candidates are $E_\alpha[c]$, $2^{-\alpha}$, $H_{\mathrm{lo}}$, $H_{\mathrm{tail10}}$, $p_\star$, fit by log-space least squares on the original 8-point grid. | \S4.3 now states all 5 formulas, the fitting procedure, and per-point error comparison between the top 2 candidates (replacing "statistically indistinguishable" with the actual per-point margins, $\le 7.4$ points). |
| Robustness table: "eight directional predictions, all confirmed" miscounted 9 listed perturbations, and depth=3 (predicted easier) was asserted confirmed without checking against baseline | MAJOR (self-caught during verification, not the reviewer's exact framing) | Verified against `m11_factorial.json` and the underlying $n{=}10$ boundary grid: baseline at the two cells is 5/5 and 3/5 grok; depth=3 is 5/5 (tied with baseline, already at ceiling) and 3/5 with a lower mean accuracy ($0.807$ vs.\ baseline $0.853$) — not an improvement. | \S4.4.1 now states 9 total perturbations (8 directional + 2 interaction-only), reports depth=1 as confirmed and depth=3 as **not confirmed**, with the exact baseline and post-perturbation means/grok-counts in Table~\ref{tab:robustness}. |
| Code/data statement said material is "retained," not actually available | MAJOR | Agreed — "retained" is not a release commitment. | Rewritten as a public-release-on-publication commitment, without fabricating a repository URL that does not yet exist. |
| $n=12$ replication asserted only as a single ratio (1.42$\times$), full grid not shown | MINOR | Verified against `p11_n12_grid.json`. | Added Table~\ref{tab:n12grid}, the full $7\times6$ grid. |
| Table~\ref{tab:heldout} declared 5 columns (`lcccc`) but had 4 | MINOR | Confirmed a genuine LaTeX mismatch. | Fixed to `lccc`. |

**Not acted on (explicitly, by design):** the reviewer's request for formal significance
tests (named test statistic / $p$-value) for "statistically indistinguishable" comparisons,
a real archived code repository with DOI, and new factorial controls to decompose breadth
from entropy/state-composition. These require either new infrastructure (a public
repository, which cannot be fabricated) or new experiments (factorial controls), not
textual correction of an existing result, and are left for future work per the user's
explicit instruction not to let review requests for additional apparatus expand this
revision indefinitely.

## Round 6 addendum (second post-revision independent re-review)

A third independent review of the round-5-revised manuscript (same external reviewer,
sophnet.com `gpt-5.6-sol`, explicitly instructed to check its own round-5 review for
over-defensiveness rather than re-litigate resolved items) scored **64/100, Major
Revision** — up from round 5's 58, with **no CRITICAL defect remaining**. The reviewer
explicitly confirmed 10 round-5 items as adequately resolved (LARGECOUNTER construction,
Dyck-1 labeling, sub-1/128 disclosure, modular-addition baseline, family formulas,
depth-3 correction, n=12 grid, table fix, code/data commitment, and accepted that no new
factorial controls or formal significance tests were required). It raised 4 new findings,
verified against code/data before any edit:

| Finding | Severity | Verification | Resolution |
|---|---|---|---|
| Sub-1/128 dose bracket confounds dose with batch size and optimizer-update count (0.391% uses batch 256/~30k updates, 0.781% uses batch 128/60k updates) | MAJOR | Confirmed against `m8_dose_response.py::DOSE_CELLS` — this is a genuine design confound, not a reporting gap; a clean test would need fixed batch/steps with probabilistic fractional injection. | Acknowledged explicitly in \S4.2 and the abstract (renamed "dose-and-batch-schedule transition"); pointed to the already-reported fixed-batch 15k-step result as partial evidence against a pure update-count explanation, rather than fabricating a new controlled experiment mid-revision. |
| Robustness section: "nine perturbations," "eight directional," "seven of eight confirmed" are mutually inconsistent, and confirmation lacked a stated decision rule (e.g. d=128 at cell 1 was labeled confirmed on a 4/5-vs-5/5 grok-count difference despite baseline already being within a few points of the accuracy ceiling) | MAJOR | Recomputed all 9 conditions' mean accuracy against baseline at both cells directly from `m11_factorial.json` and the underlying $n{=}10$ boundary grid. Correct count is 7 directional predictions + 2 non-directional interaction cells. Re-applying a single stated criterion (mean accuracy moves in the predicted direction at both cells) found only 4 of 7 confirmed at both cells, not 6 or 7. | \S4.4.1 and Table~\ref{tab:robustness} rewritten with the corrected count (7, not 8 or 9), an explicit stated criterion, and per-condition means at both cells; d=128 and lr=$5\times10^{-4}$ reclassified as "confirmed at cell 2 only" given the cell-1 ceiling effect. |
| Modular addition and Dyck-1 protocols still underspecified for reproduction (exact serialization, loss masking, injection-pool definitions, and — for Dyck-1 — the exact skew formula) | MAJOR | Verified against `task_modadd.py` (sequence `[a,b,SEP,(a+b) mod p]`, loss only at the final position, tail/head pools by operand-$a$ decile) and `task_dyck1.py` (`depth_index` = stable-sorted rank of max nesting depth, `P_alpha(pi) ∝ (rank+1)^{-alpha}`, tail/head pools by depth quintile). | \S3.5 rewritten with the exact sequence format, loss position, and injection-pool definitions for both tasks, and the precise rank-based skew formula for Dyck-1. |
| Residual causal language ("mechanism-isolating controls," "isolates coverage as the operative mechanism," related-work table's "(isolated)" column) still overstated what a 3-arm ranking without entropy/state-composition controls can support | MAJOR | Agreed — this is the same confound flagged in round 5, but the round-5 fix had only softened the abstract/results-rescue paragraph, not the contribution bullet, conclusion, and related-work table. | All remaining instances changed to "ranking"/"ranked" language: contribution bullet 2, the conclusion, and the related-work table's column now read "controlled ranking" / "(ranked)" rather than "isolated." |

Two numerical precision findings (MINOR) were also independently verified and fixed:
$E_\alpha[c]$'s maximum held-out error rounds to $27\%$, not the $26\%$ previously stated
(recomputed directly from `m4_fits.py`'s candidate functions against the rounded
measured ceilings); "exposure-matched" was narrowed to "sample-count-matched" for the
modular-addition transfer claim throughout, since only injected-slot count and batch
size are matched there, not per-state exposure or distributional support (reserving
"exposure-matched" for the $n=12$ finite-size check, where budget scaling does match
per-state visitation).

**Not acted on (explicitly, by design):** the reviewer's suggestion of a new factorial
dose experiment holding batch/steps fixed with probabilistic fractional injection. This
would require new GPU experiments beyond the scope of a text-correction revision pass;
the confound is instead disclosed plainly in one place (not repeated as a hedge
elsewhere), consistent with the user's standing instruction to fix genuine errors without
manufacturing new apparatus mid-revision or scattering the same caveat across multiple
sections.

## Round 7 addendum (new experiment closing round 6's MAJOR-1)

Contrary to the round-6 stance above ("not acted on... would require new GPU
experiments beyond scope"), the user approved running the deconfounding experiment
after all, since GPU budget and time allowed it. `experiments/m13_dose_clean.py`
holds batch size (128) and step count ($60{,}000$) fixed throughout — identical to
the paper's primary protocol — and implements fractional expected dose $q/128$ by
replacing one batch slot with probability $q$ at each step, rather than varying
batch size with dose as the original M8a sweep did. 120 runs (3 $\alpha$ values
$\times$ 5 $q$ values $\times$ 8 seeds) completed cleanly in 11{,}127s with no
anomalies.

**Result, reported as found rather than selectively**: the deconfounded sweep
confirms the dose effect's direction and rough location (pooled mean accuracy rises
monotonically from $0.478$ at $q{=}0.1$ to $0.924$ at $q{=}1.0$), but shows a
markedly more gradual rise than the original batch-varying protocol's near-binary
jump ($0$--$2$/8 $\to$ $8$/8). We read the original sharpness as partly an artifact
of the batch/update-count confound rather than a property of dose alone — this is
the honest finding, not the one that would have looked better for the paper's
"sharp transition" framing. \S4.2 and the abstract were rewritten accordingly:
the "sharp dose transition" language was replaced with a report of both sweeps
(the original batch-varying one, retained because the mechanism-isolating controls
and the $15$k-step result reuse its protocol, and the new deconfounded one, reported
as the more reliable characterization of the transition's shape), with a new table
(Table~\ref{tab:doseclean}) giving the full deconfounded grok-fraction and
mean-accuracy numbers per dose point. This closes round 6's MAJOR-1 with a genuine
new measurement rather than a textual reframing of the existing confounded data.

## Round 8-9 addendum (score jump: 64 -> 84/100, Minor Revision)

A fourth independent review of the M13-revised manuscript (same external reviewer)
scored **84/100, Minor Revision** (up from round 6's 64, Major Revision), stating
"Subject to these changes, I would support acceptance." All three dimensions rose
to 4/5. Verified prior fixes: deconfounded dose experiment, robustness count/criterion,
modular-addition/Dyck-1 protocol specificity, numerical rounding, and — new this round
— the GitHub repository (`https://github.com/yangyangtiaoguo/grokking`) was confirmed
present in the manuscript text as a real URL, not a release promise.

The reviewer also flagged one item we had judged (incorrectly, on reflection) as
acceptable in round 6: several Related Work sentences still used "mechanism-isolating"
and "isolates coverage" language that contradicts the Results section's own,
correctly-hedged statement that the ranking does not decompose breadth from entropy
and state composition. This was a genuine internal inconsistency, not an
over-demanding request — fixed by rewording the two Related Work instances to
"controlled injection ranking" / "points to a data-side coverage effect."

Remaining MINOR items (textual/reporting fixes, no new experiments): "rises
monotonically" corrected to "rises through $q=0.75$ and then plateaus" (the pooled
means are not strictly monotonic); "sufficient for rescue" softened to "onset of
substantial rescue probability" in both the dose section and abstract; the
same-distribution control's mechanism description corrected (it is a null resampling
of the same distribution, not a change to batch composition); the robustness
contribution bullet reworded to state "4 of 7 directional predictions confirmed"
rather than an unqualified "locally robust"; "validated" softened to "evaluated by"
for the family-discrimination bullet; a per-$\alpha$ breakdown of the deconfounded
dose sweep added as Appendix C (the pooled table alone obscured whether the effect
was uniform across skew values); and the Limitations subsection extended by one
sentence covering the robustness confirmation rate and the breadth/entropy/state-
composition confound, rather than the reviewer's full 8-item checklist — per the
user's explicit instruction to fix genuine issues without padding the paper with an
exhaustive limitations list.
