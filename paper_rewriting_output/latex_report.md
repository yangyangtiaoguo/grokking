# LaTeX / PDF / Word Build Report

- **Engine**: pdflatex (3 passes) + bibtex (plainnat/natbib)
- **Build sequence**: `pdflatex main.tex` → `bibtex main` → `pdflatex main.tex` → `pdflatex main.tex`
- **Status**: Clean build, no undefined references, no LaTeX errors.
- **Output**: `final_paper/main.pdf` (7+ pages), `final_paper/paper.docx`

## Bibliography
- 44 citation keys used in `main.tex`, all resolved via `\cite{}`/`\citet{}`/`\citep{}` linked to `references.bib` through `\bibliographystyle{plainnat}` + `\bibliography{references}`.
- No literal `[1]`-style hardcoded citation text anywhere in the manuscript body.
- `references.bib` was pruned from the full 80-row `citation_support_bank.md` candidate pool down to the 44 entries actually cited in the manuscript, per the citation bank's stated curation step ("the bank is a candidate pool; final writing selects a coherent subset").

## Figures
All 6 figures (`fig1_phasediagram.pdf` through `fig6_dycktrajectory.pdf`) were generated directly from `results/*.json` via `paper_rewriting_output/generate_figures.py` (matplotlib). No AI image generation was used for any figure, per the project's data-integrity discipline (all figures are direct renders of experimental result files, not illustrations).

## Tables
5 tables (grid-resolution convergence, kinetics figure caption data, robustness predictions, held-out predictions, related-work comparison) all populated with numbers traced to `evidence_bank.md` rows.

## Word Output
`pandoc main.tex -o paper.docx --from latex --to docx --resource-path=. --number-sections --bibliography=references.bib --citeproc` — resolves `\cite` to linked numeric citations in the .docx. `word_guard.py` PASS (title check, font check, both PASS).

## Known follow-up (documented, not blocking)
All three originally-flagged VERIFY candidates (C47/C48/C49 in `citation_support_bank.md`) were independently re-verified via WebSearch during this session and their full author bylines corrected in `references.bib` before this build. The manuscript's Limitations section was updated accordingly to remove the now-resolved citation-completeness item.
