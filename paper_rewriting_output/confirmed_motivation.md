# Confirmed Motivation

**Confirmed 2026-08-28** (user selected: A+B blend).

## Controlling Motivation

This paper argues two things in tandem, without treating them as competing framings:

1. **The empirical (α, weight-decay) phase diagram is a structural discovery in its own right.** Continuous data skew and weight decay jointly determine grokkability through a two-regime structure: near-boundary failures respond to additional compute budget (kinetic regime), while deep-interior failures do not escape even at 4x the originally-tested budget, up to 1M steps (deep-trap regime). This is the first continuous-skew-axis characterization of grokkability's failure geometry, extending Zhao (ACL 2026 Findings)'s coarse two-point (uniform vs. stratified) result into a full empirical map with bootstrap-quantified boundaries.

2. **The phase diagram's most important practical payoff is a precise, mechanism-isolated answer to Zhao's own stated open question**: does stratified sampling *create* or merely *extend* grokking to rare states? This paper answers with a minimal-dose rescue intervention (~0.8% uniformly-sampled injection) validated through mechanism-isolating controls (same_dist / rare_short / uniform) that separate "more samples," "rarity," and "full distributional coverage" as candidate explanations — coverage is what matters, not mere sample count or targeted rarity.

The phase diagram (1) establishes *where* rescue is needed and *why* the failure is structural, not incidental; the rescue mechanism (2) is the diagram's most actionable, most rigorously controlled finding. Neither is subordinate to the other in the paper's actual evidentiary weight — the skeleton's existing Results ordering (4.1 Failure Map + Kinetics → 4.2 Coverage Intervention as "the central result" → 4.3 Candidate Summary as a sub-analysis → 4.4 Robustness + Transfer) already reflects this blend correctly, and should not be restructured.

## What This Motivation Requires of the Abstract/Introduction

The opening framing must do both jobs in sequence, not choose one:
1. State the phase-diagram finding and its two-regime structure (the "what we mapped" claim).
2. Immediately connect it to Zhao's specific open question and this paper's mechanism-isolated answer (the "what this settles" claim).

## What This Motivation Does NOT Require

- Option C's "case study in falsifiable self-correction" framing is **not** the Abstract/Introduction's opening frame. It remains exactly where the skeleton already places it: in the Discussion section, contrasting this paper's corrected findings against the original (superseded) proposal's mispredicted boundary direction and refuted optimal-rescue-curriculum prediction. This is confirmed as supporting narrative, not the paper's primary motivation.

## Downstream Consequences

- `section_blueprints.md` and `writing_rationale_matrix.md` (next stage) must show the Abstract and Introduction opening with the phase-diagram finding, pivoting within the first 1-2 paragraphs to the Zhao open-question framing, consistent with this confirmed motivation.
- No further restructuring of the Results ordering already locked into `PAPER_SKELETON.md` is implied by this confirmation — the blend is achieved at the framing level (Abstract/Intro), not by re-weighting which Results subsection is "the" headline.
