# Estimation Cookbook for AI-assisted development (v0.2)

How to look at a task, plan it, and give a time estimate that holds up when the work is
done by a person together with Claude Code (or a similar agent).

- **v0.1** came from desk research (`sources/01–06`).
- **v0.2** recalibrated the numbers against 25 real sessions (see `PILOT_RESULTS.md`).
- **Next:** recalibrate on ~100 sessions with `SESSION_AUDIT_PROMPT.md`.

---

## 0. The five rules

1. **Never estimate in "developer hours".**
   - Models answer "how long?" with a human-developer reference class from their training data.
   - In the pilot, the actual time was a median **0.09×** the blind "experienced developer without AI" estimate, i.e. about 11× faster.
   - Anthropic's own test found the same pattern: Claude's time estimates for 1,000 real tasks overestimate short tasks and underestimate long ones (ρ 0.44).
   - A preprint (arXiv 2604.00010) found pre-task model estimates 4–7× too long.
2. **Telling the model the work is agent work removes most of the bias, but not the noise.**
   - With that framing, the blind estimate had no bias (ratio 1.00 in the pilot), but was only within 2× on 18 of 25 tasks.
   - The remaining error is not in the code. It comes from waits, the environment, and loops where the user rejects a design and Claude rebuilds it.
3. **Price the work in units, then calibrate.**
   - The research method, applied blind, ranked tasks best (Spearman 0.84) and had the lowest spread.
   - Its starting numbers were 2.6× too pessimistic.
   - Once corrected with the person's own history it gave the best accuracy: median error 0.38–0.43 vs 0.52, and within 2× on 22 of 25 tasks.
4. **Code is cheap; waiting and taste are expensive.**
   - **Building** came in at about **0.2×** the research priors.
   - **Waits** (renders, scrapes, test queues, locks) came in at **1.5×** what was predicted.
   - **"Make it look good" loops** cost 20–25 min per rejected design.
5. **Never trust anyone's sense of elapsed time, model or human. Use timestamps.**
   - Claude reported "about 20 minutes" for a dashboard that took 9.8 minutes.
   - In METR's 2025 trial, developers were 19% slower with AI and still believed they had been 20% faster.

---

## 1. Procedure: Look → Plan → Price → Combine → Report → Re-estimate

### Step 1. LOOK: intake signals (2 minutes; ask only about unknowns)

| Signal | Why it matters |
|---|---|
| Definition of done: demo, merged, or deployed? Who accepts it? | Unclear "done" adds polish rounds |
| Brief quality: exact files, a proof command, "Done when" checks? | A precise brief means no back-and-forth (strongest accelerator in the pilot) |
| Data/inputs already available? Credentials in hand? | Data access, not UI, is the critical path for dashboards |
| External APIs (documented? sandbox? creds?) | Highest variance, plus waits on the outside world |
| Long-running jobs: renders, scrapes, full test suites, builds, deploys | Count them × duration. Code size doesn't predict these waits |
| Shared machine / queues / locks / low RAM | 10–50 min of queueing per task in the pilot |
| Visual taste required ("make it nice", "not generic")? | 1–4 rebuild rounds unless concepts are shown first |
| Stakes: live data, money, security | Adds validation steps (dry run, apply to a copy, verifier) |
| Novelty to the agent: private/undocumented API, lib newer than cutoff | ×1.5–2, may need a spike |
| Who is "the human": the user live, or a parent agent? | Parent-agent briefs remove human waiting but keep the waits |

### Step 2. PLAN: classify and decompose

- **Clear** (a pattern exists): price it from the table.
- **Complicated** (known solution, needs analysis): price it with multipliers. It must be in the plan.
- **Complex** (outcome knowable only by trying: unknown bug cause, private API, "make it feel good"): **don't point-estimate.** Add a timeboxed spike (15–45 min), then re-estimate.
- **Chaotic** (production is broken): fix first, estimate afterwards.

Break the work into 3–12 units. Always include **PLAN**, **TAIL** (integration and fixes) and **REVIEW**, but size them to the task (see the table). If the task can be checked by tests, build one thin end-to-end slice first.

### Step 3. PRICE: v0.2 unit table (agent-era minutes, agent + human, synchronous)

These are the research priors with the pilot corrections applied (build ×0.2, overhead ×0.75, waits ×1.5). Recalibrate them per person.

| Unit | Median minutes | σ (log spread) | Notes |
|---|---|---|---|
| PLAN, plan already in the brief | 2–4 | 0.3 | Reading CLAUDE.md, the files named in the brief |
| PLAN, from a vague ask | 5–10 | 0.4 | + ~3 per open decision; propose a plan and confirm |
| Small edit in familiar code (1 file, clear rule) | 2–5 | 0.4 | "One-line domain bug incl. test + commit ≈ 5 min" |
| Repeated item from a precise list (fix, field, capture) | ~3 per item | 0.4 | Includes tests; 20 items ≈ 1 h |
| Bulk mechanical edit across N files | 2 + 0.2·N | 0.4 | "11 files of copy ≈ 1.5 min of editing" |
| New UI page/dashboard over data that already exists | 5–15 | 0.5 | Single-file HTML; data shape and design first |
| Logic module / rule cluster | 4–10 | 0.5 | |
| Data pipeline step (parse, join, export) with real-data probe | 10–20 | 0.6 | Probe the real source first |
| External API, documented, creds in hand | 10–20 | 0.8 | + spike if undocumented |
| Investigation ("why does X happen?") with a reproducible probe | 12–25 | 0.8 | Timebox it; stop and report if the premise doesn't reproduce |
| Live-data change (dry run → copy → apply → verify) | +10 | 0.4 | Fixed safety overhead, worth it |
| Independent verifier / review pass | +25–30% of build | 0.5 | Finds real defects in data work |
| TAIL: integration and fix-ups | 0.1–0.2 × build | 0.6 | Higher with more integrations or deploy targets |
| REVIEW: user reading the result | 2–8 | 0.4 | Parent agent reviews → ≈0 user minutes |
| **WAIT: each heavy run** (render, scrape, full suite, build) | **1.5 × its known duration** | 0.5 | Plus queue time if other sessions share the machine |
| Design rebuild round (taste rejected) | 20–25 per round | 0.5 | Expect 0 if concepts were approved first, 2–4 if not |

**Risk adders** (probability × minutes; add the expected value to P50 and the full amount to P80/P95):

| Risk | p | Minutes |
|---|---|---|
| Test gate / queue gives up (low RAM, lock held) | 0.3–0.5 on a shared PC | 11–25 |
| Tool/env friction (CRLF, heredoc escaping, worktree missing venv) | 0.4 | 2–10 |
| Credentials or access not ready | 0.5 if not confirmed | 30 (+ calendar days for approvals) |
| Mid-task priority change / scope discovery | 0.3 per vague requirement | 10–20 |
| A long job fails and must be redone | 0.2 per heavy run | 1 × run time |
| Wrong approach → re-plan | 0.15 per Complicated unit > 30 min | = unit median |

### Step 4. COMBINE: the math

- Treat each unit as lognormal (median m, spread σ).
- Never add P80s.
- Quick version, accurate enough for daily use:

```
P50 ≈ Σ medians × 1.1            (right skew pushes the sum's median up)
         + Σ p·x of risk adders
P80 ≈ P50 × 1.6                  (pilot spread σ≈0.52 → ×1.55; use ×1.8 for unfamiliar envs)
P95 ≈ P50 × 2.4
```

Exact version (Fenton–Wilkinson moment matching, within 1–5% of Monte Carlo):

```
E_i = m_i·exp(σ_i²/2)        Var_i = E_i²·(exp(σ_i²) − 1)
M = ΣE_i + Σp_j·E[X_j]       V = ΣVar_i + Σ(p_j·E[X_j²] − (p_j·E[X_j])²)
σ_T² = ln(1 + V/M²)          μ_T = ln M − σ_T²/2
σ_tot = sqrt(σ_T² + σ_c²)    σ_c = 0.2 familiar env, 0.3–0.4 unfamiliar (shared-cause factor)
P50 = e^μ_T   P80 = e^(μ_T + 0.84·σ_tot)   P95 = e^(μ_T + 1.64·σ_tot)
```

Monte Carlo (use it when there are parallel paths):

```python
import math, random
def simulate(units, risks, sigma_c=0.2, n=50_000):
    out = []
    for _ in range(n):
        t = sum(m*math.exp(random.gauss(0, s)) for m, s in units)
        t += sum(x*math.exp(random.gauss(0, 0.5)) for p, x in risks if random.random() < p)
        out.append(t*math.exp(random.gauss(0, sigma_c)))
    out.sort(); return {k: round(out[int(n*q)]) for k, q in (("P50",.5),("P80",.8),("P95",.95))}
```

**Elapsed time ≠ your time.** Report three numbers:
- **Elapsed:** critical path, including waits.
- **Your attention:** decisions, reviews, taste rounds.
- **Calendar risks:** app-store review, OAuth verification, DNS. Report these separately and never fold them into the minutes.

If a slow job can start first (a scrape, a render), elapsed ≈ max(job, build), not the sum.

### Step 5. REPORT: output format

```
ESTIMATE <task>                                   checkpoint: C0 intake | C1 plan | C2 first slice
Class: Clear/Complicated/Complex-heavy     Units: 6 (1 API, 2 heavy runs, 1 decision)
Elapsed: P50 35 min | P80 55 min | P95 ~1h25
Your attention: ~8 min (1 decision, 1 review)     Calendar risks: none
Top risks: test queue on shared PC (+15, p .4); API field missing (+20, p .2)
Would narrow it: confirm creds; sample of the data; concept approved before build
Human-developer equivalent (reference only, never quote): ~6 h
```

Machine-readable line, for future calibration (see `CLAUDE_MD_SNIPPET.md`):
`ESTIMATE task=<slug> cat=<category> p50=<min> p80=<min> units=<n> waits=<min>`

### Step 6. RE-ESTIMATE: checkpoints and tripwires

| Checkpoint | What to do |
|---|---|
| C1, after the plan is approved | Rebuild the units from the plan and drop resolved decisions. The range usually narrows. |
| C2, after the first working slice | k = geomean(actual/estimate) of finished units, shrunk as k^(n/(n+2)). Multiply the remaining units by k. |
| Tripwire: a unit passes its P80, or 2× its median with no progress | Stop. Re-classify it as Complex, timebox a spike, tell the user the new range. |
| Done | Log the actual time from timestamps (never from memory) next to the ESTIMATE line. |

---

## 2. Accelerators: do these and estimates shrink and become reliable

From the pilot, roughly in order of impact:

1. **A precise brief.** Exact files, a proof command or tool, constraints, a "Done when" list and a stop rule. Sessions with such briefs shipped with zero human turns, often under the user's own budget (16 min against "~1 h"; ~1 h against "1–2 h").
2. **Show taste choices before building.** Two or three divergent concept stills, or a "pitch strip" on real frames, then one go-ahead. The one session without this needed three rebuilds (~60 min). The one with it had zero.
3. **Start slow jobs first.** Kick off scrapes and renders in the first minutes and write code, tests and docs while they run.
4. **Probe the real data or API once before coding.** Parse rules then come from real data, not guesses.
5. **Use safe-change scaffolding for live data.** Read-only preview → apply to a copy of the DB → apply live → idempotence re-run. It adds ~10 min and prevents disasters.
6. **Prove tests on the old code.** A test that fails on old HEAD and passes on new is fast confidence.
7. **Run a verifier pass on data work.** It adds 25–30% and catches real defects.
8. **Split side questions into child sessions.** This keeps the main task short.

## 3. Time sinks to price in (pilot Pareto: share of time lost)

1. **Environment (~33% of lost time).** Shared-PC test queues and locks, low-RAM test gates that time out quietly, nested locks deadlocking, worktrees missing venvs or model files.
2. **Agent mistakes (~11%).** Shell or heredoc escaping (backslashes, `$$`, U+2028), CRLF→LF churn on Windows, wrong expected counts in tests, monitors with no timeout hiding a hung run.
3. **Tests/CI (~10%).** Full suites when a targeted set would do; fixed sleeps that turn flaky under load.
4. **Unclear spec and taste loops (~14% combined).** Drip-fed field rules (ask for one sample row up front) and design rejections.
5. **External APIs (~6%).** Undocumented endpoints, slow archives; probe first.

## 4. Reference classes from outside research (use only when you have no history of your own)

| Kind of work | Agent-era vs human-era estimate |
|---|---|
| Single-page tool / prototype | 8–20× faster |
| CRUD / dashboard prototype | 5–10× |
| Port or migration checked by an existing test suite | 10–50× |
| Production MVP | 3–7× (testing and fixing ≈ 80% of the time) |
| Auth, payments, data migrations | 1.5–3×, worst failure modes |
| Expert work in a large mature codebase | 0.8–1.3× (METR RCT: 19% slower in early 2025) |
| App store, OAuth verification, DNS | no speedup; add as calendar time |

Your own calibrated history always beats this table. In the pilot, every category came in at 7–25× faster than the blind human-developer estimate.

## 5. Calibration loop

- Keep logging `ESTIMATE` lines.
- Monthly, run `tools/cc_sessions.py` → `tasks.csv` → `tools/calibrate.py`.
- Report the bias exp(mean ln(actual/est)), the spread σ, and **P80 coverage** (should be about 80%). Report MdMRE second.
- Weight recent sessions more (90-day half-life). Recalibrate when the model or harness changes; agent capability doubles roughly every 4–7 months (METR).
