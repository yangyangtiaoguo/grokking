# Statistics Appendix (recomputed from results/*.json)

> Source: Recomputed 2026-08-28 from results/*.json per PAPER_SKELETON.md Sec 3.3 writing-stage TODO. Code: paper_rewriting_output/compute_stats_appendix.py

## 1. Bootstrap CI for boundary ceilings (n=10, 60k-step budget)

| alpha | tag | point estimate | 90% bootstrap CI | n_boot |
|---|---|---|---|---|
| 0.0 | > | 0.5000 | N/A (bound, not resolved) | - |
| 1.0 | > | 1.0000 | N/A (bound, not resolved) | - |
| 1.5 | ~ | 0.7638 | [0.7026, 0.8513] | 2000 |
| 2.0 | ~ | 0.3049 | [0.3017, 0.4009] | 2000 |
| 2.1 | ~ | 0.1901 | [0.1761, 0.2000] | 1879 |
| 2.25 | ~ | 0.1230 | [0.1216, 0.1708] | 2000 |
| 2.4 | ~ | 0.1167 | [0.1152, 0.1205] | 1994 |
| 2.5 | ~ | 0.0886 | [0.0865, 0.1012] | 2000 |
| 2.6 | ~ | 0.0697 | [0.0678, 0.0910] | 2000 |
| 2.7 | ~ | 0.0506 | [0.0438, 0.0600] | 1806 |
| 2.75 | < | 0.0200 | [0.0307, 0.1017] | 1374 |
| 2.9 | < | 0.0200 | [0.0401, 0.0458] | 704 |
| 3.0 | < | 0.0200 | N/A (bound, not resolved) | - |

## 2. Censoring-fraction tables (tau transects, results/m7_tau_dense.json)

| alpha, wd | n | censored | censoring fraction | median tau (observed) |
|---|---|---|---|---|
| alpha=2.0,wd=0.05 | 15 | 0 | 0.00 | 12000 |
| alpha=2.2,wd=0.05 | 15 | 0 | 0.00 | 17000 |
| alpha=2.4,wd=0.05 | 15 | 0 | 0.00 | 74500 |
| alpha=2.5,wd=0.05 | 15 | 0 | 0.00 | 112250 |
| alpha=2.6,wd=0.05 | 15 | 2 | 0.13 | 124250 |
| alpha=2.7,wd=0.05 | 15 | 2 | 0.13 | 177500 |
| alpha=2.75,wd=0.05 | 15 | 1 | 0.07 | 171250 |
| alpha=1.5,wd=0.3 | 15 | 0 | 0.00 | 2000 |
| alpha=1.75,wd=0.3 | 15 | 0 | 0.00 | 107500 |
| alpha=2.0,wd=0.3 | 15 | 0 | 0.00 | 197000 |
| alpha=2.1,wd=0.3 | 15 | 4 | 0.27 | 217750 |
| alpha=2.2,wd=0.3 | 15 | 8 | 0.53 | 223500 |
| alpha=2.25,wd=0.3 | 15 | 9 | 0.60 | 227500 |

## 3. Grid-resolution convergence (sparse pilot grid vs dense grid)

| alpha | sparse ceiling | sparse #wd | dense ceiling | dense #wd |
|---|---|---|---|---|
| 0.0 | >0.5000 | 6 | >0.5000 | 6 |
| 1.0 | >0.5000 | 6 | >1.0000 | 8 |
| 2.0 | ~0.3047 | 9 | ~0.3049 | 11 |
| 2.1 | ~0.1668 | 4 | ~0.1901 | 7 |
| 2.25 | ~0.1240 | 10 | ~0.1230 | 11 |
| 2.4 | >0.0800 | 4 | ~0.1167 | 9 |
| 2.5 | ~0.0862 | 10 | ~0.0886 | 11 |
| 2.6 | >0.0600 | 4 | ~0.0697 | 9 |
| 2.75 | <0.0300 | 10 | <0.0200 | 13 |
| 2.9 | <0.0200 | 4 | <0.0200 | 6 |
| 3.0 | <0.0200 | 9 | <0.0200 | 9 |

## 4. Threshold sensitivity (GROK verdict cutoff)

| threshold | overall GROK fraction (P8 grid) | ceiling(alpha=2.5) |
|---|---|---|
| 0.85 | 0.516 | ~0.1014 |
| 0.9 | 0.508 | ~0.0847 |
| 0.95 | 0.452 | ~0.0649 |
