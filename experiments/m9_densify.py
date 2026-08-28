"""M9 — densify the n=10 boundary at the M10 held-out alphas + verify deep-
trap asymptote at longer budgets (addresses auditor's C1 gap: "240k-step
non-rescue only shows non-rescue within that budget", and C4's need for a
held-out predictive test against M10's frozen predictions).

Part A: measure ceilings at the 8 alphas M10 pre-registered predictions for
        (1.7, 1.9, 2.05, 2.15, 2.35, 2.45, 2.55, 2.65), each with a small wd
        bracket around the M10 E_c-predicted value, 5 seeds/point, 60k steps
        (same budget family as the rest of the n=10 grid, for comparability).
Part B: extend two deep-trap cells (well inside the trapped region, wd >>
        ceiling) to 500k and 1M steps to test true asymptotic non-rescue vs
        merely-slow-rescue. Cells: (alpha=2.5, wd=0.3) [already trapped at
        240k per P4d/P7], (alpha=2.25, wd=0.3) [already trapped at 240k per
        M3b]. 2 seeds each (long runs are expensive; this is a confirmatory
        check, not a new sweep).

IMPORTANT: run Part A AFTER m10_preregister.py has been run and frozen
(results/m10_predictions.json must exist) -- this script does not overwrite
that file, only reads it.

Part A: 8 alphas x 3 wd brackets x 5 seeds = 120 runs x ~95s ~= 3.2h
Part B: 2 cells x 2 seeds x (500k+1M steps ~ 13min+26min) = ~2.6h
Total ~5.8h -> results/m9_densify.json, results/m9_deeptrap.json
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from campaign_lib import run_cell, verdict, summary_line


def run_part(name, jobs):
    out_path = f"results/{name}.json"
    try:
        out = json.load(open(out_path))
        print(f"[{name}] resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for j in jobs:
        key = (j['alpha'], j['wd'], j['seed'], j['max_steps'])
        if any((o['alpha'], o['wd'], o['seed'], o['max_steps']) == key for o in out):
            continue
        r = run_cell(**j)
        print(f"[{name}] {summary_line(r)}", flush=True)
        out.append(dict(verdict=verdict(r), **r))
        json.dump(out, open(out_path, "w"))
    print(f"[{name}] done: {len(out)} runs, {time.time()-t0:.0f}s")


def main():
    preds = json.load(open("results/m10_predictions.json"))
    jobs_a = []
    for a_str, p in preds["predictions"].items():
        a_ = float(a_str)
        center = p["E_c_pred"]
        for wd in (round(center * 0.7, 4), round(center, 4), round(center * 1.3, 4)):
            for s in range(8):
                jobs_a.append(dict(n=10, alpha=a_, wd=wd, seed=s, max_steps=60000))
    run_part("m9_densify", jobs_a)

    jobs_b = []
    for (alpha, wd) in [(2.5, 0.3), (2.25, 0.3)]:
        for ms in (500000, 1000000):
            for s in range(2):
                jobs_b.append(dict(n=10, alpha=alpha, wd=wd, seed=s, max_steps=ms))
    run_part("m9_deeptrap", jobs_b)


if __name__ == "__main__":
    main()
