"""
P0 — Zero-GPU combinatorics precheck for the Grokkability phase-diagram proposal.

Tests Lemma A / Lemma B on carry-chain statistics under magnitude-Zipf sampling
P_alpha(x) ∝ (x+1)^(−alpha), x ∈ {0,...,2^n−1}.

carry chain length c(x) = number of trailing 1-bits of x (bits that flip on +1).

Go/No-Go: does E_alpha[c] vs alpha show a KINK at alpha=1, and does
Pr_alpha(c>=k) decay at rate 2^(−alpha) for alpha>1?  If no kink at any n,
the alpha=1 phase-transition claim's combinatorial premise fails.

Exact enumeration (no Monte Carlo) for n<=16. Cross-checks the empirical
carry-chain distribution against the Lemma A closed form.
"""
import numpy as np


def trailing_ones(x):
    """c(x) = number of trailing 1 bits. Vectorized over a numpy int array."""
    x = x.astype(np.int64)
    c = np.zeros_like(x)
    active = np.ones_like(x, dtype=bool)
    # iterate bit by bit; cheap for n<=16
    bit = 0
    while active.any():
        mask = ((x >> bit) & 1) == 1
        c[active & mask] += 1
        active = active & mask
        bit += 1
        if bit > 64:
            break
    return c


def zipf_weights(n, alpha):
    x = np.arange(2 ** n, dtype=np.float64)
    w = (x + 1.0) ** (-alpha)
    return w / w.sum()


def carry_stats(n, alpha):
    """Return E[c], Pr(c>=k) array, and P(x) under magnitude-Zipf-alpha."""
    x = np.arange(2 ** n, dtype=np.int64)
    c = trailing_ones(x)
    p = zipf_weights(n, alpha)
    Ec = float((c * p).sum())
    kmax = n + 1
    pr_ge = np.array([p[c >= k].sum() for k in range(0, kmax + 1)])
    return Ec, pr_ge, c, p


def lemma_A_closed_form(n, alpha, k):
    """Pr_alpha(c>=k) = 2^(-k*alpha) * sum_{j=0}^{2^(n-k)-1}(j+1)^(-alpha)
                        / sum_{x=0}^{2^n-1}(x+1)^(-alpha)."""
    if k > n:
        return 0.0
    denom = ((np.arange(2 ** n) + 1.0) ** (-alpha)).sum()
    j = np.arange(2 ** (n - k))
    numer = (2.0 ** (-k * alpha)) * ((j + 1.0) ** (-alpha)).sum()
    return numer / denom


def main():
    alphas = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    ns = [8, 12, 16]

    print("=" * 70)
    print("P0: carry-chain statistics under magnitude-Zipf(alpha)")
    print("=" * 70)

    # --- 1. Cross-check Lemma A closed form vs exact enumeration ---
    print("\n[1] Lemma A closed-form vs exact enumeration (n=12):")
    n = 12
    max_err = 0.0
    for alpha in alphas:
        _, pr_ge, _, _ = carry_stats(n, alpha)
        for k in range(1, n + 1):
            cf = lemma_A_closed_form(n, alpha, k)
            max_err = max(max_err, abs(cf - pr_ge[k]))
    print(f"    max |closed_form - exact| over all (alpha,k) = {max_err:.2e}")
    print(f"    -> Lemma A {'VERIFIED' if max_err < 1e-9 else 'MISMATCH!!'}")

    # --- 2. E_alpha[c] vs alpha: look for kink at alpha=1 ---
    print("\n[2] E_alpha[c] vs alpha (kink at alpha=1?):")
    header = "  n   " + "  ".join(f"a={a:<4}" for a in alphas)
    print(header)
    Ec_table = {}
    for n in ns:
        row = []
        for alpha in alphas:
            Ec, _, _, _ = carry_stats(n, alpha)
            row.append(Ec)
        Ec_table[n] = row
        print(f"  {n:<3} " + "  ".join(f"{v:6.3f}" for v in row))

    # discrete second difference around alpha=1 as a kink diagnostic
    print("\n    Kink diagnostic: |slope(alpha>1) - slope(alpha<1)| at alpha=1")
    idx1 = alphas.index(1.0)
    for n in ns:
        row = Ec_table[n]
        left = (row[idx1] - row[idx1 - 1]) / (alphas[idx1] - alphas[idx1 - 1])
        right = (row[idx1 + 1] - row[idx1]) / (alphas[idx1 + 1] - alphas[idx1])
        print(f"      n={n:<3}  slope_left={left:+.3f}  slope_right={right:+.3f}"
              f"  |Δslope|={abs(right-left):.3f}")

    # --- 3. Decay rate of Pr(c>=k): should -> 2^(-alpha) for alpha>1 ---
    print("\n[3] Tail decay ratio Pr(c>=k+1)/Pr(c>=k) (should -> 2^(-alpha) for alpha>1):")
    n = 16
    for alpha in [0.0, 1.0, 1.5, 2.0]:
        _, pr_ge, _, _ = carry_stats(n, alpha)
        ratios = [pr_ge[k + 1] / pr_ge[k] for k in range(1, 8) if pr_ge[k] > 0]
        target = 2.0 ** (-alpha)
        mid = np.mean(ratios[2:6]) if len(ratios) >= 6 else np.mean(ratios)
        print(f"    alpha={alpha}: mid-tail ratio~{mid:.3f}  target 2^(-a)={target:.3f}"
              f"  ratios={[f'{r:.3f}' for r in ratios]}")

    # --- 4. d0(alpha) = E_0[c] - E_alpha[c], per-balanced-sample surprise ---
    print("\n[4] d0(alpha) = E_0[c] - E_alpha[c]  (n=16, monotone increasing?):")
    n = 16
    E0, _, _, _ = carry_stats(n, 0.0)
    d0s = []
    for alpha in alphas:
        Ec, _, _, _ = carry_stats(n, alpha)
        d0s.append(E0 - Ec)
    print("    " + "  ".join(f"a={a}:{d:.3f}" for a, d in zip(alphas, d0s)))
    mono = all(d0s[i] <= d0s[i + 1] + 1e-9 for i in range(len(d0s) - 1))
    print(f"    -> d0(alpha) monotone increasing: {mono}")

    # --- save numbers for the writeup ---
    np.savez("results/p0_carry_stats.npz",
             alphas=np.array(alphas), ns=np.array(ns),
             Ec={str(k): np.array(v) for k, v in Ec_table.items()},
             d0=np.array(d0s))
    print("\nSaved -> results/p0_carry_stats.npz")


if __name__ == "__main__":
    main()
