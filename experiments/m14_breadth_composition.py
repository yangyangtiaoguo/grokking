"""M14 -- breadth-vs-composition decoupling (Appendix D).

Addresses the round-8/9 external reviews' shared core question: does the
rescue effect come from BREADTH (how many distinct states the injected slot
can be drawn from) or from COMPOSITION (whether bottleneck/long-carry states
are included), given that M8b's rare_short vs uniform comparison changes both
at once (102 non-bottleneck states -> all 1024 states, crossing the
bottleneck-inclusion line at the same time)?

Design: hold composition FIXED (bottleneck states, c(x)>=n//2=5, NEVER
included in the injection pool -- there are 32 such states out of 1024) and
vary ONLY breadth: the injection pool is the K most-Zipf-rare non-bottleneck
states, K in {102, 300, 600, 992}. K=102 reproduces M8b's rare_short pool
exactly (same seeds would give the same trajectory up to the k=1 draw itself,
since rare_short_idx is deterministic given (n, alpha) and this pool
construction is identical). K=992 is ALL non-bottleneck states -- the largest
breadth achievable while keeping composition fixed (bottleneck-excluded).

If K=992 still fails to rescue (as rare_short/K=102 does), breadth alone
(within non-bottleneck states) is not sufficient -- composition (bottleneck
inclusion) is doing the work, not breadth. If some intermediate K rescues,
breadth alone is sufficient and composition is not required.

alpha=2.5, wd=0.3, k=1 per batch of 128, 60k steps -- exactly the M8b/rescue
battery cell. 4 K values x 8 seeds = 32 runs x ~90s ~= 48min ->
results/m14_breadth_composition.json.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import ARCounter, to_tensors, param_l2, scale_init
from p4_freq_phase import region_acc

DEV = "cuda"

N_BITS = 10
ALPHA = 2.5
WD = 0.3
LR = 1e-3
ISC = 10.0
D = 64
BATCH = 128
MAX_STEPS = 60000
K_VALUES = [102, 300, 600, 992]


def carry_lengths(n):
    N = 2 ** n
    return np.array([bin(i)[2:][::-1].split('0')[0].__len__() for i in range(N)], dtype=np.int64)


def run_one(K, seed, n=N_BITS, alpha=ALPHA, wd=WD, lr=LR, isc=ISC, d=D,
            batch=BATCH, max_steps=MAX_STEPS, log_every=250):
    torch.manual_seed(seed)
    N = 2 ** n
    allN = np.arange(N, dtype=np.int64)
    X, M = to_tensors(allN, n, DEV)
    w = (allN + 1.0) ** (-alpha); w /= w.sum()
    order = np.argsort(-w)
    hi_idx = order[:N // 10]
    lo_idx = order[N // 2:]
    rng = np.random.default_rng(seed + 1000)

    cl = carry_lengths(n)
    non_bottleneck = np.where(cl < n // 2)[0]
    assert len(non_bottleneck) == 992
    pool = non_bottleneck[np.argsort(w[non_bottleneck])][:K]

    model = ARCounter(n, d=d).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max_steps)
    lf = torch.nn.CrossEntropyLoss(reduction="none")

    k = 1
    steps, aunif, ahi, alo = [], [], [], []
    for step in range(max_steps + 1):
        model.train()
        inj = rng.choice(pool, size=k, replace=True)
        idx = np.concatenate([rng.choice(N, size=batch - k, replace=True, p=w), inj])
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
            aunif.append(region_acc(model, X, M, np.arange(N)))
            ahi.append(region_acc(model, X, M, hi_idx))
            alo.append(region_acc(model, X, M, lo_idx))
    tail = slice(-max(1, len(aunif) // 5), None)
    return dict(alpha=alpha, wd=wd, seed=seed, K=int(K), pool_size=int(len(pool)),
                k=k, batch=batch, max_steps=max_steps,
                unif_tail=float(np.mean(aunif[tail])), unif_min=float(np.min(aunif[tail])),
                hi_tail=float(np.mean(ahi[tail])), lo_tail=float(np.mean(alo[tail])))


def verdict(r):
    if r['unif_tail'] > 0.9:
        return "GROK"
    if r['hi_tail'] > 0.9 and r['unif_tail'] < 0.5:
        return "TRAP"
    if r['hi_tail'] < 0.9 and r['unif_tail'] < 0.5:
        return "CRUSH"
    return "PARTIAL"


def main():
    out_path = "results/m14_breadth_composition.json"
    try:
        out = json.load(open(out_path))
        print(f"resuming with {len(out)} existing runs")
    except FileNotFoundError:
        out = []
    t0 = time.time()
    for K in K_VALUES:
        for s in range(8):
            key = (K, s)
            if any((o['K'], o['seed']) == key for o in out):
                continue
            ts = time.time()
            r = run_one(K, s)
            v = verdict(r)
            print(f"K={K:4d} s{s} | unif={r['unif_tail']:.3f} hi={r['hi_tail']:.3f} | {v} ({time.time()-ts:.0f}s)",
                  flush=True)
            out.append(dict(verdict=v, **r))
            json.dump(out, open(out_path, "w"))
    print(f"\ndone: {len(out)} runs, {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
