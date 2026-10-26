# 05 — Mining past sessions and calibrating estimates

**Scope:** where session data lives, how to measure "actual time", how to reconstruct the naive estimate without hindsight bias, the calibration math, a schema for retrospective notes, and a batch procedure. Everything is ready to paste into a prompt for Claude.
**Status of claims:** **[V-local]** = checked against real transcripts on this machine (Claude Code v2.1.310, 2026-10-26). **[V-doc]** = checked against official docs. **[community]** = third-party sources only. **[verify locally]** = not confirmed; check before relying on it.

---

## 0. Key findings: read these first

1. **Back up your transcripts now. By default they are deleted after 30 days.** [V-doc] Claude Code deletes `~/.claude/projects/<project>/<session>.jsonl` files, including subagent transcripts and `tool-results/`, once they are older than `cleanupPeriodDays`. The default is 30 and the minimum is 1. The sweep runs **at startup**. Reports say it uses the file's modification time [community]. "The last ~100 sessions" may already be partly gone. Before you open another Claude Code session:
   - `cp -a ~/.claude/projects ~/claude-transcripts-backup-$(date +%F)` (also copy `~/.claude/history.jsonl`).
   - Set `"cleanupPeriodDays": 3650` (or similar) in `~/.claude/settings.json`. **[verify locally]** the maximum value the setting accepts.
   - Exception [V-doc]: transcripts of sessions started or last continued in **Claude Desktop or Cowork** are kept at any age (v2.1.248+), unless managed settings or HIPAA apply.
2. **`~/.claude/history.jsonl` is not swept.** [V-doc] It holds "Prompts you've typed, with timestamp and project path". Even after a transcript is gone, this file gives prompt timestamps per project. That is enough to rebuild rough human-activity timelines and the **first prompt of each task**, which is the input for blind estimation. **[verify locally]** the exact field names (expected: `display`, `timestamp`, `project`).
3. **Cloud sessions (claude.ai/code, mobile, `--cloud`) are not in `~/.claude/projects` on your machine.** [V-doc] Two ways to reach them:
   - **(a)** From inside a cloud session, use the `claude-code-remote` MCP tools. `list_sessions(mine:true)` returns `id, title, created_at, updated_at, origin (android/claude_code_cli/…), environment_kind (anthropic_cloud | bridge), session_context.sources (repo), task_summary, post_turn_summary`. `list_events(session_id, kinds:[user,assistant,result])` returns events with `created_at`; subagent events carry `agent_id`. [V-local]
   - **(b)** `claude --teleport <id>` pulls a cloud session into a local checkout. That writes a local transcript. **[verify locally]**
   - Local sessions that used Remote Control also show up in `list_sessions` with `environment_kind: "bridge"`. [V-local] The cloud-session docs did not state a retention period; archived sessions stay until you delete them. **[verify]**
4. **`/insights` already does part of the qualitative work.** [V-doc] It analyzes up to 200 recent local sessions (skipping very short ones) for "friction points such as misunderstood requests or buggy code". Output goes to `~/.claude/usage-data/report.html`. Use it as a seed list of friction patterns. It does **not** produce durations or estimates, and it is swept on the same 30-day schedule.
5. **Three parsing traps that inflate numbers** [V-local]:
   - **Tool results are stored as `type:"user"`.** A naive "count user messages" counts every tool result as a human message.
   - **One API response is split across several records** (one per content block: thinking, text, each tool_use). Each record **repeats the same `message.usage`**, so summing usage without deduplicating by `message.id` multiplies tokens 2–7×. ccusage has known dedup issues for this reason [community].
   - **Subagents** live in `<session>/subagents/agent-*.jsonl`, plus a `.meta.json` with `agentType, description, toolUseId, spawnDepth`. In older versions they were inline records with `isSidechain:true`. Their timestamps overlap the parent turn, so never add subagent time to parent time.

---

## 1. Data sources

| Source | Where | What it has | Retention | Use for |
|---|---|---|---|---|
| Claude Code local transcripts | `~/.claude/projects/<cwd with non-alphanumerics→"-">/<sessionId>.jsonl` (respects `CLAUDE_CONFIG_DIR`) | Every message, tool call and tool result, with ms timestamps | 30 days by default [V-doc] | Primary timing and content |
| Subagent transcripts | `…/<sessionId>/subagents/agent-<id>.jsonl` + `.meta.json` | Subagent turns | With parent | Parallelism and agent compute |
| Spilled tool output | `…/<sessionId>/tool-results/` | Large outputs | With parent | Rarely needed |
| Prompt history | `~/.claude/history.jsonl` | Typed prompts + timestamp + project path | **Kept** [V-doc] | Fallback timeline and first prompts |
| File snapshots | `~/.claude/file-history/<session>/` | Pre-edit file copies (last 100 checkpoints) | Swept | Size of change |
| Plans | `~/.claude/plans/` | Plan-mode plans | Swept | Scope at start (good blind-estimate input) |
| `/insights` | `~/.claude/usage-data/` | Friction report + per-session analysis cache | Swept | Seeding the qualitative work |
| Cloud sessions | claude.ai/code; MCP `list_sessions`/`list_events` | Title, created/updated, events | **[verify]** | Web and mobile sessions |
| claude.ai chat export | Settings → Privacy → Export data (web or Desktop, not mobile); emailed link valid 24 h [V-doc] | ZIP of JSON. `conversations.json`: per conversation `uuid, name, created_at, updated_at, chat_messages[]`; per message `sender` (`human`/`assistant`), `text`, `created_at`, `content[]` [community, **verify locally**] | Account lifetime | Chat-only work (no tool calls; timing = message timestamps) |
| Git | Each repo | Commits with author and committer dates, numstat, trailers | Permanent | Second source of truth for start/end and size |

### 1.1 Verified Claude Code transcript fields (v2.1.310) [V-local]

- **Record `type` values seen:** `user`, `assistant`, `attachment`, `ai-title`, `last-prompt`, `queue-operation`, `atis-latch`. Older versions also have `summary` and `system`. Ignore types you don't recognize.
- **Fields on message records:**

  | Field | Meaning |
  |---|---|
  | `uuid`, `parentUuid` | Record id and parent; together they form a tree |
  | `timestamp` | ISO-8601 UTC with ms and `Z` |
  | `sessionId` | Session id |
  | `cwd` | Working directory |
  | `gitBranch` | Current branch |
  | `version` | CLI version |
  | `entrypoint` | e.g. `remote_mobile`; other values **[verify]** |
  | `userType` | Seen as `external` |
  | `isSidechain` | True for subagent records |

- **`assistant` records:**
  - `message.id`: dedupe key
  - `message.model`
  - `message.content[]`: block types `thinking` / `text` / `tool_use`, where a tool_use has `name` and `input`
  - `message.stop_reason`
  - `message.usage`: `input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens, …`
  - Also: `requestId`, `requestedModel`, `effort`, and sometimes `thinkingDurationMs`
- **`user` records:**
  - `message.content` is a **string** for a typed prompt, or a **list** of `tool_result` blocks for tool output.
  - Plus `toolUseResult` (structured result), `permissionDecision`, `sourceToolAssistantUUID`.
  - Newer versions also mark human prompts with `origin:{kind:"human"}`, `turnOrigin:"human"` and `promptSource`.
- **Title:** `{"type":"ai-title","aiTitle":…}`. Older versions use `{"type":"summary","summary":…}`.
- **Not confirmed here** (older formats, community-reported): `isMeta`, `isCompactSummary`, and `<command-name>` strings in user content for slash commands. The parser handles them defensively.
- **Resume and rewind** can leave `*.orphaned-*.jsonl` and `*.jsonl.superseded-*` files [V-doc]. Skip them, and dedupe records by `uuid` if you merge files.

### 1.2 Git as the second source of truth

```bash
git log --all --no-merges --format='%H|%aI|%cI|%an|%s' --numstat > gitlog.txt
```

- Use the **author date** (`%aI`). Rebases rewrite the committer date.
- Tie commits to sessions in three ways:
  - Match the transcript's `gitBranch` to the branch.
  - Match by time window: a commit within [session start, session end + 30 min].
  - Use commit trailers. Claude Code commits often carry `Co-Authored-By: Claude …` and, in cloud sessions, a `Claude-Session: https://claude.ai/code/session_…` link. That link is an exact join key.
- Git gives `lines_added/deleted`, `files_changed`, and PR merge time, which serves as the "done" timestamp.

---

## 2. Computing actual time

### 2.1 Definitions (per session, main thread only)

Sort the session's events by `timestamp`. A **human prompt** is a `user` record that is not a tool_result, not a sidechain, not meta, and not a slash-command echo. A **turn** runs from one human prompt to the last *agent event* before the next prompt. An agent event is an `assistant` record or a `tool_result` record.

- **Turn duration:** `T_k = t(last agent event in turn k) − t(prompt k)`. This is **agent time**, Claude working. It includes tool runs and any **permission-prompt waits inside the turn**. Those waits are actually human time, so flag turns with an in-turn gap over 5 min where `permissionDecision` is present.
- **Human gap:** `G_k = t(prompt k+1) − t(end of turn k)`. This is human reading, reviewing, testing and thinking.
- **Active time** (WakaTime-style; the default timeout there is 15 min [V-doc: wakatime.com/faq]): `active = Σ T_k + Σ G_k·[G_k ≤ θ]`. Gaps longer than θ count 0, not θ.
- **Wall time:** `wall = t_last − t_first`. This is an upper bound.
- **Idle:** `Σ G_k·[G_k > θ]`.
- **Default θ = 15 min.** Always run a **sensitivity check** at θ ∈ {5, 10, 15, 30}. If a category's factor moves more than 20% between 10 and 30, its human-gap share is large. In that case report "human_attention_min" separately from "agent_min".
- **Don't apply θ to in-turn gaps.** Long builds, test suites and deploys are real work. Do cap single in-turn gaps at 60 min and log them; those are usually forgotten permission prompts.

### 2.2 Two targets: decide which one you are estimating

| Target | Formula | Answers |
|---|---|---|
| **Elapsed active time** (primary) | `active_min` of all segments of the task | "When will it be done if I sit down now?" |
| **Human attention** | `human_min` + permission waits + any user-reported off-session testing | "How much of *my* time does it cost?" |
| Agent compute (secondary) | `agent_min`, plus subagent spans if you want cost | Token/cost planning |

**Parallel sessions:** the same human can run several sessions at once. For "human attention", take the **union of human-gap intervals across all sessions on the calendar**, so time isn't double-counted. For per-task elapsed time, keep each task's own active time and set `parallel_flag=1`.

### 2.3 Splitting one session into tasks

Candidate boundaries, from strongest to weakest:
1. `/clear` or a new session.
2. Change of `cwd` or `gitBranch`.
3. A human gap longer than 45 min (`--split` in the script).
4. A new topic, judged by an LLM from the first prompt after the boundary: "Is this the same deliverable as before? yes/no".

A boundary only *proposes* a split. The extraction agent confirms it.

### 2.4 Merging tasks spread across sessions

Group segments into one `task_id` when they share a branch or PR, have a near-identical title or goal, or one says "continue/resume". Then `actual_active_min = Σ segment active_min`. **Rework:** a bugfix session within 14 days that names the same feature is **charged back** to the original task (Spolsky's EBS rule) and also logged as `rework_min`. Record `n_sessions` and `calendar_span_days`.

### 2.5 Defining "done", and time outside sessions

`done_ts` is the earliest of: PR merged, deploy confirmed, or the user says "works / ship it". Add **off-session time** only when there is evidence: user statements like "I tested it for an hour", CI waits visible in git, or deploy logs. Otherwise set `offsession_min=NA`, and mark `time_confidence` as `high`, `med` or `low`.

---

## 3. Reconstructing the naive estimate without hindsight bias

**Goal:** get the estimate that *would have been given before the work started*, by (a) a typical AI model and (b) a human-era reference, without knowing what happened next.

Order of preference:
1. **An estimate made at the time and present in the transcript.** This is the gold standard. Grep assistant text in the first two turns for `\b\d+(\.\d+)?\s*(-|–|to)?\s*\d*\s*(min|minutes|h|hrs|hours|days|weeks)\b`, and user text for "how long". Record it as `est_contemporaneous_min` with its source.
2. **Blind re-estimation with role separation.** This is the default.
   - **Card writer:** a subagent sees **only the first human prompt(s) of the task**, plus any plan-mode plan written before work began, plus static repo facts (stack, LOC bucket, greenfield or brownfield). It writes a **task card** of 150 words or fewer. It must not read later turns.
   - **Estimator:** a *fresh* subagent with no transcript access gets the card and a fixed prompt. It returns:
     - `est_ai_naive_P50/P90`: "Estimate how long this takes, as you normally would answer a user."
     - `est_human_P50/P90`: "…for a competent developer without AI tools."
     - `size_class` (XS/S/M/L/XL) and `category`.
   - Take **3 independent samples** and use the median. Record the model id, because estimates drift with model versions.
   - **Leak checks:** the card must not contain outcome words ("done", "fixed", file names created later, error messages from later turns). If the estimator mentions details that aren't on the card, discard that sample.
3. **The user's own gut estimate:** a quick blind pass where the user sees only the card list and writes minutes. This is optional, but it gives the "user bias" curve.

**Scope drift:** the first prompt often understates the final scope. Also record `scope_change ∈ {none, minor, major}` and a second blind estimate on the **final-scope card** (`est_ai_final_scope_P50`). That separates *estimation error* (naive vs actual on final scope) from *scope growth* (initial vs final card). For calibration, use the initial card (that is what forecasting will see) and keep the scope-growth ratio as its own multiplier.

---

## 4. Calibration math

Notation: for task *i*, `E_i` = naive estimate (minutes), `A_i` = actual active minutes.

**Log ratio:** `r_i = ln(A_i / E_i)`. Task durations are roughly log-normal, so log ratios are roughly normal and symmetric (Bernhardsson 2019, "blowup factor").

**Bias and correction factor (per category c):**
- `μ_c = mean(r_i)`
- `F_c = exp(μ_c)`. This is the geometric-mean ratio, i.e. the **median multiplier**. With "dashboard = 4–5 h" naive and 45 min actual, F ≈ 0.17.
- Corrected point estimate: `Ê = F_c · E` (median).
- If you **sum** several tasks, use the log-normal mean multiplier `exp(μ_c + σ_c²/2)`, or Monte Carlo (below).

**Spread:**
- `σ_c = SD(r_i)`.
- Robust alternative: `σ_rob = 1.4826 · MAD(r)`. Use it when n < 15 or there are outliers.

**Prediction interval for a new task (80%):**
`[E·exp(μ − t₀.₉,ₙ₋₁·σ·√(1+1/n)), E·exp(μ + t₀.₉,ₙ₋₁·σ·√(1+1/n))]`. Use t≈1.28 when n ≥ 30, 1.38 at n=10, 1.53 at n=5.
**Check coverage:** about 80% of held-out actuals should fall inside the interval. If not, σ is wrong.

**Small samples: shrink toward the global bias (empirical Bayes, normal–normal):**
- `w_c = (n_c/σ_c²) / (n_c/σ_c² + 1/τ²)`
- `μ_c,post = w_c·μ_c + (1−w_c)·μ_all`
- τ is the prior SD of category biases around the global bias. Start with 0.5; estimate it later as `SD(μ_c)` across categories with n ≥ 8.

**Updating as data arrives (Bayesian):**
- Treat σ as known (pooled).
- Posterior precision: `p_post = p_prior + n_new/σ²`
- Posterior mean: `μ_post = (p_prior·μ_prior + Σr_new/σ²) / p_post`
- Apply **recency decay**, because AI speed changes quickly with model releases: weight `w_i = 0.5^(age_days/90)`. Better still, stratify by model generation. Spolsky drops data older than 6 months for the same reason.

**How many tasks are enough?**
- The SE of μ is `σ/√n`. With a typical σ≈0.7:

  | n | SE of μ | Uncertainty in F |
  |---|---|---|
  | 5 | 0.31 | ±37% |
  | 10 | 0.22 | ±25% |
  | 20 | 0.16 | ±17% |
  | 40 | 0.11 | ±12% |

- **Rules of thumb:**
  - n ≥ 5 per category before it gets its own (shrunk) factor.
  - n ≥ 10–15 for a usable factor.
  - n ≥ 30 before trusting P90 tails.
  - With about 100 sessions → ~60–120 tasks → 5–8 categories is realistic.

**Outliers: don't delete them, classify them.**
- `outcome = abandoned` → exclude from duration stats, but report an **abandonment rate** per category; it is a real risk.
- `blocked_external` (waiting on API keys, approvals, outages) → exclude or move to a separate "external wait" adder.
- Otherwise keep the task, and winsorize `r` at μ ± 2.5σ for the factor. Report raw and winsorized.

**Regression (once n ≥ 40):**
`ln A = a + b·ln E + Σ category + β·(brownfield, unfamiliar_stack, needs_deploy, n_files_bucket, has_tests) + ε`.
- b < 1 means big tasks compress more than small ones. That is plausible with AI, since fixed overheads (setup, deploy, review) dominate small tasks.
- Use leave-one-out (LOO) validation.

**Evidence-Based-Scheduling Monte Carlo** (Spolsky 2007):
- For each simulation (10,000 runs), for each planned item, draw a historical ratio `A_j/E_j` from the same category (or from all history if n < 5), and set the item's time to `E_item × ratio`. Sum the items.
- Report P10/P50/P80/P90.
- Independent draws **understate** the spread when items share unknowns (same day, same new stack). Fix this by also drawing a per-plan "day factor" from the distribution of session-level mean residuals, or by block-resampling whole historical sessions.
- Spolsky seeds new estimators with a pessimistic fake history until about 6 real tasks exist. Do the same: seed new categories with the global distribution.

**Reporting accuracy** (Kitchenham et al. 2001: MMRE and PRED are really spread/kurtosis of z = E/A):
- **Primary:** μ (bias), σ (spread), and the coverage of the 80% PI.
- **Secondary, for comparability:**
  - MdMRE = median(|A−E|/A); avoid the mean MRE, which **favours underestimates**.
  - PRED(25) and PRED(50) = share of tasks with MRE ≤ 0.25 / 0.5.
- Always show **naive vs calibrated (leave-one-out)** side by side. That is the headline result: "calibration cut MdMRE from 1.8 to 0.4".

---

## 5. Qualitative retrospective schema

Per task (or per session when a session holds one task), the extraction agent emits one JSON object to `retro.jsonl`:

```json
{
  "task_id": "T042",
  "session_ids": ["…"],
  "outcome": "shipped|partial|abandoned|blocked_external",
  "went_well": [{"what": "scaffolded CRUD + tests in one turn", "why": "clear spec + existing pattern", "time_saved_est_min": 60}],
  "slowdowns": [{
    "category": "env_setup|dependency_version|ambiguous_spec|wrong_approach_rework|agent_loop_or_reread|tool_permission_friction|external_wait|flaky_tests|deploy_config|context_loss_compaction|hallucinated_api|ui_iteration|data_issue|other",
    "what": "Vercel env vars missing in preview",
    "evidence": "turn 7–12, 2026-09-14T10:32Z",
    "time_lost_min": 25,
    "root_cause": "assumed env copied from prod",
    "prevention": "checklist: set env for all environments before first deploy",
    "detectable_upfront": true
  }],
  "mistakes_by_claude": ["edited wrong config file twice"],
  "mistakes_by_user": ["spec omitted mobile layout"],
  "know_how": [{"topic": "Next.js ISR", "insight": "revalidate needs …", "reusable": "snippet|prompt|CLAUDE.md rule|skill", "text": "…"}],
  "estimation_lesson": "deploy-to-new-platform adds ~30 min regardless of feature size",
  "confidence": "high|med|low"
}
```

**Aggregating into patterns:**
1. Normalize `slowdowns[].category`, plus a short `pattern_key` written by an LLM that clusters similar `what/root_cause` texts. Do one clustering pass over all items so every key comes from the same pass.
2. For each pattern: `freq` (tasks affected / all tasks), `median_time_lost`, `total_time_lost = Σ`, and `share_of_all_active_time`.
3. **Pareto:** sort by `total_time_lost`. The top 5 patterns become:
   - (a) **estimation adders**, e.g. `+30 min if first deploy to a platform`, `×1.5 if unfamiliar API without docs`;
   - (b) **prevention rules** in CLAUDE.md, skills or checklists.
4. For "hits", aggregate `time_saved_est_min` by cause. These are "accelerators" to repeat, such as an existing pattern to copy, a clear acceptance test, or plan mode first.

---

## 6. Step-by-step procedure (for a Claude prompt)

**Phase 0: preserve the data (5 min).** Run the backup and the `cleanupPeriodDays` change from §0. Export claude.ai data if chat work matters. List the repos you worked in.

**Phase 1: inventory (script, about 1 min).**
1. Run `python3 -I cc_sessions.py --no-text --out sessions.csv --segments segments.csv` (Appendix A).
2. In a cloud session, add rows from `list_sessions` (created/updated/title/repo).
3. Keep sessions with `active_min ≥ 3` and at least 1 prompt.
4. Sort by date and assign batch numbers of **8–10 sessions per batch**.

**Phase 2: extract per batch (subagents in parallel, about 4–6 at a time).** Each subagent gets one batch's file paths plus the schema in §7, and returns rows to `tasks_raw.csv` and `retro.jsonl`. Instructions:
- Read the transcript (only `user` text and `assistant` text/tool names; skip big tool outputs).
- Confirm or adjust the segment → task mapping.
- Fill the timing fields from `sessions.csv`/`segments.csv`. **Do not recompute times by eye.**
- Write the task card (first prompt only, in a separate step) and the retro JSON.
- Redact secrets: anything matching `(?i)(api[_-]?key|secret|token|password)\s*[:=]`, `sk-[A-Za-z0-9]{20,}`, `ghp_[A-Za-z0-9]{36}`, AWS `AKIA[0-9A-Z]{16}`, emails, and private customer data.

**Phase 3: merge (one agent).** Merge tasks across batches (branch, PR, title similarity, "continue"), charge back rework, join git data, and set `include`, `outcome` and `time_confidence`.

**Phase 4: blind estimation (fresh subagents, no transcript access).** Input is `cards.csv` (task_id, card, repo facts) only. Take 3 samples per card and store the medians in `tasks.csv`. Optionally, the user does a gut-estimate pass.

**Phase 5: calibrate.**
1. Run `python3 -I calibrate.py tasks.csv` (Appendix B). It reports per category: n, μ, F, σ, shrunk F, P10/P50/P90 multipliers, MdMRE, PRED(25), and LOO-calibrated MdMRE/PRED(25).
2. Run the θ sensitivity check (re-run Phase 1 with `--idle 10/30`).
3. Check interval coverage.

**Phase 6: qualitative aggregation.** Cluster patterns and build the Pareto table, adders and rules (§5).

**Phase 7: write the cookbook and keep logging going forward.**
- The output is a table of category → (naive P50 → calibrated P50, 80% PI), plus adders, accelerators, and the top lessons.
- **Make future data prospective.** Add a CLAUDE.md rule: "Before starting any task > XS, print one line `ESTIMATE task=<slug> cat=<category> P50=<min> P90=<min>`". Then grep these lines from future transcripts. That removes the need for reconstruction.
- Re-run calibration monthly with recency decay.

**Privacy and scale tips:**
- Transcripts are **plaintext and may contain secrets**, because file contents and env output are written verbatim [V-doc].
- Process locally. Use `--no-text` in the inventory. Never publish raw excerpts; publish only aggregates and redacted lessons.
- Keep each subagent's input small: pass file paths, not contents, and have the subagent read text blocks only.
- About 100 sessions fit comfortably in 10–12 batches.
- Store intermediate CSVs so a failed batch can be re-run on its own.

---

## 7. Dataset schemas

### 7.1 `sessions.csv`, machine-generated (Appendix A output)

- **Identity and context:**
  - `session_id, file, project_dir, title, cwd, gitBranch, version, entrypoint`
  - `start_utc, end_utc`
- **Timing:**
  - `wall_min, active_min, agent_min, human_min, idle_min`
  - `n_prompts, n_segments`
- **Activity:**
  - `n_api_msgs, models, tool_calls, top_tools`
  - `files_edited, git_commit_cmds, subagent_files`
- **Tokens:** `input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens`
- **Data quality and text:** `bad_lines, unknown_types, first_prompt`

### 7.2 `segments.csv`, machine-generated

`session_id, segment, start_utc, end_utc, span_min, n_prompts, first_prompt`

### 7.3 `tasks.csv`, the calibration dataset (one row per task)

**Identity and context**

| column | type | notes |
|---|---|---|
| task_id | str | `T001…` |
| session_ids | str | `;`-separated |
| segment_refs | str | `session:segment;…` |
| date_start | ISO date | |
| repo | str | |
| branch | str | |
| pr | str | URL or number |
| title | str | ≤ 80 chars |
| category | enum | `ui_page_component, dashboard, crud_api, integration_3p_api, data_pipeline_etl, bugfix, refactor, infra_deploy_ci, auth, tests, docs_content, research_spike, script_automation, mobile, other`. Keep to ≤ 15 and stable. |
| size_class | enum | XS/S/M/L/XL (from the blind estimator) |
| greenfield | 0/1 | new repo or new module |
| stack_familiar | 0/1/NA | user/Claude worked in this stack before |
| needs_deploy | 0/1 | |
| model | str | main model id |
| parallel_flag | 0/1 | ran alongside other sessions |

**Timing**

| column | type | notes |
|---|---|---|
| n_sessions | int | |
| calendar_span_days | float | |
| actual_active_min | float | Σ segment active_min, θ = 15 |
| actual_active_min_t10 | float | sensitivity at θ = 10 |
| actual_active_min_t30 | float | sensitivity at θ = 30 |
| agent_min | float | |
| human_min | float | |
| wall_min | float | |
| offsession_min | float/NA | evidence-based only |
| rework_min | float | charged-back later fixes |
| time_confidence | enum | high/med/low |

**Estimates**

| column | type | notes |
|---|---|---|
| est_contemporaneous_min | float/NA | estimate found in the transcript |
| est_contemporaneous_src | str | who gave it and where (turn) |
| est_naive_min | float | **the column calibrated by default** = `est_ai_naive_P50` |
| est_ai_naive_P50 | float | blind estimator: "as you'd normally answer" |
| est_ai_naive_P90 | float | |
| est_human_P50 | float | blind estimator: developer without AI |
| est_human_P90 | float | |
| est_user_gut_min | float/NA | |
| est_model | str | estimator model id |
| est_ai_final_scope_P50 | float | blind estimate on the final-scope card |

**Outcome and size**

| column | type | notes |
|---|---|---|
| scope_change | enum | none/minor/major |
| outcome | enum | shipped/partial/abandoned/blocked_external |
| include | 0/1 | use in calibration |
| exclude_reason | str | |
| lines_added | int | from git |
| lines_deleted | int | from git |
| files_changed | int | from git |
| n_prompts | int | |
| n_corrections | int | user messages that redirect or fix Claude |
| top_slowdown | str | pattern_key |
| notes | str | |

Derived (computed, not stored): `log_ratio = ln(actual_active_min / est_naive_min)`, `ratio_human = actual/est_human_P50`.

### 7.4 `cards.csv`, the blind-estimation input (the estimator sees nothing else)

`task_id, card_text (≤150 words), repo_facts (stack; LOC bucket; greenfield)`

### 7.5 `retro.jsonl`

See §5.

---

## 8. Prompt skeletons

**Extraction subagent (per batch):**
> You are processing Claude Code transcripts for an estimation-calibration study. Files: <paths>. Pre-computed timings: <rows of sessions.csv/segments.csv>.
> For each session:
> (1) Decide the tasks. Use the segment boundaries as proposals; merge or split by deliverable.
> (2) For each task, fill the tasks.csv columns listed below *except all est_* columns*. Copy timing numbers from the provided rows; never estimate durations by eye.
> (3) Write card_text from the FIRST prompt(s) of the task only. Write what was asked, not what happened. Max 150 words. No outcome words, no file names created later.
> (4) Emit one retro.jsonl object per task using the schema. Cite turn timestamps as evidence, and give time_lost_min only when the timestamps support it.
> (5) Redact secrets and personal data. Output CSV rows + JSONL only.

**Blind estimator (fresh context, 3 samples):**
> Here is a task description and repo facts. You have no other information.
> Give: (a) how long you would tell the user this will take, as you normally would; (b) how long a competent developer *without* AI tools would take.
> Return JSON `{"ai_P50_min":…, "ai_P90_min":…, "human_P50_min":…, "human_P90_min":…, "size_class":"XS|S|M|L|XL", "category":"<enum>"}`.

---

## Appendix A — `cc_sessions.py` (tested on real v2.1.310 transcripts and a synthetic case)

Standard library only, and defensive about unknown fields. On the synthetic test (3 prompts, one `/clear` echo, an 80-min gap, one malformed line) it gave wall 110 / active 30 / agent 25 / human 5 / idle 80 min and 2 segments, all as expected. Source file: `/tmp/claude-0/-home-user-devcamp/841f0782-1c35-5331-8e1a-6de8920d501a/scratchpad/tools/cc_sessions.py`.

```python
#!/usr/bin/env python3
"""
cc_sessions.py - Parse Claude Code local transcripts (~/.claude/projects/<project>/<session>.jsonl)
into per-session and per-segment timing stats for estimation calibration.

Robust to unknown/missing fields: every access is defensive; unknown record types are counted
and ignored. Standard library only. Run with `python3 -I cc_sessions.py ...`.

Usage:
  python3 -I cc_sessions.py [--root ~/.claude/projects] [--idle 15] [--split 45]
                            [--out sessions.csv] [--segments segments.csv] [--no-text]

Definitions (all minutes):
  wall_min      last event ts - first event ts (main thread only)
  agent_min     sum over turns of (last agent event in turn - human prompt ts)
                = time Claude was working (incl. tool runs and permission waits inside the turn)
  human_min     sum of gaps (turn end -> next human prompt) that are <= idle threshold
                = human reading / reviewing / thinking / testing time
  idle_min      sum of human gaps > idle threshold (excluded from active time)
  active_min    agent_min + human_min   (WakaTime-style: gaps > timeout count 0)
  segments      session split wherever a human gap > --split minutes (candidate task boundaries)
"""
import argparse, csv, glob, json, os, re, sys
from collections import Counter
from datetime import datetime

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
NON_PROMPT_PREFIXES = ("<command-name>", "<local-command-stdout>", "<local-command-stderr>",
                       "<command-message>", "[Request interrupted", "Caveat: The messages below")


def ts(o):
    t = o.get("timestamp")
    if not isinstance(t, str):
        return None
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00"))
    except ValueError:
        return None


def content_blocks(msg):
    c = (msg or {}).get("content")
    if isinstance(c, str):
        return [{"type": "text", "text": c}]
    return [b for b in c if isinstance(b, dict)] if isinstance(c, list) else []


def is_human_prompt(o):
    """A 'user' record is a real human prompt only if it is not a tool_result, not meta,
    not a sidechain (subagent), and not a slash-command/system echo. Verify locally:
    newer versions also carry origin.kind == 'human' / turnOrigin == 'human'."""
    if o.get("type") != "user" or o.get("isSidechain") or o.get("isMeta") or o.get("isCompactSummary"):
        return False
    origin = o.get("origin")
    if isinstance(origin, dict) and origin.get("kind") not in (None, "human"):
        return False
    blocks = content_blocks(o.get("message"))
    if not blocks or any(b.get("type") == "tool_result" for b in blocks):
        return False
    text = " ".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
    if not text and not any(b.get("type") == "image" for b in blocks):
        return False
    return not text.startswith(NON_PROMPT_PREFIXES)


def is_agent_event(o):
    """Assistant output or a tool result: evidence the agent was working at this timestamp."""
    if o.get("type") == "assistant":
        return True
    return o.get("type") == "user" and any(b.get("type") == "tool_result" for b in content_blocks(o.get("message")))


def last_agent_ts(recs, lo, hi, default):
    """Timestamp of the last agent event in recs[lo:hi], else default."""
    for i in range(hi - 1, lo, -1):
        if is_agent_event(recs[i]):
            return ts(recs[i])
    return default


def prompt_text(o):
    return " ".join(b.get("text", "") for b in content_blocks(o.get("message")) if b.get("type") == "text").strip()


def parse_session(path, idle_min, split_min, keep_text):
    recs, unknown, bad = [], Counter(), 0
    title = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            if not isinstance(o, dict):
                continue
            t = o.get("type")
            if t == "ai-title" and o.get("aiTitle"):
                title = o["aiTitle"]
            elif t == "summary" and o.get("summary") and not title:   # older versions
                title = o["summary"]
            if t not in ("user", "assistant", "system", "attachment"):
                unknown[t] += 1
            if o.get("isSidechain"):          # subagent records inline (older versions)
                continue
            if ts(o) is not None:
                recs.append(o)
    if not recs:
        return None, []
    recs.sort(key=ts)

    sid = next((r.get("sessionId") for r in recs if r.get("sessionId")), os.path.basename(path)[:-6])
    meta = {k: next((r.get(k) for r in recs if r.get(k)), "") for k in ("cwd", "gitBranch", "version", "entrypoint")}

    # token + tool stats (dedupe usage by message.id: one API message is split across records)
    seen_msg, models, tools = set(), Counter(), Counter()
    tok = Counter()
    files_edited, git_commits = set(), 0
    for r in recs:
        if r.get("type") != "assistant":
            continue
        m = r.get("message") or {}
        mid = m.get("id") or r.get("requestId") or r.get("uuid")
        if mid not in seen_msg:
            seen_msg.add(mid)
            if m.get("model"):
                models[m["model"]] += 1
            u = m.get("usage") or {}
            for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
                if isinstance(u.get(k), (int, float)):
                    tok[k] += u[k]
        for b in content_blocks(m):
            if b.get("type") == "tool_use":
                name = b.get("name", "?")
                tools[name] += 1
                inp = b.get("input") or {}
                if name in EDIT_TOOLS and isinstance(inp, dict):
                    fp = inp.get("file_path") or inp.get("notebook_path")
                    if fp:
                        files_edited.add(fp)
                if name == "Bash" and isinstance(inp, dict) and re.search(r"\bgit\s+commit\b", str(inp.get("command", ""))):
                    git_commits += 1

    # turns: each human prompt opens a turn; turn ends at last non-human record before next prompt
    prompts = [i for i, r in enumerate(recs) if is_human_prompt(r)]
    agent_s = human_s = idle_s = 0.0
    seg_bounds, cur_start = [], 0
    for n, pi in enumerate(prompts):
        nxt = prompts[n + 1] if n + 1 < len(prompts) else len(recs)
        t0 = ts(recs[pi])
        t_end = last_agent_ts(recs, pi, nxt, t0)
        agent_s += max(0.0, (t_end - t0).total_seconds())
        if nxt < len(recs):
            gap = (ts(recs[nxt]) - t_end).total_seconds()
            if gap <= idle_min * 60:
                human_s += max(0.0, gap)
            else:
                idle_s += gap
            if gap > split_min * 60:
                seg_bounds.append((cur_start, n))
                cur_start = n + 1
    if prompts:
        seg_bounds.append((cur_start, len(prompts) - 1))

    first, last = ts(recs[0]), ts(recs[-1])
    first_prompt = prompt_text(recs[prompts[0]]) if prompts else ""
    session = {
        "session_id": sid, "file": path, "project_dir": os.path.basename(os.path.dirname(path)),
        "title": title or "", **meta,
        "start_utc": first.isoformat(), "end_utc": last.isoformat(),
        "wall_min": round((last - first).total_seconds() / 60, 1),
        "active_min": round((agent_s + human_s) / 60, 1),
        "agent_min": round(agent_s / 60, 1), "human_min": round(human_s / 60, 1),
        "idle_min": round(idle_s / 60, 1),
        "n_prompts": len(prompts), "n_segments": len(seg_bounds),
        "n_api_msgs": len(seen_msg), "models": ";".join(f"{k}:{v}" for k, v in models.most_common()),
        "tool_calls": sum(tools.values()), "top_tools": ";".join(f"{k}:{v}" for k, v in tools.most_common(6)),
        "files_edited": len(files_edited), "git_commit_cmds": git_commits,
        "subagent_files": len(glob.glob(os.path.join(path[:-6], "subagents", "*.jsonl"))),
        **{k: int(v) for k, v in tok.items()},
        "bad_lines": bad, "unknown_types": ";".join(f"{k}:{v}" for k, v in unknown.items()),
        "first_prompt": first_prompt[:500] if keep_text else "",
    }

    segments = []
    for k, (a, b) in enumerate(seg_bounds):
        pa, pb = prompts[a], prompts[b]  # first / last prompt index of the segment
        hi = prompts[b + 1] if b + 1 < len(prompts) else len(recs)
        s_t0 = ts(recs[pa])
        s_t1 = last_agent_ts(recs, pb, hi, ts(recs[pb]))
        segments.append({
            "session_id": sid, "segment": k + 1, "start_utc": s_t0.isoformat(), "end_utc": s_t1.isoformat(),
            "span_min": round((s_t1 - s_t0).total_seconds() / 60, 1), "n_prompts": b - a + 1,
            "first_prompt": prompt_text(recs[pa])[:300] if keep_text else "",
        })
    return session, segments


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude") + "/projects"))
    ap.add_argument("--idle", type=float, default=15, help="human gap (min) above which time counts as idle")
    ap.add_argument("--split", type=float, default=45, help="human gap (min) that starts a new segment")
    ap.add_argument("--out", default="sessions.csv")
    ap.add_argument("--segments", default="segments.csv")
    ap.add_argument("--no-text", action="store_true", help="omit prompt text (privacy)")
    a = ap.parse_args()

    files = [p for p in glob.glob(os.path.join(os.path.expanduser(a.root), "*", "*.jsonl"))]
    sessions, segs = [], []
    for p in sorted(files):
        try:
            s, sg = parse_session(p, a.idle, a.split, not a.no_text)
        except Exception as e:  # never die on one bad file
            print(f"WARN {p}: {e}", file=sys.stderr)
            continue
        if s:
            sessions.append(s)
            segs.extend(sg)
    for path, rows in ((a.out, sessions), (a.segments, segs)):
        if not rows:
            continue
        cols = list(dict.fromkeys(k for r in rows for k in r))
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
    print(f"{len(sessions)} sessions, {len(segs)} segments -> {a.out}, {a.segments}", file=sys.stderr)


if __name__ == "__main__":
    main()
```

## Appendix B — `calibrate.py`

Takes `tasks.csv` and outputs per-category bias, factor, σ, shrunk factor, PI multipliers, MdMRE/PRED (naive and LOO-calibrated), and an EBS Monte Carlo forecast (`--plan "dashboard:240,api:120"`). Source file: `/tmp/claude-0/-home-user-devcamp/841f0782-1c35-5331-8e1a-6de8920d501a/scratchpad/tools/calibrate.py`.

Example output on synthetic data (51 tasks):

```
category,n,mean_log,factor_raw,sigma_log,factor_shrunk,P10_mult,P50_mult,P90_mult,mean_mult,MdMRE,PRED25,PRED50,MdMRE_cal_loo,PRED25_cal_loo
dashboard,12,-1.566,0.209,0.517,0.217,0.109,0.217,0.433,0.249,4.045,0.0,0.0,0.262,0.5
ALL,51,-1.073,0.342,0.708,0.342,0.137,0.342,0.856,0.44,1.76,0.078,0.137,0.512,0.176
Monte Carlo total minutes (P10/P50/P80/P90): {0.1: 117.5, 0.5: 181.2, 0.8: 243.8, 0.9: 290.8}
```

```python
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
```

---

## Sources

- Claude Code docs: `.claude` directory and application data (retention table, `cleanupPeriodDays`, `history.jsonl`, subagents/tool-results paths, plaintext warning): https://code.claude.com/docs/en/claude-directory
- Claude Code docs: costs, `/usage`, `/insights` (up to 200 sessions, `usage-data/`): https://code.claude.com/docs/en/costs
- Claude Code docs: cloud sessions, `--teleport`, archive/delete: https://code.claude.com/docs/en/claude-code-on-the-web
- Claude Code docs: settings: https://code.claude.com/docs/en/settings
- Claude Help Center: export your Claude data (Settings → Privacy → Export data; 24 h link): https://support.claude.com/en/articles/9450526-export-your-claude-data
- claude.ai export field names (community): https://univik.com/help/export-claude-chats.html ; https://glama.ai/mcp/servers/@adamkwhite/claude-memory-mcp
- 30-day deletion reports: https://itdaily.com/news/cloud/claude-code-deletes-conversation-history-after-30-days-by-default/ ; https://brycewatson.com/blog/28-claude-code-deletes-old-logs
- ccusage (token reports from local JSONL; dedup caveats): https://github.com/ryoppippi/ccusage ; https://github.com/SingggggYee/claude-usage-analyzer ; https://aident.ai/blog/claude-code-jsonl-token-usage
- claude-code-log (JSONL → HTML): https://github.com/daaain/claude-code-log ; Simon Willison's claude-code-transcripts: https://simonwillison.net/e/9106
- WakaTime FAQ, keystroke timeout (default 15 min, how gaps are joined): https://wakatime.com/faq
- Spolsky, Evidence Based Scheduling (2007): https://www.joelonsoftware.com/2007/10/26/evidence-based-scheduling/
- Bernhardsson, "Why software projects take longer than you think" (log-normal blowup factor): https://erikbern.com/2019/04/15/why-software-projects-take-longer-than-you-think-a-statistical-model
- Kitchenham, Pickard, MacDonell, Shepperd (2001), "What accuracy statistics really measure" (MMRE/PRED = spread/kurtosis of z = E/A): https://openrepository.aut.ac.nz/bitstream/10292/2179/2/Kitchenham%2C%20Pickard%2C%20MacDonell%20and%20Shepperd%20%282001%29%20IEEProc-S.pdf
- MMRE favours underestimates; Jørgensen, Halkjelsvik & Liestøl (2022) on when MMRE is proper: via https://arxiv.org/pdf/1804.00626 and related search results
