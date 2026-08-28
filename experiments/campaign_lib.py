"""Shared library for the formal campaign (M0-M5).

Generalizes p5_rescue.run with an injection-pool parameter so the rescue
battery (M2) can inject uniform / long-carry (tail) / head states at matched
dose k. Everything else — A2 recipe defaults, region metrics, trajectory
logging — is verbatim from the pilot chain so formal results stay directly
comparable with P4-P11.

Injection pools (n=10 unless noted):
  uniform : all 2^n states                 (the m* protocol of P5/P6)
  tail    : states with carry length >= n//2 (longest carry chains — the
            bottleneck states of the ripple-carry algorithm)
  head    : lowest-x decile                (frequent head states — negative
            control: should NOT rescue if the bottleneck-coverage story holds)
"""
import sys
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import (ARCounter, to_tensors, param_l2, scale_init)
from p4_freq_phase import region_acc

DEV = "cuda"


def carry_lengths(n):
    """trailing-ones count c(x) for every x in [0, 2^n)."""
    N = 2 ** n
    return np.array([bin(i)[2:][::-1].split('0')[0].__len__()
                     for i in range(N)], dtype=np.int64)


def inject_pool(n, mode):
    N = 2 ** n
    if mode == 'uniform':
        return np.arange(N)
    if mode == 'head':
        return np.arange(N // 10)
    if mode == 'tail':
        return np.where(carry_lengths(n) >= n // 2)[0]
    raise ValueError(f"unknown inject mode {mode}")


def run_cell(n, alpha, wd, seed, max_steps=60000, lr=1e-3, batch=128,
             isc=10.0, k=0, inject='uniform', d=64, log_every=250):
    """One training run. Returns the same dict schema as p5_rescue.run
    (plus inject mode), with full A_unif/A_hi/A_lo trajectories for tau
    extraction in M3."""
    torch.manual_seed(seed)
    allN = np.arange(2 ** n, dtype=np.int64)
    X, M = to_tensors(allN, n, DEV)
    w = (allN + 1.0) ** (-alpha); w /= w.sum()
    order = np.argsort(-w)
    hi_idx = order[:len(order) // 10]
    lo_idx = order[len(order) // 2:]
    rng = np.random.default_rng(seed + 1000)
    pool = inject_pool(n, inject)
    assert 0 <= k <= batch

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
            rng.choice(pool, size=k, replace=True),
        ]) if k > 0 else rng.choice(2 ** n, size=batch, replace=True, p=w)
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
    return dict(alpha=alpha, wd=wd, seed=seed, k=k, inject=inject,
                batch=batch, max_steps=max_steps,
                unif_tail=float(np.mean(aunif[tail])), unif_min=float(np.min(aunif[tail])),
                hi_tail=float(np.mean(ahi[tail])), lo_tail=float(np.mean(alo[tail])),
                thF=th_h[-1], steps=steps, aunif=aunif, ahi=ahi, alo=alo, th=th_h)


def verdict(r):
    """Frozen P8 rule — do not change during the campaign."""
    if r['unif_tail'] > 0.9:
        return "GROK"
    if r['hi_tail'] > 0.9 and r['unif_tail'] < 0.5:
        return "TRAP"
    if r['hi_tail'] < 0.9 and r['unif_tail'] < 0.5:
        return "CRUSH"
    return "PARTIAL"


def t_grok(r, thr=0.9):
    """First step with SUSTAINED A_unif > thr (M3 kinetics). None if never."""
    a = np.asarray(r['aunif']); s = np.asarray(r['steps'])
    for i in range(len(a)):
        if a[i] > thr and np.mean(a[i:]) > thr:
            return int(s[i])
    return None


def summary_line(r):
    v = verdict(r)
    return (f"a={r['alpha']:4.2f} wd={r['wd']:4.3f} k={r.get('k', 0)} "
            f"inj={r.get('inject', '-')[:4]:<4} b={r.get('batch', 128):<3} "
            f"B={r['max_steps']//1000}k s{r['seed']} | "
            f"unif={r['unif_tail']:6.3f} hi={r['hi_tail']:6.3f} | {v}")
