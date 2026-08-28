"""Modular addition task (Power et al. 2022 style) — M6 second-task existence
check. Reuses task_ar.ARCounter verbatim (vocab param already generic; n is
unused in forward, only stored).

Sequence [a, b, SEP, c], vocab = p+1 (SEP = p). Loss only at the SEP position
(predicting c). Frequency protocol (not subset-selection, per P1v2 verdict):
population = all p^2 (a,b) pairs, minibatch sampled with replacement weighted
by Zipf(alpha) over the combined index x = a*p + b. Skew concentrates mass on
small a (since x = a*p+b, x small implies a small for large p), so it mainly
starves LARGE first-operand pairs — an arbitrary but valid analog of the
counting task's "rare state" starvation; the point of M6 is existence, not a
perfect carry-chain analog.
"""
import sys
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import ARCounter, param_l2, scale_init  # noqa: F401 (re-exported)

DEV = "cuda"


def make_batch(idx, p):
    """idx: array of combined indices in [0, p^2). Returns (B,4) int64 ids."""
    a = idx // p
    b = idx % p
    c = (a + b) % p
    seq = np.stack([a, b, np.full_like(a, p), c], axis=1).astype(np.int64)
    return seq


def to_tensor_all(p, device):
    idx = np.arange(p * p, dtype=np.int64)
    seq = make_batch(idx, p)
    return torch.from_numpy(seq).to(device), idx


@torch.no_grad()
def region_acc_modadd(model, seq_all, sub_idx, batch=8192):
    """Whole-example accuracy (predict c correctly) over a subset of pair indices."""
    model.eval()
    ok = tot = 0
    for i in range(0, len(sub_idx), batch):
        ii = sub_idx[i:i + batch]
        x = seq_all[ii]
        logits = model(x)
        pred = logits.argmax(-1)
        tgt = x.roll(-1, dims=1)
        correct = (pred[:, 2] == tgt[:, 2])  # position 2 (SEP) predicts c
        ok += correct.sum().item(); tot += len(ii)
    return ok / tot


def inject_pool_modadd(p, idx_all, a_of_idx, mode):
    """Injection pools for the targeted-rescue control, analogous to
    campaign_lib.inject_pool for the counting task. 'tail' = largest-a states
    (rarest under the operand-a Zipf skew — the modadd analogue of longest
    carry chains); 'head' = smallest-a states (most frequent, negative
    control); 'uniform' = all p^2 pairs."""
    if mode == 'uniform':
        return idx_all
    if mode == 'head':
        return idx_all[a_of_idx < max(1, p // 10)]
    if mode == 'tail':
        return idx_all[a_of_idx >= p - max(1, p // 10)]
    raise ValueError(f"unknown inject mode {mode}")


def run_modadd(p, alpha, wd, seed, max_steps, lr=1e-3, batch=128, isc=1.0,
               d=64, log_every=250, k=0, inject='uniform'):
    """Skew acts on operand `a` only (w(a,b) = Zipf(a) * Uniform(b)) — NOT on
    the combined index a*p+b. A combined-index Zipf concentrates >99.9% of
    mass on a=0 at alpha=2.5 (verified: mass(a=0)=0.9995), collapsing the
    task to a single operand value instead of the intended "rare but present
    across all classes" skew analogous to the counting task's carry chains."""
    torch.manual_seed(seed)
    seq_all, idx_all = to_tensor_all(p, DEV)
    N = p * p
    a_of_idx = idx_all // p
    wa = (np.arange(p) + 1.0) ** (-alpha); wa = wa / wa.sum()
    w = wa[a_of_idx] / p                    # uniform over b, Zipf over a
    w = w / w.sum()
    order = np.argsort(-w)
    hi_idx = order[:max(1, N // 10)]
    lo_idx = order[N // 2:]
    rng = np.random.default_rng(seed + 1000)
    pool = inject_pool_modadd(p, idx_all, a_of_idx, inject)

    model = ARCounter(n=4, d=d, vocab=p + 1).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max_steps)
    lf = torch.nn.CrossEntropyLoss(reduction="none")

    steps, aunif, ahi, alo, th_h = [], [], [], [], []
    for step in range(max_steps + 1):
        model.train()
        bidx = np.concatenate([
            rng.choice(N, size=batch - k, replace=True, p=w),
            rng.choice(pool, size=k, replace=True),
        ]) if k > 0 else rng.choice(N, size=batch, replace=True, p=w)
        xb = seq_all[torch.from_numpy(bidx).to(DEV)]
        lo = model(xb); tg = xb.roll(-1, 1)
        l = lf(lo[:, 2, :], tg[:, 2])   # single-position loss (predict c)
        loss = l.mean()
        opt.zero_grad(); loss.backward(); opt.step()
        sched.step()
        if step % log_every == 0 or step == max_steps:
            steps.append(step)
            aunif.append(region_acc_modadd(model, seq_all, np.arange(N)))
            ahi.append(region_acc_modadd(model, seq_all, hi_idx))
            alo.append(region_acc_modadd(model, seq_all, lo_idx))
            th_h.append(param_l2(model))
    tail = slice(-max(1, len(aunif) // 5), None)
    return dict(p=p, alpha=alpha, wd=wd, seed=seed, k=k, inject=inject, max_steps=max_steps,
                unif_tail=float(np.mean(aunif[tail])), unif_min=float(np.min(aunif[tail])),
                hi_tail=float(np.mean(ahi[tail])), lo_tail=float(np.mean(alo[tail])),
                thF=th_h[-1], steps=steps, aunif=aunif, ahi=ahi, alo=alo, th=th_h)


def verdict(r):
    if r['unif_tail'] > 0.9:
        return "GROK"
    if r['hi_tail'] > 0.9 and r['unif_tail'] < 0.5:
        return "TRAP"
    if r['hi_tail'] < 0.9 and r['unif_tail'] < 0.5:
        return "CRUSH"
    return "PARTIAL"
