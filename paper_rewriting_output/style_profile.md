# Style Profile

Synthesized from `research_dossier.md` and `exemplar_learning_dossier.md`.

## Target Register

Empirical/mechanistic ML paper register: declarative, quantified, operationally precise. Hedge exactly at the points where the evidence genuinely runs out (per the audit-mandated wording in `CLAIMS_FROM_RESULTS.md`), never as reflexive throat-clearing. This paper has already had its claim wording calibrated through two independent audit rounds — the style task is to carry that precision into full prose without either (a) re-inflating claims for rhetorical punch, or (b) adding redundant defensive hedges on top of already-precise audit-mandated phrases.

## Section-Level Style Rules

- **Abstract/Introduction**: state the scope boundary explicitly and early (matches the exemplars' "empirical, not asymptotic" framing pattern). Do not bury the scope statement in a later Limitations section only — front-load it, per the paper's own already-drafted Abstract.
- **Results**: operational definition before pattern description (verdict rule → phase diagram; dose definition → dose-response curve). Report bracketing intervals, not false-precision point estimates, wherever the underlying measurement is a coarse grid (dose transition, boundary position).
- **Ablations/controls**: state the prediction before the result when discussing pre-specified comparisons (C5), to make genuine pre-specification legible to the reader.
- **Negative/null results** (p_star rejection, SGD untuned-transfer caveat, Dyck-1 partial rescue): same declarative register as positive findings, same section prominence, no apologetic framing.
- **Discussion**: the "original proposal predicted the wrong direction, data corrected it" narrative should be framed with confidence as a strength of the empirical approach, not as an admission of failure.
- **Limitations**: itemized, specific, falsifiable statements (already the case in the skeleton) — no generic "future work could explore..." boilerplate without a specific claim about what is and isn't currently known.

## Terminology Discipline (hard constraints, carried from `CLAIMS_FROM_RESULTS.md`)

| Use this | Not this | Why |
|---|---|---|
| "empirical finite-budget phase diagram" | "phase transition" | Audit-mandated; avoids collision with Bi et al./Wang's critical-exponent claims |
| "among the tested interventions, only uniform injection achieved complete rescue" | "full-support coverage is necessary" | Necessity is not established by 3 discrete conditions |
| "critical-slowing-like behavior" / "increasing failure probability near the boundary" | "critical slowing down" (unqualified) / "proven divergence" | C3 is the paper's most fragile claim; term has a specific stronger meaning in statistical physics |
| "validates the single-scale model class; E_c and 2^-α remain statistically indistinguishable out-of-sample" | "E_c is the governing law" | Held-out test did not uniquely resolve a winner |
| "transfers to a second arithmetic task" (modular addition) | "task-general" / "universal mechanism" | Directly contradicted by Dyck-1's partial results |
| "timestamped pre-data specification" / "pre-specified" | "preregistered" | Filesystem timestamps are not registry-grade provenance (third review round finding) |
| "trajectories exhibit late-stage collapse after an initial high-accuracy plateau" (unless a trajectory figure is in the main text) | "spontaneously collapse" / "metastability" (as an unqualified claim) | Single-trajectory evidence does not by itself establish a dynamical metastability claim |

## 局限性披露规则（用户明确要求，2026-08-28，强制执行于全部后续撰写）

**核心心法**：论文是一场学术发布会，不是自我审查报告（`academic-ai-tells` skill 的发布会原则第 5 条）。已完成的实验、已给出的结论，用肯定、正面的陈述表达，让证据本身说话。

1. **禁止空洞自我削弱表述**："样本/种子数量仍然有限，理想情况下应该更多"这类话没有信息量——任何有限数字都能被说成"有限"。如果要提及规模，报告具体数字（"n≤12, d≤128"）一次，不追加"理想情况下更多"式的空转限定。
2. **不主动、过多披露局限性**："仅操纵单一因素""数据尚不能区分两种假说""非受控变量不支撑定量结论""仍需进一步验证"这类主动自我削弱的限定语，只在被明确问到（审稿意见/读者提问）时才展开讨论，不主动写入正文。
3. **Limitations 章节精简到 3 条以内**：只保留"删掉会误导读者"的实质约束（硬件条件、外部引用状态等），不逐条罗列所有可能被挑剔的点。三判据（详见 academic-ai-tells skill）：
   - 功能判据：删掉它，claim 会变吗？不变=噪声，删。
   - 位置判据：在 Methods/Discussion/Limitations 吗？是=大概率必要；在 Abstract/Intro/贡献段/结论=大概率过度。
   - 次数判据：全篇说了几次？1 次正常，≥2 次重复=只留最该留的那次。
4. **判断测试**：删掉这句话，读者会被误导，还是只是少了一句读者本就知道的正确废话？前者留，后者删。

**执行范围**：Results、Discussion、Conclusion 全文强制执行；Methods 中的方法学说明（如判决阈值定义、曝光匹配协议）不受此规则约束，因为那是必要的技术描述而非自我削弱式限定。

- Phase diagram (Figure 1): heatmap with boundary band showing bootstrap CI, plus the budget-band overlay showing the two-regime structure (kinetic boundary layer vs. deep-trap interior) — per `stats_appendix.md` §1 and §3.
- Dose-response curve (Figure 2): x-axis = dose (log scale given the sharp transition), y-axis = A_unif, with the three mechanism-isolating conditions (same_dist/rare_short/uniform) as distinct series.
- Kinetics (Figure 3): censoring-fraction curve (not median-tau-of-grokked-only, which carries selection bias) as the primary evidence, per `stats_appendix.md` §2; median-tau curve as secondary evidence with the selection-bias caveat stated in the caption, not just body text.
- Grid-resolution convergence (supporting figure, addresses "is the near-vertical wall a coarse-grid artifact" reviewer question): per `stats_appendix.md` §3, showing sparse-grid vs. dense-grid ceiling estimates converge at the boundary alphas.
