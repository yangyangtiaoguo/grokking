"""P8 — THE (alpha, wd) grokkability phase diagram.

All prior pilots converge here. Evidence so far (n=10, A2 recipe, 60k):
  alpha=2.5: wd=0.05 GROK 3/3 | wd=0.15 partial | wd=0.3 TRAP | wd=0.5/0.7 worse
  wd=0.3:    alpha<=2 GROK   | alpha=2.25 0/3  | alpha>=2.5 trap/starve
So the grok channel's wd-ceiling DECREASES with alpha (thermodynamic
lambda_c(alpha) decreasing, 11.2), and a second failure region (over-
regularization / crush) sits at high wd. This scan traces both boundaries.

Grid: alpha x wd, 3 seeds, full fresh runs for figure consistency.
Verdicts: GROK (A_unif>0.9) / TRAP (A_hi>0.9, A_unif<0.5) / CRUSH
(A_hi<0.9, A_unif<0.5) / PARTIAL (rest).

~126 runs x ~95s = ~3.3h. Results -> results/p8_phase_diagram.json.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p5_rescue import run

ALPHAS = [0.0, 1.0, 2.0, 2.25, 2.5, 2.75, 3.0]
WDS = [0.05, 0.1, 0.15, 0.2, 0.3, 0.5]

def verdict(r):
    if r['unif_tail'] > 0.9:
        return "GROK"
    if r['hi_tail'] > 0.9 and r['unif_tail'] < 0.5:
        return "TRAP"
    if r['hi_tail'] < 0.9 and r['unif_tail'] < 0.5:
        return "CRUSH"
    return "PARTIAL"

def main():
    seeds = [0, 1, 2]
    n, isc, lr, batch, ms = 10, 10.0, 1e-3, 128, 60000
    print(f"P8 phase diagram: n={n} init={isc} batch={batch} steps={ms} cosine")
    print(f"alphas={ALPHAS}\nwds={WDS}\n")
    out_path = "results/p8_phase_diagram.json"
    out = []
    t0 = time.time()
    for alpha in ALPHAS:
        for wd in WDS:
            for s in seeds:
                ts = time.time()
                r = run(n, alpha, 0.0, wd, isc, s, ms, lr, batch)
                v = verdict(r)
                print(f"a={alpha:4.2f} wd={wd:4.2f} | s{s} "
                      f"unif={r['unif_tail']:6.3f} hi={r['hi_tail']:6.3f} "
                      f"lo={r['lo_tail']:6.3f} | {v} ({time.time()-ts:.0f}s)", flush=True)
                out.append(dict(verdict=v, **r))
            json.dump(out, open(out_path, "w"))   # checkpoint after every cell
    # summary matrix
    print("\n=== grok-count matrix (out of 3 seeds) ===")
    print("      " + "".join(f"wd={w:<5}" for w in WDS))
    for alpha in ALPHAS:
        row = ""
        for wd in WDS:
            rs = [o for o in out if o['alpha'] == alpha and o['wd'] == wd]
            row += f"{sum(1 for x in rs if x['verdict'] == 'GROK'):>4}/3 "
        print(f"a={alpha:4.2f} {row}")
    print(f"\nelapsed {time.time()-t0:.0f}s -> {out_path}")

if __name__ == "__main__":
    main()
