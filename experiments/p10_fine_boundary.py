"""P10 — fine scan of the wd-ceiling(alpha) boundary (n=10, A2 recipe).

P9 verdict (2026-08-22): the P8 boundary shape matched NO pre-registered
single-scale law cleanly (best: H_tail10, max rel err 0.68; E_c/exp2 excluded).
But that fit rested on 3-4 resolved ceiling points, a coarse wd grid
{0.05,0.1,0.15,0.2,0.3,0.5}, 3 seeds, and a non-monotonic alpha=2 row.
This scan removes those excuses before any claim about boundary SHAPE:

  (a) boundary refinement: fine wd steps around each P8 crossing, 5 seeds;
  (b) alpha interpolation: new rows alpha in {2.1, 2.4, 2.6, 2.9} so the
      ceiling(alpha) curve has ~8 points instead of 4;
  (c) right-boundary probe: alpha=3.0 at very low wd (0.02-0.04) — does ANY
      wd rescue starvation, or is the right boundary effectively vertical?
  (d) alpha=2 row repair: extra seeds (3,4) at the dipping cells 0.15/0.2.

Verdicts identical to P8. ~142 runs x ~95s ~= 3.7h -> results/p10_fine_boundary.json.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from p5_rescue import run

# alpha -> {wd: seeds}
GRID = {
    # (a) boundary refinement, 5 seeds
    2.0:  {0.35: [0, 1, 2, 3, 4], 0.4: [0, 1, 2, 3, 4], 0.45: [0, 1, 2, 3, 4]},
    2.25: {0.11: [0, 1, 2, 3, 4], 0.12: [0, 1, 2, 3, 4],
           0.13: [0, 1, 2, 3, 4], 0.14: [0, 1, 2, 3, 4]},
    2.5:  {0.06: [0, 1, 2, 3, 4], 0.07: [0, 1, 2, 3, 4],
           0.08: [0, 1, 2, 3, 4], 0.09: [0, 1, 2, 3, 4]},
    2.75: {0.03: [0, 1, 2, 3, 4], 0.04: [0, 1, 2, 3, 4],
           0.06: [0, 1, 2, 3, 4], 0.07: [0, 1, 2, 3, 4]},
    # (b) alpha interpolation rows (coarse wd, 3 seeds)
    2.1:  {0.05: [0, 1, 2], 0.1: [0, 1, 2], 0.15: [0, 1, 2], 0.2: [0, 1, 2]},
    2.4:  {0.05: [0, 1, 2], 0.06: [0, 1, 2], 0.07: [0, 1, 2], 0.08: [0, 1, 2]},
    2.6:  {0.03: [0, 1, 2], 0.04: [0, 1, 2], 0.05: [0, 1, 2], 0.06: [0, 1, 2]},
    2.9:  {0.02: [0, 1, 2], 0.03: [0, 1, 2], 0.04: [0, 1, 2], 0.05: [0, 1, 2]},
    # (c) right-boundary probe at very low wd
    3.0:  {0.02: [0, 1, 2], 0.03: [0, 1, 2], 0.04: [0, 1, 2]},
    # (d) alpha=2 row repair: extra seeds 3,4 at the dipping cells
    #     (0.15, 0.2 already have seeds 0-2 in P8)
    2.0:  {0.35: [0, 1, 2, 3, 4], 0.4: [0, 1, 2, 3, 4], 0.45: [0, 1, 2, 3, 4],
           0.15: [3, 4], 0.2: [3, 4]},
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
    print(f"P10 fine boundary scan: n={n} init={isc} batch={batch} steps={ms} cosine")
    n_runs = sum(len(sv) for sv in GRID.values())
    print(f"{n_runs} runs (~{n_runs * 95 / 3600:.1f}h)\n")
    out_path = "results/p10_fine_boundary.json"
    out = []
    t0 = time.time()
    for alpha in sorted(GRID):
        for wd in sorted(GRID[alpha]):
            for s in GRID[alpha][wd]:
                ts = time.time()
                r = run(n, alpha, 0.0, wd, isc, s, ms, lr, batch)
                v = verdict(r)
                print(f"a={alpha:4.2f} wd={wd:4.2f} | s{s} "
                      f"unif={r['unif_tail']:6.3f} hi={r['hi_tail']:6.3f} "
                      f"lo={r['lo_tail']:6.3f} | {v} ({time.time()-ts:.0f}s)", flush=True)
                out.append(dict(verdict=v, **r))
            json.dump(out, open(out_path, "w"))   # checkpoint after every cell
    # summary: mean A_unif per cell
    print("\n=== mean A_unif per cell ===")
    for alpha in sorted(GRID):
        cells = []
        for wd in sorted(GRID[alpha]):
            rs = [o for o in out if o['alpha'] == alpha and o['wd'] == wd]
            g = sum(1 for x in rs if x['verdict'] == 'GROK')
            m = np.mean([x['unif_tail'] for x in rs])
            cells.append(f"wd={wd:.2f}: {m:.3f} ({g}/{len(rs)})")
        print(f"a={alpha:4.2f}  " + " | ".join(cells))
    print(f"\nelapsed {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
