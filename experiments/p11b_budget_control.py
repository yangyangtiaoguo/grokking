"""P11b — budget control for the n=12 inward boundary shift (kinetic vs thermodynamic).

P11 measured ceiling(2): n=10 0.305 -> n=12 0.211 (ratio 1.44), and the right
boundary at wd=0.05 moved left ~0.25 in alpha. Theory curves say: mass family
(heldout H) predicts a ~4x drop n=10->12, carry family (E_c/d0/shape_s)
predicts ~1x. Measured 1.44x sits between — BUT there is a confound: n=12 has
4x the states with the same 60k x 128 budget, so per-state exposure fell 4x.
The shift could be KINETIC (critical slowing, P7/P11 framework) rather than
thermodynamic.

Control: re-run the n=12 failing/borderline cells at 240k steps (4x budget,
cosine T_max=240k so annealing does not freeze early — same protocol as P7).
  - If they GROK at 240k: the shift is (at least partly) kinetic/budget.
  - If still TRAPPED: the shift is thermodynamic (real n-sharpening of the
    boundary).

Cells (n=12, near-boundary failures at 60k): (2.0,0.3) 0.798, (2.0,0.2) 0.913
borderline, (2.25,0.15) 0.595, (2.5,0.1) 0.670, (2.75,0.05) 0.524.
5 cells x 2 seeds x 240k steps ~= 65 min -> results/p11b_budget_control.json.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p5_rescue import run

CELLS = [(2.0, 0.3), (2.0, 0.2), (2.25, 0.15), (2.5, 0.1), (2.75, 0.05)]


def verdict(r):
    if r['unif_tail'] > 0.9:
        return "GROK"
    if r['hi_tail'] > 0.9 and r['unif_tail'] < 0.5:
        return "TRAP"
    if r['hi_tail'] < 0.9 and r['unif_tail'] < 0.5:
        return "CRUSH"
    return "PARTIAL"


def main():
    n, isc, lr, batch, ms = 12, 10.0, 1e-3, 128, 240000
    print(f"P11b budget control: n={n} steps={ms} (4x budget, cosine T_max=240k)")
    print(f"cells={CELLS}, seeds 0,1\n")
    out_path = "results/p11b_budget_control.json"
    out = []
    t0 = time.time()
    for alpha, wd in CELLS:
        for s in [0, 1]:
            ts = time.time()
            r = run(n, alpha, 0.0, wd, isc, s, ms, lr, batch)
            v = verdict(r)
            print(f"a={alpha:4.2f} wd={wd:4.2f} | s{s} "
                  f"unif={r['unif_tail']:6.3f} hi={r['hi_tail']:6.3f} "
                  f"lo={r['lo_tail']:6.3f} | {v} ({time.time()-ts:.0f}s)", flush=True)
            out.append(dict(verdict=v, **r))
        json.dump(out, open(out_path, "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
