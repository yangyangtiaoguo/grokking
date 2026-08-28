"""M4 — mechanism summary fits (CPU): merged boundary + bootstrap CI + candidates.

Merges ALL n=10 60k-step boundary data (P8 + P10 + P10b + M1a), bootstraps
over seeds per cell to get ceiling(alpha) with CIs, and fits the five
pre-registered single-scale candidates plus the ranking with uncertainty.

Also compiles the campaign summary numbers (rescue battery, tau, budget
curves) into one JSON for the paper's results section.

-> results/m4_fits.json
"""
import sys, json
sys.path.insert(0, "experiments")
import numpy as np
from collections import defaultdict

RNG = np.random.default_rng(42)
NBOOT = 1000
THR = 0.9


def load_cells():
    runs = []
    for f in ("p8_phase_diagram", "p10_fine_boundary", "p10b_gap_fill",
              "m1_n10_boundary"):
        runs += json.load(open(f"results/{f}.json"))
    cells = defaultdict(list)
    for r in runs:
        if r.get('max_steps', 60000) == 60000:  # 60k budget only; pilots are all 60k
            cells[(r['alpha'], r['wd'])].append(r['unif_tail'])
    return cells


def ceiling_of(row_means, thr=THR):
    """row_means: dict wd -> mean. Returns interpolated crossing or bound tag."""
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


def main():
    cells = load_cells()
    alphas = sorted({a for a, w in cells})

    # bootstrap ceilings per alpha
    boot = defaultdict(list)
    point = {}
    for a_ in alphas:
        wds = sorted(w for aa, w in cells if aa == a_)
        seeds_per_wd = {w: cells[(a_, w)] for w in wds}
        point[a_] = ceiling_of({w: np.mean(v) for w, v in seeds_per_wd.items()})
        for _ in range(NBOOT):
            rm = {w: float(np.mean(RNG.choice(v, size=len(v), replace=True)))
                  for w, v in seeds_per_wd.items()}
            tag, val = ceiling_of(rm)
            if tag == '~':
                boot[a_].append(val)
    resolved = sorted(a for a in alphas if point[a][0] == '~' and a >= 1.5)
    print(f"resolved ceilings ({len(resolved)} pts, 60k budget, n=10):")
    for a_ in resolved:
        b = boot[a_]
        ci = f" [{np.percentile(b,5):.3f},{np.percentile(b,95):.3f}]" if b else " [no CI]"
        print(f"  alpha={a_:<5} {point[a_][1]:.4g}{ci}  (n_boot={len(b)})")

    # candidate fits with bootstrap
    Nx = 2 ** 10
    x = np.arange(Nx, dtype=np.float64)
    cc = np.array([bin(i)[2:][::-1].split('0')[0].__len__() for i in range(Nx)], float)

    def cand(k, a_):
        w = (x + 1.0) ** (-a_); w /= w.sum()
        return {'H_lo': w[Nx // 2:].sum(), 'H_tail10': w[Nx // 10:].sum(),
                'E_c': (w * cc).sum(), 'exp2': 2.0 ** (-a_),
                'p_star': w[Nx - 1]}[k]

    names = ('H_lo', 'H_tail10', 'E_c', 'exp2', 'p_star')
    lw_point = np.log([point[a_][1] for a_ in resolved])
    print("\nsingle-scale fits (point estimate; bootstrap mean+-sd over ceiling draws):")
    fits = {}
    for k in names:
        lcv = np.log([cand(k, a_) for a_ in resolved])
        C = float(np.exp(np.mean(lw_point - lcv)))
        errs = [abs(C * cand(k, a_) - point[a_][1]) / point[a_][1] for a_ in resolved]
        # bootstrap: resample ceilings jointly
        b_errs, b_slope = [], []
        for _ in range(200):
            cs = [np.mean(RNG.choice(boot[a_], size=min(len(boot[a_]), 5))) if boot[a_]
                  else point[a_][1] for a_ in resolved]
            lwc = np.log(cs)
            Cb = np.exp(np.mean(lwc - lcv))
            b_errs.append(max(abs(Cb * cand(k, a_) - cs[i]) / cs[i]
                              for i, a_ in enumerate(resolved)))
            b_slope.append(np.polyfit(lcv, lwc, 1)[0])
        fits[k] = dict(C=C, max_err=float(max(errs)), mean_err=float(np.mean(errs)),
                       slope=float(np.polyfit(lcv, lw_point, 1)[0]),
                       boot_max_err_mean=float(np.mean(b_errs)),
                       boot_max_err_sd=float(np.std(b_errs)),
                       boot_slope_mean=float(np.mean(b_slope)))
        f = fits[k]
        print(f"  {k:<9} max={f['max_err']:.2f} (boot {f['boot_max_err_mean']:.2f}"
              f"+-{f['boot_max_err_sd']:.2f})  slope={f['slope']:.2f} "
              f"(boot {f['boot_slope_mean']:.2f})")

    out = dict(n=10, budget=60000, thr=THR,
               ceilings={str(a_): dict(tag=point[a_][0], val=point[a_][1],
                                       boot_ci05=(float(np.percentile(boot[a_], 5))
                                                  if boot[a_] else None),
                                       boot_ci95=(float(np.percentile(boot[a_], 95))
                                                  if boot[a_] else None))
                         for a_ in alphas},
               fits=fits, resolved=resolved,
               note="p_star pre-registered then rejected; boundary steeper than all candidates")
    json.dump(out, open("results/m4_fits.json", "w"), indent=1)
    print("\n-> results/m4_fits.json")


if __name__ == "__main__":
    main()
