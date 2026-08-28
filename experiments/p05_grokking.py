"""
P0.5 — Reproduce the GROKKING curve itself (prerequisite for P1/P2/P4).

We need a config where train_acc hits ~100% EARLY but eval_acc stays low for a
long delay, then jumps — the signature memorize-then-generalize separation.
Without this, "memorization checkpoint" is undefined.

Sweep weight decay x data fraction on uniform data (alpha=0), log full
trajectories, and report the grokking delay tau = (step eval crosses 0.9)
minus (step train crosses 0.99).
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_model import (Counter, make_split, to_tensors, param_l2,
                        bit_and_seq_acc)

DEV = "cuda"


def run(n, alpha, frac, wd, seed, max_steps, lr=1e-3, d=64, log_every=100):
    torch.manual_seed(seed)
    N = 2 ** n
    n_train = int(frac * N)
    train_x, eval_x = make_split(n, alpha, n_train, seed=seed)
    Xtr, Ytr = to_tensors(train_x, n, DEV)
    Xev, Yev = to_tensors(eval_x, n, DEV)
    model = Counter(n, d=d, heads=4, layers=2).to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    lossf = torch.nn.BCEWithLogitsLoss()

    steps, tr_hist, ev_hist, th_hist = [], [], [], []
    tr_cross = ev_cross = None
    for step in range(max_steps + 1):
        model.train()
        loss = lossf(model(Xtr), Ytr)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % log_every == 0 or step == max_steps:
            _, tr = bit_and_seq_acc(model, Xtr, Ytr)
            _, ev = bit_and_seq_acc(model, Xev, Yev)
            steps.append(step); tr_hist.append(tr); ev_hist.append(ev)
            th_hist.append(param_l2(model))
            if tr_cross is None and tr >= 0.99:
                tr_cross = step
            if ev_cross is None and ev >= 0.90:
                ev_cross = step
    tau = (ev_cross - tr_cross) if (tr_cross is not None and ev_cross is not None) else None
    return dict(n=n, alpha=alpha, frac=frac, wd=wd, seed=seed,
                n_train=int(train_x.size), tr_cross=tr_cross, ev_cross=ev_cross,
                tau=tau, final_eval=ev_hist[-1], final_train=tr_hist[-1],
                steps=steps, tr=tr_hist, ev=ev_hist, th=th_hist)


def main():
    n = 12
    max_steps = 30000
    seed = 0
    # sweep to find grokking: higher wd, smaller data than the smoke test
    configs = []
    for wd in [0.1, 0.3, 1.0]:
        for frac in [0.30, 0.40]:
            configs.append((wd, frac))

    print(f"P0.5: n={n} alpha=0 max_steps={max_steps} seed={seed}")
    print(f"{'wd':>5} {'frac':>5} {'ntr':>5} {'trX':>7} {'evX':>7} {'tau':>7} {'finEv':>6}")
    all_runs = []
    t0 = time.time()
    for wd, frac in configs:
        r = run(n, 0.0, frac, wd, seed, max_steps)
        all_runs.append(r)
        print(f"{wd:5.2f} {frac:5.2f} {r['n_train']:5d} "
              f"{str(r['tr_cross']):>7} {str(r['ev_cross']):>7} "
              f"{str(r['tau']):>7} {r['final_eval']:6.3f}")

    with open("results/p05_grokking_sweep.json", "w") as f:
        json.dump(all_runs, f)
    print(f"\nelapsed {time.time()-t0:.1f}s -> results/p05_grokking_sweep.json")

    # pick the clearest grokking run (largest positive tau with final_eval>0.95)
    groks = [r for r in all_runs if r['tau'] and r['tau'] > 500 and r['final_eval'] > 0.95]
    if groks:
        best = max(groks, key=lambda r: r['tau'])
        print(f"\nCLEAREST GROKKING: wd={best['wd']} frac={best['frac']} "
              f"tau={best['tau']} (train@{best['tr_cross']} eval@{best['ev_cross']})")
    else:
        print("\nNO CLEAR GROKKING in this sweep — widen wd/frac/steps.")


if __name__ == "__main__":
    main()
