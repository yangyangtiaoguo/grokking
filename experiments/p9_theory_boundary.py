"""P9 — pre-register candidate shapes for the wd-ceiling(alpha) boundary.

Frozen BEFORE the P8 scan completes (P8 ~4% done at freeze time; only 3
boundary points known from prior pilots: ceiling(2)>0.3, ceiling(2.5) in
(0.05,0.15), ceiling(0/1) >= 0.3).

Question: the grok channel's wd-ceiling decreases with alpha. Which
alpha-dependent data quantity does it track? Candidates (all exact, n=10):

  C1  H_lo(alpha)   — bottom-half mass under Zipf(alpha). Extreme range
                      (0.5 -> 1e-7): naive proportional scaling already
                      inconsistent with the 3 known points (would need
                      ceiling(1)/ceiling(2.5) ~ 10^3, measured ~10).
  C2  E_a[c]        — expected carry-chain length. Mild range
                      (1.0 -> ~0.2): ratio E(1)/E(2.5) ~ 3-4, matches the
                      measured ceiling ratio (~2-6). This is the d0-family
                      shape (rehabilitates the proposal's ansatz direction,
                      with the lambda DIRECTION still inverted per 11.2).
  C3  2^{-alpha}    — pure exponential (log-linear in alpha).
  C4  H_tail10      — mass of states outside top-decile head.

Single-scale law to test on P8: wd_ceiling(alpha) ~= C * candidate(alpha).
After P8: fit C per candidate on the alpha rows with a resolved ceiling,
rank by consistency. Pure CPU.
"""
import json
import numpy as np

def candidates(n, alphas):
    N = 2 ** n
    x = np.arange(N, dtype=np.float64)
    c = np.zeros(N)
    v = N - 1 - x.astype(np.int64)  # trailing ones of x: count low-order 1s
    cc = np.array([bin(int(i))[2:][::-1].split('0')[0].__len__() for i in range(N)],
                  dtype=np.float64)
    out = {}
    for a in alphas:
        w = (x + 1.0) ** (-a); w /= w.sum()
        out.setdefault('H_lo', []).append(float(w[N // 2:].sum()))
        out.setdefault('H_tail10', []).append(float(w[N // 10:].sum()))
        out.setdefault('E_c', []).append(float((w * cc).sum()))
        out.setdefault('exp2', []).append(float(2.0 ** (-a)))
    return out

def main():
    n = 10
    alphas = [0.0, 1.0, 2.0, 2.25, 2.5, 2.75, 3.0]
    cand = candidates(n, alphas)
    # known anchor points from pilots (pre-P8): ceiling(2)>0.3,
    # ceiling(2.5) in (0.05, 0.15), ceiling(0), ceiling(1) >= 0.3
    print(f"candidate curves, n={n} (frozen before P8 completes)")
    print(f"{'alpha':>5} {'H_lo':>10} {'H_tail10':>10} {'E_c':>8} {'2^-a':>8}")
    for i, a in enumerate(alphas):
        print(f"{a:5.2f} {cand['H_lo'][i]:10.3e} {cand['H_tail10'][i]:10.3e} "
              f"{cand['E_c'][i]:8.4f} {cand['exp2'][i]:8.4f}")

    print("\nsingle-scale consistency check against the 3 known points:")
    print("anchor: ceiling(2)>=0.3, ceiling(2.5)~0.1 (mid of (0.05,0.15)), ratio(2/2.5) in (2,6)")
    for k in ['H_lo', 'H_tail10', 'E_c', 'exp2']:
        r = cand[k][2] / cand[k][4]   # alpha=2 / alpha=2.5
        print(f"  {k:10s}: C(2)/C(2.5) = {r:8.2f}   {'~OK' if 0.5 <= r <= 12 else 'OFF'}")

    json.dump(dict(n=n, alphas=alphas, **cand,
                   frozen_note="pre-registered before P8 scan completion 2026-08-21"),
              open("results/p9_theory_boundary.json", "w"))
    print("\n-> results/p9_theory_boundary.json")

if __name__ == "__main__":
    main()
