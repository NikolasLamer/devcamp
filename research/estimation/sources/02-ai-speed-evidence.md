# 02 — Empirical evidence: how much do AI coding tools/agents change development time?

Researcher angle: measured and reported speedups, where they're large, small, or negative. Compiled 2026-10-26.

## How to read this file (provenance flags)

- **[V]**: verified in this session against the primary source (anthropic.com / claude.com pages fetched directly) or against several consistent secondary write-ups that quote the primary.
- **[S]**: secondary sources only (search-engine summaries of press or blog coverage). The primary was not reachable from this sandbox: metr.org, arxiv.org, github.blog, faros.ai and dora.dev all failed DNS through WebFetch.
- **[M]**: from my prior knowledge (training data up to mid-2026) and **not re-verified this session**. The web-search budget ran out partway through. Treat [M] items as "probably right, check before quoting."

---

## 1. Headline numbers at a glance

| Study / source | Setting | Result | Flag |
|---|---|---|---|
| METR RCT (Jul 2025) | 16 experienced OSS devs, 246 real issues in their own mature repos (avg task ~2h), early-2025 tools (Cursor + Claude 3.5/3.7) | **19% slower** with AI. Devs *believed* AI made them **~20% faster**. Before the study they forecast ~24% speedup; economists and ML experts forecast ~38–39% [M for the forecast numbers] | [S]/[M] |
| METR uplift update (24 Feb 2026) | Redesigned study, 57 devs, 143 repos, 800+ tasks, Aug 2025 onward | Returning devs (n=10): speedup **−18%** (CI −38%…+9%). New recruits (n=47): **−4%** (CI −15%…+9%). Both CIs cross zero. METR calls the data *unreliable* because many devs refused the no-AI arm (one secondary source says 30–50%), which biases the estimate downward. METR's stance: "speedups now seem likely," and the earlier 20% slowdown is "now outdated," but the size is unknown | [S] (METR X post quoted) |
| GitHub Copilot controlled experiment (Peng et al., 2023) | ~95 recruited devs, write an HTTP server in JS from scratch | **55.8% faster** (≈2.3× speed) on a small, greenfield, well-specified task | [M] |
| Google enterprise RCT (Paradis et al., ICSE-SEIP 2025) | 96 Google SWEs, one complex enterprise task, internal AI features, summer 2024 | **~21% less time** (96 vs 114 min raw). Wide CI. Devs who code more hours/day gained more | [S] |
| Cui, Demirer, Jaffe, Musolff, Peng, Salz (Management Science 2025) | 3 field RCTs (Microsoft, Accenture, Fortune-100), 4,867 devs, Copilot | **+26.08% completed tasks** (SE 10.3%). Larger gains and higher adoption among less-experienced devs | [S] |
| Microsoft OCE lab (Edelman, 2024) | 147 Upwork subjects | 29% faster, no significant accuracy change | [S] |
| Stanford, Denisov-Blanch (~100k devs, 600+ cos, 2025 talks) | Telemetry on private repos, "delivered functionality" metric | Gross output +30–40%, but rework cuts **net to ~15–20%** (matched-team median ~10%). **Simple greenfield +30–35%, complex greenfield +10–15%, simple brownfield +15–20%, complex brownfield 0–10% (can be negative).** Niche languages (COBOL/Haskell/Elixir) can go negative on complex tasks. Matrix comes from 136 teams in 27 cos | [S] |
| Faros AI "AI Productivity Paradox" (2025) | Telemetry, >10k devs, 1,255 teams | High-AI-adoption teams: **+21% tasks, +98% PRs merged, PR review time +91%, PR size +154%, bugs/dev +9%**. **No significant company-level improvement.** A later dataset (~22k devs) reports +34% task throughput [S, unverified] | [S] |
| DORA 2024 | ~3k respondents | +25% AI adoption associated with **−1.5% delivery throughput, −7.2% delivery stability**, plus small gains in docs/code quality/review speed (+3.1%) | [S] |
| DORA 2025 ("State of AI-assisted SW Dev") | ~5k respondents | ~90% use AI. >80% say it improved their productivity. AI ↔ throughput relationship flipped to **positive**. AI **still associated with higher instability** (more change failures and rework). Only 24% trust AI output highly; 30% trust it little or not at all. "AI is an amplifier" of the existing org | [S] |
| DX (getdx) Q4 2025 | 135k devs / 435 cos (self-report subset 58k) | Self-reported **3.6 h/week saved** (daily users 4.1 h, Staff+ 4.4 h), roughly 9–10% of a 40h week. Doubled from ~2 h in Q4 2024, then plateaued near 4 h despite rising adoption. Q1 2026: ~3.9 h/wk, 93% adoption | [S] |
| Atlassian State of DevEx 2025 | 3,500 devs | 68% say AI saves them >10 h/week, **but** 50% lose >10 h/week to org friction. Net ≈ 0 | [S] |
| Stack Overflow 2025 survey | ~49k devs | 66% say AI output is "almost right, but not quite." **45% say debugging AI code is more time-consuming.** Trust 33% vs active distrust 46% (3% high trust). Among agent users, 70% say agents cut dev time; 38% say quality improved | [S] |
| Stack Overflow 2026 survey (Oct 2026) | — | 73% of AI users use it daily. Agent use 59% (31% in 2025). Claude Code use 41%→55% among agent users (Apr 2026 pulse). AI rated useful for implementation (74%) and debugging/refactor (72%), but only ~34% for design or communication. 48% trust AI only when output is easy to verify. Only 9.6% use answers as-is | [S] |
| GitClear 2025 (211M changed lines, 2020–2024) | Repo-level code-change analytics | Duplicated 5+ line blocks **8×** in 2024. "Moved" (refactored) lines **−39.9%**. 2024 was the first year copy/paste exceeded moved lines. 2-week churn roughly doubled (3.3%→6.9%, 2021→2024) | [S] |
| Uplevel (2024) | ~800 devs with/without Copilot | No significant cycle-time gain, ~41% more bugs | [M] |

---

## 2. Anthropic's own data

### 2a. "Estimating AI productivity gains from Claude conversations" (Nov 2025) [V]
- 100k Claude.ai conversations. Claude itself estimated the task time with and without AI.
- Average task **~90 min without AI**, and Claude **cuts task time ~80%** (≈5×). Software developers account for 19% of the implied economy-wide gain, the largest of any occupation. Implied +1.8 pp/yr US labor productivity growth.
- **Validation is weak.** On 1,000 OSS JIRA tickets, Claude Sonnet 4.5's time estimates correlated with actual time at Spearman ρ = 0.44 (log-Pearson 0.46). Human developers scored ρ = 0.50 (0.67). **Claude overestimates short tasks and underestimates long ones.** This is directly relevant to the cookbook's problem.
- Limitations the authors state: time spent validating or refining outside the chat isn't counted. Code quality vs human isn't measured. They note that METR's RCT on end-to-end features found no time savings.

### 2b. Anthropic Economic Index, Jan 2026 ("Economic primitives", Nov-2025 data) [V]
- Software-dev requests: a competent professional would take **~3.3 h** without AI, versus **~15 min** of human-AI collaboration time. That's ≈13× *within the conversation*, model-estimated and not validated.
- **Success rate:** software development 61% versus 78% for personal tasks. Overall 67% on Claude.ai, 49% on the API.
- **Real-world task horizon:** on the API, success falls from ~60% (tasks under 1h) to ~45% (5h+), crossing **50% at ~3.5 h** of human-equivalent work. On Claude.ai, multi-turn conversations extrapolate to 50% at ~19 h, likely because human feedback rescues longer tasks.
- Speedup grows with task complexity: 9× for prompts needing high-school-level education versus 12× for college-level. Success-adjusted productivity gain drops from 1.8 to ~1.0–1.2 pp/yr.
- Top task: "Modifying software to correct errors," 6% of Claude.ai and ~10% of API records.

### 2c. Anthropic Economic Index, Mar 2026 ("Learning curves") [V]
- Users who signed up 6+ months earlier have a ~10% higher conversation success rate (≈3–5 pp in regressions with controls). **Experience with the tool matters.**
- Coding is shifting to the API and agents. Claude Code splits work into many smaller API calls.

### 2d. Anthropic Economic Index, Jun 2026 ("Cadences") [V]
- Survey of ~9,700 users (30% in computer/math jobs, so not representative): **86% report speed gains**, 82% scope gains, 69% quality gains.
- Claude Code shows higher autonomy than chat for 26 of 31 output types. App-building conversations use more than 3× the median tokens.
- No coding time-saved figures are published.

### 2e. "How AI is transforming work at Anthropic" (Dec 2025) [V]
- 132 engineers surveyed, 53 interviews, ~200k internal Claude Code transcripts.
- Claude is used in **59% of work** (28% a year earlier). Self-reported productivity **+50%** (+20% a year earlier). 14% report >100% gains.
- **+67% merged PRs per engineer per day** after Claude Code rollout.
- **27% of Claude-assisted work wouldn't have been done otherwise.** "Speedup" partly means *more scope*, not less time.
- More than half the engineers can "fully delegate" only **0–20%** of their work. Engineers delegate tasks that are easy to verify, low-stakes, repetitive, well-scoped, or outside their context and low in complexity. They keep design and "taste" work.
- Most-used for debugging (55% daily), code understanding (42%) and new features (37%). Some respondents spend *more* time, mainly debugging Claude's code.
- Transcripts Feb→Aug 2025: task complexity 3.2→3.8 (on a 1–5 scale), max consecutive tool calls 9.8→21.2, human turns per transcript 6.2→4.1.

### 2f. "Measuring AI agent autonomy in practice" (Feb 2026) [V]: Claude Code session stats
- **Median Claude Code turn ≈45 s.** The 99.9th-percentile turn grew from under 25 min to over 45 min (Oct 2025→Jan 2026), then settled around 42 min.
- Internally, success on the hardest tasks doubled (Aug→Dec 2025) and human interventions per session fell from **5.4 to 3.3**.
- Experienced users (750+ sessions) use full auto-approve in >40% of sessions (versus ~20% for new users), but *interrupt more* (9% versus 5% of turns).
- Claude's stops: presenting a choice of approach (35%), gathering diagnostics or test results (21%), clarifying vague requests (13%). Humans interrupt mostly to supply missing context or corrections (32%), or because Claude is slow or hanging (17%).

### 2g. "How Anthropic teams use Claude Code" (2025, claude.com blog) [V], anecdotes only
- Security debugging resolves "3× as quickly" (on 10–15 min problems). Documentation research went from ~1 h to 10–20 min ("80% reduction"). A K8s outage diagnosis saved ~20 min. Ad variants took "minutes instead of hours."
- Only successes are reported, so this is selection-biased.

### 2h. Anthropic coding-skills RCT (Jan 2026) [V]
- 52 mostly junior devs learning an **unfamiliar library (Trio)**. The AI group finished only **~2 min faster (23 vs 25 min, not significant, p = 0.39)**, but scored **17 pp lower** on a comprehension quiz (50% versus 67%). The biggest gap was on debugging questions.
- **Takeaway:** when the developer has to learn something new, AI gives little wall-clock speedup, and full delegation costs understanding.

### 2i. Anthropic Economic Index, Apr 2025 (software development) [V]
- Claude Code conversations are **79% automation**, versus 49% on Claude.ai.
- Top languages: JS/TS 31%, HTML/CSS 28%, Python 14%, SQL 6%. Top tasks: UI/UX component development (12%), web and mobile app development (8%).
- Startups make up 32.9% of Claude Code conversations versus 23.8% for enterprise. Front-end and CRUD work in popular stacks dominates agent use.

---

## 3. METR time horizons (what agents can do *alone*)

- Original paper (Mar 2025): 50%-success horizon doubling **~every 7 months** (212 days, 2019–2025) [S].
- **TH 1.1** (Jan 2026): suite expanded to 228 tasks (31 long). Doubling time **131 days since 2023 and ~89 days since 2024**, roughly 3–4.5 months [S].
- Data points [S]:
  - Claude Opus 4.5 (Nov 2025): **~4 h 49 min** at 50% on TH1.0 (CI 1h49m–20h25m), ~320 min on TH1.1.
  - Public frontier Feb–Mar 2026: **~12 h** (METR Frontier Risk Report, via secondary).
  - **Claude Mythos Preview (early)**, added 8 May 2026: 50% horizon **≥16 h** (point ~17.4 h, CI ~8.5–55 h), **80% horizon ~3.1 h (186 min)**. METR: ">16 h is unreliable with our current task suite."
  - The horizons page has been **frozen since 8 Sep 2026**. Claude Opus 5.5 (released 22 Sep 2026) got no numeric horizon. For GPT-5.6 Sol, METR said its numbers aren't robust.
  - A 3 Mar 2026 correction lowered recent horizons by up to 20%.
- **Caveats for estimation:**
  1. Horizons are measured in *human-expert time*. A 50% horizon means a coin flip.
  2. The 80% horizon is ~5× shorter than the 50% horizon.
  3. Success drops on "messy" tasks. METR's 16-factor messiness rubric covers things like unclear success criteria and irreversible actions.
  4. METR's Aug 2025 "algorithmic vs holistic" study: on 18 real OSS issues (maintainer time 20 min–4 h, mean 1.3 h), Claude 3.7 Sonnet passed the original tests **38%** of the time, but PRs often weren't mergeable as-is. The usual gaps were test coverage, docs, lint or format, and code quality. My memory is that ~0% were mergeable without fixes and they needed ~20–30 min of extra human work each [M — unverified].
- **Rule of thumb from §2b and §3:** tasks a human would size at ≤1–3 h are usually agent-completable with light supervision. Tasks over ~4–8 h need decomposition or human steering, or expect retries.

---

## 4. Where speedups are large vs small vs negative

### Large (≥3×)
- **Mechanical, test-verifiable migrations and codemods at scale:**
  - Airbnb: ~3.5k Enzyme→RTL test files, estimated at **1.5 engineer-years, done in 6 weeks** (≈13× calendar). 97% were migrated automatically [S, company blog].
  - Google internal LLM migrations (Jan 2025 paper): ~80% of code in migration CLs AI-authored, engineers estimate **~50% total time saved** (≈2×) [M].
  - Amazon Q Java 8/11→17 upgrades: Jassy said the average went from **~50 developer-days to a few hours**, with **~4,500 developer-years** saved [M; company claim].
- **Small, well-specified greenfield code:** HTTP server +55.8% [M], even with 2023 autocomplete. Stanford simple greenfield +30–35% net at team level with older tools. Anthropic's model-estimated 3.3 h→15 min for software requests (≈13×, unvalidated).
- **Lookups, code comprehension, docs research:** Anthropic anecdotes show ~80% reduction (≈5×).
- **Boilerplate-heavy UI/CRUD in popular stacks:** these are the dominant agent use cases (Anthropic EI Apr 2025), and language popularity predicts gains (Stanford). *No RCT directly measures agentic CRUD/UI speed.* The ≥3× figure is extrapolation from the above plus practitioner reports.

### Modest (1.1–2×)
- **Org-level throughput:** +26% tasks (Cui), +21% (Google RCT), net +10–20% (Stanford), +21% tasks (Faros), ~4 h/week self-reported (DX).
- **Complex greenfield:** +10–15% (Stanford).
- **Debugging and refactoring:** widely used (Anthropic 55% daily; SO 2026 72% "useful"), but 45% of devs say debugging AI code takes longer (SO 2025). The net effect varies widely.

### ~Zero or negative
- **Experts in large, mature codebases they know well:** METR 2025 −19%. METR 2026 −4% for new recruits (CI −15%…+9%), unreliable and probably biased toward slowdown. Stanford complex brownfield 0–10%, sometimes negative.
- **Niche or low-resource languages on complex tasks:** can be negative (Stanford).
- **Learning an unfamiliar library under time pressure:** ~0 speedup, with a comprehension cost (Anthropic Trio RCT).
- **Org-level delivery stability:** negative (DORA 2024 −7.2% stability; DORA 2025 still higher instability).

---

## 5. Mechanisms: why some tasks don't compress (the "last mile")

1. **The 70% problem (Addy Osmani, Dec 2024; book *Beyond Vibe Coding*, O'Reilly 2025):** AI gets you a convincing ~70% fast. The last 30% (edge cases, race conditions, accessibility, security, integration) "takes longer than the first 70%" and needs human judgment [S].
2. **Review and verification bottleneck:** Faros reports PR review time +91% and PR size +154%. The Fast & Spurious survey (arXiv 2510.24265, 415 practitioners) found review time didn't drop and frequent AI users do *more* reviews [S]. Generation speedup is capped by Amdahl's law on review.
3. **Rework and churn:** GitClear churn doubled and duplication rose 8×. Stanford: rework turns +30–40% gross into +15–20% net. Faros: bugs/dev +9%. DORA: more change failures.
4. **Org friction dominates:** Atlassian reports 10 h/wk saved by AI ≈ 10 h/wk lost to org inefficiency. Faros sees no company-level gain. DORA says AI "amplifies" what's already there.
5. **Context deficit in brownfield code:** METR 2025 devs cited implicit repo knowledge and high quality standards. Anthropic's JIRA validation notes Claude sees only ticket text while devs have full context.
6. **Feedback-loop wall-clock time doesn't shrink:** CI runs, deploys, cloud provisioning, data backfills and human approvals take the same time. *(Inference: no study isolates this, but it follows from the above and is why infra/data work likely compresses less.)*
7. **Scope expansion:** 27% of Anthropic's AI-assisted work wouldn't have been done otherwise. Teams spend saved time on more scope, so calendar time per project falls less than time per task.

---

## 6. Perception vs reality

| Evidence | Perceived | Measured |
|---|---|---|
| METR 2025 | +20% faster (after); +24% forecast (before) [M for 24%] | **−19%** |
| Expert forecasters (METR 2025) | +38–39% [M] | −19% |
| Anthropic internal | +50% self-reported productivity | +67% merged PRs/eng/day (an output proxy, not time) |
| Faros | (individual) +21% tasks, +98% PRs | no company-level improvement |
| DX vs Atlassian | DX: 3.6–4 h/wk saved (~10%) | Atlassian: 68% claim >10 h/wk. Self-reports differ ~2.5× depending on question framing |
| Anthropic productivity estimate | model-estimated −80% task time | Claude's time estimator: ρ ≈ 0.44 vs actuals; humans ρ ≈ 0.50 |
| Fast & Spurious survey | frequent users feel faster | little overall self-reported productivity change on SPACE dimensions |

**Implication:** self-reports and model-estimated savings run *high* for brownfield and expert work. For greenfield and mechanical work, the measured numbers are themselves large. Calibrate by task type, not by feel.

---

## 7. Speedup table for the estimation cookbook

"Speedup" = traditional human-only estimate ÷ actual wall-clock time with an agent + competent human pair, through to *merged/shipped*, not just code generated. These figures are for 2026-era frontier agents (Claude Code class).

| Task category | Typical speedup vs human-only estimate | Confidence | Basis / sources | Notes & caveats |
|---|---|---|---|---|
| Throwaway prototype / demo / internal tool, popular stack (React/TS/Python), greenfield | **4–10×** | Low–Medium | Anthropic EI Jan 2026 (3.3 h→15 min model-estimated); Peng 55.8% with 2023 autocomplete; Stanford simple greenfield highest bucket; UI/web dominate agent use (EI Apr 2025) | **Extrapolation.** No RCT on agentic greenfield. Matches the "dashboard 4–5 h → ~45 min" anecdote (≈6×). Falls fast if production-grade polish is required |
| Production CRUD/UI feature in a *clean, conventional* codebase | **2–4×** | Low–Medium | Stanford simple brownfield/greenfield; Cui +26% (autocomplete era); Anthropic +67% PRs/eng | Review + tests + polish ("last 30%") eat much of the generation gain |
| Large mechanical migration / codemod / framework upgrade with good test oracle | **3–15× calendar** | Medium | Airbnb 1.5 yr→6 wk; Amazon Java upgrades 50 days→hours [M]; Google ~2× total time [M] | Company self-reports. The wide range depends on oracle quality and long-tail manual cases (Airbnb: 3% manual) |
| Writing unit/integration tests for existing code | **2–5×** | Low–Medium | Anthropic: easy-to-verify, well-scoped tasks are delegated most; Airbnb test migration | Little direct measurement. Watch for shallow tests (METR holistic: test coverage was a common failure) |
| Docs, code explanation, codebase Q&A, API research | **3–5×** | Low–Medium | Anthropic team anecdotes (~80% reduction); code understanding is 42% of daily use | Anecdotal and selection-biased |
| Debugging: reproducible bug with clear signal (failing test, stack trace) | **1.5–3×** | Low | Anthropic security team "3×"; debugging is top use (55%) | Survey data mixed |
| Debugging: intermittent / distributed / perf / "why is prod weird" | **0.8–1.5×** | Low | SO 2025: 45% say debugging AI code takes longer; Anthropic engineers report extra time debugging Claude's code | Wall-clock dominated by reproduction and observation loops. Extrapolation |
| Feature in large, mature brownfield repo by an expert who knows it | **0.8–1.3×** | **Medium–High** (best-studied category) | METR 2025 (−19%); METR 2026 (−4%, CI −15…+9%, likely biased low); Stanford complex brownfield 0–10%; Google RCT ~1.27× (21% less time) | METR says early-2026 speedups are "likely" but unmeasured. Don't apply greenfield multipliers here |
| Complex greenfield (novel architecture, algorithms, concurrency) | **1.1–2×** | Low–Medium | Stanford complex greenfield +10–15% (older tools); horizons improve fast | Design and "taste" stay human (Anthropic) |
| Refactoring / dedup / cleanup at scale | **1.5–3×** (if test-guarded) | Low | Anthropic "papercuts" are 8.6% of Claude Code tasks; SO 2026 72% find AI useful for debug/refactor | GitClear: AI-era code shows *less* refactoring by default. Only happens if explicitly requested |
| Infra / DevOps / IaC / CI config | **1.2–2.5×** | Low (extrapolation) | No direct study found. Inferred from feedback-loop latency + irreversibility (METR messiness factors; only 0.8% of agent actions are irreversible because humans gate them) | Deploy/provision/approval wall-clock doesn't compress |
| Data pipelines / ETL / SQL / backfills | **1.5–3×** for the code; **~1×** for run/validate cycles | Low (extrapolation) | SQL is 6% of coding queries (EI); no time study found | Correctness validation on real data is the bottleneck |
| Learning an unfamiliar library/framework while building | **~1–1.3×** | Medium | Anthropic Trio RCT (~2 min faster, n.s.; −17 pp comprehension) | Juniors gain more in throughput (Cui) but learn less |
| Niche/low-resource languages, complex tasks | **0.8–1.2×** | Low–Medium | Stanford (COBOL/Haskell/Elixir) | |
| Org/team-level delivered features per quarter | **1.1–1.35×** | Medium–High | Cui +26%; Stanford net 15–20%; Faros +21% tasks / no co-level gain; DX ~10% time; DORA | Task-level speedups don't add up to calendar savings: review, coordination and scope growth absorb them |
| Code review of AI-generated PRs | **<1×** (more review time) | Medium | Faros review +91%, PR size +154%; Fast & Spurious | Budget explicitly |

---

## 8. Suggested estimation heuristics (derived from the evidence)

1. **Split the work into a generation part and a fixed part.** Estimate = (human estimate of *code-writing* share ÷ S_task) + (verification/review + integration + feedback-loop wall-clock, mostly uncompressed).
   - Typical code-writing share of a human estimate: ~30–60%. Anthropic EI: programmers spend 23% of time writing/maintaining code and 15% analyzing/rewriting programs.
   - By Amdahl's law, even infinite generation speed caps the total speedup at ~1.7–3× unless verification also speeds up. That's why the large multipliers only show up when verification is cheap: throwaway prototypes, test-oracle migrations.
2. **Use the horizon gate.** If a human would size the task at ≤1–3 h, it's well within 2026 frontier 80%-reliability horizons, so expect near-one-shot completion. For 4–16 h, expect retries and steering; decompose. For over a day, plan human checkpoints. The API real-world 50% crossing is ~3.5 h (EI Jan 2026).
3. **Apply a brownfield/familiarity discount.** Mature repo + expert owner + high quality bar → use 0.8–1.3×, not 3–10×.
4. **Add a rework tax.** Stanford: about half of gross output gain is lost to rework. GitClear/DORA show more churn and instability. Add ~15–30% for review and fixups on production work.
5. **Account for operator experience.** Six or more months of tool tenure gives ~+10% success (EI Mar 2026). Interventions per session are falling over time (5.4→3.3). New users should get lower multipliers.
6. **Don't trust self-perceived speedup or LLM-estimated "time saved."** Measured results run ~40 pp below perception in brownfield (METR). Claude's own time estimates have ρ ≈ 0.44 vs actuals, overestimate short tasks and underestimate long ones (Anthropic Nov 2025). This is exactly the bias the cookbook needs to correct.

---

## 9. Gaps / where evidence is thin

- **No published RCT measures *agentic* (Claude Code / Codex-class) speedup on greenfield CRUD/UI work**, which is the category where the ~45-min-dashboard anecdote lives. The best evidence is model-estimated (Anthropic EI) or anecdotal.
- METR's 2026 RCT is self-declared unreliable. A 2026 replication with modern agents and a credible no-AI control doesn't exist yet, because devs won't give up AI.
- Infra/DevOps, data pipelines and debugging-of-prod have essentially **no** controlled time studies. The table values for them are extrapolations.
- Most telemetry (Faros, DX, Jellyfish, LinearB) is vendor-published, mostly correlational, and from the 2024–2025 Copilot/autocomplete era. I didn't retrieve specific Jellyfish or LinearB 2025–26 numbers before the search budget ran out.
- METR horizon numbers after May 2026 (Opus 5.5, GPT-5.6) aren't robustly published. The page is frozen.

## Sources

Fetched directly this session:
- https://www.anthropic.com/research/estimating-productivity-gains
- https://www.anthropic.com/research/anthropic-economic-index-january-2026-report
- https://www.anthropic.com/research/economic-index-march-2026-report
- https://www.anthropic.com/research/economic-index-june-2026-report
- https://www.anthropic.com/research/impact-software-development
- https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- https://www.anthropic.com/research/measuring-agent-autonomy
- https://www.anthropic.com/research/AI-assistance-coding-skills
- https://claude.com/blog/how-anthropic-teams-use-claude-code

Via search results and secondary coverage:
- https://metr.org/blog/2026-02-24-uplift-update/
- https://x.com/METR_Evals/status/2026355544668385373
- https://www.matthewswong.com/en/blog/metr-developer-productivity-2026-uplift-update/
- https://particula.tech/blog/metr-reversed-19-percent-slower-ai-coding-study
- https://metr.org/blog/2026-01-29-time-horizon-1-1/
- https://metr.org/time-horizons/
- https://www.techmeme.com/251221/p1
- https://en.wikipedia.org/wiki/METR
- https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons
- https://arxiv.org/html/2410.12944v2 (Google RCT)
- https://papers.ssrn.com/abstract=4945566 (Cui et al.)
- https://www.ai.engineer/talks/tbDDYKRFjhk-ai-developer-productivity (Stanford)
- https://redmonk.com/rstephens/2025/12/18/dora2025/
- https://www.techrepublic.com/article/news-dora-ai-report-2025/
- https://redmonk.com/rstephens/2024/11/26/dora2024/
- https://getdx.com/report/ai-assisted-engineering-q4-impact-report/
- https://www.atlassian.com/blog/developer/developer-experience-report-2025
- https://stackoverflow.blog/2025/07/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here
- https://stackoverflow.blog/2026/10/06/the-results-of-the-2026-developer-survey-are-here/
- https://itbrief.com.au/story/stack-overflow-survey-shows-developers-trust-ai-with-caveats
- https://devclass.com/2025/02/20/ai-is-eroding-code-quality-states-new-in-depth-report/ (GitClear)
- https://getunblocked.com/blog/ai-productivity-paradox/ (Faros)
- https://addyosmani.com/agentic-engineering/the-70-percent-problem/
- https://addyo.substack.com/p/beyond-the-70-maximizing-the-human
- https://www.infoq.com/news/2025/03/airbnb-llm-test-migration/
- https://arxiv.org/html/2510.24265v1 (Fast & Spurious)

From memory, not re-verified this session [M]:
- Peng et al. 2023 (arXiv 2302.06590)
- METR 2025 forecasts (arXiv 2507.09089)
- Google LLM migrations (arXiv 2501.06972)
- Amazon Q Java upgrade claims (Jassy, Aug 2024)
- Uplevel 2024
- METR holistic "~0% mergeable" detail
