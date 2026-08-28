"""P0.5 v8 — minibatch SGD (Zhao protocol: batch=512) + lock-in sweep.

v7 diagnosis:
  - n=8 wd=1.0+init=5 already tried in v4 -> model COLLAPSES (finEv=0.078);
    wd=1.0+init=1 -> immediate generalization. n=8 is knife-edge.
  - n=10/12 full-batch: generalization works (n=12 init=10: 3/3 grok by
    tail-mean) but (a) no delay tau<=0, (b) violent tail oscillation (tMin~0).
Full-batch GD near the phase boundary can sit on a deterministic knife-edge;
stochastic minibatches give Kramers-like escape noise. Zhao uses batch=512.

Sweep (3 seeds each). NOTE: stochasticity requires B >> batch. n=10 frac=0.3
has B=307 so batch=128 there; n=12 uses batch=512; n=8 control batch=64.
  A. n=10 frac=0.3 wd=0.3 init=10 batch=128  (v7's delay config, now stochastic)
  B. n=10 frac=0.3 wd=1.0 init=10 batch=128  (Zhao's wd)
  C. n=12 frac=0.5 wd=0.3 init=10 batch=512  (v7's 3/3-grok config)
  D. n=12 frac=0.3 wd=0.3 init=10 batch=512
  E. n=8  frac=0.5 wd=0.3 init=5  batch=64   (control: minibatch vs v4 full-batch)
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import (ARCounter, split_train_eval, to_tensors, param_l2,
                     seq_accuracy, scale_init)

DEV = "cuda"


def run(n, frac, wd, isc, seed, max_steps, lr, batch, d=64, log_every=250):
    torch.manual_seed(seed)
    trN, evN = split_train_eval(n, frac, seed)
    Xtr, Mtr = to_tensors(trN, n, DEV)
    Xev, Mev = to_tensors(evN, n, DEV)
    model = ARCounter(n, d=d).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
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
        # (label, n, frac, wd, init, lr, batch, max_steps)
        ("A", 10, 0.3, 0.3, 10.0, 1e-3, 128, 30000),
        ("B", 10, 0.3, 1.0, 10.0, 1e-3, 128, 30000),
        ("C", 12, 0.5, 0.3, 10.0, 1e-3, 512, 30000),
        ("D", 12, 0.3, 0.3, 10.0, 1e-3, 512, 30000),
        ("E", 8, 0.5, 0.3, 5.0, 1e-3, 64, 30000),
    ]
    seeds = [0, 1, 2]
    print("P0.5v8 minibatch SGD, 3 seeds each")
    out = []
    t0 = time.time()
    for (lab, n, frac, wd, isc, lr, bs, ms) in grid:
        print(f"\n=== [{lab}] n={n} frac={frac} wd={wd} init={isc} lr={lr:.0e} "
              f"batch={bs} steps={ms} ===")
        print(f"{'seed':>4} {'trX':>6} {'evX':>6} {'tau':>7} {'tMean':>6} {'tMin':>6} "
              f"{'grok':>5} {'thF':>6}  elapsed")
        for s in seeds:
            ts = time.time()
            r = run(n, frac, wd, isc, s, ms, lr, bs)
            print(f"{s:4d} {str(r['tr_cross']):>6} {str(r['ev_cross']):>6} "
                  f"{str(r['tau']):>7} {r['ev_tail_mean']:6.3f} {r['ev_tail_min']:6.3f} "
                  f"{str(r['grokked']):>5} {r['thF']:6.1f}  {time.time()-ts:.0f}s")
            out.append(dict(label=lab, n=n, frac=frac, wd=wd, init=isc, lr=lr,
                            batch=bs, **r))
    json.dump(out, open("results/p05v8_lockin.json", "w"))
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p05v8_lockin.json")
    for lab in {o['label'] for o in out}:
        rs = [o for o in out if o['label'] == lab]
        ng = sum(r['grokked'] for r in rs)
        taus = [r['tau'] for r in rs if r['tau'] and r['tau'] > 0]
        print(f"[{lab}] n={rs[0]['n']}: grok {ng}/3, "
              f"tau_med={int(np.median(taus)) if taus else None}, "
              f"tail_min={min(r['ev_tail_min'] for r in rs):.3f}")


if __name__ == "__main__":
    main()
