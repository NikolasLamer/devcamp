# Pilot: 25 real sessions (Oct 21–26, 2026), anonymized

**Goal:** test whether the research method predicts real AI-assisted work better than a model's usual answer, and recalibrate its numbers.
**Data:** `data/pilot_tasks.csv`. Project names, clients and content are deliberately left out, because this repo is public.

## How it was measured

1. **Sessions.** 25 build sessions were picked from the user's last 100 Claude Code sessions, spread across categories: dashboards/UI, features in existing code, bug fixes, data pipelines and scrapers, agent tooling, video rendering, refactors and an investigation. Most ran on one Windows PC through Remote Control.
2. **Transcripts and timing.** Four audit agents pulled the full transcripts (`tools/cloud_timeline.py`) and computed active time from timestamps: gaps over 15 min count as idle, with 5 and 30 min as sensitivity checks. They then picked the best figure by hand, for example excluding time spent waiting on an unrelated parent session.
3. **Blind estimates.** Each task's *original request only* went to fresh agents that never saw the outcome:
   - **Naive (agent-framed):** "how long would you tell the user, working with Claude Code?"
   - **Human-developer estimate:** an experienced developer without AI.
   - **Method v0.1:** the full decomposition method from `sources/04` with research priors, P50/P80 via Monte Carlo.
4. **Scoring.** Each approach was compared with the actual time on log ratios; "after calibration" was checked by leaving out one task at a time.

## Headline numbers

| Estimator | Bias (actual ÷ estimate) | Spread σ | Rank correlation | Median error raw → after calibration | Within 2× |
|---|---|---|---|---|---|
| Human developer without AI | **0.09** (≈11× too long) | 0.75 | 0.81 | 12.9 → 0.57 | 1/25 |
| Model, told it's agent work | 1.00 | 0.61 | 0.73 | 0.50 → 0.52 | 18/25 |
| Method v0.1 (research priors) | 0.38 (2.6× too long) | **0.54** | **0.84** | 1.53 → **0.38** | 7/25 raw |
| Method, refit to v0.2 (build ×0.2, overhead ×0.75, waits ×1.5) | 1.00 | 0.52 | — | **0.43** (leave-one-out refit) | **22/25** |

- **Median actual:** 50 active minutes (range 6–311).
- **Median blind estimates:** 45 min for the agent-framed model, 480 min for the human developer.
- Method v0.1's P80 covered 25 of 25 tasks (P50 covered 24 of 25). That is far too wide, which confirms its priors were too pessimistic.

## What it means

1. **The "dashboard = 4–5 h" problem is a framing error.** Across every category, the work took 7–25× less than the human-developer estimate:

   | Category | Speedup (median) | Sessions |
   |---|---|---|
   | Dashboards/UI | ~25× | 4 |
   | Data pipelines/scrapers | ~19× | 5 |
   | Features in existing code | ~13× | 3 |
   | Video | ~11× | 2 |
   | Bug fixes | ~10× | 4 |
   | Refactors | ~10× | 2 |
   | Agent tooling | ~9× | 4 |
   | Investigation | ~7× | 1 |

2. **Once the framing is fixed, the noise comes from things outside the request.**
   - Waits (renders, scrapes, shared test queues, locks) took 20–70% of elapsed time in about half the sessions.
   - Design rejections cost 20–25 min per rebuild.
   - None of this shows in the text of the request, so the intake checklist asks about it explicitly.
3. **Brief quality is the biggest predictor.**

   | | Long, precise briefs (>1,200 chars, mostly written by a parent agent) | Short, direct asks |
   |---|---|---|
   | Tasks | 19 | 6 |
   | Correction loops (median) | 0 | 2 |
   | Actual vs naive estimate | 0.87× (slightly over-estimated) | 1.54× (under-estimated) |

4. **Coding is no longer what takes the time.** The refit says build units take ~0.2× even the "agent-era" research priors, while waits take 1.5× of what was predicted.
5. **Elapsed-time self-reports are wrong in both directions.** Claude said "about 20 minutes" for a 9.8-minute dashboard and "45–60 min" for a render that took ~23. Its estimates for short background steps were accurate.

## Time sinks (25 sessions, ~1,100 minutes of identified loss)

| Root cause | Share | Typical examples |
|---|---|---|
| Environment | 33% | Shared-PC test queue/lock, low-RAM gate timing out quietly, worktree missing venv |
| Other / mixed | 16% | Long background jobs, waiting on child sessions |
| Agent mistakes | 11% | Shell/heredoc escaping, CRLF churn, wrong test counts, no timeout on a background monitor |
| Tests/CI | 10% | Full suite instead of a targeted set, flaky fixed sleeps |
| Unclear spec + UI taste loops | 14% | Rules drip-fed over 3 messages; 3 rejected designs |
| External APIs | 6% | Undocumented endpoint probing |
| Data quality, waiting on the human, scope creep | 9% | |

## Limits

- **Small sample.** n=25 over 6 days from one person, with mostly parent-briefed child sessions. The v0.2 factors are fitted on the same data (the leave-one-out check limits over-fitting, but they are still provisional).
- **"Active time" takes judgment.** Background renders and parallel sessions make elapsed and active time diverge. Each record states which figure was trusted.
- **Requests were cut to 2,000 characters** for the blind estimators.
- **Next step:** run `SESSION_AUDIT_PROMPT.md` on ~100 sessions from local transcripts to get per-category factors with n ≥ 10.
