"""M6 — second-task existence check (modular addition, p=97).

Reduced scope per the campaign decision (EXPERIMENT_RESULTS.md): NOT a full
diagram, just a 2x2 existence check answering the reviewer question "is this
counting-task specific?" Same frequency-skew protocol as the main task
(P1v2 verdict: subset-selection has no skew effect, must use frequency
weighting), same A_unif/A_hi/A_lo metrics and verdict rule.

Grid: alpha in {0, 2.5} x wd in {0.05, 0.3}, 3 seeds. Prediction: alpha=0
grok at both wd; alpha=2.5 grok at wd=0.05, trap/partial at wd=0.3 (mirrors
the main task's boundary direction). Plus one rescue check at the trapped
cell (k=1 uniform injection) to test m*-transfer.

~14 runs x ~40s (p=97 grid is much smaller than n=10's 1024 states) -> quick.
"""
import sys, time, json
sys.path.insert(0, "experiments")
from task_modadd import run_modadd, verdict

JOBS = [
    dict(p=97, alpha=0.0, wd=0.05, seed=s, max_steps=20000) for s in range(3)
] + [
    dict(p=97, alpha=0.0, wd=0.3, seed=s, max_steps=20000) for s in range(3)
] + [
    dict(p=97, alpha=2.5, wd=0.05, seed=s, max_steps=20000) for s in range(3)
] + [
    dict(p=97, alpha=2.5, wd=0.3, seed=s, max_steps=20000) for s in range(3)
] + [
    dict(p=97, alpha=2.5, wd=0.3, seed=s, k=1, max_steps=20000) for s in range(3)  # rescue check
]


def main():
    out_path = "results/m6_modadd_existence.json"
    try:
        out = json.load(open(out_path))
        print(f"resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for j in JOBS:
        key = (j['alpha'], j['wd'], j['seed'], j.get('k', 0), j['max_steps'])
        if any((o['alpha'], o['wd'], o['seed'], o.get('k', 0), o['max_steps']) == key
               for o in out):
            continue
        ts = time.time()
        r = run_modadd(**j)
        v = verdict(r)
        print(f"a={r['alpha']:4.2f} wd={r['wd']:4.2f} k={r['k']} s{r['seed']} | "
              f"unif={r['unif_tail']:6.3f} hi={r['hi_tail']:6.3f} lo={r['lo_tail']:6.3f} "
              f"| {v} ({time.time()-ts:.0f}s)", flush=True)
        out.append(dict(verdict=v, **r))
        json.dump(out, open(out_path, "w"))
    print(f"\ndone: {len(out)} runs, {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
