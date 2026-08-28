"""M6b — second-task existence check v2 (modular addition, p=97), corrected
skew protocol.

v1 verdict (task_modadd.py, combined-index skew): BROKEN — Zipf on x=a*p+b
concentrates 99.95% of mass on a=0 at alpha=2.5, collapsing the task to a
near-single-operand problem (CRUSH everywhere, uninformative). Fixed:
skew now acts on operand `a` only, uniform over `b` (mass(a=0)=0.746 at
alpha=2.5 — comparable concentration to the counting task's tail, not total
collapse). Quick single-seed probe after the fix: alpha=2.5 wd=0.05 ->
PARTIAL(0.588), wd=0.3 -> GROK(0.986) — note this is the OPPOSITE wd
direction from the main counting task at the same alpha; needs a proper
wd sweep to see if there's a boundary at all, and where.

Grid: alpha in {0, 1, 2, 2.5, 3} x wd in {0.05, 0.1, 0.3, 0.5, 1.0}, 3 seeds,
20k steps (p=97 grid trains ~4x faster than n=10 counting). Plus rescue
check (k=1 uniform injection) at the most-trapped cell found.

~75 runs x ~32s ~= 40min.
"""
import sys, time, json
sys.path.insert(0, "experiments")
from task_modadd import run_modadd, verdict

ALPHAS = [0.0, 1.0, 2.0, 2.5, 3.0]
WDS = [0.05, 0.1, 0.3, 0.5, 1.0]


def main():
    out_path = "results/m6b_modadd_grid.json"
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
                       and o.get('k', 0) == 0 for o in out):
                    continue
                ts = time.time()
                r = run_modadd(p=97, alpha=alpha, wd=wd, seed=s, max_steps=20000)
                v = verdict(r)
                print(f"a={alpha:4.2f} wd={wd:4.2f} s{s} | unif={r['unif_tail']:6.3f} "
                      f"hi={r['hi_tail']:6.3f} lo={r['lo_tail']:6.3f} | {v} "
                      f"({time.time()-ts:.0f}s)", flush=True)
                out.append(dict(verdict=v, **r))
            json.dump(out, open(out_path, "w"))
    print(f"\ndone: {len(out)} runs, {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
