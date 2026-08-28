"""
P0.5 v2 — Induce grokking via LARGE INITIALIZATION + weight decay (Omnigrok lever).

v1 used default (small) init -> model generalizes immediately, no delay window.
Grokking = large init lands in a high-norm memorizing solution; weight decay
slowly drags norm down; generalization appears (delayed) when norm crosses a
threshold. This is exactly the H1/H2 norm-collapse mechanism, so inducing it
this way directly produces the trajectory we want to study.

Sweep init_scale, fixed small-ish data + moderate wd. Log ||theta|| trajectory.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_model import (Counter, make_split, to_tensors, param_l2,
                        bit_and_seq_acc, scale_init)

DEV = "cuda"


def run(n, alpha, frac, wd, init_scale, seed, max_steps, lr=1e-3, d=64, log_every=200):
    torch.manual_seed(seed)
    N = 2 ** n
    train_x, eval_x = make_split(n, alpha, int(frac * N), seed=seed)
    Xtr, Ytr = to_tensors(train_x, n, DEV)
    Xev, Yev = to_tensors(eval_x, n, DEV)
    model = Counter(n, d=d, heads=4, layers=2).to(DEV)
    scale_init(model, init_scale)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    lossf = torch.nn.BCEWithLogitsLoss()

    steps, tr_h, ev_h, th_h = [], [], [], []
    tr_cross = ev_cross = None
    for step in range(max_steps + 1):
        model.train()
        loss = lossf(model(Xtr), Ytr)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % log_every == 0 or step == max_steps:
            _, tr = bit_and_seq_acc(model, Xtr, Ytr)
            _, ev = bit_and_seq_acc(model, Xev, Yev)
            steps.append(step); tr_h.append(tr); ev_h.append(ev); th_h.append(param_l2(model))
            if tr_cross is None and tr >= 0.99:
                tr_cross = step
            if ev_cross is None and ev >= 0.90:
                ev_cross = step
    tau = (ev_cross - tr_cross) if (tr_cross is not None and ev_cross is not None) else None
    return dict(n=n, alpha=alpha, frac=frac, wd=wd, init_scale=init_scale, seed=seed,
                n_train=int(train_x.size), tr_cross=tr_cross, ev_cross=ev_cross, tau=tau,
                final_eval=ev_h[-1], final_train=tr_h[-1],
                steps=steps, tr=tr_h, ev=ev_h, th=th_h)


def main():
    n = 12
    max_steps = 30000
    seed = 0
    wd = 0.1
    frac = 0.30
    scales = [1.0, 3.0, 6.0, 9.0]

    print(f"P0.5v2: n={n} alpha=0 wd={wd} frac={frac} max_steps={max_steps}")
    print(f"{'scale':>6} {'ntr':>5} {'trX':>7} {'evX':>7} {'tau':>7} {'finEv':>6} {'th0':>7} {'thF':>7}")
    all_runs = []
    t0 = time.time()
    for s in scales:
        r = run(n, 0.0, frac, wd, s, seed, max_steps)
        all_runs.append(r)
        print(f"{s:6.1f} {r['n_train']:5d} {str(r['tr_cross']):>7} {str(r['ev_cross']):>7} "
              f"{str(r['tau']):>7} {r['final_eval']:6.3f} {r['th'][0]:7.1f} {r['th'][-1]:7.1f}")

    with open("results/p05v2_grokking_initscale.json", "w") as f:
        json.dump(all_runs, f)
    print(f"\nelapsed {time.time()-t0:.1f}s -> results/p05v2_grokking_initscale.json")

    groks = [r for r in all_runs if r['tau'] and r['tau'] > 1000 and r['final_eval'] > 0.95]
    if groks:
        best = max(groks, key=lambda r: r['tau'])
        print(f"\nGROKKING FOUND: init_scale={best['init_scale']} tau={best['tau']} "
              f"(train@{best['tr_cross']} eval@{best['ev_cross']}) "
              f"norm {best['th'][0]:.1f}->{best['th'][-1]:.1f}")
    else:
        print("\nStill no grokking >1000 steps — try larger scale or smaller frac.")


if __name__ == "__main__":
    main()
