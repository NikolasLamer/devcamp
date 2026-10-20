# 03 — Agents and Scripts

## Subagents (`.claude/agents/*.md`)

### cleanup-scanner

```yaml
name: cleanup-scanner
description: Classifies tracked files in one folder for a repo cleanup audit. Read-only.
tools: Read, Grep, Glob, Bash(git log *), Bash(git ls-files *)
disallowedTools: Edit, Write, Agent
```

**Input:** a folder path, the config, inventory signals for files in that folder.
**Output (JSON only):**
```json
[{"path": "...", "category": "research-note", "holds_conclusion": true,
  "summary": "one line: what this file is", "reason": "why this category"}]
```
**Instructions to include:**
- Read each file (or its first ~200 lines for large files) before classifying.
- Never guess from the filename alone.
- Mark `holds_conclusion: true` if a note/experiment records a decision, result, benchmark, or lesson worth keeping.

### keep-advocate (adversarial verifier)

```yaml
name: keep-advocate
description: Tries to prove a file or code item proposed for removal is still needed. Read-only.
tools: Read, Grep, Glob, Bash(git log *), Bash(git grep *)
disallowedTools: Edit, Write, Agent
```

**Input:** a batch of candidates (path, proposed action, evidence).
**Output (JSON only, one per candidate):**
```json
{"id": 17, "verdict": "agree|refuted|unsure", "note": "evidence found or searched"}
```
**Its job is to argue for keeping.** It must check, for each candidate:
1. Imports / requires / includes, including dynamic (`import(\`./${x}\`)`, `getattr`, glob loaders, plugin registries).
2. String references to the path or basename anywhere: CI workflows, Dockerfiles, compose files, Makefile/justfile, package scripts, `pyproject` entry points, IaC (Terraform/k8s/Helm), cron/scheduler configs, `.env*.example`, HTML/CSS (`src=`, `url()`), docs and README links.
3. Public API: is it exported from a published package?
4. Framework conventions that load files implicitly (routes folders, migrations, fixtures, auto-imports).
5. Recent activity: changed in the last `stale_days`, or on open branches.
6. For `distill`: does the draft actually capture the file's conclusions?

Rule: if it can't search something it would need (e.g. a sibling repo), verdict is `unsure`, not `agree`.

### distiller

```yaml
name: distiller
description: Condenses research notes, idea docs and experiment files into short decision records before they are removed.
tools: Read, Grep, Glob, Write(.cleanup/distill/**)
disallowedTools: Edit, Agent
```

**Input:** a group of related `distill` items.
**Output:** drafts in `.cleanup/distill/`:
- ADRs for decisions that shape the architecture — MADR minimal format:
  ```markdown
  # NNNN — <decision title>
  Status: accepted · Date: <date> · Source: pre-cleanup-<date>:<paths>
  ## Context and problem
  ## Considered options
  ## Decision outcome
  Chosen option: X, because …
  ## Consequences
  ```
- Entries for `docs/decisions/log.md` (small decisions and experiments):
  `| date | what we tried | result (worked/failed/partial) | why dropped / kept | evidence (tag:path or SHA) |`

Rules: keep conclusions, numbers, links and reasons; drop raw material. Never invent conclusions not in the source. One ADR can cover many files.

---

## Scripts

All scripts: `set -euo pipefail` (bash) or equivalent; no deletion through variables that could be empty; print every git command before running it; exit non-zero on anything unexpected. They are reviewed once by a human and then reused.

| Script | Used by | Contract |
|---|---|---|
| `preflight.sh` | preflight | Checks clean tree; creates tag, archive branch, bundle (+verify), untracked/ignored tarballs outside the repo; runs secret scanners if installed; writes `.cleanup/preflight.json`. Never pushes. |
| `baseline.sh <outdir>` | preflight, verify | Runs each `commands.*` from config with `RUN` set; saves `.log`, `.exit`; extracts test IDs (JUnit or tool-specific), lint/type error counts, sorted build output list with sizes. Never fails the script on a failing command — records it. |
| `inventory.sh` | audit, janitor | `git ls-files -z` → JSON with size, last commit date (`git log -1 --format=%cI` or `git last-modified` on git ≥ 2.52), commit count, burst flag, protected/dynamic/junk flags. |
| `verify.sh [--batch name]` | apply, verify | Runs `baseline.sh` into `.cleanup/runs/<n>/`, compares to baseline, prints a pass/fail table. Exit 0 = no regression, 1 = regression, 125 = can't build/test (usable with `git bisect run`). |
| `validate_plan.py` | plan, apply | Verbose errors. Checks: schema; every path exists and is tracked (`git ls-files --error-unmatch`); action in allowed set; no `protected`/`dynamic` path has a non-`keep` action; `move`/`distill` have a `target` and targets don't overwrite existing files; `distill` drafts exist in `.cleanup/distill/`; delete/archive/distill below `delete_min_score` are `needs-human` unless `decision: approve`; verifier verdict present; no path appears twice; no target inside a path being deleted (the "rm -rf the parent folder" failure). Writes `plan.sha256` on success. |
| `apply_plan.py --batch <name>` | apply | Reads `plan.yaml`; re-runs validation; for eligible items only: `git mv`, `git rm`, `git rm --cached` + `.gitignore` append, install distill drafts into `decisions_dir`. Stages, never commits. Refuses to touch any path not in the plan. Logs every op to `apply.log`. Has `--dry-run` that prints the exact git commands. |

### Detector notes (for the maintainer)

- **knip (JS/TS):** configure `entry`/`project` first; run report-only (`--reporter json`). Never use `--fix --allow-remove-files` inside the skill — knip findings become plan items instead. Also run `knip --production` to separate test-only code.
- **vulture (Python):** `--min-confidence 100` = near-certain; 60% = "very rough". Use `--ignore-decorators` for framework-registered code. Pair with `deptry` for unused deps.
- **Go:** `deadcode -test ./...`; `-whylive=<fn>` to explain why something is live. Results depend on build tags/OS.
- **Rust:** `cargo-udeps` (accurate, nightly) over `cargo-machete` (fast, more false positives).
- **jscpd:** duplicates in any language; good for `foo_v2` style copies.
- Archived tools to avoid: ts-prune, depcheck, unimported (all point to knip).
- Any tool output is a **candidate**, never a decision.
