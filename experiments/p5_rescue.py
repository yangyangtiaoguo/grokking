"""P5 — rescue dose m*(alpha): minimal balanced-data injection that un-traps.

P4d verdict: the trap at alpha=2.5 is a genuine steady state (120k steps do
not escape) and the LAMBDA axis points the WRONG way (smaller wd helps,
larger hurts — opposite of H3's lambda_c(alpha) rising). The natural next
lever — and the one Zhao's open limitation actually asks about — is the DATA
side (H4): inject a fraction p of uniformly-drawn samples into the Zipf
(alpha) minibatch stream and find the minimal p that restores A_unif>0.9.

Protocol: each batch of 128 = k uniform samples + (128-k) Zipf(alpha) samples,
k = round(p*128). p is the rescue dose; m* = p*N_semantic (fraction of the
stream). alpha=2.5, wd=0.3, A2 recipe, 60k steps, cosine.

Prediction (theory, direction only): m* grows with alpha; at alpha=2.5 a
modest p should suffice since the model only needs rare long-carry exposure.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import (ARCounter, to_tensors, param_l2, scale_init)
from p4_freq_phase import region_acc

DEV = "cuda"


def run(n, alpha, p, wd, isc, seed, max_steps, lr, batch, d=64, log_every=250):
    torch.manual_seed(seed)
    allN = np.arange(2 ** n, dtype=np.int64)
    X, M = to_tensors(allN, n, DEV)
    w = (allN + 1.0) ** (-alpha); w /= w.sum()
    order = np.argsort(-w)
    hi_idx = order[:len(order) // 10]
    lo_idx = order[len(order) // 2:]
    rng = np.random.default_rng(seed + 1000)
    k = int(round(p * batch))                     # uniform samples per batch

    model = ARCounter(n, d=d).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max_steps)
    lf = torch.nn.CrossEntropyLoss(reduction="none")

    steps, aunif, ahi, alo, th_h = [], [], [], [], []
    for step in range(max_steps + 1):
        model.train()
        idx = np.concatenate([
            rng.choice(2 ** n, size=batch - k, replace=True, p=w),
            rng.choice(2 ** n, size=k, replace=True),
        ])
        idx = torch.from_numpy(idx).to(DEV)
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
    return dict(alpha=alpha, p=p, wd=wd, seed=seed,
                unif_tail=float(np.mean(aunif[tail])), unif_min=float(np.min(aunif[tail])),
                hi_tail=float(np.mean(ahi[tail])), lo_tail=float(np.mean(alo[tail])),
                thF=th_h[-1], steps=steps, aunif=aunif, ahi=ahi, alo=alo, th=th_h)


def main():
    alpha, wd = 2.5, 0.3
    ps = [0.0, 1 / 64, 1 / 16, 1 / 4, 1 / 2]
    seeds = [0, 1, 2]
    n, isc, lr, batch, ms = 10, 10.0, 1e-3, 128, 60000
    print(f"P5 rescue dose: alpha={alpha} wd={wd} n={n} batch={batch} steps={ms} cosine")
    print(f"{'p':>7} {'k/batch':>7} | {'seed':>4} {'A_unif':>7} {'A_hi':>6} {'A_lo':>6} "
          f"{'thF':>5} | verdict")
    out = []
    t0 = time.time()
    for p in ps:
        for s in seeds:
            ts = time.time()
            r = run(n, alpha, p, wd, isc, s, ms, lr, batch)
            grokked = r['unif_tail'] > 0.9
            trapped = (r['hi_tail'] > 0.9) and (r['unif_tail'] < 0.5)
            v = "GROK" if grokked else ("TRAPPED" if trapped else "partial")
            print(f"{p:7.4f} {int(round(p*batch)):7d} | {s:4d} {r['unif_tail']:7.3f} "
                  f"{r['hi_tail']:6.3f} {r['lo_tail']:6.3f} {r['thF']:5.1f} | {v}"
                  f"  ({time.time()-ts:.0f}s)")
            out.append(dict(label=f"p{p:.4f}", grokked=grokked, trapped=trapped, **r))
    json.dump(out, open("results/p5_rescue.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p5_rescue.json")
    print("\nRescue dose curve (alpha=2.5):")
    for p in ps:
        rs = [o for o in out if o['p'] == p]
        print(f"p={p:7.4f}: grok {sum(r['grokked'] for r in rs)}/3, "
              f"unif={np.mean([r['unif_tail'] for r in rs]):.3f}, "
              f"lo={np.mean([r['lo_tail'] for r in rs]):.3f}")

if __name__ == "__main__":
    main()
