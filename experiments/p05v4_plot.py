"""Plot the grokking curve found in P0.5 v4 (frac=0.5, wd=0.3, init=5)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

runs = json.load(open("results/p05v4_ar_grokking.json"))
# pick the grokking run
r = [x for x in runs if x['frac'] == 0.5 and x['wd'] == 0.3 and x['init_scale'] == 5.0][0]

fig, ax1 = plt.subplots(figsize=(7, 4.5))
ax1.plot(r['steps'], r['tr'], 'C0-', lw=2, label='train acc')
ax1.plot(r['steps'], r['ev'], 'C1-', lw=2, label='eval acc')
ax1.axhline(0.9, color='gray', ls=':', lw=0.8)
ax1.set_xlabel('step'); ax1.set_ylabel('sequence accuracy')
ax1.set_ylim(-0.03, 1.03)
ax1.set_xscale('symlog')
if r['tr_cross']: ax1.axvline(r['tr_cross'], color='C0', ls='--', lw=0.8)
if r['ev_cross']: ax1.axvline(r['ev_cross'], color='C1', ls='--', lw=0.8)
ax1.legend(loc='center left')

ax2 = ax1.twinx()
ax2.plot(r['steps'], r['th'], 'C3-', lw=1.5, alpha=0.7, label='||theta||')
ax2.set_ylabel(r'$\|\theta\|_2$', color='C3')
ax2.tick_params(axis='y', labelcolor='C3')
ax2.legend(loc='lower right')

plt.title(f"Grokking (AR big-endian, n=8): tau={r['tau']}, "
          f"norm {r['th'][0]:.0f}->{r['th'][-1]:.0f}")
plt.tight_layout()
plt.savefig("figures/p05v4_grokking_curve.png", dpi=130)
print("Saved figures/p05v4_grokking_curve.png")
print(f"train hits 0.99 at step {r['tr_cross']}, eval hits 0.90 at step {r['ev_cross']}")
print(f"final train {r['final_train']:.3f}, final eval {r['final_eval']:.3f}")
# show the eval trajectory around the jump
for s, e, t in zip(r['steps'], r['ev'], r['th']):
    if 2000 <= s <= 6000:
        print(f"  step {s:5d}  eval {e:.3f}  norm {t:.1f}")
