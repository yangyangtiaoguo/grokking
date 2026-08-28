"""P7 — critical slowing down: is alpha=2.5 an ultra-long delay, not a trap?

P4d long-run (alpha=2.5, wd=0.3, T_max=120k) shows A_unif still CLIMBING
(0.07 -> 0.5, all 3 seeds) when the cosine schedule freezes it (lr -> 0 at
120k). So the 'steady-state trap' verdict may actually be 'tau(2.5) is in
(120k, infinity)'. Test: same config with T_max=240k. If it completes,
tau(2.5) in (120k, 240k] and the phase boundary is budget-dependent
(critical slowing down) — the alpha axis is then a DELAY axis, which is a
stronger and more physical story than a static boundary.

Also probes the wd-window non-monotonicity prediction (11.5.4): alpha=2.5 at
wd=0.05 — if the optimum window is non-monotonic, wd=0.05 (below 0.15)
should be WORSE than 0.15 (no driving force to escape memorization).
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p5_rescue import run

def main():
    grid = [
        # (label, alpha, p, wd, max_steps)
        ("slow-240k", 2.5, 0.0, 0.3, 240000),
        ("w005-a25", 2.5, 0.0, 0.05, 60000),
    ]
    seeds = [0, 1, 2]
    n, isc, lr, batch = 10, 10.0, 1e-3, 128
    print(f"P7 slowing-down test: n={n} init={isc} batch={batch} cosine (T_max=max_steps)")
    print(f"{'cell':>9} {'alpha':>5} {'wd':>4} {'steps':>6} | {'seed':>4} {'A_unif':>7} "
          f"{'A_hi':>6} {'A_lo':>6} | verdict")
    out = []
    t0 = time.time()
    for (lab, alpha, p, wd, ms) in grid:
        for s in seeds:
            ts = time.time()
            r = run(n, alpha, p, wd, isc, s, ms, lr, batch)
            grokked = r['unif_tail'] > 0.9
            trapped = (r['hi_tail'] > 0.9) and (r['unif_tail'] < 0.5)
            v = "GROK" if grokked else ("TRAPPED" if trapped else "partial")
            print(f"{lab:>9} {alpha:5.2f} {wd:4.2f} {ms:6d} | {s:4d} {r['unif_tail']:7.3f} "
                  f"{r['hi_tail']:6.3f} {r['lo_tail']:6.3f} | {v}  ({time.time()-ts:.0f}s)")
            out.append(dict(label=lab, grokked=grokked, trapped=trapped, **r))
    json.dump(out, open("results/p7_slowing.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p7_slowing.json")

if __name__ == "__main__":
    main()
