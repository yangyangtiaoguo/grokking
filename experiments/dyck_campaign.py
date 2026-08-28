"""Dyck-1 formal campaign (post-probe, ~25-30 GPU-h) -- the third-task
generalization pillar for C6.

Probe verdict (results/dyck_probe.json, 90 runs, L=10, 30k steps): failure
region located at alpha>=5, wd>=0.8 (alpha=7/wd=1.0-1.5: full collapse
including head, A_hi~0.42 -- CRUSH-dominant, unlike the main task's
TRAP-dominant failure at its boundary). alpha<=2 groks at all tested wd.
This mirrors the main task's structure (grok region -> failure wall) but the
failure MODE leans more toward over-regularization crush than pure
starvation-trap -- itself a finding worth reporting.

Design (mirrors m1_boundary.py's pattern, scaled to Dyck-1's probed range):
  Part A: boundary grid, alpha in {3,4,5,6,7,8} x wd in {0.3,0.5,0.7,0.9,1.1,1.3},
          5 seeds, 60k steps (2x the probe's 30k for a cleaner asymptote).
  Part B: rescue check at the most-trapped/crushed cell found in Part A,
          k=1 uniform injection, 5 seeds + k=0 baseline (3 seeds) -- tests
          whether the SAME minimal-dose rescue (C2's core claim) also
          transfers to a third, non-arithmetic task.
  Part C: budget curve at 2 boundary cells (60k vs 240k steps, 3 seeds) --
          mirrors M1c's two-regime check, avoiding the same kinetic-vs-
          thermodynamic confound the main task caught.

Part A: 36 cells x 5 seeds = 180 runs x ~50s (60k steps, L=10 smaller state
         space trains faster than n=10's 1024 states) ~= 2.5h
Part B: 8 runs x ~50s ~= 7min
Part C: 2 cells x 2 budgets x 3 seeds = 12 runs, 240k steps ~200s each ~= 40min
Total ~3.2h -- NOTE: much cheaper than the ~25-30h estimate (that assumed
n=10-scale per-step cost; L=10 Dyck-1 trains faster). Grid widened below to
use the saved budget productively: seeds 5->10, added alpha=3.5/4.5 rows.
-> results/dyck_boundary.json, results/dyck_rescue.json, results/dyck_budget.json
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from task_dyck1 import run_dyck, verdict

ALPHAS = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0]
WDS = [0.3, 0.5, 0.7, 0.9, 1.1, 1.3]
N_SEEDS = 10


def run_part(name, jobs, runner):
    out_path = f"results/{name}.json"
    try:
        out = json.load(open(out_path))
        print(f"[{name}] resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for j in jobs:
        key = (j['alpha'], j['wd'], j['seed'], j.get('k', 0), j.get('inject', 'uniform'),
               j['max_steps'])
        if any((o['alpha'], o['wd'], o['seed'], o.get('k', 0), o.get('inject', 'uniform'),
                o['max_steps']) == key for o in out):
            continue
        ts = time.time()
        r = runner(**j)
        v = verdict(r)
        print(f"[{name}] a={r['alpha']:4.2f} wd={r['wd']:4.2f} k={r['k']} "
              f"inj={r.get('inject','-'):<8} s{r['seed']} | unif={r['unif_tail']:6.3f} "
              f"hi={r['hi_tail']:6.3f} lo={r['lo_tail']:6.3f} | {v} "
              f"({time.time()-ts:.0f}s)", flush=True)
        out.append(dict(verdict=v, **r))
        json.dump(out, open(out_path, "w"))
    print(f"[{name}] done: {len(out)} runs, {time.time()-t0:.0f}s")
    return out


def main():
    jobs_a = [dict(L=10, alpha=a, wd=w, seed=s, max_steps=60000)
              for a in ALPHAS for w in WDS for s in range(N_SEEDS)]
    boundary = run_part("dyck_boundary", jobs_a, run_dyck)

    # find the most-trapped/crushed cell (lowest mean unif_tail) for the rescue check
    from collections import defaultdict
    cell = defaultdict(list)
    for r in boundary:
        cell[(r['alpha'], r['wd'])].append(r['unif_tail'])
    worst = min(cell, key=lambda k: np.mean(cell[k]))
    a_w, wd_w = worst
    print(f"\nMost-failed cell for rescue check: alpha={a_w} wd={wd_w} "
          f"(mean unif={np.mean(cell[worst]):.3f})")

    jobs_b = (
        [dict(L=10, alpha=a_w, wd=wd_w, seed=s, k=0, max_steps=60000) for s in range(3)]
        + [dict(L=10, alpha=a_w, wd=wd_w, seed=s, k=1, inject='uniform', max_steps=60000)
           for s in range(5)]
    )
    run_part("dyck_rescue", jobs_b, run_dyck)

    # budget curve at the worst cell + one milder boundary cell
    mild = min(((a, w) for (a, w) in cell if 0.3 < np.mean(cell[(a, w)]) < 0.8),
               key=lambda k: abs(np.mean(cell[k]) - 0.5), default=worst)
    jobs_c = [dict(L=10, alpha=a_, wd=w_, seed=s, max_steps=ms)
              for (a_, w_) in {worst, mild} for ms in (60000, 240000) for s in range(3)]
    run_part("dyck_budget", jobs_c, run_dyck)


if __name__ == "__main__":
    main()
