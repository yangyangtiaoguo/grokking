"""P0.5 v5 — Stability of grokking across seeds (testbed reliability check).

The P4 phase diagram dies if grokking is seed-fragile (proposal's stated risk).
Run the grok config across seeds; report tau spread and a robust final-eval
(mean over the last window, not a single possibly-in-a-dip last step).
Also track 'grokked?' = eval stabilizes above 0.9.
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
        logits = model(Xtr)
        tgt = Xtr.roll(-1, dims=1)
        lt = lossf(logits.reshape(-1, logits.size(-1)), tgt.reshape(-1))
        loss = (lt * Mtr.reshape(-1)).sum() / Mtr.sum()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % log_every == 0 or step == max_steps:
            tr = seq_accuracy(model, Xtr, Mtr)
            ev = seq_accuracy(model, Xev, Mev)
            steps.append(step); tr_h.append(tr); ev_h.append(ev); th_h.append(param_l2(model))
            if tr_cross is None and tr >= 0.99:
                tr_cross = step
            if ev_cross is None and ev >= 0.90:
                ev_cross = step
    # robust final metrics over the last 25% of logged steps
    tail = max(1, len(ev_h) // 4)
    ev_tail = np.array(ev_h[-tail:])
    ev_final_mean = float(ev_tail.mean())
    ev_final_min = float(ev_tail.min())
    grokked = ev_final_mean > 0.9
    tau = (ev_cross - tr_cross) if (tr_cross and ev_cross) else None
    return dict(seed=seed, tr_cross=tr_cross, ev_cross=ev_cross, tau=tau,
                ev_final_mean=ev_final_mean, ev_final_min=ev_final_min,
                grokked=grokked, th_final=th_h[-1], steps=steps, ev=ev_h, th=th_h)


def main():
    n, max_steps = 8, 25000
    frac, wd, isc, lr = 0.5, 0.3, 5.0, 1e-3
    seeds = [0, 1, 2, 3, 4]
    print(f"P0.5v5 stability: n={n} frac={frac} wd={wd} init={isc} lr={lr} "
          f"max_steps={max_steps} seeds={seeds}")
    print(f"{'seed':>4} {'trX':>6} {'evX':>6} {'tau':>7} {'evMean':>7} {'evMin':>6} "
          f"{'grok?':>6} {'thF':>6}")
    runs = []
    t0 = time.time()
    for s in seeds:
        r = run(n, frac, wd, isc, s, max_steps, lr=lr)
        runs.append(r)
        print(f"{s:4d} {str(r['tr_cross']):>6} {str(r['ev_cross']):>6} {str(r['tau']):>7} "
              f"{r['ev_final_mean']:7.3f} {r['ev_final_min']:6.3f} "
              f"{str(r['grokked']):>6} {r['th_final']:6.1f}")
    with open("results/p05v5_stability.json", "w") as f:
        json.dump([{k: v for k, v in r.items() if k not in ('steps','ev','th')}
                   | {'steps': r['steps'], 'ev': r['ev'], 'th': r['th']} for r in runs], f)
    ng = sum(r['grokked'] for r in runs)
    taus = [r['tau'] for r in runs if r['tau']]
    print(f"\ngrokked {ng}/{len(seeds)} seeds.")
    if taus:
        print(f"tau: mean {np.mean(taus):.0f}  std {np.std(taus):.0f}  "
              f"min {min(taus)} max {max(taus)}  (CV={np.std(taus)/np.mean(taus):.2f})")
    print(f"ev_final_mean across seeds: {[round(r['ev_final_mean'],3) for r in runs]}")
    print(f"elapsed {time.time()-t0:.1f}s -> results/p05v5_stability.json")
    print("\nVerdict: >=4/5 grok with CV(tau)<0.5 => testbed reliable for P4.")


if __name__ == "__main__":
    main()
