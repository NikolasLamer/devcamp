# 04 — Design-first, decomposition-based estimation for AI-agent software work

Researcher angle: work breakdown, decomposition granularity, uncertainty classification (Cynefin / ignorance scales), risk-adjusted P50/P80/P95, the integration tail, and how planning/spec modes change predictability. The main deliverable is the **estimation procedure in Part B**.

**Labels used throughout**
- **[E]** evidence-based: a published study, benchmark or primary source, with its limits stated.
- **[E-weak]** practitioner or secondary evidence, or a single small study.
- **[P]** a proposed prior or design choice made for this method. It is not measured and must be calibrated (see B7).

Research note: live page fetches were blocked in this environment, so primary pages (metr.org, martinfowler.com, shape-of-code.com) were read through search-engine extracts. Figures are reported as those extracts gave them, and the sources are listed at the end.

---

## Part A — Findings

### A1. Why the AI gives "4–5 hours" when the real answer is ~45 minutes

1. **LLMs estimate durations using a human reference class.** [E-weak→E] A workshop preprint at ICLR 2026, *Can LLMs Perceive Time?* (Garikaparthi, arXiv 2604.00010), tested 68 tasks across four model families. Models' estimates before starting a task were **4–7× longer than the actual duration** (p < 0.001). In multi-step agentic settings the error stayed at **5–10×**. The models also ranked tasks by duration poorly. The proposed explanation is that models know typical *human* durations from their training data but have no grounding in their own speed. A MATS write-up, *Your Agents Are Not Time Aware*, found that Claude Code and Codex agents consistently over-predicted their own time, most of all on short tasks.
   → **Implication:** never ask "how long will this take?" in one holistic step. Count units of work, price each from an agent-era table, and calibrate the table against measured actuals.
2. **The real costs have moved.** [E-weak] Anthropic's analysis of 100k Claude.ai conversations (Tamkin & McCrory, Nov 2025) estimated that tasks averaging ~90 minutes without AI were about **80% faster** with it. Those figures are themselves Claude's estimates, and the authors say they *exclude time spent outside the conversation, such as checking and verifying the output*. That excluded time is where agent-era estimates go wrong: verification, integration, decisions and waiting on the outside world.
3. **Gut feel is miscalibrated, for humans too.** [E] In METR's RCT (July 2025), 16 experienced OSS developers worked on 246 tasks in their own large repos. Before starting they forecast a **24% speed-up**. With AI they were actually **19% slower**, and afterwards they still believed AI had sped them up by about 20%. This was early-2025 tooling (Cursor with Claude 3.5/3.7) on mature, high-standard codebases where the developers were experts. That setting is close to the *worst case* for AI speed-up. The lesson is the miscalibration itself: AI speed-up varies with the setting, and self-reports are unreliable. Use a calibration log, not memory.

### A2. Task size and agent success: METR time horizons

- [E] METR's metric is the length of task, measured in *human expert time*, that an agent completes with 50% reliability. That length has doubled roughly every 7 months since 2019, and roughly every 4–4.5 months since 2023 (TH 1.1, Jan 2026). Secondary sources put the frontier 50% horizon at **≈16–17 h** (Claude Mythos Preview, May 2026). METR warns that measurements above ~16 h are unreliable on its current suite.
- [E] **The 80% horizon is much shorter**: about 4–5× shorter for Claude 3.7 Sonnet (59 min vs 15 min), and a reported ~3 h for the frontier model whose 50% horizon is ~16 h. Critics say the 80% figure depends heavily on how it is defined.
- [E] **Toby Ord's half-life model** (arXiv 2505.05115) fits METR's data with a *constant failure rate per minute of human-equivalent work*: `P(success) ≈ 0.5^(t_human / H50)`. Longer tasks contain more steps, and any single failure step sinks the attempt.
- [E] **METR's own caveats** (Jan 2026 note): the time horizon is *not* the length of work you can safely delegate. The task suites are self-contained, well-specified and graded automatically. Real work is "messier" (ambiguous specs, dynamic environments, resource limits). Secondary summaries report that success falls about 8 points per unit of messiness.
- [E] **Passing tests is not the same as done.**
  - METR, *Algorithmic vs Holistic Evaluation* (Aug 2025): Claude 3.7 Sonnet passed maintainer tests 38% of the time, yet **0 of 15 reviewed PRs were mergeable as-is**. The estimated human fix-up time was **~42 min per PR on average, and ~26 min even for PRs that passed the tests**.
  - METR note (Mar 2026): maintainers reviewed 296 agent PRs. Merge decisions ran about **24 points below SWE-bench pass rates**, and only 68% of the original human patches were re-approved by the same maintainers.
  - Watanabe et al.: 83.8% of 567 Claude Code PRs were eventually merged, but **45% of the merged PRs needed additional human changes** (bug fixes, docs, project conventions).
- [E] SWE-bench Verified tags each task by how long a human would need to fix it: ≤15 min (196 tasks), 15 min–1 h, 1–4 h (42), >4 h (3). The leaderboards show the largest spread between models on the 15 min–1 h band. One arXiv agent paper solved 0–2 of the 45 tasks over 1 hour.

**Implications for decomposition:**
- (a) Split work so that each unit is well inside the *effective* horizon for messy work, not the benchmark horizon.
- (b) Always budget a **human verification and fix-up tail** per unit and per PR. On older models this ran 15–40 min per PR. It is smaller today and for small diffs, but it never reaches zero.
- (c) Failure probability grows with unit length, so finer units give fewer catastrophic restarts.

### A3. Decomposition and accuracy

- [E] **Bottom-up beats top-down unless you have very similar reference projects** (Jørgensen 2004, an exploratory study with 7 teams). Top-down was accurate only when the estimators recalled very similar past projects. For agent-era work almost nobody has a calibrated reference class yet, so **default to bottom-up**.
- [E] **Breaking work down counters optimism.** Kruger & Evans (2004), *If you don't want to be late, enumerate*: breaking a task into steps increases estimates and reduces the planning fallacy, because holistic plans leave steps out. **Boundary conditions:**
  - The effect is weak when there are few components or the steps are easy.
  - It is not consistent across replications.
  - Carney & Ülkümen (2023) found it works mainly under *aleatory* (random-feeling) uncertainty.
- [E] **Size bias.** Small tasks tend to be over-estimated and large tasks under-estimated, though the effect depends on framing (Halkjelsvik & Jørgensen 2012 review; *Time Predictions*, 2018). Familiar, repetitive work is easier to predict than novel work.
- [E-weak] **How big the errors are.** Derek Jones's analysis of SiP data (~8k small tasks) found estimates typically off by about **a factor of 2 in either direction**. In lognormal terms that is σ ≈ 0.55–0.7. A lognormal is the standard model: the duration cannot go negative and has a heavy right tail.
- [E] **Fat tails at project scale.** Flyvbjerg & Budzier's 1,471 IT projects: the mean cost overrun was 27%, but **about 1 in 6 was a "black swan"** with a ~200% cost overrun. Reference-class forecasting picks a percentile (P50 or P80) according to risk appetite. Do not plan on the mean.
- [E] **The cone of uncertainty** (Boehm, McConnell) runs from 0.25×–4× at the initial concept, to 0.67×–1.5× once requirements are done, to about 0.9×–1.1× after detailed design. McConnell's key point: **the cone narrows only when decisions are made**, not with time or effort spent estimating. In the agent era, plan mode and spec documents are cheap ways to make those decisions early.
- [D] **Granularity sweet spot**, synthesised from the above:
  - Units that are too coarse hide steps.
  - Units that are too fine lose the "joints": the glue and integration between units, which this method budgets as a separate tail.
  - Target 5–15 units per task. Each unit should be 5–60 agent-minutes and end in a checkpoint that can be verified.

### A4. Unknown unknowns, spikes and Cynefin

- [E-weak] Practitioner consensus (Keogh, SDN, Withum):
  - **Clear and Complicated work can be estimated** in hours or days.
  - **Complex work** (cause and effect only visible afterwards) **cannot be estimated reliably**. Handle it with time-boxed experiments, or spikes.
  - **Chaotic work**: act first, stabilise, then estimate.
- [E-weak] **Liz Keogh's ignorance scale** (1 = everyone has done this … 5 = nobody in the world has). Work at the top of the scale should be run as a spike. This is the most practical complexity rating for this method, because it can be scored at intake.
- [D] In agent-era work, **novelty has three different axes**, and they behave differently:
  1. **Novelty to the agent**: is the stack and API well represented in training data? Was it released after the knowledge cutoff, or is it private?
  2. **Novelty to the environment**: is the codebase idiosyncratic, untested, or behind slow feedback loops?
  3. **Novelty to the human**: can the human *verify* the result and make the decisions?

  A mainstream stack that is new to the human is cheap with an agent. A private API that is new to the agent is expensive no matter who the human is.

### A5. The integration tail, or "last 10%"

- [E-weak] The 90-90 rule (Cargill, via Bentley in CACM 1985) is a joke, not data. Addy Osmani's **"70% problem"** describes the agent version: the AI produces a convincing 70% quickly, and the last 30% (edge cases, security, production integration) "remains as challenging as ever".
- [E] The METR fix-up times and the Watanabe revision rate (A2) quantify that tail.
- [E-weak] Building **thin end-to-end slices early** shrinks the tail, because integration risk is met sooner.
- [D] → The method budgets an **explicit integration/verification tail** that scales with the number of external integrations and deployment surfaces. It also makes the first checkpoint a *walking skeleton* that already reaches its deploy target.

### A6. Spec-driven development and plan mode

- [E-weak] **Kiro** (requirements.md → design.md → tasks.md with GIVEN/WHEN/THEN acceptance criteria), **GitHub Spec Kit** (specify → plan → tasks, plus `/analyze` to check consistency) and **Claude Code plan mode** (read-only exploration, then a plan, then execution) all generate a **work breakdown before any code is written**. The claimed benefit is that implicit requirements become explicit acceptance criteria, and that drift is reduced because every session checks against the same contract.
- [E-weak] **Costs:**
  - The upfront paperwork and review burden are not worth it for small scripts.
  - Kiro added a "Quick Spec" path and a separate bugfix spec.
  - Böckeler's review (martinfowler.com, Oct 2025) found the tools mostly "spec-first" rather than spec-anchored over time.
  - No controlled study comparing predictability with and without specs was found.
- [E-weak] Practitioner guidance: skip planning for tiny edits that are clearly scoped. Plan when the approach is uncertain, the change spans several files, or the code is unfamiliar.
- [D] **Role in this method:**
  - The plan or tasks file *is* the WBS. Re-estimate from it at checkpoint C1.
  - Planning costs about 5–15 min of agent time plus human time.
  - It pays off when there are 4 or more units, any Complicated or Complex units, or any decision point.
  - Planning narrows the cone, because it forces the decisions McConnell says are the only thing that narrows it.

### A7. Classifying tasks for AI suitability

- [E-weak] Anthropic's internal study (Dec 2025; 132 engineers surveyed, 53 interviews): engineers used AI in roughly 60% of their work but could *fully delegate* only about 0–20%, mostly work that is **easy to verify, low-stakes or routine**. About 27% of AI-assisted work would not have been done otherwise, for example "nice-to-have dashboards".
- [E-weak] Anthropic's autonomy and Claude Code research: as tasks get more complex, Claude asks for clarification more often and humans interrupt more. Human time grows with complexity faster than agent time does.
- [E] DORA 2025 (~5,000 respondents): AI is an **amplifier**. Teams with strong practices (tests, CI, small batches) gain, and weak teams see more instability.
- [D] **Three-way bottleneck classification used below.** Each unit's time is split into:
  - **Agent-bound** (A): generation, running and fixing in a loop.
  - **Human-bound** (H): decisions, taste and polish judgement, review, manual verification, handling credentials.
  - **World-bound** (W): waiting on third parties, app review, DNS, OAuth verification, CI queues, data access approvals.

  Human-era estimates mostly over-price A and leave out W.

---

## Part B — The estimation procedure

The procedure runs in seven steps: **Look → Classify → Decompose → Price → Combine → Report → Re-estimate**. Run it after (or as part of) planning, never as one holistic guess.

### B1. Intake checklist (gather signals; ask the human only when a signal is unknown)

Answer each item. An unknown answer counts as a **decision point**.

| # | Signal | Why it matters | How to measure before starting |
|---|---|---|---|
| 1 | **Definition of done**: acceptance criteria, who accepts, demo vs production | Vague "done" causes extra polish rounds | Can you write 3–7 GIVEN/WHEN/THEN lines? |
| 2 | **Greenfield vs existing code**; repo size; tests present? | Exploration cost; risk of regressions | `git ls-files \| wc -l`, test command exists and passes |
| 3 | **Files/components touched** | Breadth drives review and integration | Count from plan/grep: new files, modified files |
| 4 | **Stack mainstream?** Any library or version newer than the model cutoff, or private/internal APIs? | Novelty to the agent | List deps and versions; flag private SDKs |
| 5 | **External integrations** (APIs, OAuth, payments, email, webhooks, LLM APIs) | Highest variance plus world-bound waits | Count them; for each: are docs, sandbox and **credentials in hand now**? |
| 6 | **Data model changes**: new schema vs migration of live data; backfill? | Irreversibility, review time | Count tables/columns; live rows affected? |
| 7 | **UI fidelity**: functional / match the design system / pixel-match a mock / "make it feel good" | Number of human feedback rounds | Is there a mock? A component library? |
| 8 | **Deployment surface**: none / existing pipeline / first deploy to a new target / multiple targets (web + mobile + worker) | Infra unknowns, DNS/SSL/env vars | Is a deploy command already proven in this repo? |
| 9 | **Test expectations**: none / unit / E2E / coverage gate | Agent time and flakiness | CI config present? |
| 10 | **Feedback-loop latency and observability**: can the agent run it and *see* the result (tests, dev server, logs, screenshots)? Build/deploy cycle time? | Slow or invisible loops multiply debugging time | Time one build/test run; does it need a device, hardware or prod-only data? |
| 11 | **Human decision points**: open product questions, naming, trade-offs | Each costs human time and possibly latency | Count the "it depends" questions in the plan |
| 12 | **Human availability**: synchronous pair vs async check-ins | Elapsed time, not effort | Ask |
| 13 | **Stakes/irreversibility**: prod data, money, security, compliance | More review, more caution | Flag |
| 14 | **Known unknowns**: "why does X happen?", performance targets, "figure out how" | Complex-domain units become spikes | Phrases like "investigate", "optimise", "flaky", "sometimes" |

**Intake outputs:** counts for files (F), integrations (I), deploy surfaces (D), decision points (Q) and UI screens (S), plus a novelty score per axis (agent / environment / human, each 1–5 on Keogh's scale).

### B2. Classify each candidate unit (Cynefin plus ignorance)

| Domain | Test | Ignorance (Keogh) | Treatment |
|---|---|---|---|
| **Clear** | A pattern already exists in the repo or the stack is ubiquitous; the agent has done this thousands of times | 1–2 | Price from the table, σ low |
| **Complicated** | Known solution, but it needs analysis: specific API, several files, migration | 2–3 | Price from the table with multipliers; must be in the plan |
| **Complex** | The outcome is only knowable by trying: unknown bug cause, performance tuning, flaky integration, private or undocumented API, ML/LLM output quality, subjective UX feel | 4–5 | **Do not point-estimate.** Add a **time-boxed spike** unit (timebox = the spike's P80). After the spike, re-classify and re-price. |
| **Chaotic** | Production is broken now | – | Act and stabilise first; estimate the follow-up afterwards |
| **Disorder** | You cannot tell which domain applies | – | Intake is incomplete. Ask questions or run plan mode first. |

**[P] Gate rules:**
- If more than 30% of the P50 total sits in Complex units, report the estimate as **"spike-first"**: give a firm estimate only for the spikes plus a wide range for the rest.
- If any single unit's P50 exceeds 60 agent-minutes, decompose it further.

### B3. Decomposition template

Write the WBS as a table, one row per unit. Every task gets the **mandatory rows** (✱) even when they are small.

| id | category | description | domain | A (agent min, median) | H (human min, median) | σ | multipliers | risk events | done-check |
|---|---|---|---|---|---|---|---|---|---|
| U0 ✱ | PLAN | Explore repo, plan mode / spec, resolve decision points | | | | | | | plan approved |
| U1 | SCAFFOLD | … | | | | | | | app boots |
| … | CRUD/UI, LOGIC, INTEGRATION, DATA, INFRA, DEBUG/SPIKE, POLISH, TEST, DOCS | | | | | | | | |
| Un-1 ✱ | INTEGRATION-TAIL | End-to-end wiring, edge cases, fixes found when running the whole thing | | | | | | | full flow demo |
| Un ✱ | REVIEW/QA | Human reviews diff, manual acceptance, (deploy verification) | | | | | | | accepted |

**Rules [D]:**
- Order the units as a **vertical slice first** (walking skeleton: one path through UI → logic → data → deploy), then widen.
- Every unit must have a **done-check that the agent or human can run**.
- Units of the same category on the same pattern (e.g. "5 similar CRUD screens") can be priced as *first instance + (n−1) × repeat factor 0.3–0.5* [P]. The first instance carries the pattern discovery.

### B4. Per-unit baseline priors (AGENT-ERA minutes) — **all values [P], to be calibrated**

Assumptions behind the table:
- A current frontier coding agent (Claude Code class) with tool access, working in a repo where it can run code.
- Human paired synchronously.
- A = agent wall-clock time for a *Clear, familiar* instance. H = human active time (prompting, reviewing, deciding, clicking through).
- σ is the log-space spread before any adders.

| Category | Typical unit | A median | H median | base σ | Notes |
|---|---|---|---|---|---|
| PLAN | Explore + plan mode + Q&A | 3–10 (+1 per 10k LOC explored, cap 15) | 3–10 (+3 per decision point) | 0.3 | Skip for tiny clear edits |
| SCAFFOLD | New app/framework/project setup, deps | 3–8 | 1–3 | 0.4 | +risk event "dependency/version conflict" |
| CRUD/UI | One standard screen/component/endpoint using existing libs | 4–10 | 2–4 | 0.5 | Repeats ×0.3–0.5 |
| LOGIC | One well-specified rule cluster / pure module | 4–12 | 2–5 | 0.5 | Ambiguous rules → decision points |
| INTEGRATION | One external API/SDK with docs and creds in hand | 10–25 | 5–15 | 0.8 | OAuth, webhooks, payments: use the upper end, σ 0.9 |
| DATA (greenfield) | New schema/tables, seed | 3–8 | 2–4 | 0.4 | |
| DATA (migration) | Migrate/backfill existing live data | 10–25 | 10–20 | 0.7 | Human review ∝ stakes |
| INFRA (repeat) | Deploy via an existing, proven pipeline | 2–5 | 1–3 | 0.3 | |
| INFRA (first) | First deploy to a new target, CI, env vars, domain | 10–20 | 10–25 | 0.9 | + world-bound waits (DNS, approvals) |
| DEBUG/SPIKE | Unknown cause / feasibility question | timebox 20–45 | 10–20 | 1.0 | Complex domain; re-price afterwards |
| POLISH | Per feedback round: (agent 3–5 + human 4–8) × R rounds | R × 4 | R × 6 | 0.6 | R: functional 0–1, design system 1–2, mock-match 2–4, "feel" 3–6 |
| TEST | Unit tests for one module | 3–8 | 1–2 | 0.4 | E2E harness setup = INTEGRATION |
| DOCS | README/usage notes | 2–4 | 1–2 | 0.3 | |
| INTEGRATION-TAIL ✱ | End-to-end wiring and fix-ups | τ × Σ(A of build units) | τ × Σ(H of build units) | 0.6 | τ = 0.10 + 0.05·I + 0.05·D + 0.05·(legacy?1:0), cap 0.5 |
| REVIEW/QA ✱ | Human diff review + acceptance | 1–3 | 5 + 1 per 100 changed lines (+50% if stakes high) | 0.4 | Grounded in METR fix-up times; smaller for small diffs |

Where these numbers come from:
- They are back-solved so that a Clear "simple dashboard" lands at a P50 of roughly 45–65 min (see B8, Example A). That matches the user's observation and is about 4–5× below the human-era guess, consistent with the 4–7× over-estimation in A1.
- INTEGRATION and INFRA (first) get the widest σ because world-state, credentials and environment issues dominate them.
- REVIEW/QA is deliberately non-zero because of the METR and Watanabe tails.

**Multipliers on the median (m) and adders on σ [P]:**

| Factor | Level | × m | + σ |
|---|---|---|---|
| Novelty to agent | mainstream | 1.0 | 0 |
| | niche lib / version after model cutoff | 1.5 | +0.3 |
| | private/undocumented API | 2.0 | +0.5 (likely Complex → spike) |
| Environment | greenfield or clean repo with tests | 1.0 | 0 |
| | large/legacy, few tests, unconventional | 1.5 | +0.3 |
| Feedback loop | agent can run and observe (<1 min cycle) | 1.0 | 0 |
| | slow (>5 min build/deploy cycle) | 1.5 | +0.2 |
| | agent cannot observe (device, hardware, prod-only, visual-only) | 1.3 on A, **2.0 on H** | +0.3 |
| Spec clarity | acceptance criteria written | 1.0 | 0 |
| | vague | 1.2 | +0.3, and raise POLISH R |
| Verification | objective (tests, types, diff) | 1.0 | 0 |
| | subjective (UX taste, LLM output quality) | 1.2 on H | +0.3 |
| Stakes | normal | 1.0 | 0 |
| | prod data / money / security | 1.0 on A, 1.5 on H | +0.1 |
| Human novelty | human expert in domain | 1.0 | 0 |
| | human cannot judge correctness | 1.5 on H | +0.2 |

Cap the total σ per unit at 1.5. Above that, the unit is Complex: make it a spike.

**Discrete risk events [P].** Model each as a Bernoulli event with probability p that adds x minutes (lognormal, σ 0.5). Classify every added minute as A, H or W.

| Risk event | p (prior) | x median | Clock |
|---|---|---|---|
| Credentials/API keys/account access not ready | 0.5 if not confirmed | 30 (W) | W |
| Third-party approval: OAuth consent verification, app store, domain verification, quota raise | 0.3–0.6 | hours to days | W (report separately, never folded into minutes) |
| Dependency/version conflict on scaffold | 0.15 | 15 | A |
| CORS/auth/cookie/env-var issue at first deploy | 0.3 | 20 | A+H |
| Agent takes a wrong path, needs reset and re-plan (per Complicated unit >30 min) | 0.15 | = the unit's median | A+H |
| Flaky test / E2E harness instability | 0.25 when E2E required | 20 | A |
| Scope discovery: a decision point appears mid-build | 0.3 per vague requirement | 10 | H (+W if async) |

**Optional success-probability check, from Ord/METR [P].** For an autonomous run of a unit with human-equivalent size `t_h`:

`P(success) ≈ 0.5^(t_h / H50_eff)`

where `H50_eff = H50_benchmark / k_mess`, with `k_mess` ≈ 5–10 for real repos (a messiness and mergeability discount; prior). If P(success) < 0.8, split the unit or add a mid-unit checkpoint. Expected rework is ≈ (1 − P) × 0.5 × unit time.

### B5. Combining units into P50 / P80 / P95 (explicit math)

**Per unit i:**
- Total effort `T_i = A_i + H_i` (or treat the two separately).
- `T_i ~ LogNormal(μ_i, σ_i)`, with median `m_i = (A_i + H_i) × Πmultipliers` and `μ_i = ln m_i`.
- Mean `E_i = m_i · exp(σ_i²/2)`.
- Variance `Var_i = E_i² · (exp(σ_i²) − 1)`.

**Per risk event j** (probability `p_j`, size `X_j ~ LogNormal(ln x_j, s_j)`):
- `E[X_j] = x_j·exp(s_j²/2)` and `E[X_j²] = x_j²·exp(2 s_j²)`.
- Contribution to the mean: `p_j·E[X_j]`.
- Contribution to the variance: `p_j·E[X_j²] − (p_j·E[X_j])²`.

**Sum, using the Fenton–Wilkinson moment match to a single lognormal:**
```
M  = Σ E_i + Σ p_j E[X_j]
V  = Σ Var_i + Σ [p_j E[X_j²] − (p_j E[X_j])²]
σ_T² = ln(1 + V/M²)
μ_T  = ln M − σ_T²/2
```

**Common-cause correlation.** Units are not independent: a weird environment slows *everything*. Multiply the total by a shared factor `F ~ LogNormal(0, σ_c)`, with σ_c = 0.2 for a familiar environment and 0.3–0.4 for an unfamiliar one [P]. Then:
```
σ_tot = sqrt(σ_T² + σ_c²)
P50 = exp(μ_T)
P80 = exp(μ_T + 0.8416·σ_tot)
P95 = exp(μ_T + 1.6449·σ_tot)
```

**Sanity rules [E/statistics]:**
- The sum of unit medians is *below* the true P50, because right skew pulls the median of a sum upward.
- The sum of unit P90s is *above* the true P90.
- Never add percentiles.
- Checked against a 200k-run Monte Carlo for both worked examples, Fenton–Wilkinson was within 1–5% at P50, P80 and P95 (see B8).

**Monte Carlo version** (use it when there are parallel paths, or when the agent can execute code):
```python
import math, random
def simulate(units, risks, sigma_c=0.2, n=100_000):
    # units: [(median_min, sigma)], risks: [(p, median_min, sigma)]
    out = []
    for _ in range(n):
        t = sum(m*math.exp(random.gauss(0, s)) for m, s in units)
        t += sum(x*math.exp(random.gauss(0, s)) for p, x, s in risks if random.random() < p)
        out.append(t*math.exp(random.gauss(0, sigma_c)))
    out.sort(); q = lambda k: round(out[int(n*k)])
    return {"P50": q(.50), "P80": q(.80), "P95": q(.95)}
```

**Three-point shortcut, for when a unit is easier to bound than to model:** ask for P10 and P90 of the unit, then set `m = sqrt(P10·P90)` and `σ = ln(P90/P10) / 2.563`.

**What a given σ means:**

| σ | P90/P50 | P95/P50 | Typical for |
|---|---|---|---|
| 0.3 | 1.47 | 1.64 | repeat deploy, docs |
| 0.5 | 1.90 | 2.28 | CRUD/UI, logic |
| 0.7 | 2.45 | 3.16 | migrations, polish, "factor-of-2" human tasks (A3) |
| 0.9 | 3.17 | 4.39 | integrations, first deploy |
| 1.2 | 4.66 | 7.20 | spike territory |

**Elapsed time vs effort [P]:**
- Effort = ΣA + ΣH.
- Elapsed (synchronous pair) ≈ ΣA + ΣH × (1 − overlap) + ΣW_critical. The overlap is 0–0.3, from the human reviewing unit k while the agent builds k+1, or from parallel agents.
- Async human: add the expected response latency once per decision point and per review gate.
- World-bound waits measured in hours or days are **reported as calendar risk, not folded into the minute estimate**.

### B6. Output format

```
ESTIMATE — <task name>                         as of: <checkpoint C0/C1/C2>
Classification: <Clear | Complicated | Complex-heavy (spike-first)>   novelty A/E/H: 1/2/1
Work units: 9  (integrations: 1, deploy surfaces: 1, decision points: 2, UI screens: 3)

Effort (agent + human, pair-mode elapsed):  P50 62 min | P80 82 min | P95 ~1h45
  of which agent ≈ 55%, human active ≈ 45%  (human: 2 decisions, 2 polish rounds, review)
Calendar risks (not in the minutes above): none   |  or: "Google OAuth verification may take 1–5 days"
Human-era equivalent (for reference only): ~4–5 h — do not quote this as the estimate

Confidence: medium — units are Clear/Complicated; widest unit = first deploy (σ 0.7)
Top risks (by contribution to P80–P50 spread):
  1. First deploy env vars / CORS  (+20 min, p 0.3)
  2. Polish rounds exceed 2        (+10 min per extra round)
  3. Dependency conflict on scaffold (+15 min, p 0.15)
What would change this estimate:
  ↓ narrower: mock provided; deploy target already proven; creds confirmed
  ↑ wider: data must come from a third-party API (→ +1 integration, σ 0.9); pixel-match a design
Spikes proposed: none   |  or: "30-min spike: can the vendor API filter by date server-side?"
Re-estimate at: C1 after plan approval; C2 after walking skeleton is deployed
```

Rules [D]:
- Always give a **range**, never a single number. Lead with P50–P80.
- Quote P95 for commitments.
- State the **agent / human / world split**.
- Name the top 3 risks with what each would cost.
- List the facts that would narrow the range. Those facts are what the human should go and confirm.

### B7. Re-estimation checkpoints and calibration

| Checkpoint | Trigger | Action |
|---|---|---|
| **C0 Intake** | Before the plan | Output the class, the unit counts and a wide range (inherently about 0.25×–4× cone). For non-trivial tasks, recommend plan mode. |
| **C1 After plan/spec** | Plan approved; files to touch listed; decision points resolved | Rebuild the WBS from the plan's task list. Remove resolved decision points and re-price the units that changed. Typical effect: the range narrows (requirements-complete stage ≈ 0.67×–1.5×). |
| **C2 After first vertical slice** | Walking skeleton runs end-to-end, *including* deploy if deploy is in scope | Compute `k = geomean(actual_i / median_i)` over completed units. Shrink toward 1: `k_adj = k^(n/(n+2))` [P]. Multiply the remaining medians by k_adj. If any finished unit landed above its P80, raise σ by 0.2 on remaining units of the same category. |
| **Tripwires (continuous)** | A unit passes its **P80**, or reaches 2× its median with no visible progress | Stop. Re-classify the unit (it is probably Complex), convert it to a time-boxed spike, re-plan, and tell the human the new range. Never keep "nearly done" open-ended. |
| **C3 Pre-ship** | Build complete | Re-price the integration tail and review from the actual diff size and the issues found. |
| **Post-mortem** | Done | Append to the calibration log (below). |

**Calibration log.** Store one row per unit:
`date, task, unit_id, category, domain, multipliers, A_est, H_est, σ, A_actual, H_actual, W_actual, model/agent, notes`

**Calibration rules [D]:**
- Every 10–20 tasks, recompute the per-category median of actual/estimate, and the fraction of actuals that fall below P50 (target ≈ 50%) and below P80 (target ≈ 80%).
- Adjust the B4 medians by the category's ratio and the σ values by coverage error.
- This calibrated table is the reference class the method lacks today (Jørgensen; Flyvbjerg).
- Recalibrate whenever the model or agent harness changes. The METR horizon doubling time is about 4–7 months, so the priors drift downward over time.

### B8. Worked examples

All numbers below are [P] and come from the B4 priors, computed by Fenton–Wilkinson and checked against a 200k-run Monte Carlo.

**Example A — "Simple internal dashboard"**
- Scope: Next.js app, 3 charts + a table + a date filter over an existing Postgres database. Credentials are in the env. Deploy to an existing Vercel account. Mainstream stack, synchronous human.

| Unit | A | H | σ |
|---|---|---|---|
| PLAN | 2 | 3 | 0.3 |
| SCAFFOLD | 3 | 1 | 0.4 |
| DATA access (3 queries, existing DB) | 6 | 2 | 0.5 |
| UI: 3 charts + table + filter | 8 | 3 | 0.5 |
| POLISH (R = 1.5) | 5 | 6 | 0.6 |
| INFRA (first deploy on known platform) | 4 | 3 | 0.7 |
| INTEGRATION-TAIL + REVIEW | 4 | 3 | 0.6 |
| risk: dep/version conflict | p 0.15, 15 min | | |

- Sum of medians = 53 min, but the sum of medians understates P50 (B5).
- With σ_c = 0.2: **P50 ≈ 62 min, P80 ≈ 82 min, P95 ≈ 106 min.** Monte Carlo gives 62 / 81 / 106.
- With 20% review overlap, elapsed P50 ≈ 55 min. The human-era answer would be 4–5 h.

**Example B — the same dashboard, but the data comes from a third-party analytics API via OAuth, and credentials are not yet set up**
- DATA becomes INTEGRATION: A 25, H 15, σ 0.9.
- PLAN H rises to 5 (scopes and decisions).
- The tail rises to τ ≈ 0.2: A 6, H 5, σ 0.7.
- Risks: credentials not ready (p 0.5, 30 min); scope/quota issue (p 0.3, 20 min); dependency conflict (p 0.15, 15 min). σ_c = 0.25.
- Sum of medians = 91 min, but **P50 ≈ 2h10, P80 ≈ 3h20–3h30, P95 ≈ 5h+** (Monte Carlo 132 / 199 / 306 min).
- Calendar risk listed separately: "OAuth app verification, if required for external users, can take days."
- Swapping one unit **doubles the P50 and triples the P95**. This is the "other tasks blow up" behaviour, and it is visible *before* starting.

---

## Part C — Summary of what is evidence vs prior

- **Evidence-based [E]:**
  - LLMs overestimate their own task duration by 4–7× (5–10× in agentic settings).
  - Bottom-up estimation beats top-down without a close reference class.
  - Breaking work down reduces optimism, with boundary conditions.
  - Lognormal, fat-tailed estimation error, roughly a factor of 2 on small tasks; 1 in 6 IT projects is a black swan.
  - The cone of uncertainty narrows only through decisions.
  - Agent success decays with task length (METR horizons, Ord's half-life). The 80% horizon is about 4–5× shorter than the 50% horizon. Messiness lowers success.
  - Test-passing agent PRs still need human fix-up (METR: 26–42 min per PR on older models; maintainer merge rate ~24 points below SWE-bench; 45% of merged Claude Code PRs revised).
  - Developers misjudge AI speed-up (METR RCT).
  - AI amplifies existing practices (DORA).
  - Engineers fully delegate mainly verifiable, low-stakes work (Anthropic).
- **Practitioner/weak [E-weak]:** Cynefin and spike guidance; Keogh's ignorance scale; the 70% problem / 90-90 rule; the predictability benefits and overhead of spec-driven development; plan-mode guidance; the agent "rounds" estimation skill (2–4 min per round, unvalidated).
- **Proposed priors / design [P]/[D]:**
  - Every per-category minute value and σ in B4.
  - All multipliers and risk-event probabilities.
  - The integration-tail formula τ.
  - The success-probability messiness discount k_mess.
  - σ_c for correlation.
  - The shrinkage rule `k^(n/(n+2))`.
  - The overlap discount.
  - The gate thresholds (30% Complex → spike-first; >60 agent-min units → split).
  - The checkpoint design and output template.

  All of these should be calibrated with the B7 log.

---

## Sources

- METR, *Measuring AI Ability to Complete Long Tasks* (Mar 2025) and Time Horizon 1.1 (Jan 2026) — via https://metr.org/time-horizons/ and secondary summaries: https://forum.nunosempere.com/posts/YJ7Pk2bwTd3ieimG8/metr-measuring-ai-ability-to-complete-long-tasks , https://en.wikipedia.org/wiki/METR , https://futuresearch.ai/app/p/a/frontier-metr-time-horizon-2029
- METR, *Time horizon limitations* note (Jan 2026): https://metr.org/notes/2026-01-22-time-horizon-limitations/
- METR, *Research Update: Algorithmic vs. Holistic Evaluation* (Aug 2025): https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/
- METR, *Many SWE-bench-Passing PRs Would Not Be Merged into Main* (Mar 2026): https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/ ; https://the-decoder.com/half-of-ai-written-code-that-passes-industry-test-would-get-rejected-by-real-developers-new-study-finds/
- METR developer-productivity RCT (Jul 2025): https://techcrunch.com/2025/07/11/ai-coding-tools-may-not-speed-up-every-developer-study-shows ; https://thezvi.substack.com/p/on-metrs-ai-coding-rct
- Toby Ord, *Is there a half-life for the success rates of AI agents?*: https://arxiv.org/pdf/2505.05115
- 80% vs 50% horizon critique: https://www.greaterwrong.com/posts/sBEzomgnYJmYHki9T/updated-metr-s-data-can-t-distinguish-between-trajectories
- Garikaparthi, *Can LLMs Perceive Time?* (ICLR 2026 workshop): https://arxiv.org/abs/2604.00010
- *Your Agents Are Not Time Aware* (MATS): https://www.lesswrong.com/posts/eAbuPXbjakop5rSJx/your-agents-are-not-time-aware ; agent-estimation skill: https://skillselion.com/skills/zhanghandong/agent-estimation ; https://agentpatterns.ai/human/agent-time-estimates-not-schedules/
- Anthropic, *Estimating AI productivity gains from Claude conversations* (Nov 2025): https://www.anthropic.com/research/estimating-productivity-gains
- Anthropic, *How AI is transforming work at Anthropic* (Dec 2025): https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- SWE-bench Verified difficulty annotation: https://openai.com/index/introducing-swe-bench-verified/ ; per-bucket leaderboard: https://www.vals.ai/benchmarks/swebench-2025-09-24 ; https://arxiv.org/pdf/2608.06811
- Watanabe et al., Claude Code PRs (83.8% merged, 45.1% revised) — via https://arxiv.org/html/2509.14745v3
- Jørgensen (2004), top-down vs bottom-up: https://web-backend.simula.no/sites/default/files/publications/SE.4.Joergensen.2004.d.pdf
- Kruger & Evans (2004) unpacking, plus moderators: https://dlab.sauder.ubc.ca/sjdm/presentations/2023-Poster-Carney-Stephan-Uncertainty-Time-Forecasting.pdf ; https://uwspace.uwaterloo.ca/handle/10012/6863
- Halkjelsvik & Jørgensen, *Time Predictions* (2018) / 2012 review: https://www.simula.no/about/news/new-book-springerbriefs-series-time-predictions-torleif-halkjelsvik-and-magne-jorgensen ; https://bps.org.uk/research-digest/productivity-forecasts-depend-whether-you-focus-work-completed-or-time-taken
- Derek Jones, estimate/actual factor: https://shape-of-code.com/2022/06/19/over-under-estimation-factor-for-most-estimates/ ; lognormal task model: https://thesearesystems.substack.com/p/task-estimation-conquering-hofstadters
- Flyvbjerg & Budzier, IT overruns / reference-class forecasting: https://aaronpercival.substack.com/p/when-it-projects-go-wild-what-we ; https://www.pmi.org/learning/library/planning-fallacy-causes-solutions-project-expectations-6374 ; https://arxiv.org/pdf/2210.01573
- McConnell, Cone of Uncertainty: https://www.construx.com/blog/the-cone-of-uncertainty/ ; https://concepts.dsebastien.net/concept/cone-of-uncertainty/
- Cynefin and estimation: https://lizkeogh.com/2013/07/21/estimating-complexity/ ; https://sdn.nl/nieuws/why-we-suck-at-estimation/ ; https://www.hanssamios.com/dokuwiki/how_can_we_put_an_estimate_on_complexity
- 90-90 rule: https://en.wikipedia.org/wiki/Ninety%E2%80%93ninety_rule ; Osmani, *The 70% Problem*: https://addyosmani.com/agentic-engineering/the-70-percent-problem/
- Spec-driven development: https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html ; https://www.morphllm.com/spec-driven-development ; https://www.verdent.ai/guides/agents/kiro-spec-driven-development
- Plan mode practice: https://www.openhands.dev/blog/claude-code-best-practices-agentic-coding ; https://codewithmukesh.com/blog/plan-mode-claude-code/
- DORA 2025: https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report
- Sum of lognormals / Fenton–Wilkinson / percentile contingency: https://apps.dtic.mil/sti/pdfs/AD1016907.pdf ; https://ftp.fau.de/cran/web/packages/PRA/vignettes/MCS.html
