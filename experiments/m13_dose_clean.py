"""M13 -- clean dose-response, deconfounded from batch size / update count
(closes the round-6 reviewer's MAJOR finding: M8a's sub-1/128 doses varied
batch size and step count jointly with dose, so the reported 0.391%-0.781%
bracket could not be attributed to dose alone).

Design: batch=128 and max_steps=60000 FIXED across every dose (matching the
paper's primary LARGECOUNTER protocol exactly). Fractional expected dose is
implemented probabilistically: at each step, independently with probability
q, ONE of the 128 slots (slot 0) is replaced by a sample drawn uniformly from
the full state space; with probability 1-q, the batch is drawn entirely from
the skewed distribution P_alpha (no injection that step). Expected dose per
batch is q/128 in expectation, matching k=1 at batch 128 in the limit q=1
(i.e. q=1 reproduces exactly the M8a k=1/batch=128 condition, which is our
built-in consistency check).

q values chosen to bracket the M8a-reported transition (0.391%-0.781% in the
confounded protocol): q in {0.1, 0.25, 0.5, 0.75, 1.0} -> expected dose
0.078%, 0.195%, 0.391%, 0.586%, 0.781%. Same 3 alphas (2.5, 2.75, 3.0) at
wd=0.3, 8 seeds each, matching M8a's design exactly except for the dose
implementation. ~15 x 8 = 120 runs x ~95s ~= 3.2h -> results/m13_dose_clean.json.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import ARCounter, to_tensors, param_l2, scale_init
from p4_freq_phase import region_acc

DEV = "cuda"

Q_VALUES = [0.1, 0.25, 0.5, 0.75, 1.0]
ALPHAS = [2.5, 2.75, 3.0]
WD = 0.3
N = 10
BATCH = 128
MAX_STEPS = 60000
LR = 1e-3
ISC = 10.0
D = 64


def run_one(alpha, wd, q, seed, n=N, batch=BATCH, max_steps=MAX_STEPS,
            lr=LR, isc=ISC, d=D, log_every=250):
    torch.manual_seed(seed)
    allN = np.arange(2 ** n, dtype=np.int64)
    X, M = to_tensors(allN, n, DEV)
    w = (allN + 1.0) ** (-alpha); w /= w.sum()
    order = np.argsort(-w)
    hi_idx = order[:len(order) // 10]
    lo_idx = order[len(order) // 2:]
    rng = np.random.default_rng(seed + 1000)

    model = ARCounter(n, d=d).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max_steps)
    lf = torch.nn.CrossEntropyLoss(reduction="none")

    steps, aunif, ahi, alo = [], [], [], []
    n_injected_steps = 0
    for step in range(max_steps + 1):
        model.train()
        idx = rng.choice(2 ** n, size=batch, replace=True, p=w)
        if rng.random() < q:
            idx[0] = rng.integers(0, 2 ** n)
            n_injected_steps += 1
        idx_t = torch.from_numpy(idx).to(DEV)
        xb, mb = X[idx_t], M[idx_t]
        lo = model(xb); tg = xb.roll(-1, 1)
        l = lf(lo.reshape(-1, lo.size(-1)), tg.reshape(-1))
        loss = (l * mb.reshape(-1)).sum() / mb.sum()
        opt.zero_grad(); loss.backward(); opt.step()
        sched.step()
        if step % log_every == 0 or step == max_steps:
            model.eval()
            steps.append(step)
            aunif.append(region_acc(model, X, M, np.arange(len(allN))))
            ahi.append(region_acc(model, X, M, hi_idx))
            alo.append(region_acc(model, X, M, lo_idx))
    tail = slice(-max(1, len(aunif) // 5), None)
    return dict(alpha=alpha, wd=wd, seed=seed, q=q, batch=batch, max_steps=max_steps,
                expected_dose=q / batch, realized_injection_rate=n_injected_steps / (max_steps + 1),
                unif_tail=float(np.mean(aunif[tail])), unif_min=float(np.min(aunif[tail])),
                hi_tail=float(np.mean(ahi[tail])), lo_tail=float(np.mean(alo[tail])))


def verdict(r):
    if r['unif_tail'] > 0.9:
        return "GROK"
    if r['hi_tail'] > 0.9 and r['unif_tail'] < 0.5:
        return "TRAP"
    if r['hi_tail'] < 0.9 and r['unif_tail'] < 0.5:
        return "CRUSH"
    return "PARTIAL"


def main():
    out_path = "results/m13_dose_clean.json"
    try:
        out = json.load(open(out_path))
        print(f"resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for alpha in ALPHAS:
        for q in Q_VALUES:
            for s in range(8):
                key = (alpha, WD, q, s)
                if any((o['alpha'], o['wd'], o['q'], o['seed']) == key for o in out):
                    continue
                ts = time.time()
                r = run_one(alpha, WD, q, s)
                v = verdict(r)
                print(f"a={alpha:4.2f} q={q:4.2f} (E[dose]={r['expected_dose']*100:.3f}%) s{s} | "
                      f"unif={r['unif_tail']:.3f} hi={r['hi_tail']:.3f} | {v} ({time.time()-ts:.0f}s)",
                      flush=True)
                out.append(dict(verdict=v, **r))
                json.dump(out, open(out_path, "w"))
    print(f"\ndone: {len(out)} runs, {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
