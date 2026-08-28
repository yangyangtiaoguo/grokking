"""M5 — robustness (should-run) + M2a confound follow-ups.

Robustness of the phase-diagram STRUCTURE (not exact numbers) to optimizer /
model knobs, per EXPERIMENT_PLAN.md M5:
  (a) width d in {32, 128} at the alpha=2.5 boundary cells
  (b) lr in {5e-4, 2e-3} at two boundary cells
  (c) batch=512 (Zhao direction) at the trap/rescue cell, total samples fixed
M2a confound follow-ups (threshold: p vs total injected count):
  (d) batch=256, k=2   -> p=1/128, injected=60k  (if GROK: p or count matters)
  (e) batch=128, k=1, steps=30k -> p=1/128, injected=30k
      (d) GROK + (e) fail -> count matters at fixed p; (d)+(e) GROK -> p matters
~2h -> results/m5_robust.json, results/m2a2_confound.json
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
        key = (j['alpha'], j['wd'], j['seed'], j.get('k', 0),
               j.get('inject', 'uniform'), j.get('batch', 128),
               j['max_steps'], j.get('d', 64), j.get('lr', 1e-3))
        if any((o['alpha'], o['wd'], o['seed'], o.get('k', 0),
                o.get('inject', 'uniform'), o.get('batch', 128),
                o['max_steps'], o.get('d', 64), o.get('lr', 1e-3)) == key
               for o in out):
            continue                                            # resume-safe
        r = run_cell(**j)
        print(f"[{name}] {summary_line(r)} d={j.get('d', 64)} lr={j.get('lr', 1e-3)}", flush=True)
        out.append(dict(verdict=verdict(r), **r))
        json.dump(out, open(out_path, "w"))
    print(f"[{name}] done: {len(out)} runs, {time.time()-t0:.0f}s")


def main():
    # (a) width — d=32 and d=128 at alpha=2.5 boundary cells
    jobs = [dict(n=10, alpha=2.5, wd=w, seed=s, d=d, max_steps=60000)
            for d in (32, 128) for w in (0.05, 0.1) for s in range(3)]
    # (b) lr sensitivity at two boundary cells (d=64)
    jobs += [dict(n=10, alpha=a, wd=w, seed=s, lr=lr, max_steps=60000)
             for (a, w) in ((2.5, 0.085), (2.25, 0.125))
             for lr in (5e-4, 2e-3) for s in range(3)]
    # (c) batch=512 (Zhao direction), total samples fixed at 7.68M -> 15k steps
    jobs += [dict(n=10, alpha=2.5, wd=0.3, seed=s, k=k, batch=512, max_steps=15000)
             for k in (0, 1) for s in range(3)]
    run_part("m5_robust", jobs)

    # M2a confound follow-ups (5 seeds)
    jobs2 = [dict(n=10, alpha=2.5, wd=0.3, seed=s, k=2, batch=256, max_steps=30000)
             for s in range(5)]
    jobs2 += [dict(n=10, alpha=2.5, wd=0.3, seed=s, k=1, batch=128, max_steps=30000)
              for s in range(5)]
    run_part("m2a2_confound", jobs2)


if __name__ == "__main__":
    main()
