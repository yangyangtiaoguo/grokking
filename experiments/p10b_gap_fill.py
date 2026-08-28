"""P10b — fill the gaps P10 left unresolved (n=10, A2 recipe).

P10 refined ceilings resolved only 4 alphas; the interpolation rows 2.4 / 2.6
were mis-scanned (all tested wds grok -> ceiling unresolved above range), and
the steep 2.0->2.1 drop (0.305 -> 0.167) plus the messy 2.75/2.9 rows need
pinning. This scan targets exactly those crossings:

  2.0:  0.32                     (crossing bracketed 0.30-0.35)
  2.1:  0.17, 0.18               (crossing 0.15-0.20, steep drop from 2.0)
  2.4:  0.09, 0.10, 0.12, 0.14   (row grokked everywhere <= 0.08)
  2.6:  0.07, 0.08, 0.09, 0.10   (row grokked everywhere <= 0.06)
  2.75: 0.02, 0.025, 0.035       (0.03 borderline: 0.892 mean, 3/5)
  2.9:  0.035, 0.045             (crossing 0.04-0.05, 0.03-0.04 non-monotone)

48 runs x ~95s ~= 1.3h -> results/p10b_gap_fill.json (merged with P8+P10 in
analysis).
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p5_rescue import run

GRID = {
    2.0:  {0.32: [0, 1, 2]},
    2.1:  {0.17: [0, 1, 2], 0.18: [0, 1, 2]},
    2.4:  {0.09: [0, 1, 2], 0.10: [0, 1, 2], 0.12: [0, 1, 2], 0.14: [0, 1, 2]},
    2.6:  {0.07: [0, 1, 2], 0.08: [0, 1, 2], 0.09: [0, 1, 2], 0.10: [0, 1, 2]},
    2.75: {0.02: [0, 1, 2], 0.025: [0, 1, 2], 0.035: [0, 1, 2]},
    2.9:  {0.035: [0, 1, 2], 0.045: [0, 1, 2]},
}


def verdict(r):
    if r['unif_tail'] > 0.9:
        return "GROK"
    if r['hi_tail'] > 0.9 and r['unif_tail'] < 0.5:
        return "TRAP"
    if r['hi_tail'] < 0.9 and r['unif_tail'] < 0.5:
        return "CRUSH"
    return "PARTIAL"


def main():
    n, isc, lr, batch, ms = 10, 10.0, 1e-3, 128, 60000
    n_runs = sum(len(sv) for wds in GRID.values() for sv in wds.values())
    print(f"P10b gap fill: n={n} runs={n_runs} (~{n_runs*95/3600:.1f}h)\n")
    out_path = "results/p10b_gap_fill.json"
    out = []
    t0 = time.time()
    for alpha in sorted(GRID):
        for wd in sorted(GRID[alpha]):
            for s in GRID[alpha][wd]:
                ts = time.time()
                r = run(n, alpha, 0.0, wd, isc, s, ms, lr, batch)
                v = verdict(r)
                print(f"a={alpha:4.2f} wd={wd:4.3f} | s{s} "
                      f"unif={r['unif_tail']:6.3f} hi={r['hi_tail']:6.3f} "
                      f"lo={r['lo_tail']:6.3f} | {v} ({time.time()-ts:.0f}s)", flush=True)
                out.append(dict(verdict=v, **r))
            json.dump(out, open(out_path, "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
