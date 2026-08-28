"""M3 — kinetics (Figure 4 data): tau(alpha) slowing and alpha_c(B).

  M3a  tau transect at wd=0.05, alpha in {2.25, 2.5, 2.6, 2.75}, 240k steps
       (T_max=240k so annealing does not freeze early — P7 protocol), 3 seeds.
       t_grok = first step with sustained A_unif>0.9 (campaign_lib.t_grok).
       Complements P7b (wd=0.3 transect) with a low-wd transect.
  M3b  alpha_c(B) right-shift at wd=0.3: alpha=2.25 at {120k, 240k} and
       alpha=2.5 at 120k, 3 seeds. (alpha=2.5@240k already measured in P7:
       still trapped 2/3+1 partial; alpha<=2 rows covered by P7b/P8.)

~3h total.
"""
import sys, time, json
sys.path.insert(0, "experiments")
from campaign_lib import run_cell, verdict, summary_line, t_grok


def run_part(name, jobs):
    out_path = f"results/{name}.json"
    try:
        out = json.load(open(out_path))
        print(f"[{name}] resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for j in jobs:
        if any(o['alpha'] == j['alpha'] and o['wd'] == j['wd']
               and o['seed'] == j['seed'] and o['max_steps'] == j['max_steps']
               for o in out):
            continue                                            # resume-safe
        r = run_cell(**j)
        tg = t_grok(r)
        print(f"[{name}] {summary_line(r)}  t_grok={tg}", flush=True)
        out.append(dict(verdict=verdict(r), t_grok=tg, **r))
        json.dump(out, open(out_path, "w"))
    print(f"[{name}] done: {len(out)} runs, {time.time()-t0:.0f}s")


def main():
    jobs_a = [dict(n=10, alpha=a, wd=0.05, seed=s, max_steps=240000)
              for a in (2.25, 2.5, 2.6, 2.75) for s in range(3)]
    run_part("m3a_tau", jobs_a)

    jobs_b = [dict(n=10, alpha=2.25, wd=0.3, seed=s, max_steps=ms)
              for ms in (120000, 240000) for s in range(3)]
    jobs_b += [dict(n=10, alpha=2.5, wd=0.3, seed=s, max_steps=120000)
               for s in range(3)]
    run_part("m3b_alphac_budget", jobs_b)


if __name__ == "__main__":
    main()
