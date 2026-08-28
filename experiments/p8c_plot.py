"""P8c — plot the (alpha, wd) grokkability phase diagram from P8 results.

Reads results/p8_phase_diagram.json (checkpointed after every cell, so this
works even on a partial scan). Produces figures/p8_phase_diagram.png:
  left  — heatmap of 3-seed mean A_unif over (alpha, wd)
  right — verdict map (GROK/TRAP/CRUSH/PARTIAL by majority)
plus a printed wd-ceiling(alpha) table (max wd that still groks).
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ALPHAS = [0.0, 1.0, 2.0, 2.25, 2.5, 2.75, 3.0]
WDS = [0.05, 0.1, 0.15, 0.2, 0.3, 0.5]

def main():
    out = json.load(open("results/p8_phase_diagram.json"))
    A = np.full((len(ALPHAS), len(WDS)), np.nan)
    V = np.empty((len(ALPHAS), len(WDS)), dtype=object)
    for i, a in enumerate(ALPHAS):
        for j, w in enumerate(WDS):
            rs = [o for o in out if o['alpha'] == a and o['wd'] == w]
            if not rs:
                continue
            A[i, j] = np.mean([o['unif_tail'] for o in rs])
            vs = [o['verdict'] for o in rs]
            V[i, j] = max(set(vs), key=vs.count)   # majority verdict

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    im = axes[0].imshow(A, origin="lower", aspect="auto", cmap="RdYlGn",
                        vmin=0, vmax=1,
                        extent=[WDS[0] - 0.025, WDS[-1] + 0.025,
                                ALPHAS[0] - 0.125, ALPHAS[-1] + 0.125])
    axes[0].set_xticks(WDS); axes[0].set_yticks(ALPHAS)
    axes[0].set_xlabel("weight decay (wd)"); axes[0].set_ylabel("skew alpha")
    axes[0].set_title("A_unif (3-seed mean, tail)")
    for i in range(len(ALPHAS)):
        for j in range(len(WDS)):
            if not np.isnan(A[i, j]):
                axes[0].text(WDS[j], ALPHAS[i], f"{A[i, j]:.2f}",
                             ha="center", va="center", fontsize=7)
    plt.colorbar(im, ax=axes[0])

    cmap = {"GROK": "#2a7f3f", "TRAP": "#c0392b", "CRUSH": "#7f1d1d",
            "PARTIAL": "#e6a817"}
    for i, a in enumerate(ALPHAS):
        for j, w in enumerate(WDS):
            if V[i, j]:
                axes[1].add_patch(plt.Rectangle((w - 0.0225, a - 0.11), 0.045,
                                                0.22, color=cmap[V[i, j]]))
                axes[1].text(w, a, V[i, j][0], ha="center", va="center",
                             color="w", fontsize=9, fontweight="bold")
    axes[1].set_xlim(WDS[0] - 0.025, WDS[-1] + 0.025)
    axes[1].set_ylim(ALPHAS[0] - 0.125, ALPHAS[-1] + 0.125)
    axes[1].set_xticks(WDS); axes[1].set_yticks(ALPHAS)
    axes[1].set_xlabel("weight decay (wd)"); axes[1].set_ylabel("skew alpha")
    axes[1].set_title("verdict (majority of 3 seeds)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=k)
               for k, c in cmap.items()]
    axes[1].legend(handles=handles, loc="upper right", fontsize=8)
    fig.suptitle("Grokkability phase diagram — LARGECOUNTER n=10, 60k steps "
                 "(G=grok, T=trap, C=crush, P=partial)", y=1.02)
    fig.tight_layout()
    fig.savefig("figures/p8_phase_diagram.png", dpi=160, bbox_inches="tight")
    print("-> figures/p8_phase_diagram.png")

    print("\nwd-ceiling(alpha): largest tested wd with majority GROK")
    for i, a in enumerate(ALPHAS):
        ceil = None
        for j, w in enumerate(WDS):
            if V[i, j] == "GROK":
                ceil = w
        print(f"  alpha={a:4.2f}: "
              f"{'wd<='+str(ceil) if ceil else 'none in grid'}"
              f"   verdicts: {[V[i, j] for j in range(len(WDS))]}")

if __name__ == "__main__":
    main()
