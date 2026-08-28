# Motivation Options After Research

The controlling motivation for this paper (what argument the whole manuscript is organized around) needs user confirmation before drafting proceeds. Based on the research stage (venue analysis, exemplar patterns, and the SOTA gap map), here are three framing options — they differ in emphasis, not in evidence (the underlying results are fixed by `CLAIMS_FROM_RESULTS.md`).

## Option A — "The Diagram Is the Contribution" (lead with C1)

**Controlling motivation**: Zhao (ACL 2026 Findings) showed grokking under skew is a real, extendable phenomenon but left the shape of grokkability under continuous skew entirely uncharacterized. This paper's primary contribution is the (α, weight-decay) empirical phase diagram itself — its two-regime structure (budget-sensitive boundary vs. budget-insensitive deep trap) is the headline finding. The rescue intervention (C2), kinetics (C3), candidate discrimination (C4), robustness (C5), and cross-task check (C6) are all secondary results that flesh out and stress-test the diagram, in that priority order.

- **Strengths**: matches the double-descent/Omnigrok exemplar pattern (lead with the map). C1 is the paper's most solidly evidenced claim — leading with it plays to strength.
- **Risk**: may read as "just another phase diagram" unless the two-regime structure and the deep-trap non-escape-at-1M-steps finding are foregrounded as the specific novel structural insight (not just "a diagram exists").

## Option B — "The Rescue Mechanism Is the Contribution" (lead with C2)

**Controlling motivation**: Zhao's paper's stated open limitation is explicitly about rescue — "does stratification create or merely extend grokking to rare states?" This paper directly answers that open question with a precise, mechanism-isolated answer: a specific low dose of *distributionally diverse* (not merely rare, not merely more-numerous) injection rescues both trap and starvation failure modes, and this mechanism (not just the phenomenon) transfers to a second task. The phase diagram (C1) becomes the necessary backdrop that establishes where rescue is needed, not the headline.

- **Strengths**: most directly answers a stated open problem from the predecessor paper — strong "gap-closing" narrative for Introduction. The mechanism-isolating controls (same_dist/rare_short/uniform) are the paper's cleanest piece of causal reasoning, a strong methodological centerpiece.
- **Risk**: requires C1 to still be presented in full (the rescue claims are meaningless without the failure map that motivates them), so this option mostly changes emphasis/ordering rather than removing content — practically converges toward a similar Results section to Option A, just re-weighted in the Abstract/Introduction framing.

## Option C — "A Case Study in Falsifiable Self-Correction" (lead with the corrected-hypothesis narrative)

**Controlling motivation**: This paper is framed around the process as much as the findings — an initial theoretical proposal made a specific, falsifiable prediction about the phase boundary's direction; controlled experiments showed the opposite; two independent audit rounds then further narrowed every downstream claim to what the evidence actually supports (including rejecting and later partially reinstating the kinetics claim, and rejecting a proposed governing law). The paper argues for this as a model of how empirical ML phenomenology should be done — happy to report being wrong, precise about how far each claim extends.

- **Strengths**: distinctive narrative angle, plays well to reviewers who value methodological honesty (per `exemplar_learning_dossier.md`'s note on how well genre reviewers respond to honest self-correction narratives, e.g. Omnigrok's own "not weight decay per se" correction). Provides a natural, confident frame for the Discussion section's existing content.
- **Risk**: over-indexing on "process" framing in the Abstract/Introduction can read as less substantive than leading with a concrete finding — this angle probably belongs prominently in Discussion (where it's already planned) rather than as the Abstract's opening framing, unless the user specifically wants a "methods paper about doing empirical science honestly" flavor.

## Recommendation

Options A and B produce nearly identical Results sections (the skeleton's ordering already reflects a version of Option A/B blend: C1+C3 merged first, C2 promoted as "the central result" second). The practical choice is mainly an **Abstract/Introduction framing decision**: does the opening paragraph sell "we mapped grokkability under skew" (A) or "we answered Zhao's open rescue question" (B)? Option C's narrative should be present in Discussion regardless of which opening framing is chosen — it doesn't require an either/or with A/B.

**Awaiting user confirmation**: choose A, B, C, a blend, or provide your own framing.
