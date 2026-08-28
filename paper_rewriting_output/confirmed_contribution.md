# Confirmed Contribution

## Core Contribution

| Field | Content |
|---|---|
| Main contribution statement | Grokkability under continuous data skew is governed by a two-regime $(\alpha,\lambda)$ boundary (kinetic near the boundary, a non-escaping deep trap in the interior), and both of its failure modes are rescued by a single, mechanism-isolated intervention: injecting a small dose ($\sim0.8\%$) of examples drawn from the full, uniform support, which succeeds specifically because it restores distributional coverage rather than because it adds samples or targets rare states. |
| Contribution type | new empirical finding (with a validated methodological contribution: mechanism-isolating controls + a pre-specified held-out test for boundary-shape discrimination) |
| One-sentence reviewer payoff | The paper turns Zhao's single qualitative comparison (uniform vs. stratified sampling) into a continuous, causally-dissected map of exactly where grokking fails under skew and exactly what minimal intervention fixes it, and shows precisely how far that fix travels across tasks. |

## Why This Contribution Is Needed

| Field | Content |
|---|---|
| Field problem | Grokking (delayed generalization) is a widely-studied but still poorly predicted training-dynamics phenomenon; practitioners and theorists alike lack a way to know, for a given data distribution and regularization strength, whether a model will grok, how long it will take, and how to rescue it if it does not. |
| Specific gap | Zhao (ACL 2026 Findings) shows on LARGECOUNTER that grokking occurs under both uniform and stratified sampling, and that stratification extends (but does not create) generalization on rare carry-chain states --- a single discrete, two-point comparison with no continuous skew axis, no characterized failure boundary, and no dose-response characterization of what minimal intervention rescues a trapped model. |
| Concrete challenge | Constructing a genuine grokking testbed under frequency skew is nontrivial: subset-selection protocols leave carry-chain composition flat in $\alpha$ (no skew effect at all), and a naive combined-index skew on a second task (modular addition) collapses the task to a near-single-operand problem. Isolating *why* a rescue intervention works (sample count vs. rarity vs. coverage) requires matched controls that no prior rescue-mechanism paper reports together. |
| Why prior work leaves it unresolved | Liu et al.'s effective-theory/Omnigrok line maps phase diagrams against *data fraction*, not skew. Singh et al.'s knowledge-distillation rescue scales with data *quantity*, not skew, and offers no dose characterization. Bi et al. and Wang treat grokking as a genuine statistical-mechanical phase transition on a different extensive variable (group order), not an $(\alpha,\lambda)$ empirical map. None of these works isolates coverage as a mechanism via matched controls, and none tests transfer to a task deliberately chosen to be harder than the original testbed. |

## How This Paper Responds

| Field | Content |
|---|---|
| Design response | A continuous Zipf-weighted skew axis $\alpha$ crossed against weight decay $\lambda$, mapped via a frozen four-way verdict rule; an exposure-matching protocol that prevents training-step-count confounds from being misread as thermodynamic structure; and three sample-count-matched injection conditions (same-distribution / rare-but-short / full-uniform) that causally separate the candidate rescue mechanisms. |
| Evidence required | A boundary that a skeptical reviewer can trust: replication at a second problem size, budget bounds ruling out "just needs more training," bootstrap uncertainty, and grid-resolution checks. A rescue mechanism a skeptical reviewer can trust: dose-response sharpness, mechanism-isolating controls with a null condition, and a check that the effect is not counting-task-specific. |
| Evidence available | $n{=}10$ boundary with bootstrapped 90\% intervals at 8 resolved $\alpha$ values; $n{=}12$ exposure-matched replication; 1M-step (4x-budget) non-escape at two deep-interior cells; a grid-resolution convergence check; a 15-seed censoring-fraction kinetic signature; a three-condition mechanism-isolating dose battery with a same-distribution null; a pre-specified held-out family-discrimination test at 8 new $\alpha$ values; 8 pre-specified directional robustness predictions, all confirmed; and an exposure-matched replication of the injection-ranking mechanism on modular addition, plus a third, deliberately harder non-arithmetic task (Dyck-1) that tests transfer honestly rather than merely restating it. |
| Evidence missing | None of the required evidence categories is missing; the family-discrimination analysis (\S\ref{sec:results-family}) explicitly stops at model-class validation rather than a unique closed-form law, and this is stated as the nature of that contribution, not as an evidentiary gap. |

## Claim Boundary

| Field | Content |
|---|---|
| Strong claims allowed | The two-regime $(\alpha,\lambda)$ boundary structure, replicated at a second problem size under exposure matching. The coverage mechanism for rescue, established by matched controls with a null condition. The rescue mechanism's transfer to a second arithmetic task under exposure-matched controls. All eight pre-specified robustness predictions, confirmed. |
| Claims to soften or avoid | No claim of an asymptotic phase transition or a critical exponent (the boundary is a finite-budget empirical map). No claim that full-support coverage is necessary for rescue (only that it is the best-performing tested intervention). No claim of a unique closed-form governing law for the boundary's shape (a model class is validated, not a law). No claim that the coverage mechanism is task-general (it is confirmed on a second arithmetic task and only partially replicates on a non-arithmetic stress test). |
| Novelty risk | "Isn't this just Omnigrok's phase diagram again?" --- Omnigrok's diagram sweeps data fraction; ours sweeps a continuous skew parameter at fixed data fraction, and adds the mechanism-isolating rescue battery and cross-task transfer test that no data-fraction paper reports. |
| Significance risk | "This is one toy counting task plus two extensions --- too narrow to matter?" --- The paper's significance rests on the causal dissection (matched controls isolating coverage, not just observing that injection helps) and on the honest cross-task boundary drawn by the Dyck-1 stress test, which is exactly the kind of falsifiable scope statement the empirical-phenomenology genre (double descent, scaling laws) is judged on, not on scale. |
