# Evidence Bank

> Maps every quantitative claim in the manuscript to its exact source file/computation. No number in the manuscript may lack a row here.

| Claim ID | Statement | Source File(s) | Computation | Verified |
|---|---|---|---|---|
| E-C1-01 | wd-ceiling decreases monotonically with α on n=10, 60k-step budget | `results/m4_fits.json`, `results/p8_phase_diagram.json`, `results/m1_n10_boundary.json` | `paper_rewriting_output/compute_stats_appendix.py` Analysis 1 | yes (recomputed 2026-08-28) |
| E-C1-02 | Boundary ceilings with 90% bootstrap CI (8 alphas, n=10, 60k budget) | same as above | `stats_appendix.json` §analysis_1_bootstrap_ci_boundary | yes |
| E-C1-03 | Grid-resolution convergence: sparse vs. dense grid ceilings agree at α≥2.5 | `results/p8_phase_diagram.json`, `results/p10_fine_boundary.json`, `results/p10b_gap_fill.json`, `results/m1_n10_boundary.json` | `stats_appendix.json` §analysis_3_grid_resolution_convergence | yes |
| E-C1-04 | n=12 exposure-matched boundary reproduces n=10 structure (ceiling ratio ~1.42) | `results/m1_n12_boundary.json`, `results/p11_n12_grid.json` | manual ratio computation, session analysis 2026-08-25/26 | yes |
| E-C1-05 | Deep-trap cells (α=2.25, 2.5 @ wd=0.3) do not escape at 1M steps (4x budget) | `results/m9_deeptrap.json` | direct read, 8 runs | yes |
| E-C4-01 | Threshold sensitivity: GROK fraction stable across thr=0.85/0.90/0.95 | `results/p8_phase_diagram.json` | `stats_appendix.json` §analysis_4_threshold_sensitivity | yes |
| E-C2-01 | Dose-response: sharp transition bracketed 0.391%-0.781%, consistent across 3 alphas | `results/m8a_dose_sweep.json` | direct read, 120 runs | yes |
| E-C2-02 | Mechanism isolation: same_dist (0.282) < rare_short (0.750) < uniform (0.956) | `results/m8b_confound.json`, `results/m2b_targeted.json` | direct read | yes |
| E-C2-03 | Minimal rescue at B=15k steps (3/3 grok with only ~15k injected samples) | `results/m2c_mstar_budget.json` | direct read | yes |
| E-C3-01 | Censoring-fraction curve, wd=0.3 transect, monotonic 0%→60% across α=1.5-2.25, 15 seeds | `results/m7_tau_dense.json` | `stats_appendix.json` §analysis_2_censoring_tables | yes |
| E-C3-02 | Median tau (observed, wd=0.05 transect), 12k→171k across α=2.0-2.75 | `results/m7_tau_dense.json` | same | yes |
| E-C4-02 | Held-out predictive test: E_c and 2^-alpha error 15%/18% mean, 26%/33% max, both below in-sample max error | `results/m10_predictions.json`, `results/m9_densify.json` | session analysis 2026-08-27 | yes |
| E-C4-03 | p_star candidate pre-registered and rejected (max err 20.5x vs E_c's 0.96x) | `results/m4_fits.json` | direct field read | yes |
| E-C5-01 | 8/8 pre-specified directional predictions confirmed (width/lr/depth/SGD) | `results/m11_factorial.json` | direct read, 90 runs | yes |
| E-C5-02 | SGD+momentum near-chance performance (mean unif=0.001) vs AdamW baseline (~0.9-0.97) | `results/m11_factorial.json` | direct read | yes |
| E-C6-01 | Modular addition exposure-matched injection ranking: uniform (0.934, 3/5 grok) ≫ tail (0.721, 0/5) ≫ head (0.396, 0/5) | `results/m12_modadd_targeted.json` | direct read, 18 runs | yes |
| E-C6-02 | Dyck-1 formal boundary: 540 runs, failure region α≥5/wd≥0.8-ish, deep collapse to fixed degenerate accuracy | `results/dyck_boundary.json` | direct read | yes |
| E-C6-03 | Dyck-1 rescue: uniform k=1 gives only 2/5 partial improvement (0.398 mean) vs full rescue elsewhere | `results/dyck_rescue.json` | direct read, 18 runs (incl. tail/head follow-up) | yes |
| E-C6-04 | Dyck-1 budget: 60k→240k at (α=6.0, wd=0.9) shows shallow-grok metastability, not "more training hurts" | `results/dyck_budget.json` | trajectory-level diagnosis, session 2026-08-27 | yes |
| E-M0-01 | Sanity: tail injection (0.575) vs uniform injection (0.956) at same cell | `results/m0_sanity.json` | direct read | yes |

## Provenance note

All rows recomputed or read directly from raw JSON in `results/` during this project's own sessions (P0-P11b pilot chain, M0-M12 formal campaign, Dyck-1 campaign). No number is estimated, extrapolated, or carried forward from an unlogged source.
