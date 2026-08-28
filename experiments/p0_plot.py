"""P0 visualization: E_alpha[c] vs alpha (multi-n) and d0(alpha)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, "experiments")
from p0_combinatorics import carry_stats

alphas = np.linspace(0, 2.5, 51)
ns = [8, 12, 16]

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))

# left: E_alpha[c] vs alpha, multiple n, + asymptotic 1/(2^a-1) for a>1
for n in ns:
    Ec = [carry_stats(n, a)[0] for a in alphas]
    ax[0].plot(alphas, Ec, label=f"n={n}", lw=2)
a_hi = alphas[alphas > 1.0]
ax[0].plot(a_hi, 1.0 / (2.0 ** a_hi - 1.0), "k--", lw=1.2,
           label=r"$1/(2^\alpha-1)$ (a>1 asymp.)")
ax[0].axvline(1.0, color="gray", ls=":", lw=1)
ax[0].set_xlabel(r"skew exponent $\alpha$")
ax[0].set_ylabel(r"$\mathbb{E}_\alpha[c]$  (mean carry-chain length)")
ax[0].set_title("Carry-chain length vs skew (kink near α=1)")
ax[0].legend(fontsize=8)
ax[0].grid(alpha=0.3)

# right: d0(alpha) = E_0[c]-E_alpha[c]
n = 16
E0 = carry_stats(n, 0.0)[0]
d0 = [E0 - carry_stats(n, a)[0] for a in alphas]
ax[1].plot(alphas, d0, "C3", lw=2)
ax[1].axvline(1.0, color="gray", ls=":", lw=1)
ax[1].set_xlabel(r"skew exponent $\alpha$")
ax[1].set_ylabel(r"$d_0(\alpha)=\mathbb{E}_0[c]-\mathbb{E}_\alpha[c]$")
ax[1].set_title("Per-balanced-sample surprise (n=16)")
ax[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("figures/p0_carry_stats.png", dpi=130)
print("Saved figures/p0_carry_stats.png")

# finite-size sharpening of the kink: |Δslope| at alpha=1 vs n
print("\nFinite-size kink sharpening:")
for n in [6, 8, 10, 12, 14, 16, 18, 20]:
    h = 0.25
    el = (carry_stats(n, 1.0)[0] - carry_stats(n, 1.0 - h)[0]) / h
    er = (carry_stats(n, 1.0 + h)[0] - carry_stats(n, 1.0)[0]) / h
    print(f"  n={n:<3} |Δslope@α=1| = {abs(er - el):.4f}")
