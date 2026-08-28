# Citation Quality Audit

- Output directory: `paper_rewriting_output`
- Scene: conference
- Target citation count: 25
- Entries analyzed: 30
- Verified: 28 | Mismatched: 0 | Dead: 1
- Overall quality score: 67/100
- Status: PASS

> Each entry below includes a teaching note explaining *why* the citation quality matters.

## Per-Citation Analysis

| ID | DOI | Type | Resolves | Title Match | Year Match | Score | Status |
|---|---|---|---|---|---|---|---|
| C01 | arXiv:2201.02177 | benchmark | yes | 0% | no | 75 | verified |
| C02 | arXiv:2205.10343 | foundational | yes | 0% | no | 75 | verified |
| C03 | arXiv:2210.01117 | sota | yes | 0% | no | 55 | verified |
| C04 | arXiv:2301.05217 | sota | yes | 0% | no | 75 | verified |
| C05 | arXiv:2302.03025 | sota | yes | 0% | no | 75 | verified |
| C06 | arXiv:2301.02679 | sota | yes | 0% | no | 75 | verified |
| C07 | arXiv:2309.02390 | sota | yes | 0% | no | 75 | verified |
| C08 | arXiv:2603.24746 | sota | yes | 0% | no | 90 | verified |
| C09 | arXiv:2604.04655 | sota | yes | 0% | no | 90 | verified |
| C10 | arXiv:2509.22445 | sota | yes | 0% | no | 55 | verified |
| C11 | arXiv:2607.23967 | sota | yes | 0% | no | 90 | verified |
| C12 | arXiv:2511.04760 | sota | yes | 0% | no | 85 | verified |
| C13 | arXiv:2602.08857 | sota | yes | 0% | no | 90 | verified |
| C14 | arXiv:2510.19315 | sota | yes | 0% | no | 55 | verified |
| C15 | https://aclanthology.org/2026. | sota | yes | 0% | no | 90 | verified |
| C16 | arXiv:2106.06981 | sota | yes | 0% | no | 65 | verified |
| C17 | arXiv:1912.02292 | sota | yes | 0% | no | 55 | verified |
| C18 | arXiv:1711.05101 | sota | yes | 0% | no | 55 | verified |
| C19 | https://proceedings.mlr.press/ | critique | yes | 0% | no | 85 | verified |
| C20 | 10.1145/1553374.1553380 | sota | yes | 100% | yes | 60 | verified |
| C21 | arXiv:2110.04596 | survey | yes | 0% | no | 65 | verified |
| C22 | arXiv:2404.15593 | survey | yes | 0% | no | 85 | verified |
| C23 | 10.1214/ss/1177013815.full | sota | no | 0% | no | 10 | dead |
| C24 | 10.1201/9780429246593 | sota | yes | 100% | no | 60 | verified |
| C25 | https://pmc.ncbi.nlm.nih.gov/a | sota | yes | 0% | no | 50 | verified |
| C26 | arXiv:2001.08361 | sota | yes | 0% | no | 65 | verified |
| C27 | https://arxiv.org/abs/2206.076 | sota | yes | 0% | no | 75 | verified |
| C28 | https://arxiv.org/abs/1706.037 | sota | yes | 0% | no | 50 | verified |
| C29 | arXiv:2104.09864 | sota | yes | 0% | no | 65 | verified |
| C30 | - | foundational | no | 0% | no | 27 | pending |

### C23 — 10.1214/ss/1177013815.full

Status: **dead**

- DOI 10.1214/ss/1177013815.full does not resolve via Crossref

> Dead DOIs suggest the citation was hallucinated or the paper was retracted. Replace with a verified alternative or remove the citation.

### C30 — 

Status: **pending**

- Verified flag set but no stable identifier (DOI, arXiv ID, or URL) found in the row; self-attestation alone cannot confirm the citation

> A Verified=yes flag is not enough on its own. Record a stable identifier (DOI, arXiv ID, or URL) in the reference, source, or verification note so the citation can be independently re-checked. Until then this row stays unverified.

## Citation Diversity Gaps

**Missing dataset, benchmark, or evaluation protocol papers.** Only 1 of 30 entries (3%). Cite all datasets used. Standard benchmarks are expected. Consider adding 1-3 dataset, benchmark, or evaluation protocol paper references.

**Missing domain-application or impact papers.** Only 0 of 30 entries (0%). Optional. Consider adding 1-3 domain-application or impact paper references.


## Replacement Recommendations

- 1 dead DOIs detected. For each: (1) verify the paper exists via Google Scholar, (2) find the correct DOI, (3) update the citation bank, (4) re-run this audit.

## Scene-Specific Citation Strategy

For **conference** papers, your citation strategy should:

- **direct task or state-of-the-art paper**: Cite the 5-8 most recent competing methods. Conference reviewers check recency aggressively.
- **foundational method or theory paper**: Cite the 2-3 methods you build on. Be specific about what you inherit vs. change.
- **dataset, benchmark, or evaluation protocol paper**: Cite all datasets used. Standard benchmarks are expected.
- **survey, review, or meta-analysis**: Cite 1 recent survey if it helps position your work concisely.
- **domain-application or impact paper**: Optional.
- **limitation, robustness, reproducibility, or ethics paper**: Optional but helpful for discussion section.

## Citation Strategy Principles

- **Diversity over density.** A narrow citation pool makes your Introduction read as insular. Mix SOTA, foundational, benchmark, survey, and application papers.
- **Recency signals engagement.** Most citations should be from the last 3 years. Older citations are fine for foundational work, but they need a reason to be there.
- **Verifiability is non-negotiable.** Every DOI must resolve. A dead DOI in your final paper is a credibility failure that reviewers notice immediately.
- **Type matters by venue.** Journals expect deep SOTA coverage. Reports expect broad survey coverage. Competitions expect benchmark and leaderboard coverage. Match your strategy to your scene.
