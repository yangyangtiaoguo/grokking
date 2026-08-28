"""P9b — compare measured wd-ceiling(alpha) against the pre-registered
candidates (P9), then (clearly labeled post-hoc) against P(c>=k|alpha).

Measured ceilings from P8 (majority-GROK max wd; interval = [passing wd,
next failing wd]):
  alpha : ceiling interval        point (log-mid)
  0.0   : (0.5, 1.0]  (P4: wd=1.0 crushes)   ~0.7
  1.0   : (0.5, 1.0]  (P4)                   ~0.7
  2.0   : [0.3, 0.5)                           0.39
  2.25  : [0.1, 0.15)                          0.12
  2.5   : [0.05, 0.1)                          0.07
  2.75  : [0.05, 0.1)                          0.07
  3.0   : (0, 0.05)                            0.02

Pre-registered single-scale test: ceiling(alpha) = C * cand(alpha).
Pass criterion per anchor: cand ratio to alpha=2 must lie within the
measured interval ratio (log-mid +- factor covering interval).
"""
import json
import numpy as np

ALPHAS = [0.0, 1.0, 2.0, 2.25, 2.5, 2.75, 3.0]
CEIL_LO = [0.5, 0.5, 0.3, 0.1, 0.05, 0.05, 0.025]   # lower/point estimates
CEIL_HI = [1.0, 1.0, 0.5, 0.15, 0.1, 0.1, 0.05]     # upper bounds

def zipf_stats(n, alphas, ks=(1, 2, 3, 4)):
    N = 2 ** n
    x = np.arange(N, dtype=np.int64)
    cc = np.array([bin(int(i))[2:][::-1].split('0')[0].__len__() for i in range(N)])
    out = {f"Pc>= {k}": [] for k in ks}
    out.update({'E_c': [], 'exp2': [], 'H_lo': [], 'H_tail10': []})
    for a in alphas:
        w = (x + 1.0) ** (-a); w /= w.sum()
        for k in ks:
            out[f'Pc>= {k}'].append(float(w[cc >= k].sum()))
        out['E_c'].append(float((w * cc).sum()))
        out['exp2'].append(float(2.0 ** (-a)))
        out['H_lo'].append(float(w[N // 2:].sum()))
        out['H_tail10'].append(float(w[N // 10:].sum()))
    return out

def main():
    n = 10
    stats = zipf_stats(n, ALPHAS)
    i2 = ALPHAS.index(2.0)
    # measured ratio intervals vs alpha=2 (point = lo)
    print("measured ceiling and ratio-to-alpha=2 interval:")
    for i, a in enumerate(ALPHAS):
        r_lo = CEIL_LO[i] / CEIL_HI[i2]   # conservative lower ratio
        r_hi = CEIL_HI[i] / CEIL_LO[i2]   # conservative upper ratio
        print(f"  alpha={a:4.2f}: ceiling in [{CEIL_LO[i]:.3f},{CEIL_HI[i]:.3f}) "
              f"-> ratio in ({r_lo:.2f}, {r_hi:.2f})")

    print("\npre-registered candidates: implied ratio cand(a)/cand(2) vs measured interval")
    cands = ['E_c', 'exp2', 'H_lo', 'H_tail10']
    print(f"{'alpha':>5} {'measured':>14} " + " ".join(f"{c:>10}" for c in cands))
    npass = {c: 0 for c in cands}
    ntest = 0
    for i, a in enumerate(ALPHAS):
        if i == i2:
            continue
        ntest += 1
        r_lo = CEIL_LO[i] / CEIL_HI[i2]
        r_hi = CEIL_HI[i] / CEIL_LO[i2]
        row = []
        for c in cands:
            r = stats[c][i] / stats[c][i2]
            ok = r_lo <= r <= r_hi
            npass[c] += ok
            row.append(f"{r:8.3g}{'+' if ok else '-'}")
        print(f"{a:5.2f} ({r_lo:5.2f},{r_hi:5.2f}) " + " ".join(f"{r:>10}" for r in row))
    print(f"\npass counts (of {ntest}): " + ", ".join(f"{c}={npass[c]}" for c in cands))

    # post-hoc: P(c>=k) family
    print("\nPOST-HOC (not pre-registered): P(c>=k|alpha) single-scale pass counts")
    pc = [k for k in stats if k.startswith('Pc')]
    for c in pc:
        cnt = 0
        for i, a in enumerate(ALPHAS):
            if i == i2:
                continue
            r = stats[c][i] / stats[c][i2]
            r_lo = CEIL_LO[i] / CEIL_HI[i2]
            r_hi = CEIL_HI[i] / CEIL_LO[i2]
            cnt += (r_lo <= r <= r_hi)
        print(f"  {c}: {cnt}/{ntest}")

    # implied log-slope of the boundary in [2, 3]
    lm = np.log([CEIL_LO[i] for i in range(i2, len(ALPHAS))])
    da = np.array(ALPHAS[i2:])
    slope = np.polyfit(da, lm, 1)[0]
    print(f"\nmeasured log-slope of ceiling over [2,3]: {slope:.2f} per unit alpha "
          f"(= 2^({slope/np.log(2):.2f} alpha) decay)")
    for c in cands + pc:
        lm2 = np.log(stats[c][i2:])
        s2 = np.polyfit(da, lm2, 1)[0]
        print(f"  {c:10s} log-slope [2,3]: {s2:6.2f}")

if __name__ == "__main__":
    main()
