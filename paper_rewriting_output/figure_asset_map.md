# Figure/Table Asset Map

| Asset ID | Type | Content | Source Data | Section | Status |
|---|---|---|---|---|---|
| Fig1 | Figure | (α, weight-decay) phase diagram heatmap with bootstrap-CI boundary band + budget-band overlay (two-regime structure) | `results/p8_phase_diagram.json` + `results/m1_n10_boundary.json` + `results/m9_deeptrap.json`, via `stats_appendix.json` §1/§3 | 4.1 Failure Map and Kinetics | to generate (matplotlib, no AI image generation per academic-ai-tells hard rule on data figures) |
| Fig2 | Figure | Dose-response curve: A_unif vs. injection dose (log scale), three mechanism-isolating conditions (same_dist/rare_short/uniform) as distinct series | `results/m8a_dose_sweep.json`, `results/m8b_confound.json` | 4.2 Coverage Intervention | to generate |
| Fig3 | Figure | Censoring-fraction curve (primary) + median-tau curve (secondary) across two wd transects | `results/m7_tau_dense.json`, via `stats_appendix.json` §2 | 4.1.3 Kinetics | to generate |
| Fig4 (supporting) | Figure | Grid-resolution convergence: sparse-grid vs. dense-grid ceiling estimates | `stats_appendix.json` §3 | 4.1 (supporting, addresses "coarse-grid artifact" question) | to generate |
| Fig5 | Figure | Modular-addition exposure-matched injection ranking bar chart (uniform/tail/head) | `results/m12_modadd_targeted.json` | 4.4.2 Modular Addition Transfer | to generate |
| Fig6 (appendix) | Figure | Dyck-1 60k vs. 240k trajectory comparison at (α=6.0, wd=0.9), showing peak-then-collapse pattern | `results/dyck_budget.json` (full 241-point aunif sequences per run) | Appendix C (cited in 4.4.3 main text) | to generate |
| Table1 | Table | Held-out prediction test: 8 alphas, E_c/2^-alpha predicted vs. measured, error columns | `results/m10_predictions.json`, `results/m9_densify.json` | 4.3 Boundary Candidate Summary | to generate |
| Table2 | Table | 8 pre-specified directional predictions vs. measured outcomes (width/lr/depth/SGD, 2 interaction cells) | `results/m11_factorial.json` | 4.4.1 Robustness | to generate |
| Table3 | Table | Related-work comparison: nearest works × (tests skew / finite-budget mapping / rescue controls / exposure matching / task transfer / scale) | `sota_gap_map.md` | Related Work / Discussion | to generate |
| Table4 (appendix) | Table | Full hyperparameters (n, d, layers, heads, lr, batch, isc, optimizer, steps) per experiment family | `refine-logs/EXPERIMENT_PLAN.md`, `experiments/*.py` | Appendix A | to generate |

## Notes

- No figure in this paper uses AI-generated images; all are produced directly from the JSON result files via matplotlib/plotting scripts, per the project's own data-integrity discipline and the academic-ai-tells hard rule (raw experimental data figures must never be AI-generated or AI-modified).
- Fig6 (Dyck-1 trajectory) is the one figure the auto-review-loop process specifically required be placed in the main text if the word "metastability" is retained in body prose (per Round-2 review finding) — currently planned for Appendix C with a citation from the main-text paragraph; confirm placement when drafting 4.4.3.
