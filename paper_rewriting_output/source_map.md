# Source Map

Maps this project's material base (`build_from_materials` workflow) to paper sections.

| Material | Path | Maps To |
|---|---|---|
| Reviewed paper skeleton (3-round cross-model review, 8.5/10) | `review-stage/PAPER_SKELETON.md` | Overall structure, section ordering, exact claim wording (C1-C6) |
| Independent claim audit (2 rounds) | `refine-logs/CLAIMS_FROM_RESULTS.md` | Authoritative wording for every quantitative claim; do not drift stronger |
| Experiment tracker (full run history) | `refine-logs/EXPERIMENT_TRACKER.md` | Methods/Compute Accounting, provenance for every reported number |
| Experiment plan | `refine-logs/EXPERIMENT_PLAN.md` | Methods design rationale, pre-registration references |
| Pilot + formal + supplementary results (all raw data) | `results/*.json` (53 files) | All figures/tables; source of truth, no fabricated numbers |
| Recomputed writing-stage statistics | `paper_rewriting_output/stats_appendix.{json,md}` | Bootstrap CI, censoring tables, grid convergence, threshold sensitivity (Results + Appendix) |
| Project history / theory derivation notes | `选题现状说明.md` | Discussion (contrast with original mispredicted proposal), Related Work framing |
| Foundational paper (task definition source) | `papers/zhao_counting.pdf` | Setup (task definition), Related Work (open problem this paper answers) |
| Citation audit memory | (session memory `grokking-citation-audit`) | Related Work citation accuracy — verified arXiv IDs, corrected hallucinated ref |
| Experiment code (for method reproducibility) | `experiments/*.py` | Methods section code-path citations |

## Notes

- This is a `build_from_materials` paper: there is no prior "original manuscript" to rewrite. The skeleton in `review-stage/` already encodes the argument structure after independent review; this stage's job is to source external SOTA/venue context and citations to wrap around that already-audited internal structure, not to re-derive the argument from scratch.
- All quantitative claims trace to `results/*.json`; any number appearing in the manuscript must be traceable to a specific result file (per project's own evidence-precheck discipline established during the `/result-to-claim` audits).
