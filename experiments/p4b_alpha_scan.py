"""P4b — alpha-axis scan to locate the measured critical alpha.

P4 verdict: at wd=0.3, alpha=2 still groks (A_unif=0.918) but the tail already
lags (A_lo=0.882 vs A_hi=0.998). The critical alpha is ABOVE 2. wd=1.0 is a
numerical crush, not a transition. So: finer alpha scan at wd=0.3.

Reuses run() from p4_freq_phase (same protocol, same metrics).
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p4_freq_phase import run

def main():
    alphas = [2.5, 3.0, 4.0]
    seeds = [0, 1, 2]
    n, wd, isc, lr, batch, ms = 10, 0.3, 10.0, 1e-3, 128, 60000
    print(f"P4b alpha scan: n={n} wd={wd} init={isc} batch={batch} steps={ms} cosine")
    print(f"{'alpha':>5} {'seed':>4} {'A_unif':>7} {'A_hi':>6} {'A_lo':>6} {'thF':>5} | verdict")
    out = []
    t0 = time.time()
    for alpha in alphas:
        for s in seeds:
            ts = time.time()
            r = run(n, alpha, wd, isc, s, ms, lr, batch)
            grokked = r['unif_tail'] > 0.9
            trapped = (r['hi_tail'] > 0.9) and (r['unif_tail'] < 0.5)
            v = "GROK" if grokked else ("TRAPPED" if trapped else "partial")
            print(f"{alpha:5.1f} {s:4d} {r['unif_tail']:7.3f} {r['hi_tail']:6.3f} "
                  f"{r['lo_tail']:6.3f} {r['thF']:5.1f} | {v}  ({time.time()-ts:.0f}s)")
            out.append(dict(label=f"a{alpha}", grokked=grokked, trapped=trapped, **r))
    json.dump(out, open("results/p4b_alpha_scan.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p4b_alpha_scan.json")
    for alpha in alphas:
        rs = [o for o in out if o['alpha'] == alpha]
        print(f"alpha={alpha}: grok {sum(r['grokked'] for r in rs)}/3, "
              f"unif={np.mean([r['unif_tail'] for r in rs]):.3f}, "
              f"hi={np.mean([r['hi_tail'] for r in rs]):.3f}, "
              f"lo={np.mean([r['lo_tail'] for r in rs]):.3f}")

if __name__ == "__main__":
    main()
