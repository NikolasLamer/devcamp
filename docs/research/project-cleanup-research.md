# Project Cleanup ("Day One") — Research Report

**Date:** 2026-10-20
**Goal:** Design a repeatable Claude Code workflow (skill set) that turns a cluttered, AI-assisted dev repo into a clean, production-like baseline — **without deleting important files or breaking the project** — and keeps it lean afterwards.

Research was done by 5 parallel agents covering: dead-code detection tools, git safety nets, knowledge preservation, Claude Code skill design, and verification/regrowth prevention. Sources are listed at the end.

---

## 1. TL;DR — the recommended approach

1. **Keep git history. Don't start a new repo.** Do the cleanup as a series of small commits/PRs grouped by category, then tag the result `day-one`. Rewriting history is only worth it for leaked secrets or huge binaries.
2. **Back up everything before touching anything:** tag + archive branch + `git bundle` + a tarball of **untracked/ignored files** (git can't recover those — `git clean` is permanent).
3. **Distill, then delete.** Research notes, ideas, and failed experiments get condensed into short decision records (ADRs / a "what we tried" log) that point to the archive tag. Then the raw files go.
4. **Plan file + human approval gate.** The agent never deletes on its own judgement in the moment. It writes a `CLEANUP_PLAN.md` (every file, action, reason, confidence). A human approves it. A deterministic script applies it.
5. **Adversarial "keep-advocate" agent.** For every delete candidate, a second agent tries to *prove the file is still needed*. If it can, or if it's unsure → `needs-human`, never delete.
6. **Verify every batch.** Baseline (build, tests, lint, smoke run) captured before; same checks after each batch; a failing batch is reverted.
7. **Prevent regrowth.** One gitignored scratch folder for agents, rules in `CLAUDE.md`, pre-commit/CI checks that block junk files, and a monthly "janitor" run.

---

## 2. Proposed skill set

Several small skills plus a thin orchestrator. The destructive step is **manual-only**.

| Skill | Invocation | What it does |
|---|---|---|
| `/day-one` | Manual | Orchestrator: runs preflight → audit → plan, then stops and tells the human to review the plan. |
| `/cleanup-preflight` | Manual | Clean-tree check, backup tag, archive branch, bundle, untracked/ignored tarball, secret scan, baseline capture. |
| `/cleanup-audit` | Read-only (`disallowed-tools: Edit Write`) | Inventories tracked files; parallel scanner subagents per directory classify each file; runs dead-code/duplicate tools; writes `.cleanup/inventory.json`. |
| `/cleanup-plan` | User | Runs the keep-advocate verifier on every candidate, writes `CLEANUP_PLAN.md` + machine-readable plan, validates it with a script. **Stops for approval.** |
| `/cleanup-apply` | **`disable-model-invocation: true`** (manual only) | Refuses unless: plan approved + hash matches, clean tree, on a `cleanup/day-one` branch. Runs a bundled `apply_plan.py` — Claude does not improvise `rm` commands. One commit per category. |
| `/cleanup-verify` | Any | Re-runs baseline checks, diffs against pre-cleanup baseline, greps remaining files (CI, Docker, scripts, docs) for references to removed paths. Reverts a failing batch. |
| `/janitor` (later) | Scheduled monthly | Lightweight re-run of audit + checks; opens an issue/PR with findings. |

**Agents** (`.claude/agents/`):
- `cleanup-scanner` — read-only tools, classifies files.
- `keep-advocate` — adversarial verifier; told to prove the file is needed.
- (optional) `cleanup-executor` — runs in an isolated git worktree.

**Bundled scripts** (deterministic, reviewed once, reused forever): `inventory.sh`, `baseline.sh`, `validate_plan.py`, `apply_plan.py`, `verify.sh`.

### Plan row format
```
path | category | action | reason + evidence | confidence | verifier verdict | approved
```
- **category:** source / config / config-variant / docs / research-note / idea-doc / experiment / duplicate / generated / dead-code / agent-artifact
- **action:** keep / move / distill / archive / delete / gitignore / needs-human
- **evidence:** references found, last commit date, reachable from entry point?, duplicate of X

---

## 3. The workflow, step by step

### Phase 0 — Preflight (safety nets)
```bash
git status --porcelain                      # must be empty
TAG=pre-cleanup-$(date +%F)
git tag -a "$TAG" -m "Snapshot before day-one cleanup" && git push origin "$TAG"
git branch archive/pre-cleanup "$TAG" && git push origin archive/pre-cleanup
git bundle create ../repo-$TAG.bundle --all && git bundle verify ../repo-$TAG.bundle
# Untracked + ignored files are NOT in git or the bundle:
git ls-files --others --exclude-standard -z | tar --null -T - -czf ../untracked-$TAG.tgz
git ls-files --others --ignored --exclude-standard -z | tar --null -T - -czf ../ignored-$TAG.tgz
git stash list                              # stashes are local-only; turn keepers into branches
```
- **Secret scan** (cleanup is the right moment): `gitleaks git -v --log-opts="--all" .` and `trufflehog git file://. --results=verified,unknown`. **Rotate first** — a revoked secret often doesn't need a history rewrite.
- **Capture baseline** into a gitignored `.cleanup/baseline/`: build exit code + output file list, test pass/fail/skip + test IDs, lint/type error counts, bundle size, `--help` output / route list, smoke run (start app, hit health + main pages).
- If test coverage is weak → add a few **characterization (golden-master) tests** on main entry points first. They lock in current behavior so deletions that change it get caught.

### Phase 1 — Audit (read-only)
Signals per file:
1. **Static reachability** — is it reachable from real entry points?
2. **Text references** — repo-wide grep for path and basename (incl. CI workflows, Dockerfiles, Makefile, `package.json` scripts, HTML/CSS, docs, IaC, `.env*`). Any hit sharply lowers delete confidence — this catches files loaded by string path.
3. **Git history** — last modified, "added in one burst commit and never touched again", name patterns (`*_v2`, `*_old`, `final`, `copy`, `try*`, `scratch`, `experiment`).
4. **Duplicates** — exact or near clones of a file that *is* referenced.
5. **Runtime** (optional) — coverage / logs show it never ran. Raises confidence, never enough alone.

Tools by ecosystem:
| Ecosystem | Tools | Notes |
|---|---|---|
| JS/TS | **knip** (files, exports, deps), madge `--orphans` | ts-prune, depcheck, unimported are archived → use knip. Configure `entry` before trusting it. Never run `--fix --allow-remove-files` blindly. |
| Python | vulture, deadcode, skylos, deptry, ruff F401 | vulture: only 100% confidence is reliable; 60% is "very rough". Use `--ignore-decorators` for frameworks. |
| Go | `golang.org/x/tools/cmd/deadcode`, staticcheck U1000 | `-whylive` explains why something is kept. |
| Rust | cargo-udeps (accurate, nightly), cargo-machete (fast, rough) | |
| Any | **jscpd** (code clones, near-duplicates), fclones/jdupes (identical files), `git last-modified` (git ≥ 2.52), code-maat (age, churn, coupling) | |

**Hard vetoes (never auto-delete):** public API of a published package, framework/plugin directories, DB migrations, test fixtures, `.env*`, licenses, lockfiles, CI/deploy config, anything on an explicit allow-list.

### Phase 2 — Triage & plan
Every file goes into one bucket. Deciding question: *"Does this still describe reality, or explain why reality is the way it is?"*

| Bucket | Typical files | Action |
|---|---|---|
| **KEEP** | live source, real config, accurate docs | leave, or `git mv` to canonical place |
| **DISTILL** | research notes, brainstorms, abandoned experiments, try2/v3/final_final | extract decision + outcome + reason into an ADR / log entry citing the archive tag, **then** delete raw file |
| **ARCHIVE** | working prototypes, datasets, long papers worth keeping | `archive/*` tag or branch, or external storage; not on main |
| **IGNORE** | tool/agent state, local settings, scratch | add to `.gitignore`, `git rm --cached` |
| **DELETE** | agent-made `IMPLEMENTATION_SUMMARY.md`, `PR_INFO.md`, stale plans/checklists, unreachable code | delete — git history is the backup |
| **NEEDS-HUMAN** | anything the keep-advocate refuted or couldn't verify | human decides |

**Confidence tiers → action:**
- **High** (static + text + history agree, verifier agrees) → delete in a dedicated commit.
- **Medium** → archive / quarantine.
- **Low** → report only.

**Config variants:** keep the one referenced by code/CI; merge differences into one config + environment variables (12-factor); keep a single `.env.example`; delete dead feature flags *together with* their code paths and tests.

### Phase 3 — Apply (manual, after approval)
- On a `cleanup/day-one` branch (or worktree). Only tracked files, only via `git mv` / `git rm`.
- **One commit per category**, e.g.:
  `chore(cleanup): remove agent summary docs` → `… distill research into ADRs` → `… remove abandoned experiments` → `… consolidate configs` → `… remove unused code/deps`.
- After each commit: run `verify.sh` (build + tests + lint + baseline diff). Red → revert that batch, mark files `needs-human`, continue.
- Every commit stays green, so `git bisect run ./verify.sh` works later.

### Phase 4 — Verify & anchor
- Full baseline diff (a test that *disappeared* counts as a failure).
- Grep remaining files for any removed path. Run a local link check (`lychee --offline './**/*.md'`).
- Write `CLEANUP.md` (or release notes): what was removed, per category, and how to restore it.
- `git tag -a day-one -m "Clean baseline"` and push.

### Restoring anything later
```bash
git show pre-cleanup-2026-10-20:path/to/file                  # view
git restore --source=pre-cleanup-2026-10-20 -SW -- path/      # restore (specific paths, never ".")
git diff --stat --diff-filter=D pre-cleanup-2026-10-20 day-one  # list everything removed
git log --diff-filter=D --summary -- '<glob>'                 # find which commit deleted it
```

---

## 4. Safety rules (defense in depth)

Real incidents show why: an agent ran `rm -rf` on a parent directory during a "move files" reorg (~1,500 files lost, claude-code #49129); `rm -rf "$HOME"` hidden in a compound command (#93099); deletes hidden inside a script the agent wrote itself, so the permission check only saw `bash script.sh` (#88462); production DBs dropped by agents at Replit (2025) and PocketOS (2026).

1. **Git is the undo button.** `/rewind` checkpoints do *not* track Bash `rm`/`mv`. Only touch tracked files; never run `git clean -f`.
2. **Deny rules** in `.claude/settings.json`: `Bash(rm *)`, `Bash(git clean *)`, `Bash(git reset --hard*)`, `Bash(git checkout -- *)`, `Bash(git push --force*)`, `Bash(find * -delete*)`. Docs warn these are *not* a hard boundary (`/bin/rm`, `bash -c`, scripts bypass them).
3. **PreToolUse hook** that blocks destructive commands (e.g. `claude-code-safety-net`, which parses `bash -c` and wrappers).
4. **Sandbox** (`sandbox.enabled: true`) confines writes to the repo, including from subprocesses.
5. **No auto/bypass mode for apply.** Approval gate is human-only; another agent can't approve.
6. **No improvised deletion scripts.** Only the reviewed `apply_plan.py` that reads the approved plan.
7. **Stop on unexpected errors.** Don't delete via variables that might be empty or wrong.
8. **Never force-push or rewrite history** without explicit human confirmation.

---

## 5. Target "day one" layout

```
README.md  CONTRIBUTING.md  LICENSE  CHANGELOG.md
CLAUDE.md / AGENTS.md          # short, human-written
docs/                          # user/operator docs
docs/decisions/                # ADRs (MADR format) + log.md ("what we tried")
src/  tests/  config/  (+ build files)
.env.example  .gitignore
```
Acceptance test: **the root holds only README, CONTRIBUTING, LICENSE, CHANGELOG, agent instructions, and config/build files.**

Keep `CLAUDE.md` short and hand-written — an ETH Zurich study (ICLR 2026) found auto-generated agent instruction files *lowered* task success and raised cost by 20%+.

**ADR (MADR) minimal template:** Title · Context and problem · Considered options (← this is where failed experiments live) · Decision outcome ("Chosen option: X, because…") · Consequences. One ADR can replace a whole folder of drafts.

**"What we tried" log entry:** goal · approach · result (worked/failed/partial) · evidence (commit SHA / archive tag) · why dropped.

---

## 6. Preventing regrowth

**Rules for agents (in `CLAUDE.md`):**
- All notes, plans, research, experiments go in the gitignored scratch folder (e.g. `.scratch/`). Some teams put scratch *outside* the repo entirely, since `.gitignore` can be bypassed.
- Never create summary/plan/report `.md` files in the repo root.
- Durable knowledge goes only into `docs/` or `docs/decisions/`.
- Experiments live on branches or worktrees; when abandoned, tag `archive/<name>` and delete the branch.

**Make it enforced, not advisory** (CLAUDE.md is advice; hooks/CI are guarantees):
- **pre-commit:** `check-added-large-files --maxkb=500`, `detect-private-key`, `check-merge-conflict`, plus a local hook blocking junk patterns:
  `\.(tmp|bak|orig|log)$|^(notes|scratch|experiments)/|(^|/)(NOTES|TODO|PLAN|SUMMARY)[^/]*\.md$|_v[0-9]+\.|final|copy`
- **CI:** knip / vulture / deptry (clear the backlog first, or the check gets switched off); file-count budget (`git ls-files | wc -l` vs a reviewed budget file); new root files or top-level folders flagged (Danger JS); gitleaks/betterleaks.
- **CODEOWNERS** on root, `.github/`, dependency manifests, and budget files.
- **Monthly janitor run** (scheduled Claude task or cron workflow) that opens an issue/PR with findings.
- **Track trends:** file count, LOC (`scc`), dependency count, dead-code findings, duplication % (jscpd), largest blob (`git-sizer`). GitClear's 2025 data: duplicated code blocks rose ~8× in 2024 with AI assistance, while refactoring dropped from ~25% to <10% of changes — this is the growth pattern to watch.

---

## 7. What already exists (to borrow from)

- **cjber/skills `/deadcode`** — closest match. "No deletion without reading the real files, proving non-use, and user approval." Rules out 5 hidden-liveness paths: dynamic dispatch, public API, docs/runbooks, config/string refs, cross-boundary (routes, IaC, sibling repos).
- **petekp/agent-skills `dead-code-sweep`** (archived) — targets agent-generated cruft; parallel subagents over 7 categories; "confirmed dead" vs "needs review" report; per-category approval; auto-revert on broken build.
- **Anthropic `code-simplifier`, `hookify`, `skill-creator`** (claude-plugins-official) — useful building blocks; `skill-creator` helps build and evaluate the new skills.
- **github/awesome-copilot `janitor.agent.md`** — weak safety rules; don't copy as-is.

---

## 8. Decisions needed before building

1. **Which project(s)?** Stack determines which detectors to bundle (knip vs vulture vs Go/Rust tools).
2. **Anchor style:** keep history + `day-one` tag (recommended) vs fresh orphan history / new repo.
3. **Where archives live:** `archive/*` tags (recommended default) vs a separate archive repo vs `docs/archive/` (distilled summaries only).
4. **Scratch location:** in-repo gitignored `.scratch/` vs outside the repo.
5. **Packaging:** committed `.claude/skills/` in each repo vs a shared plugin used across projects.
6. **Enforcement level:** pre-commit only, or also CI blocking.

---

## Sources

Read directly (selection): Claude Code docs — skills, sub-agents, hooks, permissions, sandboxing, checkpointing, workflows, best practices (code.claude.com, platform.claude.com); anthropics/skills; anthropics/claude-plugins-official; cjber/skills deadcode; petekp/agent-skills dead-code-sweep; github/awesome-copilot janitor agent; kenryu42/claude-code-safety-net; claude-code issues #49129, #88462, #93099; knip docs (entry files, production mode, auto-fix, handling issues, CI); madge; vulture; deadcode; autoflake; skylos; golang deadcode; cargo-machete; cargo-udeps; jscpd; code-maat; git docs (bundle, restore, clean, switch); Pro Git (replace); git-filter-repo; GitHub sensitive-data removal guide; git-sizer; git-lfs migrate; gitleaks; betterleaks; trufflehog; lychee + lychee-action; pre-commit-hooks; danger-js; size-limit; adr/madr; escrow-frontend issue #608 (agent-doc clutter cleanup); ddyy/repoyard.

From search summaries only (pages didn't load): Meta SCARF dead-code removal (engineering.fb.com, FSE 2023); Bugsnag tombstones; ETH Zurich AGENTS.md study (arXiv 2602.11988); GitClear 2025 AI code-quality report; Replit and PocketOS incident write-ups; Microsoft decision-log playbook; 12-factor config; Diátaxis; Git 2.52 release notes; Ona knip automation; hungv47 code-cleanup skill.
