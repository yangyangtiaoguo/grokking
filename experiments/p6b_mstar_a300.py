"""P6b — fill the gap: m*(3.0) at small doses.

P6 found m* FLAT at <=1/128 for alpha in [2.25, 2.75] — theory predicted
growth. The decisive missing cell: alpha=3.0 at p=1/128 (and 1/32). If 1/128
rescues alpha=3.0 too, then m* is flat-and-tiny across the whole trapped
regime ('one balanced sample per batch suffices, independent of skew') — a
stronger, cleaner claim than growth. If it fails while 1/32 works, m* is a
STEP function somewhere in (2.75, 3.0].

Note alpha=3.0 p=0 fails differently (P4b: A_hi=0.6 — head itself starves),
so rescue here means restoring the full cascade, not just un-trapping.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p5_rescue import run

def main():
    cells = [(3.0, 1 / 128), (3.0, 1 / 32)]
    seeds = [0, 1, 2]
    n, wd, isc, lr, batch, ms = 10, 0.3, 10.0, 1e-3, 128, 60000
    print(f"P6b m*(3.0): n={n} wd={wd} batch={batch} steps={ms} cosine, 3 seeds")
    print(f"{'alpha':>5} {'p':>7} | {'seed':>4} {'A_unif':>7} {'A_hi':>6} {'A_lo':>6} | verdict")
    out = []
    t0 = time.time()
    for (alpha, p) in cells:
        for s in seeds:
            ts = time.time()
            r = run(n, alpha, p, wd, isc, s, ms, lr, batch)
            grokked = r['unif_tail'] > 0.9
            trapped = (r['hi_tail'] > 0.9) and (r['unif_tail'] < 0.5)
            v = "GROK" if grokked else ("TRAPPED" if trapped else "partial")
            print(f"{alpha:5.2f} {p:7.4f} | {s:4d} {r['unif_tail']:7.3f} "
                  f"{r['hi_tail']:6.3f} {r['lo_tail']:6.3f} | {v}  ({time.time()-ts:.0f}s)")
            out.append(dict(label=f"a{alpha}-p{p:.4f}",
                            grokked=grokked, trapped=trapped, **r))
    json.dump(out, open("results/p6b_mstar_a300.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p6b_mstar_a300.json")
    for (alpha, p) in cells:
        rs = [o for o in out if o['alpha'] == alpha and o['p'] == p]
        print(f"alpha={alpha} p={p:.4f}: grok {sum(x['grokked'] for x in rs)}/3, "
              f"unif={np.mean([x['unif_tail'] for x in rs]):.3f}")

if __name__ == "__main__":
    main()
