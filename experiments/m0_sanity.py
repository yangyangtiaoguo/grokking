"""M0 — sanity: verify the campaign pipeline against three known pilot cells.

  (alpha=0,   wd=0.3)          -> expect GROK   (P8: 3/3)
  (alpha=2.5, wd=0.3)          -> expect TRAP   (P4b/P8: steady trap)
  (alpha=2.5, wd=0.3, k=1, tail injection) -> expect GROK
       (verifies the injection path; P5 showed k=1 UNIFORM rescues; tail is
        the new path — if tail fails while uniform succeeds that is a finding,
        not a sanity failure, but check the plumbing first)

~3 runs x 95s -> results/m0_sanity.json. Any unexpected verdict -> STOP.
"""
import sys, time, json
sys.path.insert(0, "experiments")
from campaign_lib import run_cell, verdict, summary_line

CHECKS = [
    dict(n=10, alpha=0.0, wd=0.3, seed=0, k=0),
    dict(n=10, alpha=2.5, wd=0.3, seed=0, k=0),
    dict(n=10, alpha=2.5, wd=0.3, seed=0, k=1, inject='tail'),
    dict(n=10, alpha=2.5, wd=0.3, seed=0, k=1, inject='uniform'),  # known-good ref
]


def main():
    out = []
    for c in CHECKS:
        t0 = time.time()
        r = run_cell(**c)
        print(f"{summary_line(r)}  ({time.time()-t0:.0f}s)", flush=True)
        out.append(dict(verdict=verdict(r), **r))
    json.dump(out, open("results/m0_sanity.json", "w"))

    v = {i: out[i]['verdict'] for i in range(len(out))}
    ok = (v[0] == 'GROK' and v[1] == 'TRAP'
          and v[3] == 'GROK'                      # uniform rescue reference
          and v[2] in ('GROK', 'PARTIAL'))        # tail: finding either way
    print(f"\nsanity verdict: {'PASS' if ok else 'FAIL'}  {v}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
