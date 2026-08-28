"""P0.5 v9 — can lr annealing lock in the tail without killing the delay?

v8 best testbed candidate: A = n=10 frac=0.3 wd=0.3 init=10 batch=128,
3/3 grok by tail-mean, tau_med=1000, but tail oscillation (tMin 0.06-0.92).
Hypothesis: the oscillation is a noisy orbit near the phase boundary at
constant lr; annealing late should freeze it WITHOUT removing the early
delay (delay happens at constant lr anyway, before annealing kicks in).

Variants (5 seeds each):
  A1: constant lr 1e-3, 60k steps (does it self-lock with more time?)
  A2: cosine anneal 1e-3 -> 0 over 60k
  E2: n=8 control (frac=0.5 wd=0.3 init=5 batch=64) with cosine anneal —
      can the classic tau~2750 delay be made seed-stable?
Success for the testbed: >=4/5 seeds grok with tMin>0.85 AND tau_med>=500.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import (ARCounter, split_train_eval, to_tensors, param_l2,
                     seq_accuracy, scale_init)

DEV = "cuda"


def run(n, frac, wd, isc, seed, max_steps, lr, batch, anneal, d=64, log_every=250):
    torch.manual_seed(seed)
    trN, evN = split_train_eval(n, frac, seed)
    Xtr, Mtr = to_tensors(trN, n, DEV)
    Xev, Mev = to_tensors(evN, n, DEV)
    model = ARCounter(n, d=d).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    sched = (torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max_steps)
             if anneal else None)
    lf = torch.nn.CrossEntropyLoss(reduction="none")
    rng = np.random.default_rng(seed + 1000)
    B = Xtr.shape[0]
    steps, tr_h, ev_h, th_h = [], [], [], []
    tr_cross = ev_cross = None
    for step in range(max_steps + 1):
        model.train()
        idx = torch.from_numpy(rng.choice(B, size=min(batch, B), replace=False)).to(DEV)
        xb, mb = Xtr[idx], Mtr[idx]
        lo = model(xb); tg = xb.roll(-1, 1)
        l = lf(lo.reshape(-1, lo.size(-1)), tg.reshape(-1))
        loss = (l * mb.reshape(-1)).sum() / mb.sum()
        opt.zero_grad(); loss.backward(); opt.step()
        if sched is not None:
            sched.step()
        if step % log_every == 0 or step == max_steps:
            tr = seq_accuracy(model, Xtr, Mtr)
            ev = seq_accuracy(model, Xev, Mev)
            steps.append(step); tr_h.append(tr); ev_h.append(ev)
            th_h.append(param_l2(model))
            if tr_cross is None and tr >= 0.99:
                tr_cross = step
            if ev_cross is None and ev >= 0.90:
                ev_cross = step
    tail = ev_h[-max(1, len(ev_h) // 5):]
    tau = (ev_cross - tr_cross) if (tr_cross is not None and ev_cross is not None) else None
    return dict(seed=seed, tr_cross=tr_cross, ev_cross=ev_cross, tau=tau,
                ev_tail_mean=float(np.mean(tail)), ev_tail_min=float(np.min(tail)),
                grokked=bool(float(np.mean(tail)) > 0.9),
                th0=th_h[0], thF=th_h[-1],
                steps=steps, tr=tr_h, ev=ev_h, th=th_h)


def main():
    grid = [
        # (label, n, frac, wd, init, lr, batch, max_steps, anneal)
        ("A1", 10, 0.3, 0.3, 10.0, 1e-3, 128, 60000, False),
        ("A2", 10, 0.3, 0.3, 10.0, 1e-3, 128, 60000, True),
        ("E2", 8, 0.5, 0.3, 5.0, 1e-3, 64, 60000, True),
    ]
    seeds = [0, 1, 2, 3, 4]
    print("P0.5v9 lr-annealing lock-in test, 5 seeds each")
    out = []
    t0 = time.time()
    for (lab, n, frac, wd, isc, lr, bs, ms, ann) in grid:
        print(f"\n=== [{lab}] n={n} frac={frac} wd={wd} init={isc} lr={lr:.0e} "
              f"batch={bs} steps={ms} anneal={ann} ===")
        print(f"{'seed':>4} {'trX':>6} {'evX':>6} {'tau':>7} {'tMean':>6} {'tMin':>6} "
              f"{'grok':>5} {'thF':>6}  elapsed")
        for s in seeds:
            ts = time.time()
            r = run(n, frac, wd, isc, s, ms, lr, bs, ann)
            print(f"{s:4d} {str(r['tr_cross']):>6} {str(r['ev_cross']):>6} "
                  f"{str(r['tau']):>7} {r['ev_tail_mean']:6.3f} {r['ev_tail_min']:6.3f} "
                  f"{str(r['grokked']):>5} {r['thF']:6.1f}  {time.time()-ts:.0f}s")
            out.append(dict(label=lab, n=n, frac=frac, wd=wd, init=isc, lr=lr,
                            batch=bs, anneal=ann, **r))
    json.dump(out, open("results/p05v9_anneal.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p05v9_anneal.json")
    for lab in ["A1", "A2", "E2"]:
        rs = [o for o in out if o['label'] == lab]
        ng = sum(r['grokked'] for r in rs)
        locked = sum(r['ev_tail_min'] > 0.85 for r in rs)
        taus = [r['tau'] for r in rs if r['tau'] and r['tau'] > 0]
        print(f"[{lab}] n={rs[0]['n']}: grok {ng}/5, locked(tMin>0.85) {locked}/5, "
              f"tau_med={int(np.median(taus)) if taus else None}, "
              f"tail_min={min(r['ev_tail_min'] for r in rs):.3f}")


if __name__ == "__main__":
    main()
