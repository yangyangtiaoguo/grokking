"""
P1 v2 — Does the memorizing solution get CHEAPER under skew? (CORRECT AR task)

v1 used the wrong (little-endian parallel) task; this is the rewrite on
task_ar.py. Same Go/No-Go logic:

  Train to MEMORIZATION only (low wd, until train_seq_acc >= 0.99) at several
  alpha. At the memorization checkpoint measure:
    - ||theta||_2            (empirical complexity proxy -> Deltaell(alpha) trend)
    - K(alpha)               # distinct carry patterns the train set must fit
    - carry coverage         mean/max c in train set, #samples with c >= n/2
                             (does skew starve long-carry pressure?)
    - eval seq acc           generalization gap at the memorization moment

  optimistic  : ||theta||, K ~ flat in alpha  -> Deltaell ~ const, theory kink intact
  pessimistic : both fall fast with alpha     -> skew doubly benefits memorization,
                reframe as such (this is falsifiable content, not failure)

CLI (defaults = locked testbed A2: n=10, frac=0.3, init=10, batch=128; only wd
is lowered to stop at the memorization checkpoint):
  .venv/bin/python experiments/p1v2_memorization_ar.py [--n 10] [--frac 0.3]
      [--wd 0.01] [--init 10.0] [--batch 128] [--lr 1e-3] [--steps 8000]
      [--seeds 0,1,2] [--alphas 0.0,0.5,1.0,1.5,2.0]
"""
import sys, time, json, argparse
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_ar import (ARCounter, split_train_eval, zipf_split_train, to_tensors,
                     param_l2, seq_accuracy, scale_init)

DEV = "cuda"


def trailing_ones(x):
    x = np.asarray(x, dtype=np.int64)
    c = np.zeros_like(x)
    active = np.ones_like(x, dtype=bool)
    bit = 0
    while active.any():
        mask = ((x >> bit) & 1) == 1
        c[active & mask] += 1
        active &= mask
        bit += 1
        if bit > 60:
            break
    return c


def carry_coverage(train_x, n):
    c = trailing_ones(train_x)
    # distinct (c, low-prefix) classes = distinct flip patterns the memorizer fits
    key = train_x % (2 ** np.minimum(c + 1, n))
    K = len(set(zip(c.tolist(), key.tolist())))
    return dict(K=K, c_mean=float(c.mean()), c_max=int(c.max()),
                n_long=int((c >= n // 2).sum()),
                frac_long=float((c >= n // 2).mean()))


def run_one(n, alpha, frac, wd, lr, seed, max_steps, isc, batch,
            mem_thresh=0.99, d=64):
    torch.manual_seed(seed)
    if alpha == 0.0:
        trN, evN = split_train_eval(n, frac, seed)
    else:
        trN, evN = zipf_split_train(n, alpha, frac, seed)
    Xtr, Mtr = to_tensors(trN, n, DEV)
    Xev, Mev = to_tensors(evN, n, DEV)
    model = ARCounter(n, d=d).to(DEV)
    scale_init(model, isc)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    lf = torch.nn.CrossEntropyLoss(reduction="none")
    rng = np.random.default_rng(seed + 1000)
    B = Xtr.shape[0]

    mem_step = None
    for step in range(max_steps + 1):
        model.train()
        idx = torch.from_numpy(rng.choice(B, size=min(batch, B),
                                          replace=False)).to(DEV)
        xb, mb = Xtr[idx], Mtr[idx]
        lo = model(xb); tg = xb.roll(-1, 1)
        l = lf(lo.reshape(-1, lo.size(-1)), tg.reshape(-1))
        loss = (l * mb.reshape(-1)).sum() / mb.sum()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 100 == 0 or step == max_steps:
            tr = seq_accuracy(model, Xtr, Mtr)
            if tr >= mem_thresh and mem_step is None:
                mem_step = step
                ev = seq_accuracy(model, Xev, Mev)
                stats = dict(alpha=alpha, seed=seed, mem_step=step,
                             train_seq=float(tr), eval_seq=float(ev),
                             theta=param_l2(model), n_train=int(trN.size),
                             **carry_coverage(trN, n))
                return stats
    tr = seq_accuracy(model, Xtr, Mtr)
    ev = seq_accuracy(model, Xev, Mev)
    return dict(alpha=alpha, seed=seed, mem_step=None,
                train_seq=float(tr), eval_seq=float(ev),
                theta=param_l2(model), n_train=int(trN.size),
                **carry_coverage(trN, n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--frac", type=float, default=0.3)
    ap.add_argument("--wd", type=float, default=0.01)
    ap.add_argument("--init", type=float, default=10.0)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--seeds", type=str, default="0,1,2")
    ap.add_argument("--alphas", type=str, default="0.0,0.5,1.0,1.5,2.0")
    a = ap.parse_args()
    seeds = [int(x) for x in a.seeds.split(",")]
    alphas = [float(x) for x in a.alphas.split(",")]

    print(f"P1v2 (AR big-endian): n={a.n} N={2**a.n} frac={a.frac} wd={a.wd} "
          f"init={a.init} batch={a.batch} lr={a.lr} steps={a.steps} seeds={seeds}")
    print(f"{'alpha':>6} {'seed':>4} {'mem@':>6} {'trSeq':>6} {'evSeq':>6} "
          f"{'|th|':>7} {'K':>6} {'cMean':>6} {'cMax':>4} {'nLong':>5}")
    rows = []
    t0 = time.time()
    for alpha in alphas:
        for s in seeds:
            r = run_one(a.n, alpha, a.frac, a.wd, a.lr, s, a.steps,
                        a.init, a.batch)
            rows.append(r)
            print(f"{alpha:6.1f} {s:4d} {str(r['mem_step']):>6} "
                  f"{r['train_seq']:6.3f} {r['eval_seq']:6.3f} {r['theta']:7.2f} "
                  f"{r['K']:6d} {r['c_mean']:6.3f} {r['c_max']:4d} {r['n_long']:5d}")

    print("\nAggregate (mean over seeds):")
    print(f"{'alpha':>6} {'|theta|':>9} {'K':>7} {'evSeq':>7} {'cMean':>7}")
    agg = {}
    for alpha in alphas:
        rs = [r for r in rows if r['alpha'] == alpha]
        agg[str(alpha)] = dict(
            theta=float(np.mean([r['theta'] for r in rs])),
            K=float(np.mean([r['K'] for r in rs])),
            eval=float(np.mean([r['eval_seq'] for r in rs])),
            c_mean=float(np.mean([r['c_mean'] for r in rs])),
            n_mem=sum(r['mem_step'] is not None for r in rs))
        print(f"{alpha:6.1f} {agg[str(alpha)]['theta']:9.2f} "
              f"{agg[str(alpha)]['K']:7.0f} {agg[str(alpha)]['eval']:7.3f} "
              f"{agg[str(alpha)]['c_mean']:7.3f}")

    t0v, t2v = agg['0.0'], agg['2.0']
    print(f"\ntheta(2)/theta(0) = {t2v['theta']/t0v['theta']:.3f}   "
          f"K(2)/K(0) = {t2v['K']/t0v['K']:.3f}   "
          f"c_mean(2)/c_mean(0) = {t2v['c_mean']/t0v['c_mean']:.3f}")
    print("both ratios ~1 => optimistic (Deltaell flat); <<1 => skew cheapens memory.")

    json.dump(dict(config=vars(a) | dict(alphas=alphas), rows=rows, agg=agg),
              open("results/p1v2_memorization_ar.json", "w"), indent=2)
    print(f"\nelapsed {time.time()-t0:.0f}s -> results/p1v2_memorization_ar.json")


if __name__ == "__main__":
    main()
