"""Generate all figures for the manuscript directly from results/*.json and
paper_rewriting_output/stats_appendix.json. No AI image generation is used
for any of these -- all are matplotlib renders of real experimental data,
per the project's own data-integrity discipline.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict

OUT = "paper_rewriting_output/final_paper"


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
    marked deep-trap non-escape point and the resolved ceiling curve."""
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

    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(Z, aspect='auto', origin='lower', cmap='viridis', vmin=0, vmax=1,
                    extent=[min(alphas), max(alphas), 0, len(wds)])
    ax.set_yticks(np.arange(len(wds)) + 0.5)
    ax.set_yticklabels([f"{w:.3f}" for w in wds])
    ax.set_xlabel(r"skew $\alpha$")
    ax.set_ylabel(r"weight decay $\lambda$")
    ax.set_title(r"$(\alpha,\lambda)$ phase diagram, $n{=}10$, 60k-step budget (mean $A_{\mathrm{unif}}$)")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(r"$A_{\mathrm{unif}}$")

    ceil_alphas, ceil_vals = [], []
    for a_ in alphas:
        wds_a = sorted(w for aa, w in cell if aa == a_)
        rm = {w: np.mean(cell[(a_, w)]) for w in wds_a}
        c = ceiling_of(rm)
        ceil_alphas.append(a_)
        ceil_vals.append(c)
    y_ceil = [np.interp(c, wds, np.arange(len(wds)) + 0.5) for c in ceil_vals]
    ax.plot(ceil_alphas, y_ceil, 'r-o', markersize=3, linewidth=1.2, label='resolved ceiling')
    ax.legend(loc='upper right', fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig1_phasediagram.pdf")
    plt.close(fig)
    print("fig1 done")


def fig2_kinetics():
    d = json.load(open('results/m7_tau_dense.json'))
    cell = defaultdict(list)
    for r in d:
        cell[(r['alpha'], r['wd'])].append(r)

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    ax = axes[0]
    alphas_03 = [1.5, 1.75, 2.0, 2.1, 2.2, 2.25]
    censf = []
    for a_ in alphas_03:
        rs = cell.get((a_, 0.3), [])
        n = len(rs)
        c = sum(1 for r in rs if r['t_grok'] is None)
        censf.append(c / n if n else np.nan)
    ax.plot(alphas_03, censf, 'o-', color='crimson')
    ax.set_xlabel(r"skew $\alpha$ ($\lambda=0.3$)")
    ax.set_ylabel("fraction not generalized by 240k steps")
    ax.set_title("(a) censoring fraction")
    ax.set_ylim(-0.05, 1.05)

    ax2 = axes[1]
    alphas_005 = [2.0, 2.2, 2.4, 2.5, 2.6, 2.7, 2.75]
    meds = []
    for a_ in alphas_005:
        rs = cell.get((a_, 0.05), [])
        obs = sorted(r['t_grok'] for r in rs if r['t_grok'] is not None)
        meds.append(np.median(obs) if obs else np.nan)
    ax2.plot(alphas_005, meds, 's-', color='steelblue')
    ax2.set_xlabel(r"skew $\alpha$ ($\lambda=0.05$)")
    ax2.set_ylabel("median steps to generalize (observed)")
    ax2.set_title("(b) median generalization time")
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig2_kinetics.pdf")
    plt.close(fig)
    print("fig2 done")


def fig3_doseresponse():
    d = json.load(open('results/m8a_dose_sweep.json'))
    cell = defaultdict(lambda: defaultdict(list))
    for r in d:
        p = r['k'] / r['batch']
        cell[r['alpha']][round(p, 5)].append(r['unif_tail'])

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = {2.5: 'crimson', 2.75: 'darkorange', 3.0: 'steelblue'}
    for a_, series in cell.items():
        ps = sorted(series)
        means = [np.mean(series[p]) for p in ps]
        ax.plot([p * 100 for p in ps], means, 'o-', label=fr"$\alpha={a_}$", color=colors.get(a_))
    ax.set_xscale('log')
    ax.set_xlabel("injection dose (% of minibatch)")
    ax.set_ylabel(r"mean $A_{\mathrm{unif}}$")
    ax.set_title("dose-response for uniform injection")
    ax.axvspan(0.391, 0.781, alpha=0.15, color='gray', label='transition bracket')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig3_doseresponse.pdf")
    plt.close(fig)
    print("fig3 done")


def fig4_modadd():
    d = json.load(open('results/m12_modadd_targeted.json'))
    cell = defaultdict(list)
    for r in d:
        if r['k'] == 1:
            cell[r.get('inject', 'uniform')].append(r['unif_tail'])
    modes = ['uniform', 'tail', 'head']
    means = [np.mean(cell[m]) for m in modes]
    sems = [np.std(cell[m]) / np.sqrt(len(cell[m])) for m in modes]

    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.bar(modes, means, yerr=sems, color=['steelblue', 'darkorange', 'crimson'], capsize=4)
    ax.axhline(0.9, linestyle='--', color='gray', linewidth=1, label='GROK threshold')
    ax.set_ylabel(r"mean $A_{\mathrm{unif}}$")
    ax.set_title(r"modular addition, $\alpha{=}3.0$, injection ranking")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig4_modadd.pdf")
    plt.close(fig)
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
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    im = ax.imshow(Z, aspect='auto', origin='lower', cmap='viridis', vmin=0, vmax=1,
                    extent=[min(alphas), max(alphas), 0, len(wds)])
    ax.set_yticks(np.arange(len(wds)) + 0.5)
    ax.set_yticklabels([f"{w:.2f}" for w in wds])
    ax.set_xlabel(r"skew $\alpha$ (by max nesting depth)")
    ax.set_ylabel(r"weight decay $\lambda$")
    ax.set_title(r"Dyck-1 failure region, $L{=}10$")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(r"$A_{\mathrm{unif}}$")
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig5_dyckboundary.pdf")
    plt.close(fig)
    print("fig5 done")


def fig6_dycktrajectory():
    d = json.load(open('results/dyck_budget.json'))
    cell = defaultdict(list)
    for r in d:
        if r['alpha'] == 6.0 and r['wd'] == 0.9:
            cell[r['max_steps']].append(r)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for ms, rs in sorted(cell.items()):
        for r in rs:
            ax.plot(r['steps'], r['aunif'], alpha=0.7,
                     label=f"B={ms//1000}k, seed{r['seed']}" if r['seed'] == 0 else None,
                     linestyle='-' if ms == 60000 else '--',
                     color='steelblue' if ms == 60000 else 'crimson')
    ax.set_xlabel("training step")
    ax.set_ylabel(r"$A_{\mathrm{unif}}$")
    ax.set_title(r"Dyck-1 shallow-grok metastability, $\alpha{=}6.0$, $\lambda{=}0.9$")
    ax.legend(fontsize=7, loc='lower right')
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig6_dycktrajectory.pdf")
    plt.close(fig)
    print("fig6 done")


if __name__ == "__main__":
    fig1_phasediagram()
    fig2_kinetics()
    fig3_doseresponse()
    fig4_modadd()
    fig5_dyckboundary()
    fig6_dycktrajectory()
