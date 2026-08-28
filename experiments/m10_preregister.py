"""M10 — pre-registered held-out boundary predictions (must run BEFORE M9).

C4 audit gap: family ranking (E_c best) was done in-sample on the 8 points
that DEFINED the ranking — no predictive test. This script commits to
predictions for alphas NOT yet measured, using ONLY the existing fit,
BEFORE any new training run happens. M9 then measures these alphas; a
separate comparison step (run after M9) checks predicted vs actual.

Held-out alphas chosen to densely fill gaps in the existing n=10 grid
(1.5, 2.0, 2.1, 2.25, 2.4, 2.5, 2.6, 2.7) without overlapping it:
  1.7, 1.9, 2.05, 2.15, 2.35, 2.45, 2.55, 2.65

Uses the E_c single-scale fit from results/m4_fits.json (C=0.474,
best-ranked candidate). Also predicts with the runner-up (exp2, C=0.59) for
comparison — a real test should show whether E_c's advantage holds out of
sample, not just in-sample.

Output: results/m10_predictions.json (frozen, timestamped, git-diffable —
do not edit after M9 starts).
"""
import json
import numpy as np

HELD_OUT_ALPHAS = [1.7, 1.9, 2.05, 2.15, 2.35, 2.45, 2.55, 2.65]


def main():
    fits = json.load(open("results/m4_fits.json"))["fits"]
    N = 2 ** 10
    x = np.arange(N, dtype=np.float64)
    cc = np.array([bin(i)[2:][::-1].split('0')[0].__len__() for i in range(N)], float)

    def cand(k, a_):
        w = (x + 1.0) ** (-a_); w /= w.sum()
        return {'H_lo': w[N // 2:].sum(), 'H_tail10': w[N // 10:].sum(),
                'E_c': (w * cc).sum(), 'exp2': 2.0 ** (-a_),
                'p_star': w[N - 1]}[k]

    preds = {}
    print(f"Pre-registered predictions for held-out alphas: {HELD_OUT_ALPHAS}\n")
    print(f"{'alpha':>6} {'E_c pred':>10} {'exp2 pred':>10}")
    for a_ in HELD_OUT_ALPHAS:
        C_ec = fits['E_c']['C']
        C_exp2 = fits['exp2']['C']
        p_ec = C_ec * cand('E_c', a_)
        p_exp2 = C_exp2 * cand('exp2', a_)
        preds[str(a_)] = dict(E_c_pred=float(p_ec), exp2_pred=float(p_exp2))
        print(f"{a_:>6.2f} {p_ec:>10.4f} {p_exp2:>10.4f}")

    out = dict(frozen_note="pre-registered 2026-08-25, BEFORE M9 measures these alphas",
               held_out_alphas=HELD_OUT_ALPHAS,
               fit_source="results/m4_fits.json",
               fit_C={"E_c": fits['E_c']['C'], "exp2": fits['exp2']['C']},
               predictions=preds)
    json.dump(out, open("results/m10_predictions.json", "w"), indent=1)
    print("\n-> results/m10_predictions.json (FROZEN — do not edit)")


if __name__ == "__main__":
    main()
