"""M8 — fine-grained dose-response + confound-separating controls (addresses
auditor's C2 gap: "minimal dose" claim needs a sub-1/128 dose sweep, and the
mechanism behind why uniform injection works is unisolated — support
coverage? gradient diversity? distribution entropy? carry-chain composition?).

Three parts:

  M8a dose sweep: p in {0.1%, 0.25%, 0.4%, 0.8%(=1/128 baseline), 1.6%} at
      THREE trapped/starved cells (alpha=2.5/wd=0.3 [trap], alpha=3.0/wd=0.3
      [starvation], alpha=2.75/wd=0.3 [mixed]), 8 seeds each.
  M8b confound controls at the alpha=2.5/wd=0.3 cell, k=1 (p=1/128), 8 seeds
      each, comparing FOUR injection distributions of the SAME size:
        - uniform     (baseline, already have 5-seed data from M2b)
        - tail        (longest-carry only, already have M2b data)
        - head        (highest-freq only, already have M2b data)
        - rare_short  (NEW: samples weighted toward LOW-frequency states
                       that do NOT have long carry chains -- isolates
                       "rarity" from "carry-chain length": if this rescues
                       as well as uniform, the mechanism is "any rare-state
                       exposure"; if it fails like tail, "coverage of THE
                       FULL SUPPORT" (not just non-head) is what matters)
        - same_dist   (NEW: k samples drawn from the SAME Zipf(alpha)
                       distribution as the rest of the batch, i.e. a no-op
                       control -- isolates "more samples" from "different
                       distribution": if THIS also rescues, the effect is
                       just "batch size perturbation", not distributional)

~ (5 doses x 3 cells x 8 seeds) + (2 new controls x 8 seeds) = 120 + 16 = 136
runs x ~95s ~= 3.6h -> results/m8a_dose_sweep.json, results/m8b_confound.json.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
from campaign_lib import run_cell, verdict, summary_line

DOSES = [1, 2, 3, 6, 10]  # /1280 batch-equivalent: use batch=128 so k directly
# maps to p = k/128: 1->0.78%, but we want finer -- use larger effective batch
# via multiple k values at batch=128 is coarse below k=1. Instead vary batch.
DOSE_CELLS = [
    # (batch, k) pairs giving p in {0.1%, 0.25%, 0.4%, 0.8%, 1.6%} approx
    (1024, 1), (512, 1), (256, 1), (128, 1), (128, 2),
]


def run_part(name, jobs):
    out_path = f"results/{name}.json"
    try:
        out = json.load(open(out_path))
        print(f"[{name}] resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for j in jobs:
        key = (j['alpha'], j['wd'], j['seed'], j.get('k', 0), j.get('inject', 'uniform'),
               j.get('batch', 128), j['max_steps'])
        if any((o['alpha'], o['wd'], o['seed'], o.get('k', 0), o.get('inject', 'uniform'),
                o.get('batch', 128), o['max_steps']) == key for o in out):
            continue
        r = run_cell(**j)
        print(f"[{name}] {summary_line(r)}", flush=True)
        out.append(dict(verdict=verdict(r), **r))
        json.dump(out, open(out_path, "w"))
    print(f"[{name}] done: {len(out)} runs, {time.time()-t0:.0f}s")


def main():
    # M8a: dose sweep at 3 cells, total-sample-count fixed via steps scaling
    jobs_a = []
    for (alpha, wd) in [(2.5, 0.3), (3.0, 0.3), (2.75, 0.3)]:
        for (batch, k) in DOSE_CELLS:
            steps = round(60000 * 128 / batch)  # keep total samples ~constant
            for s in range(8):
                jobs_a.append(dict(n=10, alpha=alpha, wd=wd, seed=s, k=k,
                                   batch=batch, max_steps=steps))
    run_part("m8a_dose_sweep", jobs_a)

    # M8b: confound controls (same_dist / rare_short) at alpha=2.5/wd=0.3, k=1
    run_m8b()


def run_m8b():
    """same_dist and rare_short controls need custom injection pools not in
    campaign_lib.inject_pool -- implemented here directly."""
    import torch
    sys.path.insert(0, "experiments")
    from task_ar import ARCounter, to_tensors, param_l2, scale_init
    from p4_freq_phase import region_acc
    DEV = "cuda"
    n, alpha, wd, isc, lr, batch, ms = 10, 2.5, 0.3, 10.0, 1e-3, 128, 60000
    out_path = "results/m8b_confound.json"
    try:
        out = json.load(open(out_path))
    except FileNotFoundError:
        out = []

    def carry_lengths(n):
        N = 2 ** n
        return np.array([bin(i)[2:][::-1].split('0')[0].__len__() for i in range(N)], np.int64)

    cl = carry_lengths(n)
    N = 2 ** n
    allN = np.arange(N, dtype=np.int64)
    w_zipf = (allN + 1.0) ** (-alpha); w_zipf /= w_zipf.sum()
    # rare_short: low frequency under Zipf(alpha) AND short carry chain (< n//2)
    rare_short_idx = np.where(cl < n // 2)[0]
    rare_short_idx = rare_short_idx[np.argsort(w_zipf[rare_short_idx])][:N // 10]  # 10% rarest-short

    for mode in ('same_dist', 'rare_short'):
        for s in range(8):
            if any(o.get('inject') == mode and o['seed'] == s for o in out):
                continue
            torch.manual_seed(s)
            X, M = to_tensors(allN, n, DEV)
            order = np.argsort(-w_zipf)
            hi_idx = order[:N // 10]; lo_idx = order[N // 2:]
            rng = np.random.default_rng(s + 1000)
            model = ARCounter(n, d=64).to(DEV)
            scale_init(model, isc)
            opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
            sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=ms)
            lf = torch.nn.CrossEntropyLoss(reduction="none")
            k = 1
            steps, aunif, ahi, alo = [], [], [], []
            for step in range(ms + 1):
                model.train()
                if mode == 'same_dist':
                    inj = rng.choice(N, size=k, replace=True, p=w_zipf)
                else:
                    inj = rng.choice(rare_short_idx, size=k, replace=True)
                idx = np.concatenate([rng.choice(N, size=batch - k, replace=True, p=w_zipf), inj])
                idx_t = torch.from_numpy(idx).to(DEV)
                xb, mb = X[idx_t], M[idx_t]
                lo = model(xb); tg = xb.roll(-1, 1)
                l = lf(lo.reshape(-1, lo.size(-1)), tg.reshape(-1))
                loss = (l * mb.reshape(-1)).sum() / mb.sum()
                opt.zero_grad(); loss.backward(); opt.step(); sched.step()
                if step % 250 == 0 or step == ms:
                    model.eval()
                    steps.append(step)
                    aunif.append(region_acc(model, X, M, np.arange(N)))
                    ahi.append(region_acc(model, X, M, hi_idx))
                    alo.append(region_acc(model, X, M, lo_idx))
            tail = slice(-max(1, len(aunif) // 5), None)
            r = dict(alpha=alpha, wd=wd, seed=s, k=k, inject=mode, max_steps=ms,
                     unif_tail=float(np.mean(aunif[tail])), hi_tail=float(np.mean(ahi[tail])),
                     lo_tail=float(np.mean(alo[tail])))
            v = "GROK" if r['unif_tail'] > 0.9 else ("TRAP" if r['hi_tail'] > 0.9 and r['unif_tail'] < 0.5
                 else ("CRUSH" if r['hi_tail'] < 0.9 and r['unif_tail'] < 0.5 else "PARTIAL"))
            print(f"[m8b] inject={mode} s{s} unif={r['unif_tail']:.3f} hi={r['hi_tail']:.3f} | {v}", flush=True)
            out.append(dict(verdict=v, **r))
            json.dump(out, open(out_path, "w"))


if __name__ == "__main__":
    main()
