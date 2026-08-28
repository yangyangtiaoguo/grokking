"""Dyck-1 balanced-parenthesis task -- third-task generalization check
(user-approved addition to the C6 generalization battery, alongside the
existing modular-addition task).

Design rationale: mirrors LARGECOUNTER's core structure (a model must
INTERNALLY TRACK a running state -- there, the carry/counter value; here,
the current bracket-nesting depth -- since the input does not expose it
directly) and its "deterministic positions only" loss masking (there: target
bits after '#'; here: positions where the next token is FORCED by Dyck-1
grammar, not free).

Vocab: {'(', ')', SEP} (ids 0, 1, 2; SEP acts as BOS, mirroring task_ar.py's
'#' role). For a full sequence of length 2L, a position t (predicting token
at t+1 from prefix up to t) is DETERMINISTIC iff:
  - depth_t == 0                (must open: only '(' is grammatically valid)
  - remaining == depth_t          (must close everything: only ')' is valid)
All other positions are AMBIGUOUS (either bracket keeps the path completable)
and are masked out of the loss -- exactly analogous to task_ar.py masking
loss to only the n forced target bits.

Skew axis: max-depth(path) is the Dyck-1 analogue of carry-chain length --
shallow (low max-depth) paths are common/easy, deep paths are rare and
require longer-range depth tracking. Paths are indexed by max-depth
(ascending) and Zipf(alpha)-weighted minibatch sampling (same frequency
protocol as task_ar.zipf_batch_sampler / task_modadd, per the P1v2 verdict
that subset-selection has no skew effect) concentrates training on shallow
paths as alpha grows, starving deep ones.

L=8 (2L=16) gives Catalan(8)=1430 valid paths -- small enough to enumerate
exhaustively and hold entirely in memory/GPU, matching the counting task's
exhaustive-state-space design (n=10 -> 1024 states).
"""
import sys
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import ARCounter, param_l2, scale_init  # noqa: F401 (re-exported)

DEV = "cuda"
SEP = 2
VOCAB = 3


def enumerate_dyck1(L):
    """All valid length-2L Dyck-1 paths as 0/1 arrays (1='(', 0=')'), plus
    each path's max nesting depth."""
    paths = []
    depths = []

    def rec(seq, depth, opens, closes):
        if opens == L and closes == L:
            paths.append(list(seq))
            depths.append(max(running_depth(seq)))
            return
        if opens < L:
            rec(seq + [1], depth + 1, opens + 1, closes)
        if closes < opens:
            rec(seq + [0], depth - 1, opens, closes + 1)

    def running_depth(seq):
        d, out = 0, []
        for tok in seq:
            d += 1 if tok == 1 else -1
            out.append(d)
        return out

    rec([], 0, 0, 0)
    return np.array(paths, dtype=np.int64), np.array(depths, dtype=np.int64)


def build_dataset(L, device):
    """Returns (seq, mask, depth_index):
    seq: (M, 2L+1) token ids = [SEP, path...] (SEP as BOS so the model
         predicts path[0] from a fixed start token, mirroring task_ar's
         '#'-then-target structure).
    mask: (M, 2L+1) 1.0 at deterministic-next-token positions, 0.0 elsewhere.
    depth_index: (M,) rarity index = argsort(max_depth) rank, ascending
         (shallow=common=low index, deep=rare=high index -- same convention
         as task_ar's x itself, where skew concentrates on LOW x)."""
    paths, max_depths = enumerate_dyck1(L)
    M = len(paths)
    seq = np.concatenate([np.full((M, 1), SEP, dtype=np.int64), paths], axis=1)
    mask = np.zeros((M, 2 * L + 1), dtype=np.float32)
    for i in range(M):
        d = 0
        for t in range(2 * L):
            remaining = 2 * L - t
            if d == 0 or remaining == d:
                mask[i, t] = 1.0   # predicting token at t+1 is forced
            d += 1 if paths[i, t] == 1 else -1
    order = np.argsort(max_depths, kind='stable')
    depth_index = np.empty(M, dtype=np.int64)
    depth_index[order] = np.arange(M)
    return (torch.from_numpy(seq).to(device), torch.from_numpy(mask).to(device),
            depth_index, max_depths)


@torch.no_grad()
def region_acc_dyck(model, seq, mask, sub_idx, batch=4096):
    model.eval()
    ok = tot = 0
    for i in range(0, len(sub_idx), batch):
        ii = sub_idx[i:i + batch]
        x = seq[ii]; m = mask[ii]
        logits = model(x)
        pred = logits.argmax(-1)
        tgt = x.roll(-1, dims=1)
        correct = ((pred == tgt) | (m == 0)).all(dim=1)
        ok += correct.sum().item(); tot += len(ii)
    return ok / tot


def run_dyck(L, alpha, wd, seed, max_steps, lr=1e-3, batch=128, isc=10.0,
             d=64, log_every=250, k=0, inject='uniform'):
    torch.manual_seed(seed)
    seq, mask, depth_index, max_depths = build_dataset(L, DEV)
    M = seq.shape[0]
    w = (depth_index + 1.0) ** (-alpha); w = w / w.sum()
    order = np.argsort(-w)
    hi_idx = order[:max(1, M // 10)]   # shallow/common paths
    lo_idx = order[M // 2:]            # deep/rare paths
    rng = np.random.default_rng(seed + 1000)

    if inject == 'uniform':
        pool = np.arange(M)
    elif inject == 'tail':
        pool = np.where(max_depths >= np.percentile(max_depths, 80))[0]
    elif inject == 'head':
        pool = np.where(max_depths <= np.percentile(max_depths, 20))[0]
    else:
        raise ValueError(inject)

    model = ARCounter(n=2 * L + 1, d=d, vocab=VOCAB).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max_steps)
    lf = torch.nn.CrossEntropyLoss(reduction="none")

    steps, aunif, ahi, alo, th_h = [], [], [], [], []
    for step in range(max_steps + 1):
        model.train()
        idx = np.concatenate([
            rng.choice(M, size=batch - k, replace=True, p=w),
            rng.choice(pool, size=k, replace=True),
        ]) if k > 0 else rng.choice(M, size=batch, replace=True, p=w)
        idx_t = torch.from_numpy(idx).to(DEV)
        xb, mb = seq[idx_t], mask[idx_t]
        lo = model(xb); tg = xb.roll(-1, 1)
        l = lf(lo.reshape(-1, lo.size(-1)), tg.reshape(-1))
        loss = (l * mb.reshape(-1)).sum() / mb.sum()
        opt.zero_grad(); loss.backward(); opt.step()
        sched.step()
        if step % log_every == 0 or step == max_steps:
            steps.append(step)
            aunif.append(region_acc_dyck(model, seq, mask, np.arange(M)))
            ahi.append(region_acc_dyck(model, seq, mask, hi_idx))
            alo.append(region_acc_dyck(model, seq, mask, lo_idx))
            th_h.append(param_l2(model))
    tail = slice(-max(1, len(aunif) // 5), None)
    return dict(L=L, alpha=alpha, wd=wd, seed=seed, k=k, inject=inject, max_steps=max_steps,
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
