# Section Blueprints

> Manuscript order and per-section function. Detailed writing decisions are in `writing_rationale_matrix.md`; this file is the navigable outline.

## Title
Empirical Phase Diagrams of Grokking Failure under Data Skew, and a Low-Dose Rescue Intervention

## Abstract
Locked wording from `PAPER_SKELETON.md` (already passed 3 review rounds). States: finite-budget empirical phase diagram; sharp dose transition bracketed 0.391%-0.781%; among-tested-interventions coverage claim; second-task transfer + Dyck-1 qualification; scale disclaimer stated once.

## 1. Introduction
1.1 Grokking phenomenon + Zhao's open question (what stratification does/does not do)
1.2 Confirmed motivation statement (A+B blend): phase diagram as structural discovery + precise answer to Zhao's rescue question
1.3 Contribution list in narrative order (C1+C3 map → C2 central rescue result → C4 sub-analysis → C5+C6 validation)
1.4 Explicit scope statement paragraph (empirical, not asymptotic; two arithmetic tasks + one exploratory stress test)

## 2. Related Work
2.1 Foundational grokking (Power et al., Liu et al. effective theory, Omnigrok, Nanda et al.)
2.2 Mechanism-diversity survey (circuit efficiency, group-theoretic, implicit-bias, complexity/compression, circuit-synchronization, representational-prior accounts) — positions this paper's coverage-mechanism finding among competing accounts
2.3 Phase-transition-framing papers (Bi et al., Wang, Rubin et al., Truong et al.) — explicit differentiation from this paper's empirical/finite-budget framing
2.4 Data-fraction / rescue-mechanism precedents (Liu et al. x2, Singh et al., Xu et al., Zhou et al.) — positions C2's dose characterization
2.5 Succinctness/RASP/formal-language foundations (Bergsträßer et al., Weiss et al., Merrill/Sabharwal line, Dyck-recognition papers) — grounds task design (LARGECOUNTER + Dyck-1)
2.6 Comparison table (Table3): nearest works × axes tested

## 3. Setup
3.1 Main task: LARGECOUNTER autoregressive big-endian counter (n=10/12)
3.2 Frozen verdict rule (GROK/TRAP/CRUSH/PARTIAL)
3.3 Statistical analysis plan (bootstrap CI, censoring treatment, grid-resolution convergence, threshold sensitivity) — executed, results in `stats_appendix.md`
3.4 Second/third tasks: modular addition (p=97), Dyck-1 (L=10)
3.5 Exposure-matching protocol (necessary experimental control, not a standalone methods contribution)
3.6 Preregistration protocol (M10 held-out predictions, M11 directional predictions — timestamped pre-data specification)
3.7 Compute accounting
3.8 Cross-task exposure/verdict comparability statement (qualitative ranking replication, not numeric-exposure-matched comparison)

## 4. Results
4.1 Failure Map and Kinetics (C1+C3 merged)
4.2 Coverage Intervention: The Central Result (C2)
4.3 Boundary Candidate Summary (C4, sub-analysis)
4.4 Local Robustness and Task Transfer (C5+C6)
  4.4.1 Robustness (C5)
  4.4.2 Modular Addition Transfer (C6.1)
  4.4.3 Dyck-1 Stress Test (C6.2)

## 5. Discussion
5.1 Contrast with the original proposal (λ_c direction correction, refuted curriculum prediction)
5.2 Related-work synthesis (Table3 discussion)
5.3 Limitations (≤3 items, per style_profile.md disclosure rules)

## 6. Conclusion

## Appendix
A. Hyperparameters — B. Full boundary/dose/tau data tables — C. Dyck-1 full data + trajectory figure — D. Citation audit record
