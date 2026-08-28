"""M1 — formal boundary measurement (Figure 1 data).

Three parts, checkpointed to separate JSONs so a crash loses at most one part:

  M1a  n=10 probes (60k, A2 recipe):
       - tight interpolation points inside the pilot brackets (5 seeds)
       - new row alpha=2.7 (trend interpolation, 3 wd x 5 seeds)
       - right-wall pinning alpha=2.75/2.9 (5 seeds) and 3.0 (3 seeds)
       - NEW TERRITORY: low-alpha high-wd probes (alpha=1.0/1.5, wd 0.6-1.0,
         3 seeds) — the CRUSH-overlap frontier where E_c and 2^-alpha differ
         most (18% vs 50% predicted drop); never scanned in the pilots.
  M1b  n=12 exposure-matched (240k steps = 4x, per P11b protocol), 3 seeds
  M1c  budget curves at three boundary points (120k/240k, 3 seeds) —
       separates kinetic slowing from thermodynamic boundary per point.

Verdict rule frozen (campaign_lib.verdict). ~5.6h total.
"""
import sys, time, json
sys.path.insert(0, "experiments")
from campaign_lib import run_cell, verdict, summary_line

M1A = [  # (alpha, wd, n_seeds)
    # tight points inside pilot brackets
    (2.0, 0.31, 5), (2.1, 0.19, 5), (2.25, 0.125, 5), (2.4, 0.11, 5),
    (2.5, 0.085, 5), (2.6, 0.065, 5),
    # new row alpha=2.7 (trend: ceiling ~0.05)
    (2.7, 0.04, 5), (2.7, 0.05, 5), (2.7, 0.06, 5),
    # right wall
    (2.75, 0.02, 5), (2.75, 0.03, 5), (2.75, 0.04, 5),
    (2.9, 0.03, 5), (2.9, 0.04, 5),
    (3.0, 0.03, 3), (3.0, 0.04, 3),
    # NEW TERRITORY: low-alpha high-wd (CRUSH-overlap frontier)
    (1.0, 0.7, 3), (1.0, 1.0, 3),
    (1.5, 0.6, 3), (1.5, 0.8, 3), (1.5, 1.0, 3),
]
M1B = [  # n=12, exposure-matched 240k
    (2.0, 0.25, 3), (2.0, 0.30, 3),
    (2.25, 0.12, 3), (2.25, 0.15, 3),
    (2.5, 0.06, 3), (2.5, 0.08, 3),
    (2.75, 0.05, 3), (3.0, 0.05, 3),
]
M1C = [  # n=10 budget curves at boundary points: (alpha, wd, n_seeds, steps)
    # NOTE: original 3-tuple form made `steps` land in n_seeds (120k seeds!)
    # — fixed 2026-08-22 after the bug was caught by monitoring. The 9 stray
    # (2.25, 0.125, 60k) runs recorded before the fix double as the B=60k
    # baseline point of that cell, so they are kept, not deleted.
    (2.25, 0.125, 3, 120000), (2.25, 0.125, 3, 240000),
    (2.5, 0.085, 3, 120000), (2.5, 0.085, 3, 240000),
    (2.75, 0.03, 3, 120000), (2.75, 0.03, 3, 240000),
]


def run_part(name, jobs, n, default_steps):
    out_path = f"results/{name}.json"
    try:
        out = json.load(open(out_path))
        print(f"[{name}] resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for alpha, wd, n_seeds, *rest in jobs:
        ms = rest[0] if rest else default_steps
        for s in range(n_seeds):
            if any(o['alpha'] == alpha and o['wd'] == wd and o['seed'] == s
                   and o['max_steps'] == ms for o in out):
                continue                                    # resume-safe
            r = run_cell(n, alpha, wd, s, max_steps=ms)
            print(f"[{name}] {summary_line(r)}", flush=True)
            out.append(dict(verdict=verdict(r), **r))
            json.dump(out, open(out_path, "w"))
    print(f"[{name}] done: {len(out)} runs, {time.time()-t0:.0f}s")


def main():
    run_part("m1_n10_boundary", M1A, n=10, default_steps=60000)
    run_part("m1_n12_boundary", M1B, n=12, default_steps=240000)
    run_part("m1_budget_curves", M1C, n=10, default_steps=60000)


if __name__ == "__main__":
    main()
