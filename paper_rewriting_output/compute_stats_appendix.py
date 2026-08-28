"""Writing-stage statistical analyses required by PAPER_SKELETON.md Section 3.3.

Recomputes (not re-runs) from existing results/*.json:
  1. Bootstrap CI for the n=10 60k-budget boundary ceilings (extends m4_fits.py's
     bootstrap to ALL resolved alphas, with cited code path).
  2. Censoring-fraction tables for both tau transects (wd=0.05 and wd=0.3) from
     results/m7_tau_dense.json.
  3. Grid-resolution convergence: ceiling(alpha) estimate before densification
     (P8/P10 sparse grid) vs after (M1a+P10b dense grid), to answer "is the
     near-vertical wall a coarse-grid artifact?"
  4. Threshold sensitivity: recompute GROK verdict counts at thr in {0.85, 0.90,
     0.95} to show the phase-diagram conclusions are not an artifact of the
     0.9 cutoff choice.

Output: paper_rewriting_output/stats_appendix.json (machine-readable) +
paper_rewriting_output/stats_appendix.md (human-readable tables for the paper).
"""
import json
import numpy as np
from collections import defaultdict

RNG = np.random.default_rng(7)
NBOOT = 2000


def load_boundary_60k():
    runs = []
    for f in ("p8_phase_diagram", "p10_fine_boundary", "p10b_gap_fill",
              "m1_n10_boundary"):
        runs += json.load(open(f"results/{f}.json"))
    cells = defaultdict(list)
    for r in runs:
        if r.get('max_steps', 60000) == 60000:
            cells[(r['alpha'], r['wd'])].append(r['unif_tail'])
    return cells


def ceiling_of(row_means, thr):
    pts = sorted(row_means.items())
    above = [(w, m) for w, m in pts if m >= thr]
    below = [(w, m) for w, m in pts if m < thr]
    if not below:
        return ('>', pts[-1][0])
    if not above:
        return ('<', below[0][0])
    w0, m0 = above[-1]
    cands = [(w, m) for w, m in below if w > w0]
    if not cands:
        return ('~', w0)
    w1, m1 = cands[0]
    if m1 >= thr:
        return ('~', w1)
    return ('~', w0 + (m0 - thr) / (m0 - m1) * (w1 - w0))


def analysis_1_bootstrap_ci():
    cells = load_boundary_60k()
    alphas = sorted({a for a, w in cells})
    out = {}
    for a_ in alphas:
        wds = sorted(w for aa, w in cells if aa == a_)
        seeds_per_wd = {w: cells[(a_, w)] for w in wds}
        point_tag, point_val = ceiling_of({w: np.mean(v) for w, v in seeds_per_wd.items()}, 0.9)
        boot_vals = []
        for _ in range(NBOOT):
            rm = {w: float(np.mean(RNG.choice(v, size=len(v), replace=True)))
                  for w, v in seeds_per_wd.items()}
            tag, val = ceiling_of(rm, 0.9)
            if tag == '~':
                boot_vals.append(val)
        entry = dict(tag=point_tag, point_estimate=point_val, n_seeds_per_wd={str(w): len(v) for w, v in seeds_per_wd.items()})
        if boot_vals:
            entry['boot_ci90'] = [float(np.percentile(boot_vals, 5)), float(np.percentile(boot_vals, 95))]
            entry['boot_n'] = len(boot_vals)
        out[str(a_)] = entry
    return out


def analysis_2_censoring_tables():
    d = json.load(open('results/m7_tau_dense.json'))
    cell = defaultdict(list)
    for r in d:
        cell[(r['alpha'], r['wd'])].append(r)
    out = {}
    for (a_, w_), rs in cell.items():
        n = len(rs)
        censored = sum(1 for r in rs if r['t_grok'] is None)
        observed = sorted(r['t_grok'] for r in rs if r['t_grok'] is not None)
        out[f"alpha={a_},wd={w_}"] = dict(
            n=n, censored=censored, censoring_fraction=censored / n,
            median_tau_observed=(float(np.median(observed)) if observed else None),
            observed_taus=observed)
    return out


def analysis_3_grid_convergence():
    """Ceiling(alpha) from sparse pilot grid (P8+P10 pre-densification) vs
    dense grid (adding P10b+M1a). Answers: does the 'near-vertical wall'
    survive densification, or was it a coarse-grid artifact?"""
    sparse = defaultdict(list)
    for f in ("p8_phase_diagram", "p10_fine_boundary"):
        for r in json.load(open(f"results/{f}.json")):
            if r.get('max_steps', 60000) == 60000:
                sparse[(r['alpha'], r['wd'])].append(r['unif_tail'])
    dense = load_boundary_60k()

    def ceilings_for(cells):
        out = {}
        for a_ in sorted({a for a, w in cells}):
            wds = sorted(w for aa, w in cells if aa == a_)
            rm = {w: np.mean(cells[(a_, w)]) for w in wds}
            tag, val = ceiling_of(rm, 0.9)
            out[a_] = (tag, val, len(wds))
        return out

    sp = ceilings_for(sparse)
    de = ceilings_for(dense)
    common_alphas = sorted(set(sp) & set(de))
    out = {}
    for a_ in common_alphas:
        out[str(a_)] = dict(
            sparse_grid=dict(tag=sp[a_][0], val=sp[a_][1], n_wd_points=sp[a_][2]),
            dense_grid=dict(tag=de[a_][0], val=de[a_][1], n_wd_points=de[a_][2]),
        )
    return out


def analysis_4_threshold_sensitivity():
    p8 = json.load(open('results/p8_phase_diagram.json'))
    out = {}
    for thr in (0.85, 0.90, 0.95):
        cell = defaultdict(lambda: {'a': [], 'g': 0})
        for r in p8:
            cell[(r['alpha'], r['wd'])]['a'].append(r['unif_tail'])
            cell[(r['alpha'], r['wd'])]['g'] += (r['unif_tail'] > thr)
        # summary: total GROK cells at each threshold, and ceiling(alpha=2.5) at each
        total_grok_runs = sum(v['g'] for v in cell.values())
        total_runs = sum(len(v['a']) for v in cell.values())
        row25 = {w: np.mean(cell[(2.5, w)]['a']) for w in sorted(w for a, w in cell if a == 2.5)}
        tag25, val25 = ceiling_of(row25, thr)
        out[str(thr)] = dict(total_grok_fraction=total_grok_runs / total_runs,
                             ceiling_alpha_2_5=dict(tag=tag25, val=val25))
    return out


def main():
    out = dict(
        source_note="Recomputed 2026-08-28 from results/*.json per PAPER_SKELETON.md Sec 3.3 writing-stage TODO. Code: paper_rewriting_output/compute_stats_appendix.py",
        analysis_1_bootstrap_ci_boundary=analysis_1_bootstrap_ci(),
        analysis_2_censoring_tables=analysis_2_censoring_tables(),
        analysis_3_grid_resolution_convergence=analysis_3_grid_convergence(),
        analysis_4_threshold_sensitivity=analysis_4_threshold_sensitivity(),
    )
    json.dump(out, open("paper_rewriting_output/stats_appendix.json", "w"), indent=1)

    # human-readable markdown
    lines = ["# Statistics Appendix (recomputed from results/*.json)\n",
             f"> Source: {out['source_note']}\n"]

    lines.append("## 1. Bootstrap CI for boundary ceilings (n=10, 60k-step budget)\n")
    lines.append("| alpha | tag | point estimate | 90% bootstrap CI | n_boot |")
    lines.append("|---|---|---|---|---|")
    for a_, e in out['analysis_1_bootstrap_ci_boundary'].items():
        ci = e.get('boot_ci90')
        ci_str = f"[{ci[0]:.4f}, {ci[1]:.4f}]" if ci else "N/A (bound, not resolved)"
        lines.append(f"| {a_} | {e['tag']} | {e['point_estimate']:.4f} | {ci_str} | {e.get('boot_n','-')} |")

    lines.append("\n## 2. Censoring-fraction tables (tau transects, results/m7_tau_dense.json)\n")
    lines.append("| alpha, wd | n | censored | censoring fraction | median tau (observed) |")
    lines.append("|---|---|---|---|---|")
    for k, e in out['analysis_2_censoring_tables'].items():
        mt = f"{e['median_tau_observed']:.0f}" if e['median_tau_observed'] is not None else "N/A (all censored)"
        lines.append(f"| {k} | {e['n']} | {e['censored']} | {e['censoring_fraction']:.2f} | {mt} |")

    lines.append("\n## 3. Grid-resolution convergence (sparse pilot grid vs dense grid)\n")
    lines.append("| alpha | sparse ceiling | sparse #wd | dense ceiling | dense #wd |")
    lines.append("|---|---|---|---|---|")
    for a_, e in out['analysis_3_grid_resolution_convergence'].items():
        s, dd = e['sparse_grid'], e['dense_grid']
        lines.append(f"| {a_} | {s['tag']}{s['val']:.4f} | {s['n_wd_points']} | {dd['tag']}{dd['val']:.4f} | {dd['n_wd_points']} |")

    lines.append("\n## 4. Threshold sensitivity (GROK verdict cutoff)\n")
    lines.append("| threshold | overall GROK fraction (P8 grid) | ceiling(alpha=2.5) |")
    lines.append("|---|---|---|")
    for thr, e in out['analysis_4_threshold_sensitivity'].items():
        c = e['ceiling_alpha_2_5']
        lines.append(f"| {thr} | {e['total_grok_fraction']:.3f} | {c['tag']}{c['val']:.4f} |")

    open("paper_rewriting_output/stats_appendix.md", "w").write("\n".join(lines) + "\n")
    print("Wrote paper_rewriting_output/stats_appendix.json and .md")


if __name__ == "__main__":
    main()
