"""P4 (freq protocol) — 2x2 phase-diagram corners under FREQUENCY skew.

p1v2 verdict: subset-selection leaves the train-set carry composition ~flat in
alpha, so the d0 mechanism does not exist there. The correct protocol (and
Zhao's naturalistic semantics) is FREQUENCY skew: train pool = all 2^n states,
minibatches drawn WITH replacement weighted by (x+1)^(-alpha).

Metrics per run:
  A_unif : uniform full-space sequence accuracy (the order parameter;
           "grokked" = A_unif tail-mean > 0.9 = the algorithm everywhere)
  A_hi   : accuracy on the top-10%-weight states (what a heuristic fits)
  A_lo   : accuracy on the lowest-50%-weight states (the rare tail)
  trapped = A_hi high, A_unif low (fits the head, never finds the algorithm)

Grid (testbed A2 recipe: n=10, init=10, lr=1e-3, batch=128, 60k, cosine):
  ctl : alpha=0, wd=0.3  (control; no held-out semantics, just full acc)
  lo1 : alpha=1, wd=0.3
  lo2 : alpha=2, wd=0.3  <- core prediction: TRAPPED
  hi1 : alpha=1, wd=1.0
  hi2 : alpha=2, wd=1.0  <- does larger lambda rescue?
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import (ARCounter, to_tensors, param_l2, seq_accuracy, scale_init,
                     zipf_batch_sampler)

DEV = "cuda"


@torch.no_grad()
def region_acc(model, X, M, idx):
    """Sequence accuracy restricted to rows idx (numpy array)."""
    if len(idx) == 0:
        return float("nan")
    ok = tot = 0
    for i in range(0, len(idx), 4096):
        j = idx[i:i + 4096]
        x, m = X[j], M[j]
        logits = model(x)
        pred = logits.argmax(-1)
        tgt = x.roll(-1, dims=1)
        correct = ((pred == tgt) | (m == 0)).all(dim=1)
        ok += correct.sum().item(); tot += len(j)
    return ok / tot


def run(n, alpha, wd, isc, seed, max_steps, lr, batch, d=64, log_every=250):
    torch.manual_seed(seed)
    allN = np.arange(2 ** n, dtype=np.int64)
    X, M = to_tensors(allN, n, DEV)                      # full-space pool
    w = (allN + 1.0) ** (-alpha); w /= w.sum()
    order = np.argsort(-w)                               # by weight desc
    hi_idx = order[:len(order) // 10]                    # top-10% weight
    lo_idx = order[len(order) // 2:]                     # bottom-50% weight
    sampler = zipf_batch_sampler(n, alpha, batch, seed + 1000)

    model = ARCounter(n, d=d).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max_steps)
    lf = torch.nn.CrossEntropyLoss(reduction="none")

    steps, aunif, ahi, alo, th_h = [], [], [], [], []
    for step in range(max_steps + 1):
        model.train()
        idx = torch.from_numpy(next(sampler)).to(DEV)
        xb, mb = X[idx], M[idx]
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
            th_h.append(param_l2(model))
    tail = slice(-max(1, len(aunif) // 5), None)
    return dict(alpha=alpha, wd=wd, seed=seed,
                unif_tail=float(np.mean(aunif[tail])), unif_min=float(np.min(aunif[tail])),
                hi_tail=float(np.mean(ahi[tail])), lo_tail=float(np.mean(alo[tail])),
                thF=th_h[-1],
                steps=steps, aunif=aunif, ahi=ahi, alo=alo, th=th_h)


def main():
    grid = [
        # (label, alpha, wd)
        ("ctl", 0.0, 0.3),
        ("lo1", 1.0, 0.3),
        ("lo2", 2.0, 0.3),
        ("hi1", 1.0, 1.0),
        ("hi2", 2.0, 1.0),
    ]
    seeds = [0, 1, 2]
    n, isc, lr, batch, ms = 10, 10.0, 1e-3, 128, 60000
    print(f"P4 freq protocol: n={n} init={isc} lr={lr:.0e} batch={batch} "
          f"steps={ms} cosine; 3 seeds per cell")
    print(f"{'cell':>4} {'alpha':>5} {'wd':>4} | {'seed':>4} {'A_unif':>7} {'A_hi':>6} "
          f"{'A_lo':>6} {'thF':>5} | verdict")
    out = []
    t0 = time.time()
    for (lab, alpha, wd) in grid:
        for s in seeds:
            ts = time.time()
            r = run(n, alpha, wd, isc, s, ms, lr, batch)
            grokked = r['unif_tail'] > 0.9
            trapped = (r['hi_tail'] > 0.9) and (r['unif_tail'] < 0.5)
            v = "GROK" if grokked else ("TRAPPED" if trapped else "partial")
            print(f"{lab:>4} {alpha:5.1f} {wd:4.1f} | {s:4d} {r['unif_tail']:7.3f} "
                  f"{r['hi_tail']:6.3f} {r['lo_tail']:6.3f} {r['thF']:5.1f} | {v}"
                  f"  ({time.time()-ts:.0f}s)")
            out.append(dict(label=lab, **r, grokked=grokked, trapped=trapped))
    json.dump(out, open("results/p4_freq_phase.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p4_freq_phase.json")
    print("\nCell summary:")
    for lab in ["ctl", "lo1", "lo2", "hi1", "hi2"]:
        rs = [o for o in out if o['label'] == lab]
        print(f"[{lab}] alpha={rs[0]['alpha']} wd={rs[0]['wd']}: "
              f"grok {sum(r['grokked'] for r in rs)}/3, "
              f"trapped {sum(r['trapped'] for r in rs)}/3, "
              f"unif_tail={np.mean([r['unif_tail'] for r in rs]):.3f}, "
              f"lo_tail={np.mean([r['lo_tail'] for r in rs]):.3f}")


if __name__ == "__main__":
    main()
