"""Plot v9: locked testbed A2 curves + E2 classic-delay curve."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

runs = json.load(open("results/p05v9_anneal.json"))

fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))

ax = axes[0]
for r in [x for x in runs if x['label'] == 'A2']:
    ax.plot(r['steps'], r['ev'], lw=1.6, alpha=0.85,
            label=f"eval s{r['seed']} (tau={r['tau']})")
    ax.plot(r['steps'], r['tr'], lw=0.8, alpha=0.4, color='gray')
ax.set_title("v9[A2] LOCKED testbed: n=10, frac=0.3, wd=0.3, init=10,\n"
             "batch=128, cosine anneal, 5/5 grok, 4/5 tail-locked")
ax.set_xlabel("step"); ax.set_ylabel("eval sequence accuracy")
ax.set_ylim(-0.03, 1.03); ax.legend(fontsize=7); ax.grid(alpha=0.3)

ax = axes[1]
r = [x for x in runs if x['label'] == 'E2' and x['seed'] == 0][0]
ax.plot(r['steps'], r['tr'], 'C0-', lw=1.5, label='train acc')
ax.plot(r['steps'], r['ev'], 'C1-', lw=1.8, label='eval acc')
if r['tr_cross']: ax.axvline(r['tr_cross'], color='C0', ls='--', lw=0.8)
if r['ev_cross']: ax.axvline(r['ev_cross'], color='C1', ls='--', lw=0.8)
ax.set_title(f"v9[E2] classic delayed grokking, n=8: tau={r['tau']} "
             f"(train@{r['tr_cross']}, eval@{r['ev_cross']})")
ax.set_xlabel("step"); ax.set_ylabel("sequence accuracy")
ax.set_ylim(-0.03, 1.03); ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax2 = ax.twinx()
ax2.plot(r['steps'], r['th'], 'C3-', lw=1.2, alpha=0.6)
ax2.set_ylabel(r'$\|\theta\|_2$', color='C3'); ax2.tick_params(axis='y', labelcolor='C3')

plt.tight_layout()
plt.savefig("figures/p05v9_testbed_locked.png", dpi=130)
print("Saved figures/p05v9_testbed_locked.png")
