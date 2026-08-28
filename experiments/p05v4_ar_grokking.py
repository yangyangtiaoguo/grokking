"""P0.5 v4 — grokking with the CORRECT autoregressive big-endian task.

Test whether the faithful task (AR, big-endian, loss on bin(N+1) tokens) produces
a memorize-then-generalize delay under high weight decay + subset training.
Sweep a couple of configs at small n first (cheap), log full trajectories.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import (ARCounter, split_train_eval, to_tensors, param_l2,
                     seq_accuracy, scale_init)

DEV = "cuda"


def run(n, frac, wd, init_scale, seed, max_steps, lr=1e-3, d=64, log_every=200):
    torch.manual_seed(seed)
    trN, evN = split_train_eval(n, frac, seed)
    Xtr, Mtr = to_tensors(trN, n, DEV)
    Xev, Mev = to_tensors(evN, n, DEV)
    model = ARCounter(n, d=d).to(DEV)
    scale_init(model, init_scale)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    lossf = torch.nn.CrossEntropyLoss(reduction="none")

    steps, tr_h, ev_h, th_h = [], [], [], []
    tr_cross = ev_cross = None
    for step in range(max_steps + 1):
        model.train()
        logits = model(Xtr)                       # (B,L,V)
        tgt = Xtr.roll(-1, dims=1)
        loss_tok = lossf(logits.reshape(-1, logits.size(-1)), tgt.reshape(-1))
        loss = (loss_tok * Mtr.reshape(-1)).sum() / Mtr.sum()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % log_every == 0 or step == max_steps:
            tr = seq_accuracy(model, Xtr, Mtr)
            ev = seq_accuracy(model, Xev, Mev)
            steps.append(step); tr_h.append(tr); ev_h.append(ev); th_h.append(param_l2(model))
            if tr_cross is None and tr >= 0.99:
                tr_cross = step
            if ev_cross is None and ev >= 0.90:
                ev_cross = step
    tau = (ev_cross - tr_cross) if (tr_cross is not None and ev_cross is not None) else None
    return dict(n=n, frac=frac, wd=wd, init_scale=init_scale, seed=seed,
                n_train=int(trN.size), tr_cross=tr_cross, ev_cross=ev_cross, tau=tau,
                final_train=tr_h[-1], final_eval=ev_h[-1],
                steps=steps, tr=tr_h, ev=ev_h, th=th_h)


def main():
    n = 8
    max_steps = 20000
    seed = 0
    configs = [
        # (frac, wd, init_scale)
        (0.5, 1.0, 1.0),
        (0.5, 1.0, 5.0),
        (0.5, 0.3, 5.0),
        (0.7, 1.0, 5.0),
    ]
    print(f"P0.5v4 (AR big-endian): n={n} N={2**n} max_steps={max_steps}")
    print(f"{'frac':>5} {'wd':>5} {'init':>5} {'ntr':>5} {'trX':>7} {'evX':>7} {'tau':>7} "
          f"{'finTr':>6} {'finEv':>6} {'th0':>6} {'thF':>6}")
    runs = []
    t0 = time.time()
    for frac, wd, isc in configs:
        r = run(n, frac, wd, isc, seed, max_steps)
        runs.append(r)
        print(f"{frac:5.2f} {wd:5.2f} {isc:5.1f} {r['n_train']:5d} "
              f"{str(r['tr_cross']):>7} {str(r['ev_cross']):>7} {str(r['tau']):>7} "
              f"{r['final_train']:6.3f} {r['final_eval']:6.3f} {r['th'][0]:6.1f} {r['th'][-1]:6.1f}")
    with open("results/p05v4_ar_grokking.json", "w") as f:
        json.dump(runs, f)
    print(f"\nelapsed {time.time()-t0:.1f}s -> results/p05v4_ar_grokking.json")
    groks = [r for r in runs if r['tau'] and r['tau'] > 1000 and r['final_eval'] > 0.9]
    if groks:
        b = max(groks, key=lambda r: r['tau'])
        print(f"\nGROKKING! frac={b['frac']} wd={b['wd']} init={b['init_scale']} "
              f"tau={b['tau']} (tr@{b['tr_cross']} ev@{b['ev_cross']}) "
              f"norm {b['th'][0]:.0f}->{b['th'][-1]:.0f}")
    else:
        near = [(r['frac'],r['wd'],r['init_scale'],r['final_train'],r['final_eval']) for r in runs
                if r['final_train']>0.95 and r['final_eval']<0.8]
        print(f"\nno clear grok. memorized-but-not-generalized: {near}")


if __name__ == "__main__":
    main()
