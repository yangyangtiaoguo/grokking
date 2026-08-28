# 论文骨架 v2（第一轮审稿后修订，2026-08-27）

> 第一轮审稿：6.5/10, not_ready（.aris/traces/auto-review-loop/20260827_run01/）
> 本版按 CRITICAL→MAJOR→MINOR 全部修订，修订点标注 [R1-#]

## Title [R1-1 修订]
~~Data Skew, Weight Decay, and the Geometry of Grokking Failure: An Empirical Phase Diagram with a Minimal Rescue Intervention~~
**Empirical Phase Diagrams of Grokking Failure under Data Skew, and a Low-Dose Rescue Intervention**
（去掉未支撑的"Geometry"；"Minimal"改为"Low-Dose"，避免暗示全局最优剂量）

## Abstract [R1-2 新增，此前缺失]
This paper reports an empirical study, not a closed-form theory. We map (α, weight-decay) grokkability on an autoregressive counting task via a finite compute budget (up to 1M steps); the resulting boundary is a **finite-budget empirical phase diagram**, not evidence of an asymptotic phase transition. A sharp dose transition for rescue is bracketed between 0.391% and 0.781% injected samples — we report this bracket, not a claimed critical point at exactly 1/128. Mechanism-isolating controls show that **among the tested interventions**, only full-support uniform injection achieves complete rescue; this does not establish necessity of full support. The failure/rescue pattern transfers to a second arithmetic task (modular addition) under exposure-matched controls; a third, non-arithmetic task (Dyck-1) is included as a deliberately harder out-of-domain stress test, and it qualifies rather than confirms the transfer claim: failure topology and injection-ranking direction replicate, but complete rescue and budget-monotonicity do not. All findings carry seed-level uncertainty and are reported at n≤12, d≤128 scale; we make no claim beyond this scale.

## 1. Introduction
- Grokking 回顾 + Zhao 开放问题
- **明确范围声明段落**（保留，措辞强化）：本文是实证研究，不识别渐近律或临界指数；理论track不适用的原因直接写一句话带过，不单开小节 [R1: 采纳"不需要专门章节"的建议]
- 贡献列表改写为**叙事顺序**而非并列清单 [R1-6 采纳重排序建议]：
  1. Failure map + kinetics（原C1+C3合并）
  2. Coverage intervention + mechanism controls（原C2，作为中心结果）
  3. Boundary candidate summary（原C4，降级为子分析）
  4. Local robustness + task transfer（原C5+C6，作为验证性章节）

## 2. Related Work [R1-5 补充引用面]
除原有引用外新增覆盖：
- **Grokking 奠基**：Power et al. 2022（grokking现象首次系统报告，此前遗漏，CRITICAL级遗漏已修正）
- **机制/表征层面的grokking分析**：需检索补充（占位，写作阶段查）
- **优化器/weight-decay对grokking的解释**：Omnigrok(Liu 2210.01117)已有，补充其他optimizer-centric工作
- **偏斜数据学习**：long-tail learning, importance sampling, curriculum design 相关工作
- **生存/删失分析方法论**：既然C3核心是censoring-fraction曲线，需引用标准生存分析文献支撑方法选择
- **有限尺寸标度语言**：明确引用为何本文避免"相变"用词而选更弱表述
- 新增**对照表**（不只是姓氏引用列表）：每个最近邻工作 × (是否测偏斜/是否finite-budget映射/是否有救援对照/是否曝光匹配/是否任务迁移/规模) 的表格

## 3. Setup
### 3.1-3.2 不变（主任务定义、判决规则）
### 3.3 频率偏斜协议 + **[R1新增] 统计分析小节**
- 明确报告：每格seeds数、bootstrap CI构造方法、censoring处理方式、多重比较是否校正、判决阈值(0.9)的敏感性
- **[R1新增] 网格分辨率说明**：α轴网格间距 + 由此带来的边界定位不确定性（"近垂直墙"的表述需说明是否只是粗网格假象——已用密化网格验证，写明密化后的间距）
### 3.4 曝光匹配协议 [R1-CRITICAL修订]
~~"方法论贡献"~~ → **改为"必要的实验控制"**，不作为独立第七贡献。说明它是从本项目自己的先导数据混淆中发现并修正的（P11b教训），本身不作为可迁移的方法论主张单独申领。
### 3.5 [R1新增] Preregistration Protocol
- 列出：M10（held-out α预测，冻结时间戳）、M11（8项方向性预测，冻结时间戳）的具体协议、冻结文件位置、confirmatory vs exploratory的明确划分标准
### 3.6 [R1新增] Compute Accounting
- 总GPU-h（先导~25h + 正式战役~17h + 补充~90h = 约132h）、硬件(RTX 5080)、总run数、是否有探索性结果反过来影响了后续确认性实验设计的选择（如实说明：M9的α点选择部分依据M4/M9探索性拟合结果，这是exploratory→confirmatory的合理链条而非污染，但需明说）

## 4. Results（重排序，采纳R1-6叙事重排）

### 4.1 Failure Map and Kinetics（原C1+C3合并）[R1-6]
- 4.1.1 相图结构：**[R1修订]** "finite-budget empirical phase diagram"；n=12"rules out an n=10-specific artifact **under the tested exposure-matching protocol**"（而非笼统"rules out finite-size artifact"）
- 4.1.2 两区制：边界层vs深腔，**[R1修订]** "trap"全程加引号或改"non-escape within tested budget"，避免暗示已证明真实稳态
- 4.1.3 Kinetics：**[R1-CRITICAL修订]** 删失率曲线作为主证据（censoring-robust），中位数τ曲线**明确标注selection bias警告**（只在grok的种子上取中位数，随censoring增加而向下偏——已知局限，非隐藏）
- 网格分辨率图：展示密化前后edge位置的收敛，回应"近垂直墙是否只是粗网格假象"的质疑

### 4.2 Coverage Intervention: The Central Result（原C2）
- 剂量-响应：**[R1修订]** 明确报告为"跃迁被0.391%和0.781%两个测试点括住"，不声称精确临界点
- 机制分离三元组（same_dist/rare_short/uniform）
- **[R1修订]** "完全支撑覆盖是必要的" → **"在测试的干预中，只有全支撑均匀注入达成完全救援"**
- **[R1新增]** 剂量匹配细节：注入样本是否在token数/优化步数/唯一样本数/总曝光量上都做了匹配，明确写出

### 4.3 Boundary Candidate Summary（原C4，降级为4.1的子分析）[R1-6]
- 五候选拟合 + held-out验证，篇幅缩短，作为4.1.1的补充分析而非独立主结果
- **[R1新增]** 与零模型/常数模型/简单插值的对照，否则"合理近似"无基准可评判
- p_star被拒的诚实负结果保留

### 4.4 Local Robustness and Task Transfer（原C5+C6）[R1-6]
- 4.4.1 鲁棒性：8项预注册预测对照表，**[R1新增]** 冻结的量化确认判据（不只是定性"方向对了"）；SGD结果**明确标注为"未调参的optimizer迁移失败"**而非"SGD更差"的排名声明
- 4.4.2 模加任务迁移：曝光匹配对照完整数据
- 4.4.3 **Dyck-1（按第一轮审稿要求重新定位）**[R1-CRITICAL修订]：
  - **开篇即说明其角色**："Dyck-1被刻意选作比前两个算术任务更难的域外压力测试，用于防止对'覆盖机制'做无依据的任务通用声明——不是又一个正面复现"
  - 区分confirmatory/exploratory状态（这整个第三任务都是exploratory，非预注册）
  - 说明为何选择该cell（α=5.5, wd=1.3——深崩溃区，而非边界层）
  - **[R1修订]** "spontaneously collapse"/"metastability" → 若只有单轨迹证据，改用更保守的"trajectories exhibit late-stage collapse after an initial high-accuracy plateau"；若要保留metastability措辞，需在正文放至少一张轨迹图（已有数据，见results/dyck_budget.json的完整aunif序列）
  - 明确一句"Dyck-1结果限定而非等权重支撑覆盖叙事"

## 5. Discussion
- 与原提案对照（λ_c方向修正、T4课程预言证伪）
- **[R1新增]** 与前人工作的对照表移到这里总结（如果Related Work只放in-line引用，对照表放这里更合适）
- **Limitations（2026-08-28 按防御性写作规则重审，三判据逐条处理）**：
  - **保留（正面表述，非道歉语气）**：全部结果在 n≤12、d≤128、单一 decoder-only 架构家族的受控设置下确立（Abstract 已陈述一次，Discussion/Limitations 不重复该句，只在此处补充"未跨越更大规模验证"这一具体、可核查的边界，一句带过，不展开）。
  - **保留（正面表述）**：C4 建立了五个预注册候选间的家族判别（held-out 预测验证），未建立闭式定律——这是对贡献性质的精确刻画，不是不足的道歉。
  - **保留（外部引用状态，实质性约束）**：citation_support_bank.md 中 C47/C48/C49 三条候选的完整作者名单在写作定稿前需核实。
  - **删除**：~~"每格2-15 seeds，非大规模统计"~~——空洞自我削弱，任何具体数字都能被说成"有限"，无信息量；具体 seeds 数、bootstrap CI、censoring 处理已在 Methods/Results 逐一报告，无需在此重复削弱。
  - **删除**：~~"Dyck-1 的救援/预算发现留待后续刻画"~~——实质内容（该格救援不完全、预算效应已诊断为亚稳态坍缩）已在正文 4.4.3 具体交代，此处若重复只是空洞的"待验证"用语，删除不影响信息量。
  - 原则：Limitations 精简到 3 条以内，每条必须是"删掉会误导读者"的实质约束，不逐条罗列可被挑剔的点（academic-ai-tells 三判据：功能/位置/次数）。

## 6. Conclusion

## Appendix
- A. 超参数表
- B. 全部boundary/dose/tau数据表
- C. Dyck-1完整数据 + **[R1新增]** 至少一张60k vs 240k的完整轨迹对比图（支撑4.4.3的坍缩描述）
- D. 引用审计记录
- E. **[R1新增]** Preregistration文件时间戳记录（M10/M11冻结文件路径+校验）

---

## v3 补丁（第二轮审稿后，2026-08-27，处理3项剩余阻塞项）

### 阻塞项1：M11量化确认判据（诚实核查后处理）

**核查结果**：`experiments/m11_factorial.py` 文件时间戳 2026-08-25 18:58（含PREREGISTERED_DIRECTIONS字典），`results/m11_factorial.json` 时间戳 2026-08-27 04:43——**方向性预测确系数据收集前冻结**（文件时间戳为证）。但脚本中只写了定性方向（"shifts LEFT/RIGHT"），**未预先固定具体数值判据**（如"grok-count需变化≥2/5"）。

**采纳审判方案（不倒填）**：4.4.1改写为——
> "8项方向性预测（宽度↓/↑、学习率↓/↑、深度↓/↑、2个交互格作中性测试、SGD+momentum预测更差）已于数据收集前**以文件时间戳形式**指定（见experiments/m11_factorial.py时间戳）——**明确措辞为"timestamped pre-data specification / pre-specified"，不用"formally preregistered"**（第三轮审稿意见：文件系统时间戳可变，不构成正式预注册的证据强度，需说明溯源局限，除非有仓库commit/存档/注册表记录）。**我们仅将方向声明为pre-specified**；量化判据（多大幅度算"确认"）未预先固定，故按事后分析报告，明确标注为post-hoc grading。**方向命中的操作定义**：contrast=处理组vs基线组的grok-count或mean unif_tail差值符号；跨5 seeds按符号一致性判定（非严格>0/<0需注明ties处理，本次8格无ties案例）；命中定义为符号与预测方向一致。"
> 具体数值：8/8方向命中（详见Table X），量化幅度见原始数据（results/m11_factorial.json）。

### 阻塞项2：跨任务曝光匹配与判决定义可比性

**去掉占位符**，明确写入Setup 3.6：
- 三个任务的"曝光单位"定义：主任务=(batch中该状态出现次数)；模加=同理(对操作数a的出现次数)；Dyck-1=(该max-depth路径的出现次数)
- **明确"什么被跨任务匹配"（第三轮审稿追问，此前遗漏）**：三任务之间**不做数值曝光计数的匹配**（词表大小不同导致每步有效信息量不可比），**只匹配"稀有度分位数排序"这一定性结构**——即三任务的Zipf(α)偏斜都按"分位数从常见到稀有"的相同排序逻辑构造训练分布。**因此三任务结果应表述为"定性复现"（qualitative replication of ranking direction），不是"受控的跨任务对照实验"（controlled cross-task comparison）**——这条限定必须写入4.4.2/4.4.3开头，不能让读者误以为做了数值可比的对照。
- **无法匹配的部分**：三任务词表大小不同(3-way vs 98-way vs 3-way)，故wd的绝对数值不可跨任务比较（已在M6b分析中发现并如实报告，这是本文承认的限制，非新发现）
- 判决阈值(A_unif>0.9)在三任务上使用同一数值，但由于任务复杂度不同（LARGECOUNTER需完整n-bit正确，模加需单token正确，Dyck-1需完整2L-bit序列正确），**阈值的"难度"不完全可比**——这一点写入Limitations，不试图强行归一化

### 阻塞项3：草稿阶段执行统计分析（骨架阶段不可能完成，明确标注为写作阶段TODO）

在3.3小节末尾加一行：
> **[写作阶段TODO，非骨架阶段可交付]**：本节所有统计量（bootstrap CI、censoring fraction表、网格分辨率收敛图、阈值敏感性分析）需在正式撰写Results时从results/*.json重新计算并附带代码路径，不得只在骨架阶段承诺后忘记执行。负责人自查清单已加入EXPERIMENT_TRACKER.md。

---

**当前状态**：CRITICAL/MAJOR项全部处理（阻塞项1-2为骨架阶段可完成的诚实修订，已完成；阻塞项3标注为写作阶段强制TODO，骨架阶段不可能提前完成，如实说明而非假装解决）。

---

## Round 3 微调（2026-08-27，纯措辞修正，未新增实质性问题）

按第三轮审稿意见（8.5/10, almost）修正两处纯措辞问题：
1. "preregistered"→"timestamped pre-data specification / pre-specified"（溯源强度诚实降级：文件时间戳非仓库commit/存档级证据）+ 补充"方向命中"的操作定义（符号对照，5 seeds一致性，本次无ties）
2. 明确"三任务之间不做数值曝光匹配，只匹配稀有度分位数排序这一定性结构"——三任务结果应表述为"定性复现"而非"受控跨任务对照"

第三轮审稿原话："No substantive new empirical problem emerged... Full-draft work may proceed in parallel"——**已达到auto-review-loop停止条件（score≥6 且 verdict∈{ready,almost}，本轮8.5/almost）**，两处剩余为精确措辞修正非实验缺口，可并行推进正式撰写。

**审稿轮次记录**：Round1 6.5/not_ready → Round2 8.1/almost → Round3 8.5/almost（收敛，未再有新实质性问题）。Trace: .aris/traces/auto-review-loop/20260827_run0{1,2,3}/
