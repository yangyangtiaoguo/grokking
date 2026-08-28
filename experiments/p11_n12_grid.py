"""P11 — finite-size check: the full P8 grid re-run at n=12.

Theory pre-registration (theory_curves.py) predicts n-sharpening: the
boundary structure should SHARPEN/MOVE as n grows (|slope@alpha=1| rises
8->16: 0.099->0.317). If the (alpha, wd) diagram at n=12 reproduces with the
boundary shifted in the predicted direction, the phase diagram is a property
of the task distribution, not an n=10 artifact.

Recipe transferred VERBATIM from P8 (v6 lesson: one knob at a time — here the
only change is n: 10 -> 12; state space 1024 -> 4096, everything else fixed).
Note v8[D] saw n=12 grok WITHOUT delay (eval crosses before train) — that is
fine for verdict purposes: the diagram classifies FINAL states, not delays.

Grid: same as P8. 7 alpha x 6 wd x 3 seeds = 126 runs ~3.5h
-> results/p11_n12_grid.json.
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
    n, isc, lr, batch, ms = 12, 10.0, 1e-3, 128, 60000
    print(f"P11 n=12 grid: n={n} init={isc} batch={batch} steps={ms} cosine")
    print(f"alphas={ALPHAS}\nwds={WDS}\n")
    out_path = "results/p11_n12_grid.json"
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
