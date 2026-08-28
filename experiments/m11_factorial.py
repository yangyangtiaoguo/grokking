"""M11 — partial factorial robustness design (addresses auditor's C5 gap:
"a few one-factor perturbations do not establish broad architectural or
optimization robustness" + "post hoc unless directions were preregistered").

Pre-registered predictions (frozen before running, so directions are not
post-hoc): at the alpha=2.5 boundary region,
  - width d up: ceiling should shift RIGHT (more capacity -> easier grok)
  - width d down: ceiling should shift LEFT
  - lr down: ceiling should shift RIGHT (slower optimizer -> more time to
    find the generalizing solution before overfitting to head)
  - lr up: ceiling should shift LEFT
  - depth (layers) up: ceiling should shift RIGHT (more capacity)
  - optimizer SGD+momentum (vs AdamW): expect WORSE grokking overall
    (Omnigrok/Power literature: adaptive optimizers help grokking) --
    this one is a stronger/riskier prediction than the others.
These match M5's already-confirmed single-factor directions (d, lr) --
this design ADDS: (a) width x lr INTERACTION cells (2x2, testing whether
the two knobs combine additively or not), (b) depth as a new factor,
(c) optimizer as a new factor, (d) explicit pre-registered direction so
"expected" is not asserted after seeing data.

Design: 2 (width: 32,128) x 2 (lr: 5e-4, 2e-3) interaction grid + depth in
{1,3} + optimizer in {sgd_momentum} as separate one-off arms, all at 2
boundary-adjacent (alpha, wd) cells (2.5,0.085) and (2.25,0.125), 5 seeds.

(2x2 + 2 + 1) x 2 cells x 5 seeds = 70 runs x ~95s ~= 1.85h
-> results/m11_factorial.json
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import ARCounter, to_tensors, param_l2, scale_init
from p4_freq_phase import region_acc

DEV = "cuda"
CELLS = [(2.5, 0.085), (2.25, 0.125)]

PREREGISTERED_DIRECTIONS = {
    "d=32": "ceiling shifts LEFT (harder) vs baseline d=64",
    "d=128": "ceiling shifts RIGHT (easier) vs baseline d=64",
    "lr=5e-4": "ceiling shifts RIGHT (easier) vs baseline lr=1e-3",
    "lr=2e-3": "ceiling shifts LEFT (harder) vs baseline lr=1e-3",
    "d=32,lr=5e-4": "interaction: direction of (d=32 harder) + (lr=5e-4 easier) -- net unclear, this cell tests additivity",
    "d=128,lr=2e-3": "interaction: direction of (d=128 easier) + (lr=2e-3 harder) -- net unclear, this cell tests additivity",
    "layers=1": "ceiling shifts LEFT (less capacity)",
    "layers=3": "ceiling shifts RIGHT (more capacity)",
    "sgd_momentum": "worse grokking overall (Omnigrok/Power: adaptive optimizers help grokking)",
}


def run_variant(n, alpha, wd, seed, max_steps, d=64, layers=2, lr=1e-3,
                 batch=128, isc=10.0, optimizer='adamw', log_every=250):
    torch.manual_seed(seed)
    allN = np.arange(2 ** n, dtype=np.int64)
    X, M = to_tensors(allN, n, DEV)
    w = (allN + 1.0) ** (-alpha); w /= w.sum()
    order = np.argsort(-w)
    hi_idx = order[:len(order) // 10]
    lo_idx = order[len(order) // 2:]
    rng = np.random.default_rng(seed + 1000)

    model = ARCounter(n, d=d, layers=layers).to(DEV)
    scale_init(model, isc)
    if optimizer == 'adamw':
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    elif optimizer == 'sgd_momentum':
        opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=wd)
    else:
        raise ValueError(optimizer)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max_steps)
    lf = torch.nn.CrossEntropyLoss(reduction="none")

    steps, aunif, ahi, alo = [], [], [], []
    for step in range(max_steps + 1):
        model.train()
        idx = rng.choice(2 ** n, size=batch, replace=True, p=w)
        idx_t = torch.from_numpy(idx).to(DEV)
        xb, mb = X[idx_t], M[idx_t]
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
    tail = slice(-max(1, len(aunif) // 5), None)
    return dict(alpha=alpha, wd=wd, seed=seed, d=d, layers=layers, lr=lr,
                optimizer=optimizer, max_steps=max_steps,
                unif_tail=float(np.mean(aunif[tail])),
                hi_tail=float(np.mean(ahi[tail])), lo_tail=float(np.mean(alo[tail])))


def verdict(r):
    if r['unif_tail'] > 0.9:
        return "GROK"
    if r['hi_tail'] > 0.9 and r['unif_tail'] < 0.5:
        return "TRAP"
    if r['hi_tail'] < 0.9 and r['unif_tail'] < 0.5:
        return "CRUSH"
    return "PARTIAL"


VARIANTS = [
    dict(d=32), dict(d=128),
    dict(lr=5e-4), dict(lr=2e-3),
    dict(d=32, lr=5e-4), dict(d=128, lr=2e-3),
    dict(layers=1), dict(layers=3),
    dict(optimizer='sgd_momentum'),
]


def main():
    out_path = "results/m11_factorial.json"
    try:
        out = json.load(open(out_path))
        print(f"resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for alpha, wd in CELLS:
        for variant in VARIANTS:
            for s in range(5):
                key = (alpha, wd, s, variant.get('d', 64), variant.get('layers', 2),
                       variant.get('lr', 1e-3), variant.get('optimizer', 'adamw'))
                if any((o['alpha'], o['wd'], o['seed'], o['d'], o['layers'],
                        o['lr'], o['optimizer']) == key for o in out):
                    continue
                ts = time.time()
                r = run_variant(10, alpha, wd, s, max_steps=60000, **variant)
                v = verdict(r)
                tag = ",".join(f"{k}={v_}" for k, v_ in variant.items())
                print(f"[{tag}] a={alpha} wd={wd} s{s} | unif={r['unif_tail']:.3f} "
                      f"hi={r['hi_tail']:.3f} | {v} ({time.time()-ts:.0f}s)", flush=True)
                out.append(dict(verdict=v, tag=tag, **r))
                json.dump(out, open(out_path, "w"))
    print(f"\ndone: {len(out)} runs, {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
