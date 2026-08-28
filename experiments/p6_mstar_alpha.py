"""P6 — m*(alpha) curve: does the minimal rescue dose grow with alpha?

Known so far (wd=0.3, n=10, 60k, batch=128, A2 recipe):
  m*(2.0) = 0            (groks with no injection, A_unif=0.918)
  m*(2.5) <= 1/128       (k=1 uniform per batch rescues 3/3)
  alpha=3.0 p=0: head itself fails (A_hi=0.6) — beyond trap, signal starvation
Theory (T4 direction): m* should GROW with alpha (deeper skew needs more
balanced data; each balanced sample is worth more, d0 rises).

Cells:
  a225: alpha=2.25, p in {0, 1/128}          (just inside/at the boundary)
  a275: alpha=2.75, p in {0, 1/128, 1/32, 1/8}
  a300: alpha=3.00, p in {1/8, 1/2}          (large doses; can it be saved at all?)
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p5_rescue import run

def main():
    grid = [
        ("a225", 2.25, [0.0, 1 / 128]),
        ("a275", 2.75, [0.0, 1 / 128, 1 / 32, 1 / 8]),
        ("a300", 3.00, [1 / 8, 1 / 2]),
    ]
    seeds = [0, 1, 2]
    n, wd, isc, lr, batch, ms = 10, 0.3, 10.0, 1e-3, 128, 60000
    print(f"P6 m*(alpha): n={n} wd={wd} batch={batch} steps={ms} cosine, 3 seeds")
    print(f"{'alpha':>5} {'p':>7} | {'seed':>4} {'A_unif':>7} {'A_hi':>6} {'A_lo':>6} | verdict")
    out = []
    t0 = time.time()
    for (lab, alpha, ps) in grid:
        for p in ps:
            for s in seeds:
                r = run(n, alpha, p, wd, isc, s, ms, lr, batch)
                grokked = r['unif_tail'] > 0.9
                trapped = (r['hi_tail'] > 0.9) and (r['unif_tail'] < 0.5)
                v = "GROK" if grokked else ("TRAPPED" if trapped else "partial")
                print(f"{alpha:5.2f} {p:7.4f} | {s:4d} {r['unif_tail']:7.3f} "
                      f"{r['hi_tail']:6.3f} {r['lo_tail']:6.3f} | {v}")
                out.append(dict(label=f"{lab}-p{p:.4f}",
                                grokked=grokked, trapped=trapped, **r))
            rs = [o for o in out if o['alpha'] == alpha and o['p'] == p]
            print(f"      -> alpha={alpha} p={p:.4f}: grok "
                  f"{sum(x['grokked'] for x in rs)}/3, "
                  f"unif={np.mean([x['unif_tail'] for x in rs]):.3f}")
    json.dump(out, open("results/p6_mstar_alpha.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p6_mstar_alpha.json")

if __name__ == "__main__":
    main()
