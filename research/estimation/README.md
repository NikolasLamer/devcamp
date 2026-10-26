# Estimating development time in the AI-agent era

**Problem:** asked "how long will this take?", models answer with a human-developer time model ("simple dashboard: 4–5 h"). Real work with Claude Code ships far faster. A few tasks, though, still blow up for reasons that have nothing to do with code.

**Short answer from this research and a 25-session pilot:**
- Actual time was **~11× shorter** than the blind human-developer estimate. Dashboards/UI ran ~25× shorter, bug fixes ~10×.
- Framing the question as agent work removes the bias, but leaves ±1.8× noise.
- The noise comes from **waits** (renders, scrapes, test queues), **design-taste loops** and **environment friction**, not from coding.
- A unit-based method, calibrated on your own sessions, gave the best accuracy (within 2× on 22 of 25 tasks, versus 18 of 25 for the plain AI guess).

## Files

| File | What it is |
|---|---|
| [COOKBOOK.md](COOKBOOK.md) | **The method.** Rules, intake checklist, unit price table (v0.2), the math, output format, checkpoints, accelerators, time sinks |
| [PILOT_RESULTS.md](PILOT_RESULTS.md) | 25 real sessions: blind naive vs human-dev vs method estimates against actual times |
| [SESSION_AUDIT_PROMPT.md](SESSION_AUDIT_PROMPT.md) | Prompt to give Claude Code for the full ~100-session audit and personal calibration |
| [CLAUDE_MD_SNIPPET.md](CLAUDE_MD_SNIPPET.md) | Rules to paste into CLAUDE.md so every session estimates this way and logs it |
| `tools/cc_sessions.py` | Parses local Claude Code transcripts (`~/.claude/projects/*.jsonl`) into active/agent/human minutes |
| `tools/calibrate.py` | Bias, spread, shrunk per-category factors, leave-one-out accuracy, Monte Carlo for a plan |
| `tools/cloud_timeline.py` | Builds timelines for cloud/Remote Control sessions from `list_events` dumps |
| `data/pilot_tasks.csv` | Anonymized pilot dataset |
| `sources/01–06` | Research notes with citations: classic estimation science; AI speed evidence; why LLMs misestimate and what a session's time is made of; decomposition method; session-mining and calibration; practitioner reference data |

## Caveats

- Several research agents couldn't open full papers: the network policy blocked most sites and the shared search quota ran out. Claims are tagged in the sources ([V] verified, [M] from memory, [S]/2° from search snippets or secondary coverage, [MKT] marketing).
- Spot-check the primary pages before quoting a number publicly.
- The pilot is one person over 6 days (n=25). Treat the v0.2 numbers as provisional until the 100-session audit.
- **Transcripts are deleted after 30 days by default.** Back up `~/.claude/projects` and raise `cleanupPeriodDays` before auditing.
