#!/usr/bin/env python3
"""
calibrate.py - Calibrate naive (human-era / blind-model) estimates against actual AI-assisted times.

Input: tasks.csv with at least: task_id, category, est_naive_min, actual_active_min, include (1/0)
Output: per-category table (n, bias, factor, sigma, shrunk factor, P10/P50/P90 multipliers,
        MdMRE, PRED(25), PRED(50)) and an optional Monte Carlo forecast for a new plan.

  python3 -I calibrate.py tasks.csv
  python3 -I calibrate.py tasks.csv --plan "dashboard:240,api:120,api:60"   # naive minutes per item
"""
import argparse, csv, math, random, statistics as st
from collections import defaultdict


def load(path):
    rows = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        try:
            if str(r.get("include", "1")).strip() in ("0", "false", "no"):
                continue
            e, a = float(r["est_naive_min"]), float(r["actual_active_min"])
            if e > 0 and a > 0:
                rows.append((r.get("category") or "other", e, a))
        except (KeyError, ValueError):
            continue
    return rows


def q(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def summarize(rows, prior_tau=0.5):
    allr = [math.log(a / e) for _, e, a in rows]
    mu0 = st.mean(allr)
    s_pool = st.stdev(allr) if len(allr) > 1 else 1.0
    by = defaultdict(list)
    for c, e, a in rows:
        by[c].append((e, a))
    out = []
    for c, xs in sorted(by.items(), key=lambda kv: -len(kv[1])) + [("ALL", [(e, a) for _, e, a in rows])]:
        r = [math.log(a / e) for e, a in xs]
        n = len(r)
        m = st.mean(r)
        s = st.stdev(r) if n > 1 else s_pool
        # empirical-Bayes / normal-normal shrinkage of category mean toward global mean
        w = (n / s**2) / (n / s**2 + 1 / prior_tau**2) if c != "ALL" else 1.0
        m_post = w * m + (1 - w) * mu0
        # prediction interval for a NEW task (t-dist approximated by z when n>=10)
        tq = 1.2816 * math.sqrt(1 + 1 / n)  # 80% PI half-width multiplier (z_0.9)
        mre = [abs(a - e) / a for e, a in xs]
        # leave-one-out calibrated accuracy: each task predicted with factor from the OTHER tasks
        mre_cal = []
        for i, (e, a) in enumerate(xs):
            rest = r[:i] + r[i + 1:]
            if not rest:
                continue
            mloo = st.mean(rest)
            sl = st.stdev(rest) if len(rest) > 1 else s_pool
            wl = (len(rest) / sl**2) / (len(rest) / sl**2 + 1 / prior_tau**2) if c != "ALL" else 1.0
            pred = e * math.exp(wl * mloo + (1 - wl) * mu0)
            mre_cal.append(abs(a - pred) / a)
        out.append({
            "category": c, "n": n, "mean_log": round(m, 3), "factor_raw": round(math.exp(m), 3),
            "sigma_log": round(s, 3), "factor_shrunk": round(math.exp(m_post), 3),
            "P10_mult": round(math.exp(m_post - tq * s), 3), "P50_mult": round(math.exp(m_post), 3),
            "P90_mult": round(math.exp(m_post + tq * s), 3),
            "mean_mult": round(math.exp(m_post + s**2 / 2), 3),  # lognormal mean (for summing tasks)
            "MdMRE": round(st.median(mre), 3),
            "PRED25": round(sum(x <= .25 for x in mre) / n, 3), "PRED50": round(sum(x <= .5 for x in mre) / n, 3),
            "MdMRE_cal_loo": round(st.median(mre_cal), 3) if mre_cal else "",
            "PRED25_cal_loo": round(sum(x <= .25 for x in mre_cal) / len(mre_cal), 3) if mre_cal else "",
        })
    return out


def monte_carlo(rows, plan, n_sims=10000, seed=7):
    """Evidence-Based-Scheduling style: for each plan item, multiply naive estimate by a ratio
    resampled from that category's history (fallback: all history)."""
    rnd = random.Random(seed)
    by = defaultdict(list)
    for c, e, a in rows:
        by[c].append(a / e)
    allv = [a / e for _, e, a in rows]
    totals = []
    for _ in range(n_sims):
        t = 0.0
        for c, est in plan:
            pool = by[c] if len(by[c]) >= 5 else allv
            t += est * rnd.choice(pool)
        totals.append(t)
    return {p: round(q(totals, p), 1) for p in (0.1, 0.5, 0.8, 0.9)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--plan", default="", help="cat:naive_min,cat:naive_min,...")
    ap.add_argument("--tau", type=float, default=0.5, help="prior SD of category log-bias around global")
    a = ap.parse_args()
    rows = load(a.csv)
    if len(rows) < 3:
        raise SystemExit("need >= 3 usable rows")
    res = summarize(rows, a.tau)
    w = csv.DictWriter(__import__("sys").stdout, fieldnames=list(res[0]))
    w.writeheader()
    w.writerows(res)
    if a.plan:
        plan = [(p.split(":")[0], float(p.split(":")[1])) for p in a.plan.split(",") if ":" in p]
        print("\nMonte Carlo total minutes (P10/P50/P80/P90):", monte_carlo(rows, plan))


if __name__ == "__main__":
    main()
