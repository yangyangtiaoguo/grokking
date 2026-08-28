"""
Theory pre-registration (CPU only, no GPU).

Pre-computes the PARAMETER-FREE shape predictions that the alpha-sweep
experiment (M4) will be compared against, so the comparison is honest:
the curves are frozen BEFORE any training run under skew exists.

Quantities (all exact enumeration, Lemma A verified in P0 to 5.5e-17):
  E_alpha[c]      expected carry-chain length under magnitude-Zipf(alpha)
  d0(alpha)       = E_0[c] - E_alpha[c]   (per-sample carry-info deficit)
  s_n(alpha)      = d0(alpha)/E_0[c] = 1 - E_alpha[c]/E_0[c]
                  NOTE: E_0[c] == 1 - 2^(-n) EXACTLY (geom tail, truncated at c=n),
                  so d0(0)=0 and normalization must be by E_0[c], not d0(0).
                  s_n is the normalized lambda_c(alpha) SHAPE
                  (theory: lambda_c(alpha) = DeltaD(alpha)/Deltaell,
                   DeltaD(alpha) prop d0(alpha) under the weak ansatz;
                   overall scale/slope-sign pinned by measurement)
  kink(n)         |slope change at alpha=1|  -> n-sharpening crossover
  m*(alpha,lam)   = kappa*N*(1 - lam/lambda_c(alpha))
                  = kappa*N*(1 - (lam/lam_c0)/s_n(alpha))   [Deltaell-free]
                  (lam_c0 := lambda_c(0); m*(0,lam) = kappa*N*(1-lam/lam_c0))
  H(alpha)        held-out population mass if the frac-sized train set takes the
                  HIGHEST-weight states (deterministic version of skewed
                  without-replacement sampling). Diagnostic for the sign
                  question: does skew shrink the algorithm's data advantage
                  via rare long carries (d0 view) or via small held-out mass
                  (H view)?

Outputs: results/theory_curves.json, figures/theory_curves.png
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


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


def zipf_weights(n, alpha):
    x = np.arange(2 ** n, dtype=np.float64)
    w = (x + 1.0) ** (-alpha)
    return w / w.sum()


def Ec_exact(n, alpha):
    x = np.arange(2 ** n, dtype=np.int64)
    c = trailing_ones(x)
    p = zipf_weights(n, alpha)
    return float((c * p).sum())


def heldout_mass(n, alpha, frac):
    """Population mass of the states NOT in a top-weight train set of size frac*N."""
    p = zipf_weights(n, alpha)
    N = 2 ** n
    ntr = int(frac * N)
    if ntr <= 0:
        return 1.0
    top = np.sort(p)[-ntr:]          # frac*N largest weights
    return float(1.0 - top.sum())


def main():
    alphas = np.array([0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0])
    ns = [8, 10, 12, 16, 20]
    frac = 0.5

    print("=" * 72)
    print("Theory pre-registration: carry-chain combinatorics under Zipf(alpha)")
    print("=" * 72)

    Ec = {}     # n -> array over alphas
    d0 = {}
    s = {}
    H = {}
    for n in ns:
        row = np.array([Ec_exact(n, a) for a in alphas])
        Ec[n] = row
        d = row[0] - row
        d0[n] = d
        assert abs(row[0] - (1.0 - 2.0 ** (-n))) < 1e-12, \
            f"E_0[c] should be exactly 1-2^-n={1-2**-n}, got {row[0]}"
        s[n] = d / row[0]                    # = 1 - E_alpha[c]/E_0[c]; s(0)=0
        H[n] = np.array([heldout_mass(n, a, frac) for a in alphas])

    print("\n[1] E_alpha[c] (rows = n):")
    print("  n  " + " ".join(f"a={a:<4}" for a in alphas))
    for n in ns:
        print(f"  {n:<3}" + " ".join(f"{v:6.3f}" for v in Ec[n]))

    print("\n[2] normalized shape s_n(alpha) = d0(alpha)/E_0[c] = 1-E_a[c]/E_0  (lambda_c shape):")
    print("  n  " + " ".join(f"a={a:<4}" for a in alphas))
    for n in ns:
        print(f"  {n:<3}" + " ".join(f"{v:6.3f}" for v in s[n]))

    # n-sharpening: |slope_right - slope_left| at alpha=1
    print("\n[3] n-sharpening of the alpha=1 crossover (kink diagnostic on s_n):")
    i1 = list(alphas).index(1.0)
    kink = {}
    for n in ns:
        left = (s[n][i1] - s[n][i1 - 1]) / (alphas[i1] - alphas[i1 - 1])
        right = (s[n][i1 + 1] - s[n][i1]) / (alphas[i1 + 1] - alphas[i1])
        kink[n] = abs(right - left)
        print(f"    n={n:<3} slope_left={left:+.3f} slope_right={right:+.3f} "
              f"|Dkink|={kink[n]:.3f}")
    kns = sorted(kink)
    mono_sharpen = all(kink[kns[i]] < kink[kns[i + 1]] for i in range(len(kns) - 1))
    print(f"    sharpening monotone in n: {mono_sharpen}")

    print("\n[4] held-out mass H(alpha) under top-weight train selection "
          f"(frac={frac}):")
    print("  n  " + " ".join(f"a={a:<4}" for a in alphas))
    for n in ns:
        print(f"  {n:<3}" + " ".join(f"{v:6.3f}" for v in H[n]))
    print("  -> if H collapses with alpha, the population-penalty view says skew")
    print("     HELPS memorization; the d0 view says skew STARVES the algorithm of")
    print("     long-carry pressure. The alpha-sweep decides which dominates.")

    # m* curves at testbed-candidate n=12. Ansatz: lambda_c(alpha) = Lambda*s_n(alpha)
    # with ONE unknown scale Lambda (and lambda_c(0)=0: uniform data needs no rescue).
    # m*/(kappa*N) = max(0, 1 - lam/(Lambda*s_n(alpha))), parametrized by lam/Lambda.
    nstar = 12
    lam_ratios = [0.25, 0.5, 0.75]
    mstar = {}
    print(f"\n[5] m*(alpha)/(kappa*N) = max(0, 1 - (lam/Lambda)/s_n(alpha))  at n={nstar}:")
    print("  lam/Lam " + " ".join(f"a={a:<4}" for a in alphas))
    for r in lam_ratios:
        with np.errstate(divide="ignore", invalid="ignore"):
            row = np.where(s[nstar] > 0, 1.0 - r / s[nstar], -np.inf)
        row = np.clip(row, 0.0, None)
        mstar[r] = row
        print(f"  {r:6.2f} " + " ".join(f"{v:6.3f}" for v in row))
    print("  (lam/Lambda <= s_n(alpha) means the model is already grokkable at that")
    print("   alpha without rescue; m*=0 there. Rescue dose grows once skew deepens.)")

    # ------------------------------- figure -------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    ax = axes[0]
    for n in ns:
        ax.plot(alphas, s[n], "o-", lw=1.5, label=f"n={n}")
    ax.axvline(1.0, color="gray", ls=":", lw=0.8)
    ax.set_xlabel(r"$\alpha$"); ax.set_ylabel(r"$d_0(\alpha)/d_0(0)$")
    ax.set_title(r"$\lambda_c(\alpha)$ shape (parameter-free)")
    ax.legend(fontsize=8)

    ax = axes[1]
    ax.plot(kns, [kink[k] for k in kns], "s-", color="C3")
    ax.set_xlabel("n"); ax.set_ylabel(r"$|\Delta$slope at $\alpha$=1|")
    ax.set_title("n-sharpening of the crossover")
    ax.grid(alpha=0.3)

    ax = axes[2]
    for r in lam_ratios:
        ax.plot(alphas, mstar[r], "o-", lw=1.5, label=r"$\lambda/\Lambda$=%.2f" % r)
    ax.set_xlabel(r"$\alpha$"); ax.set_ylabel(r"$m^*/(\kappa N)$")
    ax.set_title(f"rescue dose (n={nstar})")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("figures/theory_curves.png", dpi=130)
    print("\nSaved figures/theory_curves.png")

    out = {
        "alphas": alphas.tolist(), "ns": ns, "frac": frac,
        "Ec": {str(n): Ec[n].tolist() for n in ns},
        "d0": {str(n): d0[n].tolist() for n in ns},
        "shape_s": {str(n): s[n].tolist() for n in ns},
        "kink_diag": {str(n): kink[n] for n in ns},
        "heldout_mass_H": {str(n): H[n].tolist() for n in ns},
        "mstar_over_kappaN": {str(r): mstar[r].tolist() for r in lam_ratios},
        "mstar_n": nstar,
        "note": ("Pre-registered before any skew training run. lambda_c(alpha) = "
                 "Lambda*s_n(alpha) (one unknown scale Lambda; lambda_c(0)=0). "
                 "s_n monotone increasing, alpha=1 crossover sharpens with n. "
                 "ALSO recorded H(alpha)=held-out population mass, a competing "
                 "shape candidate: alpha-sweep distinguishes d0-shape vs H-shape."),
    }
    json.dump(out, open("results/theory_curves.json", "w"), indent=2)
    print("Saved results/theory_curves.json")


if __name__ == "__main__":
    main()
