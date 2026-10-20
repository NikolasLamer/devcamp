# Day-One Cleanup Skills — Build Spec

Hand-off spec for building a set of Claude Code skills that turn a cluttered development repo into a clean, production-like baseline ("day one") **without deleting important files or breaking the project**, and then keep it lean.

- Background research and sources: [`../research/project-cleanup-research.md`](../research/project-cleanup-research.md)
- Scope of first rollout: **one project** (project-local `.claude/` folder). Package as a shared plugin only after it has worked on that project.

## Files in this spec

| File | Contents |
|---|---|
| `README.md` | Overview, architecture, build order, non-negotiable rules (this file) |
| [`01-config-and-data.md`](01-config-and-data.md) | Project config file, `.cleanup/` working folder, plan schema, scoring rubric |
| [`02-skills.md`](02-skills.md) | Each skill: frontmatter, inputs, steps, outputs, stop conditions |
| [`03-agents-and-scripts.md`](03-agents-and-scripts.md) | Subagents and the deterministic scripts the skills call |
| [`04-safety.md`](04-safety.md) | Permission rules, hooks, sandbox, failure handling |
| [`05-regrowth-prevention.md`](05-regrowth-prevention.md) | CLAUDE.md rules, pre-commit, CI checks, monthly janitor |
| [`06-acceptance-tests.md`](06-acceptance-tests.md) | Fixture repo with traps, and the expected result for each |

## What "day one" means here

- Git history is **kept**. Clutter is removed in small, reviewed commits on a branch, then the result is tagged `day-one`.
- Everything removed stays recoverable from a `pre-cleanup-<date>` tag and archive branch.
- Useful knowledge from research notes and experiments is **distilled** into short decision records before the raw files are removed.
- The project builds, tests and runs exactly as before.

**Not in scope by default:** rewriting git history (orphan branch, new repo, `git filter-repo`). Only done as a separate, explicitly approved step for leaked secrets or very large files. See `04-safety.md`.

## Architecture

```
/day-one  (orchestrator, manual)
   │
   ├─ /cleanup-preflight   backups, secret scan, baseline           [manual]
   ├─ /cleanup-audit       read-only inventory + scoring             [read-only]
   │      └─ cleanup-scanner agents (parallel, one per folder)
   ├─ /cleanup-plan        verify candidates, draft decision records,
   │      │                write plan, validate, STOP for approval
   │      ├─ keep-advocate agents (try to prove each file is needed)
   │      └─ distiller agent (drafts ADRs / "what we tried" log)
   │
   │   ── HUMAN reviews .cleanup/plan.yaml + CLEANUP_PLAN.md ──
   │
   ├─ /cleanup-apply <plan-hash>   manual only; applies approved plan
   │                               in batches, verify after each
   └─ /cleanup-verify      final baseline diff, reference check, tag

/janitor   monthly, report only (after day one)
```

Data flows through files in a gitignored `.cleanup/` folder, so every phase can be inspected, re-run, or resumed.

## Non-negotiable rules (every skill and agent)

1. **Only tracked files are ever changed**, and only through `git mv` / `git rm` / normal edits. Never `rm`, `find -delete`, `git clean`, `git reset --hard`, `git checkout -- .`.
2. **No deletion without an approved plan.** Approval = the human runs `/cleanup-apply <hash>` with the hash printed at the end of `/cleanup-plan`. Claude cannot invoke `/cleanup-apply` itself.
3. **File operations are done by the bundled `apply_plan.py`**, never by commands Claude writes on the fly.
4. **When in doubt → `needs-human`.** Any unverifiable or contested candidate is never deleted automatically.
5. **Distill before delete.** A `distill` item cannot be removed until its decision record exists.
6. **Every batch is verified.** A batch that fails verification is reverted and its files marked `needs-human`.
7. **Stop on unexpected errors.** Don't retry destructive steps with different commands.
8. **Never push, force-push, or rewrite history** without an explicit human instruction in the conversation.

## Build order (suggested)

1. Config file + `.cleanup/` layout + plan schema (`01`).
2. Safety layer: settings deny rules + guard hook (`04`). Build this **first** so everything after is protected.
3. Scripts: `inventory.sh`, `baseline.sh`, `verify.sh`, `validate_plan.py`, `apply_plan.py` (`03`).
4. `/cleanup-preflight`, then `/cleanup-audit`, then `/cleanup-plan` (read-only phases first).
5. Acceptance fixture repo (`06`); run the read-only phases against it until results match.
6. `/cleanup-apply` and `/cleanup-verify`; finish acceptance tests.
7. `/day-one` orchestrator.
8. Regrowth prevention + `/janitor` (`05`).

## Target layout for the target project (the definition of "clean")

```
README.md  CONTRIBUTING.md  LICENSE  CHANGELOG.md
CLAUDE.md                       # short, human-written
docs/                           # user / operator docs
docs/decisions/                 # ADRs (MADR) + log.md ("what we tried")
src/ tests/ config/ (+ build files, lockfiles)
.env.example  .gitignore
```
Acceptance check: the repo root contains only the files listed in `root_allowlist` in the project config.
