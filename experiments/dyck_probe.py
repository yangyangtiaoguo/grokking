"""Dyck-1 existence probe (M11c precursor) -- quick grid to locate the
failure region before committing to a full campaign, mirroring the lesson
from modadd (M6 v1 bug): a 1-2 point manual probe gave PARTIAL results
non-monotonically (wd=0.5/alpha=6 GROK, wd=0.5/alpha=4 PARTIAL) -- do not
draw conclusions from sparse manual probing, run the grid.

L=10 (16796 paths), wd in {0.3, 0.5, 0.8, 1.0, 1.5}, alpha in {0, 2, 4, 5, 6,
7}, 30k steps (shorter than the main task's 60k for this probe -- extend if
promising), 3 seeds.

~90 runs x ~50s (30k steps) ~= 75min -> results/dyck_probe.json.
"""
import sys, time, json
sys.path.insert(0, "experiments")
from task_dyck1 import run_dyck, verdict

WDS = [0.3, 0.5, 0.8, 1.0, 1.5]
ALPHAS = [0.0, 2.0, 4.0, 5.0, 6.0, 7.0]


def main():
    out_path = "results/dyck_probe.json"
    try:
        out = json.load(open(out_path))
        print(f"resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for alpha in ALPHAS:
        for wd in WDS:
            for s in range(3):
                if any(o['alpha'] == alpha and o['wd'] == wd and o['seed'] == s
                       for o in out):
                    continue
                ts = time.time()
                r = run_dyck(L=10, alpha=alpha, wd=wd, seed=s, max_steps=30000)
                v = verdict(r)
                print(f"a={alpha:4.2f} wd={wd:4.2f} s{s} | unif={r['unif_tail']:6.3f} "
                      f"hi={r['hi_tail']:6.3f} lo={r['lo_tail']:6.3f} | {v} "
                      f"({time.time()-ts:.0f}s)", flush=True)
                out.append(dict(verdict=v, **r))
            json.dump(out, open(out_path, "w"))
    print(f"\ndone: {len(out)} runs, {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
