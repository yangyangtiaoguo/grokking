"""
P1 — Does the memorizing solution get CHEAPER under skew?  i.e. is Δℓ(α) flat or falling?

Train to MEMORIZATION only (low weight decay, until train_acc≈100%, eval low),
at several alpha. Measure at the memorization checkpoint:
  - ||theta||_2                          (empirical complexity proxy)
  - K(alpha) = # distinct carry patterns the train set must fit  (zero-cost theory proxy)

Go/No-Go:
  optimistic  : L(C_mem,alpha) ~ flat        -> Δℓ≈const, α=1 crossover in λ_c stable
  neutral     : slow decline (< ΔD's)        -> crossover shifted, needs numeric λ_c
  pessimistic : falls ~ as fast as ΔD(alpha) -> reframe as "skew doubly benefits memorization"

C2 (rescue dose) is SAFE regardless (uses measured λ_c), so P1 only decides the C1 kink story.
"""
import sys, time, json
sys.path.insert(0, "experiments")
import numpy as np
import torch
from task_model import (Counter, make_split, to_tensors, param_l2,
                        bit_and_seq_acc, carry_chain_len, int_to_bits_lsb)

DEV = "cuda"


def distinct_carry_patterns(train_x, n):
    """K = number of distinct (value mod 2^k for the maximal trailing-run) patterns
    the memorizer must handle. Proxy: distinct low-order residues that determine the
    output flip pattern = distinct (trailing-ones length, plus the bit above) classes,
    but simplest faithful proxy = # distinct carry-chain lengths present weighted by
    how many distinct low-prefixes appear. We use: # distinct values of (x mod 2^{c(x)+1}).
    That is exactly the info determining which bits flip."""
    c = carry_chain_len(train_x)
    key = train_x % (2 ** np.minimum(c + 1, n))
    # combine (c, key) to be safe
    combo = set(zip(c.tolist(), key.tolist()))
    return len(combo)


def train_to_memorization(n, alpha, n_train, seed, wd, max_steps, lr=1e-3,
                          mem_thresh=0.999, d=64):
    torch.manual_seed(seed)
    train_x, eval_x = make_split(n, alpha, n_train, seed=seed)
    Xtr, Ytr = to_tensors(train_x, n, DEV)
    Xev, Yev = to_tensors(eval_x, n, DEV)
    model = Counter(n, d=d, heads=4, layers=2).to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    lossf = torch.nn.BCEWithLogitsLoss()

    mem_step = None
    for step in range(max_steps + 1):
        model.train()
        loss = lossf(model(Xtr), Ytr)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 200 == 0 or step == max_steps:
            _, tr_seq = bit_and_seq_acc(model, Xtr, Ytr)
            _, ev_seq = bit_and_seq_acc(model, Xev, Yev)
            if tr_seq >= mem_thresh and mem_step is None:
                mem_step = step
                # record memorization-checkpoint stats
                stats = dict(mem_step=step, train_seq=tr_seq, eval_seq=ev_seq,
                             theta=param_l2(model),
                             n_train_unique=int(train_x.size),
                             K=distinct_carry_patterns(train_x, n),
                             frac_states=float(train_x.size / 2 ** n))
                # keep training a bit to confirm it stays memorized (not grokking away)
                return stats, model
    # never memorized
    _, tr_seq = bit_and_seq_acc(model, Xtr, Ytr)
    _, ev_seq = bit_and_seq_acc(model, Xev, Yev)
    return dict(mem_step=None, train_seq=tr_seq, eval_seq=ev_seq,
                theta=param_l2(model), n_train_unique=int(train_x.size),
                K=distinct_carry_patterns(train_x, n),
                frac_states=float(train_x.size / 2 ** n)), model


def main():
    n = 12
    N = 2 ** n
    n_train = int(0.5 * N)          # sample budget; Zipf collapses to fewer unique
    alphas = [0.0, 0.5, 1.0, 1.5, 2.0]
    seeds = [0, 1, 2]
    wd = 0.01                        # low: memorize, don't grok
    max_steps = 4000

    print(f"P1: n={n} N={N} n_train_samples={n_train} wd={wd} max_steps={max_steps}")
    print(f"{'alpha':>6} {'seed':>4} {'uniq':>6} {'frac':>5} {'K':>6} "
          f"{'mem@':>6} {'trSeq':>6} {'evSeq':>6} {'|th|':>7}")
    results = []
    t0 = time.time()
    for alpha in alphas:
        for seed in seeds:
            s, _ = train_to_memorization(n, alpha, n_train, seed, wd, max_steps)
            s.update(alpha=alpha, seed=seed)
            results.append(s)
            print(f"{alpha:6.1f} {seed:4d} {s['n_train_unique']:6d} "
                  f"{s['frac_states']:.2f} {s['K']:6d} "
                  f"{str(s['mem_step']):>6} {s['train_seq']:6.3f} "
                  f"{s['eval_seq']:6.3f} {s['theta']:7.2f}")

    # aggregate: theta and K vs alpha
    print("\nAggregate (mean over seeds):")
    print(f"{'alpha':>6} {'K':>8} {'|theta|':>9} {'evalSeq':>8}")
    agg = {}
    for alpha in alphas:
        rs = [r for r in results if r['alpha'] == alpha]
        K = np.mean([r['K'] for r in rs])
        th = np.mean([r['theta'] for r in rs])
        ev = np.mean([r['eval_seq'] for r in rs])
        agg[alpha] = dict(K=K, theta=th, eval=ev)
        print(f"{alpha:6.1f} {K:8.0f} {th:9.2f} {ev:8.3f}")

    # verdict on K trend (theory proxy) — normalized drop from alpha=0
    K0 = agg[0.0]['K']; K2 = agg[2.0]['K']
    th0 = agg[0.0]['theta']; th2 = agg[2.0]['theta']
    print(f"\nK(2)/K(0) = {K2/K0:.3f}   theta(2)/theta(0) = {th2/th0:.3f}")
    print("Interpretation guide: both ~1.0 => optimistic (Δℓ flat);"
          " both <<1 => pessimistic (skew cheapens memory).")

    with open("results/p1_memorization.json", "w") as f:
        json.dump({"results": results,
                   "agg": {str(k): v for k, v in agg.items()},
                   "config": dict(n=n, n_train=n_train, wd=wd,
                                  max_steps=max_steps, seeds=seeds)}, f, indent=2)
    print(f"\nelapsed {time.time()-t0:.1f}s  -> results/p1_memorization.json")


if __name__ == "__main__":
    main()
