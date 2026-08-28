"""P4d — resolve the lambda-direction anomaly from P4c.

P4c: at alpha=2.5, wd 0.3->0.5->0.7 made things WORSE (A_hi drops), and
wd=0.5 even dragged alpha=2.0 from grok (0.918) to partial (0.639).
H3 predicts larger lambda RESCUES the trapped state — opposite of observed.

Two candidate explanations to separate:
  (i)  lambda window is BELOW 0.3: test alpha=2.5 at wd=0.15 (and alpha=2.0
       at wd=0.15 as consistency). If wd=0.15 rescues -> the boundary
       lambda_c(alpha) DECREASES with alpha (theory sign flipped, but a
       boundary still exists -> C1 reframed, not dead).
  (ii) it's not a steady-state boundary but a TIME issue: 60k steps may be
       inside a longer grokking delay. Test alpha=2.5, wd=0.3, 120k steps.
       If it eventually groks -> "trapped" was "delayed", tau(alpha) is the
       right observable, and the phase diagram becomes a delay diagram.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p4_freq_phase import run

def main():
    grid = [
        # (label, alpha, wd, max_steps)
        ("w15-a25", 2.5, 0.15, 60000),
        ("w15-a20", 2.0, 0.15, 60000),
        ("long-a25", 2.5, 0.3, 120000),
    ]
    seeds = [0, 1, 2]
    n, isc, lr, batch = 10, 10.0, 1e-3, 128
    print(f"P4d lambda-direction resolution: n={n} init={isc} batch={batch} cosine")
    print(f"{'cell':>9} {'alpha':>5} {'wd':>4} {'steps':>6} | {'seed':>4} {'A_unif':>7} "
          f"{'A_hi':>6} {'A_lo':>6} {'thF':>5} | verdict")
    out = []
    t0 = time.time()
    for (lab, alpha, wd, ms) in grid:
        for s in seeds:
            ts = time.time()
            r = run(n, alpha, wd, isc, s, ms, lr, batch)
            grokked = r['unif_tail'] > 0.9
            trapped = (r['hi_tail'] > 0.9) and (r['unif_tail'] < 0.5)
            v = "GROK" if grokked else ("TRAPPED" if trapped else "partial")
            print(f"{lab:>9} {alpha:5.1f} {wd:4.2f} {ms:6d} | {s:4d} {r['unif_tail']:7.3f} "
                  f"{r['hi_tail']:6.3f} {r['lo_tail']:6.3f} {r['thF']:5.1f} | {v}"
                  f"  ({time.time()-ts:.0f}s)")
            out.append(dict(label=lab, grokked=grokked, trapped=trapped, **r))
    json.dump(out, open("results/p4d_lambda_dir.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p4d_lambda_dir.json")
    for lab in ["w15-a25", "w15-a20", "long-a25"]:
        rs = [o for o in out if o['label'] == lab]
        print(f"[{lab}]: grok {sum(r['grokked'] for r in rs)}/3, "
              f"unif={np.mean([r['unif_tail'] for r in rs]):.3f}, "
              f"hi={np.mean([r['hi_tail'] for r in rs]):.3f}, "
              f"lo={np.mean([r['lo_tail'] for r in rs]):.3f}")

if __name__ == "__main__":
    main()
