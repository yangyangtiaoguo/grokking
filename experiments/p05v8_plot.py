"""Plot v8 minibatch results: candidate testbed A (n=10) + classic-delay E (n=8)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

runs = json.load(open("results/p05v8_lockin.json"))

fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))

ax = axes[0]
for r in [x for x in runs if x['label'] == 'A']:
    ax.plot(r['steps'], r['tr'], lw=1.2, alpha=0.8, label=f"train s{r['seed']}")
    ax.plot(r['steps'], r['ev'], lw=1.6, alpha=0.8, label=f"eval s{r['seed']}")
ax.set_title("v8[A] candidate testbed: n=10, frac=0.3, wd=0.3, init=10, batch=128")
ax.set_xlabel("step"); ax.set_ylabel("sequence accuracy")
ax.set_ylim(-0.03, 1.03); ax.legend(fontsize=7, ncol=2); ax.grid(alpha=0.3)

ax = axes[1]
r = [x for x in runs if x['label'] == 'E' and x['seed'] == 0][0]
ax.plot(r['steps'], r['tr'], 'C0-', lw=1.5, label='train acc')
ax.plot(r['steps'], r['ev'], 'C1-', lw=1.8, label='eval acc')
ax.axvline(r['tr_cross'], color='C0', ls='--', lw=0.8)
ax.axvline(r['ev_cross'], color='C1', ls='--', lw=0.8)
ax.set_title(f"v8[E] classic delay at n=8 (minibatch): tau={r['tau']}")
ax.set_xlabel("step"); ax.set_ylabel("sequence accuracy")
ax.set_ylim(-0.03, 1.03); ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax2 = ax.twinx()
ax2.plot(r['steps'], r['th'], 'C3-', lw=1.2, alpha=0.6)
ax2.set_ylabel(r'$\|\theta\|_2$', color='C3'); ax2.tick_params(axis='y', labelcolor='C3')

plt.tight_layout()
plt.savefig("figures/p05v8_testbed.png", dpi=130)
print("Saved figures/p05v8_testbed.png")
