"""P4c — does the LAMBDA axis rescue the trapped state? (phase diagram 2nd axis)

P4b: trapped at (alpha=2.5, wd=0.3) — A_hi~0.9, A_lo~0.05. Theory (H3):
lambda_c(alpha) rises with alpha, so escape needs LARGER lambda. The usable
lambda window is (0.3, 1.0): wd=1.0 numerically crushes (P4 hi2, v8B).

Cells (3 seeds each, A2 recipe):
  a25-w50 : alpha=2.5, wd=0.5   <- if GROK: lambda lever works, lambda_c(2.5) in (0.3,0.5]
  a25-w70 : alpha=2.5, wd=0.7   <- bracket the boundary
  a20-w50 : alpha=2.0, wd=0.5   <- consistency: alpha=2 should stay grokked
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p4_freq_phase import run

def main():
    grid = [
        ("a25-w50", 2.5, 0.5),
        ("a25-w70", 2.5, 0.7),
        ("a20-w50", 2.0, 0.5),
    ]
    seeds = [0, 1, 2]
    n, isc, lr, batch, ms = 10, 10.0, 1e-3, 128, 60000
    print(f"P4c lambda rescue: n={n} init={isc} batch={batch} steps={ms} cosine")
    print(f"{'cell':>8} {'alpha':>5} {'wd':>4} | {'seed':>4} {'A_unif':>7} {'A_hi':>6} "
          f"{'A_lo':>6} {'thF':>5} | verdict")
    out = []
    t0 = time.time()
    for (lab, alpha, wd) in grid:
        for s in seeds:
            ts = time.time()
            r = run(n, alpha, wd, isc, s, ms, lr, batch)
            grokked = r['unif_tail'] > 0.9
            trapped = (r['hi_tail'] > 0.9) and (r['unif_tail'] < 0.5)
            v = "GROK" if grokked else ("TRAPPED" if trapped else "partial")
            print(f"{lab:>8} {alpha:5.1f} {wd:4.1f} | {s:4d} {r['unif_tail']:7.3f} "
                  f"{r['hi_tail']:6.3f} {r['lo_tail']:6.3f} {r['thF']:5.1f} | {v}"
                  f"  ({time.time()-ts:.0f}s)")
            out.append(dict(label=lab, grokked=grokked, trapped=trapped, **r))
    json.dump(out, open("results/p4c_lambda.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p4c_lambda.json")
    for lab in ["a25-w50", "a25-w70", "a20-w50"]:
        rs = [o for o in out if o['label'] == lab]
        print(f"[{lab}]: grok {sum(r['grokked'] for r in rs)}/3, "
              f"unif={np.mean([r['unif_tail'] for r in rs]):.3f}, "
              f"hi={np.mean([r['hi_tail'] for r in rs]):.3f}, "
              f"lo={np.mean([r['lo_tail'] for r in rs]):.3f}")

if __name__ == "__main__":
    main()
