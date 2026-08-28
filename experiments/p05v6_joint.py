"""P0.5 v6 — Find a config with BOTH grokking delay AND seed stability at larger n.

n=8 showed delay and stability are mutually exclusive (basin too small).
Move to n=10, 12. For each (n, init_scale, lr): run 3 seeds, report
  - delay: median (eval_cross - train_cross)
  - stability: min over seeds of tail-mean eval, and #seeds grokked
A good testbed = delay>1000 AND >=3/3 seeds grok with tail-min eval>0.85.
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
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd, betas=(0.9, 0.98))
    lf = torch.nn.CrossEntropyLoss(reduction="none")
    tr_cross = ev_cross = None
    evs = []
    ths = []
    for step in range(max_steps + 1):
        model.train()
        lo = model(Xtr); tg = Xtr.roll(-1, 1)
        l = lf(lo.reshape(-1, lo.size(-1)), tg.reshape(-1))
        loss = (l * Mtr.reshape(-1)).sum() / Mtr.sum()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % log_every == 0 or step == max_steps:
            tr = seq_accuracy(model, Xtr, Mtr)
            ev = seq_accuracy(model, Xev, Mev)
            evs.append(ev); ths.append(param_l2(model))
            if tr_cross is None and tr >= 0.99:
                tr_cross = step
            if ev_cross is None and ev >= 0.90:
                ev_cross = step
    tail = evs[-max(1, len(evs)//5):]
    tau = (ev_cross - tr_cross) if (tr_cross is not None and ev_cross is not None) else None
    return dict(seed=seed, tr_cross=tr_cross, ev_cross=ev_cross, tau=tau,
                ev_tail_mean=float(np.mean(tail)), ev_tail_min=float(np.min(tail)),
                grokked=float(np.mean(tail)) > 0.9, th0=ths[0], thF=ths[-1])


def main():
    seeds = [0, 1, 2]
    grid = [
        # (n, frac, wd, init, lr, max_steps)
        (10, 0.5, 0.3, 3.0, 5e-4, 30000),
        (10, 0.5, 0.3, 4.0, 5e-4, 30000),
        (12, 0.4, 0.3, 3.0, 5e-4, 30000),
        (12, 0.4, 0.3, 4.0, 5e-4, 30000),
    ]
    print("P0.5v6 joint delay+stability search (3 seeds each)")
    print(f"{'n':>3} {'frac':>5} {'wd':>4} {'init':>5} {'lr':>7} "
          f"{'#grok':>6} {'tauMed':>7} {'tailMin':>8} {'normF':>6}")
    out = []
    t0 = time.time()
    for (n, frac, wd, isc, lr, ms) in grid:
        rs = [run(n, frac, wd, isc, s, ms, lr) for s in seeds]
        ng = sum(r['grokked'] for r in rs)
        taus = [r['tau'] for r in rs if r['tau']]
        tau_med = int(np.median(taus)) if taus else None
        tail_min = min(r['ev_tail_min'] for r in rs)
        normF = np.mean([r['thF'] for r in rs])
        out.append(dict(n=n, frac=frac, wd=wd, init=isc, lr=lr,
                        n_grok=ng, tau_med=tau_med, tail_min=tail_min,
                        runs=rs))
        print(f"{n:3d} {frac:5.2f} {wd:4.1f} {isc:5.1f} {lr:7.0e} "
              f"{ng:>4}/3 {str(tau_med):>7} {tail_min:8.3f} {normF:6.1f}")
    json.dump(out, open("results/p05v6_joint.json", "w"), indent=2)
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p05v6_joint.json")
    good = [o for o in out if o['n_grok'] >= 3 and o['tau_med'] and o['tau_med'] > 1000
            and o['tail_min'] > 0.85]
    if good:
        b = good[0]
        print(f"\nRELIABLE TESTBED: n={b['n']} frac={b['frac']} wd={b['wd']} "
              f"init={b['init']} lr={b['lr']:.0e} tau~{b['tau_med']} tailMin={b['tail_min']:.2f}")
    else:
        print("\nNo config yet meets delay>1000 & 3/3 stable. Best candidates above; may need larger n or step budget.")


if __name__ == "__main__":
    main()
