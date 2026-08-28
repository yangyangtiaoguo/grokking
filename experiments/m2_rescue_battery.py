"""M2 — rescue battery (Figure 3 data): mechanism discriminators for m*.

  M2a  k-vs-p discriminator (NEW, mechanism core):
       batch in {64, 128, 256} with TOTAL SAMPLES held fixed at 7.68M
       (steps inversely proportional to batch), k in {0, 1}, alpha=2.5, wd=0.3,
       5 seeds. If k=1 rescues at EVERY batch size -> the threshold is a
       per-batch coverage floor (bottleneck-coverage mechanism). If only a
       constant fraction p rescues -> mass mechanism. Either answer is a
       finding; this is the cleanest discriminator between the two stories.
  M2b  targeted rescue: alpha in {2.5, 3.0} (trap mode / starvation mode),
       inject in {uniform, tail, head} at k=1, 5 seeds (+ k=0 baselines,
       3 seeds). Prediction (per-state coverage story, doc section 10.4-3):
       tail rescues at lower dose than uniform; head does NOT rescue.
  M2c  m* vs budget: alpha=2.5, B in {15k, 30k}, k in {0, 1}, 3 seeds.

All n=10, wd=0.3, A2 recipe. ~2h total.
"""
import sys, time, json
sys.path.insert(0, "experiments")
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
        key = lambda o: (o['alpha'], o['wd'], o['seed'], o.get('k', 0),
                         o.get('inject', 'uniform'), o.get('batch', 128),
                         o['max_steps'])
        if any(key(o) == key(dict(alpha=j['alpha'], wd=j['wd'], seed=j['seed'],
                                  k=j.get('k', 0), inject=j.get('inject', 'uniform'),
                                  batch=j.get('batch', 128),
                                  max_steps=j['max_steps'])) for o in out):
            continue                                            # resume-safe
        r = run_cell(**j)
        print(f"[{name}] {summary_line(r)}", flush=True)
        out.append(dict(verdict=verdict(r), **r))
        json.dump(out, open(out_path, "w"))
    print(f"[{name}] done: {len(out)} runs, {time.time()-t0:.0f}s")


def main():
    # M2a: k-vs-p, total samples fixed at 60k*128 = 7.68M
    jobs_a = []
    for batch, steps in [(64, 120000), (128, 60000), (256, 30000)]:
        for k in (0, 1):
            for s in range(5):
                jobs_a.append(dict(n=10, alpha=2.5, wd=0.3, seed=s, k=k,
                                   batch=batch, max_steps=steps))
    run_part("m2a_k_vs_p", jobs_a)

    # M2b: targeted rescue (uniform already covered by P5/P6 pilots at k=1,
    # but re-run here at 5 seeds for error bars; head = negative control)
    jobs_b = []
    for alpha in (2.5, 3.0):
        for mode in ('uniform', 'tail', 'head'):
            for s in range(5):
                jobs_b.append(dict(n=10, alpha=alpha, wd=0.3, seed=s, k=1,
                                   inject=mode, max_steps=60000))
        for s in range(3):
            jobs_b.append(dict(n=10, alpha=alpha, wd=0.3, seed=s, k=0,
                               max_steps=60000))
    run_part("m2b_targeted", jobs_b)

    # M2c: m* vs budget
    jobs_c = []
    for ms in (15000, 30000):
        for k in (0, 1):
            for s in range(3):
                jobs_c.append(dict(n=10, alpha=2.5, wd=0.3, seed=s, k=k,
                                   max_steps=ms))
    run_part("m2c_mstar_budget", jobs_c)


if __name__ == "__main__":
    main()
