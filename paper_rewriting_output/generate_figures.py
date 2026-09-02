"""Generate all figures for the manuscript directly from results/*.json and
paper_rewriting_output/stats_appendix.json. All figures are matplotlib
renders of real experimental data -- no AI image generation is used
anywhere, per the project's data-integrity discipline.

Style follows the publication-figure conventions summarized in
ChenLiu-1996/figures4papers's scientific-figure-making skill (house style
used for figures published at Nature Machine Intelligence, ICML, NeurIPS):
minimalist spines, frameless legends, a semantic color palette, and
consistent typography matching the LaTeX body text.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict

OUT = "paper_rewriting_output/final_paper"

# ---------------------------------------------------------------------------
# Publication style: fonts to match the LaTeX body (Times/serif + STIX math),
# clean spines, frameless legends, and a semantic color palette
# (blue = uniform/proposed, orange/red = targeted/rare, gray/pink = head/
# baseline/null), following the figures4papers house style.
# ---------------------------------------------------------------------------
PALETTE = {
    "blue_main": "#0F4D92",      # proposed / uniform / key result
    "blue_light": "#3775BA",
    "green_1": "#4C9A6B",        # secondary positive series
    "red_strong": "#B64342",     # baseline / rare / head / contrast
    "orange": "#D98C3D",
    "neutral": "#767676",
    "neutral_light": "#B3B3B3",
}

plt.rcParams.update({
    "font.family": ["Times New Roman", "DejaVu Serif", "serif"],
    "mathtext.fontset": "stix",
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 10.5,
    "ytick.labelsize": 10.5,
    "legend.fontsize": 10.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 1.1,
    "legend.frameon": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
    "lines.linewidth": 2.0,
    "lines.markersize": 6,
    "savefig.dpi": 300,
    "figure.dpi": 150,
})


def finalize(fig, path):
    fig.tight_layout(pad=1.2)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def ceiling_of(row_means, thr=0.9):
    pts = sorted(row_means.items())
    above = [(w, m) for w, m in pts if m >= thr]
    below = [(w, m) for w, m in pts if m < thr]
    if not below:
        return pts[-1][0]
    if not above:
        return below[0][0]
    w0, m0 = above[-1]
    cands = [(w, m) for w, m in below if w > w0]
    if not cands:
        return w0
    w1, m1 = cands[0]
    if m1 >= thr:
        return w1
    return w0 + (m0 - thr) / (m0 - m1) * (w1 - w0)


def fig1_phasediagram():
    """Heatmap of mean A_unif over (alpha, wd), n=10, 60k budget, plus a
    resolved ceiling overlay. wd is treated as a categorical axis with
    uniform row spacing (its raw values are highly non-uniform, 0.02-1.0)
    and displayed on a log-scaled label axis so ticks stay legible."""
    runs = []
    for f in ("p8_phase_diagram", "p10_fine_boundary", "p10b_gap_fill",
              "m1_n10_boundary"):
        runs += json.load(open(f"results/{f}.json"))
    cell = defaultdict(list)
    for r in runs:
        if r.get('max_steps', 60000) == 60000:
            cell[(r['alpha'], r['wd'])].append(r['unif_tail'])

    alphas = sorted({a for a, w in cell})
    wds = sorted({w for a, w in cell})
    Z = np.full((len(wds), len(alphas)), np.nan)
    for i, w in enumerate(wds):
        for j, a in enumerate(alphas):
            if (a, w) in cell:
                Z[i, j] = np.mean(cell[(a, w)])

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(Z, aspect='auto', origin='lower', cmap='viridis', vmin=0, vmax=1,
                    extent=[min(alphas), max(alphas), 0, len(wds)])
    # Show every 3rd wd label to avoid crowding; ticks still mark true rows.
    tick_idx = list(range(0, len(wds), 3))
    if (len(wds) - 1) not in tick_idx:
        tick_idx.append(len(wds) - 1)
    ax.set_yticks([i + 0.5 for i in tick_idx])
    ax.set_yticklabels([f"{wds[i]:.3g}" for i in tick_idx])
    ax.set_xlabel(r"skew $\alpha$")
    ax.set_ylabel(r"weight decay $\lambda$")
    ax.set_title(r"$(\alpha,\lambda)$ phase diagram, $n{=}10$, 60k-step budget")
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label(r"mean $A_{\mathrm{unif}}$")
    cbar.outline.set_linewidth(0.8)
    ax.grid(False)

    ceil_alphas, ceil_vals = [], []
    for a_ in alphas:
        wds_a = sorted(w for aa, w in cell if aa == a_)
        rm = {w: np.mean(cell[(a_, w)]) for w in wds_a}
        c = ceiling_of(rm)
        ceil_alphas.append(a_)
        ceil_vals.append(c)
    y_ceil = [np.interp(c, wds, np.arange(len(wds)) + 0.5) for c in ceil_vals]
    ax.plot(ceil_alphas, y_ceil, '-o', color=PALETTE["red_strong"],
             markersize=4, linewidth=1.8, markeredgecolor="white",
             markeredgewidth=0.6, label='resolved ceiling')
    leg = ax.legend(loc='upper right')
    leg.get_frame().set_alpha(0)
    finalize(fig, f"{OUT}/fig1_phasediagram.pdf")
    print("fig1 done")


def fig2_kinetics():
    d = json.load(open('results/m7_tau_dense.json'))
    cell = defaultdict(list)
    for r in d:
        cell[(r['alpha'], r['wd'])].append(r)

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.0))
    ax = axes[0]
    alphas_03 = [1.5, 1.75, 2.0, 2.1, 2.2, 2.25]
    censf = []
    for a_ in alphas_03:
        rs = cell.get((a_, 0.3), [])
        n = len(rs)
        c = sum(1 for r in rs if r['t_grok'] is None)
        censf.append(c / n if n else np.nan)
    ax.plot(alphas_03, censf, 'o-', color=PALETTE["red_strong"],
            markeredgecolor="white", markeredgewidth=0.6)
    ax.set_xlabel(r"skew $\alpha$ ($\lambda=0.3$)")
    ax.set_ylabel("fraction not generalized\nby 240k steps")
    ax.set_title("(a) censoring fraction")
    ax.set_ylim(-0.05, 1.05)

    ax2 = axes[1]
    alphas_005 = [2.0, 2.2, 2.4, 2.5, 2.6, 2.7, 2.75]
    meds = []
    for a_ in alphas_005:
        rs = cell.get((a_, 0.05), [])
        obs = sorted(r['t_grok'] for r in rs if r['t_grok'] is not None)
        meds.append(np.median(obs) if obs else np.nan)
    ax2.plot(alphas_005, meds, 's-', color=PALETTE["blue_main"],
             markeredgecolor="white", markeredgewidth=0.6)
    ax2.set_xlabel(r"skew $\alpha$ ($\lambda=0.05$)")
    ax2.set_ylabel("median steps to\ngeneralize (observed)")
    ax2.set_title("(b) median generalization time")
    finalize(fig, f"{OUT}/fig2_kinetics.pdf")
    print("fig2 done")


def fig3_doseresponse():
    d = json.load(open('results/m8a_dose_sweep.json'))
    cell = defaultdict(lambda: defaultdict(list))
    for r in d:
        p = r['k'] / r['batch']
        cell[r['alpha']][round(p, 5)].append(r['unif_tail'])

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    colors = {2.5: PALETTE["blue_main"], 2.75: PALETTE["orange"], 3.0: PALETTE["red_strong"]}
    markers = {2.5: 'o', 2.75: 's', 3.0: '^'}
    for a_, series in sorted(cell.items()):
        ps = sorted(series)
        means = [np.mean(series[p]) for p in ps]
        ax.plot([p * 100 for p in ps], means, marker=markers[a_], color=colors[a_],
                 label=fr"$\alpha={a_}$", markeredgecolor="white", markeredgewidth=0.6)
    ax.set_xscale('log')
    ax.set_xlabel("injection dose (% of minibatch)")
    ax.set_ylabel(r"mean $A_{\mathrm{unif}}$")
    ax.set_title("dose-response for uniform injection\n(batch-varying protocol)")
    ax.axvspan(0.391, 0.781, alpha=0.15, color=PALETTE["neutral"], label='transition region')
    leg = ax.legend(fontsize=9.5, loc='lower right')
    leg.get_frame().set_alpha(0)
    finalize(fig, f"{OUT}/fig3_doseresponse.pdf")
    print("fig3 done")


def fig4_modadd():
    d = json.load(open('results/m12_modadd_targeted.json'))
    cell = defaultdict(list)
    for r in d:
        if r['k'] == 1:
            cell[r.get('inject', 'uniform')].append(r['unif_tail'])
    modes = ['uniform', 'tail', 'head']
    labels = ['uniform', 'tail\n(rare, large-operand)', 'head\n(most frequent)']
    colors = [PALETTE["blue_main"], PALETTE["orange"], PALETTE["red_strong"]]
    means = [np.mean(cell[m]) for m in modes]
    sems = [np.std(cell[m]) / np.sqrt(len(cell[m])) for m in modes]

    fig, ax = plt.subplots(figsize=(4.8, 4.4))
    bars = ax.bar(labels, means, yerr=sems, color=colors, capsize=4,
                   edgecolor='black', linewidth=1.2,
                   error_kw=dict(elinewidth=1.3, ecolor='black'))
    for b, m in zip(bars, means):
        ax.text(b.get_x() + b.get_width() / 2, m + 0.03, f"{m:.2f}",
                 ha='center', va='bottom', fontsize=10)
    ax.axhline(0.9, linestyle='--', color=PALETTE["neutral"], linewidth=1.2, label='GROK threshold')
    ax.set_ylabel(r"mean $A_{\mathrm{unif}}$")
    ax.set_title(r"modular addition, $\alpha{=}3.0$" + "\ninjection ranking")
    ax.set_ylim(0, 1.08)
    leg = ax.legend(fontsize=9.5, loc='upper right')
    leg.get_frame().set_alpha(0)
    finalize(fig, f"{OUT}/fig4_modadd.pdf")
    print("fig4 done")


def fig5_dyckboundary():
    d = json.load(open('results/dyck_boundary.json'))
    cell = defaultdict(list)
    for r in d:
        cell[(r['alpha'], r['wd'])].append(r['unif_tail'])
    alphas = sorted({a for a, w in cell})
    wds = sorted({w for a, w in cell})
    Z = np.full((len(wds), len(alphas)), np.nan)
    for i, w in enumerate(wds):
        for j, a in enumerate(alphas):
            if (a, w) in cell:
                Z[i, j] = np.mean(cell[(a, w)])
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    im = ax.imshow(Z, aspect='auto', origin='lower', cmap='viridis', vmin=0, vmax=1,
                    extent=[min(alphas), max(alphas), 0, len(wds)])
    ax.set_yticks(np.arange(len(wds)) + 0.5)
    ax.set_yticklabels([f"{w:.2g}" for w in wds])
    ax.set_xlabel(r"skew $\alpha$ (by max nesting depth)")
    ax.set_ylabel(r"weight decay $\lambda$")
    ax.set_title(r"Dyck-1 failure region, $L{=}10$")
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label(r"mean $A_{\mathrm{unif}}$")
    cbar.outline.set_linewidth(0.8)
    ax.grid(False)
    finalize(fig, f"{OUT}/fig5_dyckboundary.pdf")
    print("fig5 done")


def fig6_dycktrajectory():
    d = json.load(open('results/dyck_budget.json'))
    cell = defaultdict(list)
    for r in d:
        if r['alpha'] == 6.0 and r['wd'] == 0.9:
            cell[r['max_steps']].append(r)
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    style = {60000: dict(color=PALETTE["blue_main"], linestyle='-', label='60k-step runs'),
             240000: dict(color=PALETTE["red_strong"], linestyle='--', label='240k-step runs')}
    for ms, rs in sorted(cell.items()):
        for i, r in enumerate(rs):
            ax.plot(r['steps'], r['aunif'], alpha=0.75, linewidth=1.6,
                     color=style[ms]["color"], linestyle=style[ms]["linestyle"],
                     label=style[ms]["label"] if i == 0 else None)
    ax.set_xlabel("training step")
    ax.set_ylabel(r"$A_{\mathrm{unif}}$")
    ax.set_title(r"Dyck-1 shallow-grok metastability, $\alpha{=}6.0$, $\lambda{=}0.9$")
    leg = ax.legend(fontsize=10, loc='center right')
    leg.get_frame().set_alpha(0)
    finalize(fig, f"{OUT}/fig6_dycktrajectory.pdf")
    print("fig6 done")


if __name__ == "__main__":
    fig1_phasediagram()
    fig2_kinetics()
    fig3_doseresponse()
    fig4_modadd()
    fig5_dyckboundary()
    fig6_dycktrajectory()
