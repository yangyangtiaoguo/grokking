"""P0.5 v7 — transfer the ONLY working recipe (v4: n=8) to n=10/12, one knob at a time.

v6 changed three knobs at once (lr 1e-3->5e-4, betas->(0.9,0.98), init 5->3/4)
and got immediate generalization + heavy eval oscillation everywhere. v7 step 1
(v4 recipe verbatim at n=10, seed 0) shows immediate but STABLE generalization:
larger n makes memorization harder at fixed model size, so the model skips the
memory basin entirely. Step 2 (this run): push toward memorization with the
Omnigrok lever (init scale 7/10) and frac 0.5->0.3, one knob at a time.

Success: delay>1000 AND >=2/3 seeds grok with tail-min eval>0.85.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import (ARCounter, split_train_eval, to_tensors, param_l2,
                     seq_accuracy, scale_init)

DEV = "cuda"


def run(n, frac, wd, isc, seed, max_steps, lr, d=64, log_every=250):
    torch.manual_seed(seed)
    trN, evN = split_train_eval(n, frac, seed)
    Xtr, Mtr = to_tensors(trN, n, DEV)
    Xev, Mev = to_tensors(evN, n, DEV)
    model = ARCounter(n, d=d).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    lf = torch.nn.CrossEntropyLoss(reduction="none")
    steps, tr_h, ev_h, th_h = [], [], [], []
    tr_cross = ev_cross = None
    for step in range(max_steps + 1):
        model.train()
        lo = model(Xtr); tg = Xtr.roll(-1, 1)
        l = lf(lo.reshape(-1, lo.size(-1)), tg.reshape(-1))
        loss = (l * Mtr.reshape(-1)).sum() / Mtr.sum()
        opt.zero_grad(); loss.backward(); opt.step()
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
    # n=10 seed0 with v4-verbatim (init=5): IMMEDIATE but stable generalization
    # (trX=evX=250, tMin=0.934). Larger n => memorization harder (same param
    # budget, more states) => model goes straight to the algorithm. To INDUCE a
    # delay we must push toward the memorization basin: raise init scale
    # (Omnigrok lever) and/or cut frac. One knob at a time at n=10:
    grid = [
        # (n, frac, wd, init, lr, max_steps)
        (10, 0.5, 0.3, 7.0, 1e-3, 30000),
        (10, 0.5, 0.3, 10.0, 1e-3, 30000),
        (10, 0.3, 0.3, 10.0, 1e-3, 30000),
        (12, 0.5, 0.3, 10.0, 1e-3, 30000),
    ]
    seeds = [0, 1, 2]
    print("P0.5v7 v4-recipe transfer to larger n (3 seeds each)")
    out = []
    t0 = time.time()
    for (n, frac, wd, isc, lr, ms) in grid:
        print(f"\n=== n={n} frac={frac} wd={wd} init={isc} lr={lr:.0e} steps={ms} ===")
        print(f"{'seed':>4} {'trX':>6} {'evX':>6} {'tau':>7} {'tMean':>6} {'tMin':>6} "
              f"{'grok':>5} {'thF':>6}  elapsed")
        for s in seeds:
            ts = time.time()
            r = run(n, frac, wd, isc, s, ms, lr)
            print(f"{s:4d} {str(r['tr_cross']):>6} {str(r['ev_cross']):>6} "
                  f"{str(r['tau']):>7} {r['ev_tail_mean']:6.3f} {r['ev_tail_min']:6.3f} "
                  f"{str(r['grokked']):>5} {r['thF']:6.1f}  {time.time()-ts:.0f}s")
            out.append(dict(n=n, frac=frac, wd=wd, init=isc, lr=lr, **r))
    # slim json: full trajectories for plotting
    json.dump(out, open("results/p05v7_transfer.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p05v7_transfer.json")
    for n in {o['n'] for o in out}:
        rs = [o for o in out if o['n'] == n]
        ng = sum(r['grokked'] for r in rs)
        taus = [r['tau'] for r in rs if r['tau'] and r['tau'] > 0]
        print(f"n={n}: grok {ng}/3, tau_med={int(np.median(taus)) if taus else None}, "
              f"tail_min={min(r['ev_tail_min'] for r in rs):.3f}")


if __name__ == "__main__":
    main()
