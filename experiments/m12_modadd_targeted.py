"""M12 — exposure-matched targeted-injection controls on modular addition
(the auditor's single most important gap for C6).

C6 audit verdict (partial): uniform-injection rescue on modadd (M6) shows
the failure structure transfers, but WITHOUT a targeted-injection control on
this second task, the "genuine coverage mechanism" story is indistinguishable
from "any injection of anything rescues a high-vocabulary softmax under wd"
(a task-specific/coincidental alternative). This directly mirrors M2b on the
counting task (uniform rescues, tail/head do not) — running the SAME
discriminator on modadd is the exposure-matched control the auditor asked for.

Design: alpha=3.0 (the clean modadd failure region, M6b verdict TRAP, A_hi=1.0
constant / A_lo~0.2-0.3), wd=0.3, k=1 (p=1/128, same dose as M2b), inject in
{uniform, tail, head}, 5 seeds each + k=0 baseline (3 seeds), 20k steps
(matches M6's protocol). If uniform >> tail/head here too -> C6 upgraded from
"phenomenon transfers" to "mechanism transfers" (auditor's bar). If uniform
does NOT clearly beat tail/head -> the coincidental-softmax alternative gains
support and C6 must stay at its conservative wording.

~28 runs x ~35s ~= 16min -> results/m12_modadd_targeted.json.
"""
import sys, time, json
sys.path.insert(0, "experiments")
from task_modadd import run_modadd, verdict

JOBS = (
    [dict(p=97, alpha=3.0, wd=0.3, seed=s, k=0, max_steps=20000) for s in range(3)]
    + [dict(p=97, alpha=3.0, wd=0.3, seed=s, k=1, inject=m, max_steps=20000)
       for m in ('uniform', 'tail', 'head') for s in range(5)]
)


def main():
    out_path = "results/m12_modadd_targeted.json"
    try:
        out = json.load(open(out_path))
        print(f"resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for j in JOBS:
        key = (j['alpha'], j['wd'], j['seed'], j.get('k', 0), j.get('inject', 'uniform'),
               j['max_steps'])
        if any((o['alpha'], o['wd'], o['seed'], o.get('k', 0), o.get('inject', 'uniform'),
                o['max_steps']) == key for o in out):
            continue
        ts = time.time()
        r = run_modadd(**j)
        v = verdict(r)
        print(f"a={r['alpha']:4.2f} wd={r['wd']:4.2f} k={r['k']} inj={r.get('inject','-'):<8} "
              f"s{r['seed']} | unif={r['unif_tail']:6.3f} hi={r['hi_tail']:6.3f} "
              f"lo={r['lo_tail']:6.3f} | {v} ({time.time()-ts:.0f}s)", flush=True)
        out.append(dict(verdict=v, **r))
        json.dump(out, open(out_path, "w"))
    print(f"\ndone: {len(out)} runs, {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
