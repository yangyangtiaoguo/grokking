"""M7 — densified tau(alpha) transect with censoring-aware analysis
(addresses the auditor's rejection of C3: "3 seeds + high variance +
unexplained non-monotone point insufficient for divergence/critical slowing
down").

Design per auditor's suggestion: 8-10 seeds, denser distance-to-boundary
sampling, explicit censoring rule (a run that never crosses A_unif>0.9 by
max_steps is RIGHT-CENSORED at max_steps, not treated as tau=infinity or
dropped — this matters for the survival-style analysis in the companion
m7_analysis.py).

Two wd transects (matches existing pilot data for continuity):
  wd=0.05: alpha in {2.0, 2.2, 2.4, 2.5, 2.6, 2.7, 2.75} (denser than M3a's
           {2.25,2.5,2.6,2.75})
  wd=0.3:  alpha in {1.5, 1.75, 2.0, 2.1, 2.2, 2.25} (denser than P7b's
           {0,1,2,2.5})
8 seeds each cell, 240k steps (T_max=240k, cosine not frozen early).

~13*8=104 runs x ~95s (240k steps ~ 4x60k so ~380s each)... wait: 240k steps
at ~1.6ms/step (60k~=95s) -> 240k~=380s. 104 runs x 380s ~= 11h.
-> results/m7_tau_dense.json.
"""
import sys, time, json
sys.path.insert(0, "experiments")
from campaign_lib import run_cell, verdict, t_grok, summary_line

CELLS = (
    [(a, 0.05) for a in (2.0, 2.2, 2.4, 2.5, 2.6, 2.7, 2.75)]
    + [(a, 0.3) for a in (1.5, 1.75, 2.0, 2.1, 2.2, 2.25)]
)
N_SEEDS = 15


def main():
    out_path = "results/m7_tau_dense.json"
    try:
        out = json.load(open(out_path))
        print(f"resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for alpha, wd in CELLS:
        for s in range(N_SEEDS):
            if any(o['alpha'] == alpha and o['wd'] == wd and o['seed'] == s
                   and o['max_steps'] == 240000 for o in out):
                continue
            r = run_cell(10, alpha, wd, s, max_steps=240000)
            tg = t_grok(r)
            censored = tg is None
            print(f"[m7] {summary_line(r)} t_grok={tg if tg is not None else 'CENSORED@240k'}",
                  flush=True)
            out.append(dict(verdict=verdict(r), t_grok=tg, censored=censored, **r))
            json.dump(out, open(out_path, "w"))
    print(f"\ndone: {len(out)} runs, {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
