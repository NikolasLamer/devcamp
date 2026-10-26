# 03 — Why LLMs mis-estimate, and what an agentic session's wall clock is made of

Researcher angle: (a) why LLM time estimates are wrong, (b) the anatomy of agent-session wall-clock time, (c) blow-up risks.
Date: 2026-10-26.

**How to read the evidence labels**
- **[P]** = primary source I read directly in this session: an Anthropic page or doc, a GitHub issue page, or prompt text in a git repo.
- **[S]** = secondary. These come from search-engine summaries or third-party coverage. I could not open the primary page because of fetch restrictions in this sandbox.
- **[M]** = from my own background knowledge (training data). I did not re-verify these in this session, so treat them as leads.
- **[J]** = my judgment or synthesis.

**Coverage limits**
- The web-search budget ran out partway through.
- Many domains failed DNS lookup in WebFetch: metr.org, arxiv.org, lesswrong, simonwillison.net, harper.blog and others.
- So the practitioner section (Willison, Yegge, Beck, Reed, Huntley, agency pricing) is thinner than planned and mostly [M].

---

## 1. Why LLMs produce bad time estimates

### 1.1 The mechanism: "anthropocentric time bias"

**Monperrus & Stenqvist, "Coding Agents Have Completely Wrong Sense of Time" (blog) [S]**
- Agents estimate in *human* time but run in *machine* time.
- They put the gap at **1–3 orders of magnitude**.
- Example: a plan Claude priced at "3–4 weeks" (with a "Phase 1: schema migration (3–4 days)") finished in **~11 minutes**.
- They give two causes:
  1. Training data is written by humans and about humans, so it prices work in human-days and human-weeks.
  2. The model has no proprioception of elapsed time. In their words, "positional encoding represents token order, not elapsed wall-clock time."
- Their recommended fix: stop the agent estimating in days or weeks. Have it describe **files touched, tool calls, and breakage risk** instead.
- URL: https://www.monperrus.net/martin/coding-agents-sense-of-time

**MATS-program study, via The Decoder and a LessWrong post "Your Agents Are Not Time Aware" [S]**
- Setup:
  - 200 ProgramBench tasks plus an 18-benchmark suite.
  - Claude Code and Codex predicted their runtime before each task and reported elapsed time afterwards.
- Findings:
  - Pre-task estimates clustered around **~90 minutes regardless of difficulty**.
  - Retrospective elapsed-time error was **~3× for Claude** and **6–10× for Codex**.
  - Error was worst on short tasks.
  - Agents also overrated the quality of their own work.
- The harness matters:
  - Claude Code kept going until it judged the task done.
  - Codex stopped after about 30 minutes almost regardless of the task.
  - The same model took ~2.5× as many steps in Claude Code as in Codex.
- The fix: giving the agent an **elapsed-time tool** "largely fixed" estimation. Stripping timestamps from transcripts roughly doubled the error.
- I could not open the primary write-up. Related arXiv paper: "AgentTime: Can Agents Estimate and Control Their Own Runtime?" (arXiv 2610.09944), not read.
- URLs:
  - https://the-decoder.com/ai-agents-have-no-sense-of-time-and-are-not-aware-of-it/
  - https://www.lesswrong.com/posts/eAbuPXbjakop5rSJx/your-agents-are-not-time-aware

**Eivind Kjosbakken, "Why Claude Code Time Estimates Are Poor" (Towards Data Science / Substack) [S]**
- Same diagnosis: the model reports human-scale durations learned from blog posts about how long implementations took.
- Fix 1: ask Claude to estimate each step "from the perspective of how long an LLM would spend on it."
- Fix 2: decompose into small tasks, because small tasks are easier to estimate.
- URL: https://towardsdatascience.com/why-claude-code-time-estimates-are-poor/

**Anecdotes [S]**
- Stark Insider (May 2026): Claude estimated a phase at "6–8 hours of coding"; it was done in ~10 minutes.
- Digg thread: an estimate of "3 weeks" actually took 126 min.
- Reddit (Apr 2026): an estimate of "about 2 days" actually took 12 min. The user built a calibration plugin; I could not find the plugin.

### 1.2 The best quantitative data: Anthropic's JIRA validation of Claude's estimates [P]

Source: Anthropic, "Estimating AI productivity gains from Claude conversations" (Tamkin & McCrory, Nov 2025). https://www.anthropic.com/research/estimating-productivity-gains

The validation set was a JIRA benchmark of 1,000 software tasks with real actual durations:

| Estimator | Spearman ρ vs actual | r on log scale |
|---|---|---|
| Human developers | **0.50** | **0.67** |
| Claude Sonnet 4.5 (title + description only) | 0.44 | 0.46 |
| Claude Sonnet 4.5 + 10 calibration examples | 0.39 | 0.48 |

- The paper's key qualitative finding: Claude's estimates are **compressed**. It "significantly **overestimates short tasks and underestimates long ones**" and is "more prone to overestimates" overall.
- Self-consistency across prompt variants was high, r = 0.89–0.93. So the estimates are *reliably* biased, not noisy.
- Note what this benchmark measures: *human* task durations. Even at estimating human time, Claude is only "directional." Asked about its *own* agentic time, it has no ground truth at all.
- The paper also notes Claude sometimes produces outliers, such as programming tasks it rates as taking humans *years*.
- **[J] Why this matters for the cookbook:** the compression pattern explains *both* halves of the observed problem:
  - Small, well-specified tasks get inflated estimates. "Dashboard: 4–5 h" becomes ~45 min actual.
  - Large or ambiguous tasks get deflated estimates. That is where the "took much longer than predicted" cases live.
  - Add the anthropocentric bias on top (human time instead of agent time) and small tasks are inflated twice.

### 1.3 Humans are miscalibrated too (perception gap)

**METR RCT, July 2025 [S]**
- 16 experienced open-source developers, 246 real tasks in their own mature repos, Cursor with early-2025 models.
- Before the study, the developers predicted **−24%** time with AI.
- Measured result: **+19%** time (slower), 95% CI roughly +2% to +39%.
- Afterwards they still believed AI had sped them up by ~20%.
- The slowdown was attributed to time spent reviewing and correcting AI output.

**METR update, Feb 2026 [S]**
- Point estimates:
  - Returning developers: −18% (CI −38% to +9%).
  - New recruits: −4% (CI −15% to +9%).
- Secondary sources disagree on the sign convention. Either way, both intervals cross zero.
- METR said the data was unreliable for two main reasons:
  - **30–50% of developers declined the no-AI arm.**
  - Time tracking broke down for developers running **multiple agents concurrently**.
- METR's view: developers are "likely more sped up" in early 2026 than in early 2025, but the size is unknown.
- **[J]** Self-reports, and LLM estimates of speed-up, should be discounted. "Estimate vs actual" logs with timestamps are the only trustworthy calibration data.

### 1.4 Anthropic's own product response: Claude Code's "no time estimates" rule [P]

The system-prompt history is reconstructed from the Piebald-AI/claude-code-system-prompts git history. I cloned it and read the diffs. https://github.com/Piebald-AI/claude-code-system-prompts

**v2.0.43 (2025-11-19)** added a section "Planning without timelines":
> "When planning tasks, provide concrete implementation steps without time estimates. Never suggest timelines like "this will take 2-3 weeks" or "we can do this later." Focus on what needs to be done, not when. Break work into actionable steps and let users decide scheduling."

**v2.0.56 (2025-12-02)** added to the AskUserQuestion guidance:
> "When presenting options or plans, never include time estimates - focus on what each option involves, not how long it takes."

**v2.1.9 (2026-01-15)** renamed the section to "No time estimates" and expanded it:
> "Never give time estimates or predictions for how long tasks will take, whether for your own work or for users planning their projects. Avoid phrases like "this will take me a few minutes," "should be done in about 5 minutes," "this is a quick fix," "this will take 2-3 weeks," or "we can do this later." Focus on what needs to be done, not how long it might take. Break work into actionable steps and let users judge timing for themselves."

**v2.1.53 (2026-02-24)** split the prompt into atomic files. The rule became:
> "Avoid giving time estimates or predictions for how long tasks will take, whether for your own work or for users planning projects. Focus on what needs to be done, not how long it might take."

**v2.1.111 (2026-04-16)**: the file was **REMOVED**. It went out in the same release as several other "Doing tasks" rules (read before modifying, no premature abstractions, and others). I found no current replacement in the repo.
- [J] My guess is that the removal was part of a broader prompt slimming for newer models, not a policy reversal. That is unconfirmed.

**Related GitHub issues on anthropics/claude-code [P]**
- **#8952** (Oct 5, 2025), "Agents inappropriately report time estimates":
  - Agents said "This will take 2-3 days", "Migration effort: 1-2 days", "Effort: 3-5 days".
  - The reporter's reasons this is wrong: "Agents don't implement in real-time"; "User works at their own pace"; it "Creates false expectations".
  - Proposed fix: "Report complexity (simple/moderate/complex), not duration."
  - Auto-closed as not planned.
- **#20270** (Jan 23, 2026), "'No time estimates' rule might be making Claude Code lazy":
  - Claude refused ~4-line changes as "not worth the complexity" or "we can do that later."
  - Suggested fix: "don't give the user time estimates, but do assess effort internally to calibrate your responses."
  - **[J]** Lesson: suppressing the *output* of an estimate doesn't fix the model's internal effort prior. That prior still inflates small tasks.
- **#55576** (May 2, 2026), "Claude Code overestimates task duration and bails from tasks claiming they're too complicated":
  - "unprompted provide time estimates numbered in weeks for tasks that I know in the past would take it 30 minutes."
  - The reporter suspects the "offer to /schedule" prompt frames every task as a weeks-long project. That is a hypothesis.
- **#101700** (feature request): show an ETA for the current prompt by default. Users want measured ETAs, not predicted ones.

### 1.5 Academic work on LLM effort and story-point estimation [S]

- **arXiv 2603.06276:**
  - LLMs on story-point estimation across 16 projects, zero-shot, few-shot and comparative judgment.
  - Performance was comparable to state-of-the-art deep-learning estimators without training data, and improved with a few labelled examples.
- **arXiv 2403.08430:** search-optimized few-shot examples gave a 59% MAE improvement over zero-shot.
- **arXiv 2604.03443 (ICPC '26):** RAG for story points. I only saw the intro.
- **"Hybrid Intelligence Effort" (VTT):**
  - 22 developers, 110 tasks, 3 LLMs.
  - Argues story points and size metrics fail to capture effort in LLM-assisted development, because effort shifts toward **oversight**.
  - This matches the cookbook's premise.
- **Calibration generally:**
  - arXiv 2604.01896: 11 LLMs gave 95% intervals that contained the true value only **9–44%** of the time. More reasoning effort did not help consistently.
  - General finding: LLM numeric estimates are overconfident.
- **Critique:** shape-of-code (May 2026), "software task estimation using LLMs is fake research." Many papers use human *estimates* as ground truth rather than actuals.
- **[J] Gap:** I found no paper benchmarking LLMs at estimating *agent+human* wall-clock time. All of the above estimates human effort.

---

## 2. Anatomy of an agentic session's wall clock

### 2.1 Measured data points

**Anthropic, "Measuring AI agent autonomy in practice" (early 2026) [P]** — https://www.anthropic.com/research/measuring-agent-autonomy

| Metric | Value |
|---|---|
| Median Claude Code **turn** duration (prompt → agent stops) | **~45 s**, fluctuating 40–55 s |
| 99.9th-percentile turn | **<25 min (Oct 2025) → >45 min (Jan 2026)**; elsewhere cited as ~42 min; declined somewhat after mid-Jan |
| Human interventions per session (internal, Aug→Dec 2025) | **5.4 → 3.3** |
| Full auto-approve use | ~20% of sessions for new users (<50 sessions) → >40% by 750 sessions |
| Human interrupt rate | ~5% of turns for new users, ~9% for experienced users (they monitor actively) |
| On complex tasks | Claude stops to ask >2× as often as humans interrupt it |

Why Claude stops itself:

| Reason | Share |
|---|---|
| Choosing between approaches | **35%** |
| Gathering diagnostic info / test results | **21%** |
| Clarifying vague requests | **13%** |
| **Requesting credentials or access** | **12%** |
| Approval before acting | 11% |

Why humans interrupt:

| Reason | Share |
|---|---|
| Missing technical context / corrections | **32%** |
| Claude slow, hanging or excessive | **17%** |
| Enough help to proceed | 7% |
| Want to take next step themselves | 7% |
| Changing requirements | 5% |

**Anthropic, "How AI is transforming work at Anthropic" (survey of 132 staff plus 200k internal Claude Code transcripts) [P]**

| Metric | Feb 2025 | Aug 2025 |
|---|---|---|
| Max consecutive tool calls per transcript | 9.8 | **21.2** |
| Human turns per transcript | 6.2 | **4.1** |
| Task complexity (1–5 scale) | 3.2 | 3.8 |
| Transcripts implementing new features | 14.3% | 36.9% |

Survey results:
- Most staff can "fully delegate" only **0–20%** of their work.
- Self-reported productivity boost: +50%.
- Merged PRs per engineer per day: +67%.
- 27% of Claude-assisted work wouldn't have been done otherwise. This scope expansion is an estimation hazard in itself.

**Claude Code docs `/usage` example [P]** — https://code.claude.com/docs/en/costs
- The example output shows `Total duration (API): 6m 20s` against `Total duration (wall): 6h 33m 10s`.
- This is a doc illustration, not a statistic. It still shows the point well: **model time can be a small fraction of wall time.** The rest is the human, tools, and idle.

**METR time horizons [S]**
- The 50%-success task length, measured in *human* expert time, doubled roughly every 7 months from 2019; possibly every ~4 months in 2024–25.
- Measured values:
  - Claude 3.7 Sonnet: ~50 min (Mar 2025).
  - Opus 4.5: "nearly 5 hours", cited by Anthropic [P].
  - Opus 4.6: ~12–14.5 h [S].
  - Later models: ≥16 h; METR says its suite saturates there.
  - 80%-success horizons are several times shorter, e.g. ~3 h for the best model [S].
- **[J]** The horizon is a capability ceiling under ideal autonomy, not a session duration. Anthropic explicitly says its turn-length data and METR horizons are "not directly comparable."

**METR "algorithmic vs holistic" (Aug 2025) [S]**
- Claude 3.7 Sonnet passed maintainer tests on **38%** of real OSS issues.
- **None** of the reviewed test-passing PRs were mergeable as-is. Failures were inadequate tests, missing docs, lint/format/type issues, and code quality.
- A secondary blog cites an average **~42 min** to fix agent PRs to mergeable, "about a third of the original human time." I could NOT verify this on METR's page.
- METR follow-up (Mar 2026): **~half** of test-passing SWE-bench-Verified PRs from recent agents would not be merged by maintainers. The agents had no chance to iterate on feedback.

### 2.2 Generation speed

**Claude output throughput [S]**
- Artificial Analysis snapshots: about **43–60 output tokens/s** for Sonnet 4.6 and Opus 4.5/4.6. The figure varies by effort setting.
- Claude Code "fast mode" makes Opus "up to **2.5×** faster" at higher price [P]. Supported on Opus 5.5, Opus 5 and Opus 4.8. https://code.claude.com/docs/en/fast-mode
- Current models (Opus 5.5, Sonnet 5.5, Haiku 5.5) **always use extended thinking**, and thinking tokens count as output [P, costs doc].

**[J] Back-of-envelope**
- 1,000 lines of code ≈ 10–15k tokens, which is ~3–6 min of pure generation at ~50 tok/s.
- Thinking can double or triple the output tokens.
- So pure generation for a "simple dashboard" (~500–1,500 LOC including tests) is about **5–15 min**.
- The rest of a 45-minute session is reading, tool runs, human review and iteration.

### 2.3 Tool and environment latency

**Harness limits [P]** — from this session's own tool definitions and the Piebald prompt repo:
- Bash commands default to a **2 min** timeout, with a **10 min** foreground maximum.
- Long jobs go to background with monitoring.
- Claude Code's wake-up guidance uses "a CI run that takes ~8 minutes" as its canonical example.
- Prompt cache TTL is 5 min or 1 h. A break longer than the TTL makes the next turn re-process the full context, which is slower and costlier.

**[J] Typical ranges**
- File reads, grep and edits: sub-second each.
- Unit test subset: 5–60 s.
- Full test suite or build: 1–10 min.
- Dependency install: 0.5–5 min.
- Container or dev-env cold start: 1–10 min.
- CI pipeline: 5–30 min.
- Deploy: 2–20 min.

### 2.4 Context management [P]

Claude Code best-practices doc: https://code.claude.com/docs/en/best-practices

- "Claude's context window fills up fast, and performance degrades as it fills."
- Auto-compaction summarizes history. Instructions from early in the conversation "may be lost."
- "If you've corrected Claude more than twice on the same issue in one session, the context is cluttered with failed approaches. Run `/clear` and start fresh." A clean session with a better prompt "almost always outperforms" a long one.
- "Give Claude a check it can run … It's the difference between a session you watch and one you walk away from. … Without a check … you become the verification loop: every mistake waits for you to notice it."
- "If you could describe the diff in one sentence, skip the plan."
- "Time spent making the spec precise pays off more than time spent watching the implementation."

---

## 3. Model: agent-era task time = components

```
T_wall ≈ T_frame                                   (spec / prompt / plan approval)
       + N_iter × (T_turn + T_review + T_respond)  (the interactive loop)
       + T_env                                     (setup, installs, auth, creds, deploy, CI)
       + T_verify_final                            (human acceptance: run app, click through, read diff)
       + T_blowup                                  (rabbit holes; see section 4)

T_turn  ≈ T_prefill/TTFT + (output+thinking tokens)/(tok/s) + Σ tool latency
```

| Component | Typical range | Evidence |
|---|---|---|
| **T_frame**: writing the prompt or spec, answering clarifying questions, approving the plan | 2–10 min for small tasks; 15–60 min for a feature spec ("interview me → SPEC.md") | [J]. The docs recommend spec-first for larger features [P]. 13% of Claude stops are vague-request clarifications [P]. |
| **T_turn**: one agent turn | median **~45 s**; long tail to **25–45+ min** at p99.9 | [P] Anthropic autonomy data |
| Generation inside a turn | ~50 tok/s, ~2.5× faster in fast mode; ~3–6 min per 1k LOC before thinking | [S]/[P]/[J] |
| Tool latency inside a turn | seconds (edit/grep/unit test) to minutes (build, full suite, install) | [J], harness caps [P] |
| **N_iter**: human turns per session | ~**3–6**; Anthropic internal 4.1 per transcript, 3.3–5.4 interventions per session | [P] |
| **T_review**: human reads diff, checks the output | 1–5 min per turn for code; 2–10 min for UI (run, look, screenshot) | [J]. METR: review and correction drove the 2025 slowdown [S]. |
| **T_respond**: human latency before the next prompt | 10 s–2 min if attentive; **minutes to hours** if multitasking or running parallel agents | [J]. The docs' `/usage` example shows API 6 min vs wall 6.5 h [P, illustrative]. |
| **T_env**: auth, credentials, deploy, env friction | 0 if the env is warm; **10–60+ min** for first-time setup, OAuth apps, cloud consoles, DNS | [J]. 12% of agent stops are for credentials or access [P]. |
| **T_verify_final**: making output mergeable to human standard | Not mergeable as-is is common. Secondary figure: ~42 min, or ~⅓ of the original human time, for 2025-era agents | [S], unverified |
| Context resets / compaction | +2–10 min per reset (re-prompting, re-orienting); quality drops if not reset | [P] qualitative, [J] numbers |

**[J] Worked example: "simple dashboard," ~45 min actual**

| Phase | Time |
|---|---|
| Frame | ~5 min |
| ~4 iterations × (≈2 min agent + ≈3 min review/respond) | ~20 min |
| Env (npm install, dev server) | ~5 min |
| Visual polish loop (2 rounds) | ~10 min |
| Final check | ~5 min |
| **Total** | **≈45 min** |

- The pure model time inside that is maybe 8–12 min.
- The LLM's "4–5 h" is the human-developer typing and lookup time it remembers from training data. That cost has nearly vanished.

**[J] The structural insight:** in agent-era work, **wall time is dominated by human-in-the-loop latency and external-system waits, not by code production.**
- Estimate by counting **iterations, human decisions, and external waits**, not lines of code.
- Rough rule: one agent turn plus review is about 3–8 min.
- A well-specified small feature is about 3–6 such cycles.

---

## 4. Blow-up risk factors and suggested multipliers

Multipliers apply to the baseline "happy-path" estimate from section 3. Labels: **E** = some evidence; **J** = judgment.

| Risk factor | Why it blows up | Suggested multiplier | Basis |
|---|---|---|---|
| **Unclear or changing requirements** | Agent builds the wrong thing fast; each redirect costs a full cycle | ×1.5–3 | E (partial): 32% of human interrupts are missing context or corrections, 5% changing requirements; 13% of agent stops are vague requests [P]. Multiplier is J. |
| **No automated verifier** (no tests or screenshot loop) | Human becomes the test loop; every bug waits for a human to notice | ×1.5–2 | E (qualitative): Anthropic docs [P]. Multiplier is J. |
| **Visual/UI polish to a taste bar** | Subjective, unbounded iterations; each round needs a human look | ×1.5–3; open-ended without a reference design | J. Docs recommend screenshot comparison [P]. |
| **External services, credentials, OAuth, cloud consoles** | Human must act in another system; waits on propagation, approvals, rate limits | +15–60 min flat per new integration, or ×1.5–2 | E (partial): 12% of agent stops are credential/access requests [P]. Numbers are J. |
| **Unfamiliar or hallucination-prone APIs** (new SDK versions, niche libraries) | Plausible-but-wrong code; debug loops | ×1.5–2 | J. Osmani's "70% problem": the last 30% is "as time consuming as ever" [S]. |
| **Flaky or slow environment** (slow CI, flaky tests, broken local env) | Each verify cycle costs minutes; agent may chase flakes | ×1.5–3 (scales with CI time × iterations) | J |
| **Debugging production issues** | Needs logs, access and reproduction; hypothesis loops; agent can't see prod | ×2–4, wide variance | J. Debugging is the top Claude Code use (55% daily, survey [P]), but I found no duration data. |
| **Data migrations / irreversible operations** | Require human approval, dry runs and backups; "approval before acting" stops | ×1.5–3 | J. 11% of stops are approval-before-acting [P]. Irreversible actions are 0.8% of API tool calls [P]. |
| **Large or legacy codebase, mature repo standards** | Context gathering; output not mergeable to maintainer standards | ×1.3–2 | E: METR RCT (+19% time for experts in their own mature repos) [S]; agent PRs not mergeable as-is [S]. |
| **Long sessions / context saturation** | Degraded performance after many corrections; compaction loses instructions | ×1.2–1.5, or reset | E (qualitative): Anthropic docs ("after two failed corrections, /clear") [P]. |
| **Rabbit holes / agent over-engineering** | Agent pursues a wrong approach autonomously; "Claude slow, hanging, or excessive" is 17% of interrupts | ×1.3–2 | E (partial) [P]. Multiplier is J. |
| **Scope creep ("while we're at it")** | Cheap generation invites extra features; 27% of AI-assisted work is work that "wouldn't have been done otherwise" | ×1.2–2 | E (partial) [P]. Multiplier is J. |
| **Multiple parallel agents** | Throughput rises but per-task wall clock rises (human attention is time-sliced); time tracking breaks | Per task ×1.5–3 latency; total throughput up | E (qualitative): METR's 2026 time-tracking problems with concurrent agents [S]. Numbers are J. |
| **Well-specified, greenfield, verifiable, familiar stack** | The good case | ×0.5–1 against the baseline | J. Consistent with the Monperrus/Stark/Reddit anecdotes of 10–100× under the LLM's human-time estimate [S]. |

**[J] Combining multipliers**
- Don't multiply them all together. Take the largest one or two and add +25% for each additional factor.
- Report a range, not a point. LLM intervals are badly under-covered: 9–44% coverage of nominal 95% intervals.

---

## 5. Practitioner rules of thumb (collected)

| Rule | Source | Status |
|---|---|---|
| Don't express agent work in human days. Use **files touched, tool calls, breakage risk**. | Monperrus | [S] |
| Report **complexity (simple/moderate/complex), not duration**. | GH #8952 | [P] |
| Suppress user-facing estimates but still **assess effort internally**, so the agent doesn't bail on small tasks. | GH #20270 | [P] |
| Ask the model to estimate "from the perspective of an LLM", and decompose into small steps. | TDS / Kjosbakken | [S] |
| **Give the agent a clock** (elapsed-time tool, timestamps). Estimation errors largely disappear. | MATS study | [S] |
| Give it a verifier; that is what makes a session "walk-away-able." | Anthropic best practices | [P] |
| One-sentence diff → skip planning. Multi-file or unfamiliar → plan first. | Anthropic best practices | [P] |
| Two failed corrections → `/clear` and re-prompt. | Anthropic best practices | [P] |
| Spec precision beats watching implementation. | Anthropic best practices | [P] |
| The first ~70% comes fast; the last ~30% (edge cases, security, integration) is as slow as ever. | Addy Osmani, "The 70% Problem" | [S] |
| **Review is the bottleneck.** High-AI-adoption teams merged many more PRs but PR review time rose sharply (Faros AI 2025 reported ~+98% PRs and ~+91% review time). | Faros AI 2025 | [M], verify before citing |
| Spec → plan → execute in small prompts; brainstorming the spec takes ~15 min. | Harper Reed, "My LLM codegen workflow atm" (Feb 2025) | [M], not re-verified |
| Running agents in a loop ("Ralph Wiggum") turns time into cost; he framed agent labor in $/hour terms. | Geoffrey Huntley | [M], not re-verified |
| Measure, don't self-report: perceived speed-up diverges from measured speed-up. | METR 2025 | [S] |

**Not covered for lack of search budget:**
- Simon Willison's specific estimation posts.
- Steve Yegge / Gene Kim *Vibe Coding*.
- Kent Beck "augmented coding."
- HN "estimate vs actual" threads.
- Agency pricing of AI-assisted projects. One Portuguese post, horadecodar.com.br "Como precificar um projeto que você vai construir com Claude Code?", was found but not read.

---

## 6. Implications for an estimation cookbook [J]

1. **Never let the model estimate in human hours from its prior.** Its prior is *compressed human time*, which is double-wrong:
   - It is human-paced rather than agent-paced.
   - It is compressed, inflating small tasks and deflating large ones.
2. **Estimate in cycles.**
   - Count the human decisions and iterations expected (≈3–6 for a small well-specified feature), times 3–8 min per cycle.
   - Add external waits (installs, CI, deploys, credentials) explicitly.
   - Then apply risk multipliers.
3. **Separate deterministic waits from human waits.** CI and deploys are measurable; human latency dominates and depends on attention mode (focused vs parallel agents).
4. **Large or ambiguous tasks are where the model under-estimates.** That is exactly where the agent era has *not* removed time: requirements, integration, production debugging, taste. Decompose those before estimating.
5. **Calibrate locally.**
   - Log timestamps per session (turn starts and ends, human-response gaps).
   - Feed past estimate-vs-actual pairs back in as few-shot examples. Note that Anthropic's own few-shot calibration did *not* help on human-time JIRA estimates, so local, agent-time actuals are what matter.

## Sources

**Primary — read directly**
- Anthropic, Estimating AI productivity gains: https://www.anthropic.com/research/estimating-productivity-gains
- Anthropic, Measuring AI agent autonomy in practice: https://www.anthropic.com/research/measuring-agent-autonomy
- Anthropic, How AI is transforming work at Anthropic: https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- Claude Code docs:
  - https://code.claude.com/docs/en/best-practices
  - https://code.claude.com/docs/en/costs
  - https://code.claude.com/docs/en/fast-mode
  - https://code.claude.com/docs/en/how-claude-code-works
- GitHub issues on anthropics/claude-code:
  - #8952: https://github.com/anthropics/claude-code/issues/8952
  - #20270: https://github.com/anthropics/claude-code/issues/20270
  - #55576: https://github.com/anthropics/claude-code/issues/55576
  - #101700: https://github.com/anthropics/claude-code/issues/101700
- Piebald-AI/claude-code-system-prompts (git history: commits 36fded1, 47571b6, 0f37d97, f7330d2, c1b7c8b): https://github.com/Piebald-AI/claude-code-system-prompts

**Secondary — search summaries only**
- METR:
  - https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/
  - https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/
  - https://metr.org/blog/2026-02-24-uplift-update/
  - https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/
  - https://arxiv.org/pdf/2507.09089
- Time awareness:
  - https://www.monperrus.net/martin/coding-agents-sense-of-time
  - https://the-decoder.com/ai-agents-have-no-sense-of-time-and-are-not-aware-of-it/
  - https://www.lesswrong.com/posts/eAbuPXbjakop5rSJx/your-agents-are-not-time-aware
  - https://arxiv.org/html/2610.09944v1
- Estimation practice:
  - https://towardsdatascience.com/why-claude-code-time-estimates-are-poor/
  - https://www.starkinsider.com/2026/05/claude-code-autonomous-coding-time-hack.html
  - https://addyosmani.com/agentic-engineering/the-70-percent-problem/
- Estimation research:
  - https://arxiv.org/pdf/2603.06276
  - https://arxiv.org/pdf/2403.08430
  - https://arxiv.org/pdf/2604.01896
  - https://cris.vtt.fi/en/publications/hybrid-intelligence-effort-for-software-effort-estimation-in-llm-/
  - https://shape-of-code.com/2026/05/10/software-task-estimation-using-llms-is-fake-research/
- Artificial Analysis Claude speed comparisons: https://artificialanalysis.ai/
