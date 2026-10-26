# CLAUDE.md snippet: estimating time

Paste this into your global `~/.claude/CLAUDE.md` (or a project's), after running the full audit to replace the pilot numbers with your own.

```markdown
## Time estimates
- Never give "developer hours". Estimate agent-era ELAPSED time for this user + Claude Code, from
  units, not gut feel. Method: research/estimation/COOKBOOK.md (devcamp repo).
- Before any task bigger than a one-file fix, print one line and then start:
  `ESTIMATE task=<slug> cat=<category> p50=<min> p80=<min> units=<n> waits=<min>`
  P80 ≈ 1.6 × P50. Name the top risk in a few words if it's material.
- Price waits explicitly: each render / scrape / full test suite / build = 1.5 × its known duration,
  plus queue time if other sessions share this PC. Start slow jobs first and work in parallel.
- Code is cheap: a precise list item ≈ 3 min incl. tests; small edit in familiar code 2–5 min;
  a new single-page UI over existing data 5–15 min.
- Expensive: design taste (20–25 min per rejected rebuild — show 2–3 concept stills first),
  undocumented APIs (probe first, timebox 15–30 min), live-data changes (+10 min safety path).
- Tripwire: if a unit passes its P80, stop, say so, and re-plan with a timeboxed spike.
- Never guess elapsed time from memory. Compute it from timestamps (`date`/tool output) when reporting.
- Don't quote the human-developer equivalent as the estimate; at most mention it as reference.
```

**Why the one-line `ESTIMATE` log matters:** future audits can grep these lines from transcripts and compare them with timestamps. Calibration then becomes automatic: no reconstruction, no hindsight bias.

Example grep:
`rg -o "ESTIMATE task=\S+ cat=\S+ p50=\d+ p80=\d+" ~/.claude/projects`
