"""P7b — zero-cost tau(alpha) extraction from existing trajectories.

Critical slowing down (11.5 prediction 1) predicts tau(alpha) diverges as
alpha approaches the effective boundary from below. Existing P4/P4b/P4d/P5
runs all log A_unif every 250 steps; extract t_grok = first step where
A_unif > 0.9 (sustained: mean of next 4 logs also > 0.85, to skip transient
spikes) and see the trend across alpha at fixed (wd=0.3, budget, recipe).

Pure CPU — reads results/*.json, no GPU. Complements P7 (which tests
alpha=2.5 at 240k directly).
"""
import json
import numpy as np

def first_cross(steps, a, thr=0.9, sustain=4, susthr=0.85):
    """First step where a > thr and the next `sustain` log points average
    above susthr (None if never)."""
    arr = np.asarray(a)
    for i in range(len(arr) - sustain):
        if arr[i] > thr and arr[i + 1:i + 1 + sustain].mean() > susthr:
            return steps[i]
    return None

def load(fname):
    try:
        return json.load(open(f"results/{fname}"))
    except FileNotFoundError:
        return []

def main():
    # (file, alpha, steps-budget, source label) — all wd=0.3, A2 recipe, n=10
    sources = []
    for rec in load("p4_freq_phase.json"):
        if rec.get("wd") == 0.3:
            sources.append(("P4", rec))
    for rec in load("p4b_alpha_scan.json"):
        if rec.get("wd") == 0.3:
            sources.append(("P4b", rec))
    for rec in load("p4d_lambda_dir.json"):
        if rec.get("wd") == 0.3 and rec.get("alpha") == 2.5:
            sources.append(("P4d-120k", rec))
    for rec in load("p5_rescue.json"):
        if rec.get("p") == 0.0 and rec.get("wd") == 0.3:
            sources.append(("P5-p0", rec))

    # P4b/P5 60k runs share config with P4 60k runs: dedup by (alpha, seed)
    # keeping the longest-budget run.
    best = {}
    for src, r in sources:
        key = (r["alpha"], r["seed"])
        cur = best.get(key)
        if cur is None or len(r["steps"]) > len(cur[1]["steps"]):
            best[key] = (src, r)

    print(f"tau(alpha) @ wd=0.3, A2 recipe (t_grok = first sustained A_unif>0.9)\n")
    print(f"{'alpha':>5} | {'seed':>4} {'budget':>7} {'t_grok':>7} {'A_end':>6} | src")
    rows = {}
    for (alpha, seed), (src, r) in sorted(best.items()):
        t = first_cross(r["steps"], r["aunif"])
        budget = r["steps"][-1]
        te = "-" if t is None else f"{t}"
        print(f"{alpha:5.2f} | {seed:4d} {budget:7d} {te:>7} "
              f"{r['aunif'][-1]:6.3f} | {src}")
        rows.setdefault(alpha, []).append((t, budget, r["aunif"][-1]))

    print("\nsummary (median over seeds):")
    print(f"{'alpha':>5} {'tau_med':>8} {'never':>6} {'A_end_med':>9}")
    for alpha, rs in sorted(rows.items()):
        taus = [t for t, _, _ in rs if t is not None]
        ends = np.median([a for _, _, a in rs])
        never = sum(1 for t, _, _ in rs if t is None)
        tm = "-" if not taus else f"{int(np.median(taus))}"
        print(f"{alpha:5.2f} {tm:>8} {never:6d} {ends:9.3f}")

if __name__ == "__main__":
    main()
