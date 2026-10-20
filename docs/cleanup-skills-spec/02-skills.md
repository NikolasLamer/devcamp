# 02 — Skills

All skills live in the target project under `.claude/skills/<name>/SKILL.md`, with scripts in `.claude/skills/<name>/scripts/` (or a shared `.claude/skills/cleanup-lib/scripts/`).

> Frontmatter field names below reflect Claude Code docs as of Oct 2026 (`name`, `description`, `disable-model-invocation`, `allowed-tools`, `disallowed-tools`, `context`, `agent`, `hooks`). **The maintainer should check them against the current docs** (code.claude.com/docs/en/skills) before building. Note: `allowed-tools` only *pre-approves* tools; it does not restrict. Use `disallowed-tools` to restrict.

Keep each `SKILL.md` under ~500 lines. Put long references (detector notes, ADR template) in sibling files and link them.

---

## /cleanup-preflight

**Purpose:** make the cleanup reversible and record how the project behaves today.

```yaml
name: cleanup-preflight
description: Prepare a repo for a day-one cleanup — backups, secret scan, baseline of build/test/lint/smoke. Run before /cleanup-audit.
disable-model-invocation: true
```

**Steps**
1. Check `git status --porcelain` is empty. If not → stop and tell the user to commit or stash.
2. If `.claude/cleanup.config.yaml` is missing → inspect the repo (package manifests, CI workflow, Makefile, README) and write a **draft** config. Stop and ask the human to review it. Don't continue on the same run.
3. Create backups (via `preflight.sh`):
   - annotated tag `pre-cleanup-<date>`;
   - branch `archive/pre-cleanup` at that tag;
   - `git bundle create ../<repo>-cleanup-backups/<date>/repo.bundle --all` and `git bundle verify`;
   - tarball of untracked files and of ignored files (excluding heavy dirs like `node_modules`, `.venv`, `target`). Warn that the tarball may contain secrets.
   - list stashes; suggest turning keepers into branches.
   - **Do not push** tags/branches; tell the user the push commands.
4. Secret scan: `gitleaks git --log-opts="--all"` (or betterleaks) and `trufflehog git file://. --results=verified,unknown` if installed. Report findings; recommend **rotating** first. Do not rewrite history.
5. Baseline (via `baseline.sh`): run each configured command, save logs, exit codes, test IDs, lint/type counts, build file list. Missing commands are reported as gaps.
6. If the test suite is weak or missing: report it, and suggest adding a few characterization tests on main entry points before continuing.
7. Write `.cleanup/preflight.json` and print a short summary.

**Stops if:** dirty tree, no config yet, baseline build fails (a broken baseline makes verification meaningless — the user must fix or accept it explicitly).

---

## /cleanup-audit

**Purpose:** read-only inventory and scoring of every tracked file.

```yaml
name: cleanup-audit
description: Read-only audit of a repo for clutter — classifies every tracked file, runs dead-code and duplicate detectors, scores deletion candidates. Writes .cleanup/inventory.json. Changes nothing.
disallowed-tools: Edit, Write(!.cleanup/**)   # maintainer: express "write only inside .cleanup/" with current syntax or a hook
```

**Steps**
1. Require `.cleanup/preflight.json` (else tell user to run `/cleanup-preflight`).
2. `inventory.sh`: list tracked files with size, last commit date, commit count, burst flag, protected/dynamic/junk-pattern flags.
3. Run configured detectors; save raw output in `.cleanup/detectors/`.
4. Reference scan: for each file, search the repo for its path and basename (excluding itself). Record referencing files.
5. Duplicate scan (jscpd for code; content hash for whole files).
6. Spawn `cleanup-scanner` agents in parallel, one per top-level folder (split large folders). Each returns category + short reason per file as JSON.
7. Compute scores (`01-config-and-data.md` §5). Write `inventory.json`.
8. Print summary: counts per category, top candidates, size that could be removed, gaps (e.g. no detector for this stack).

**Must not:** change any file outside `.cleanup/`.

---

## /cleanup-plan

**Purpose:** turn the inventory into a reviewed, validated plan, then stop for human approval.

```yaml
name: cleanup-plan
description: Build the day-one cleanup plan from the audit — verify each candidate with a keep-advocate, draft decision records for research to distill, write and validate .cleanup/plan.yaml and CLEANUP_PLAN.md, then stop for approval.
disallowed-tools: Edit     # writes only into .cleanup/ and CLEANUP_PLAN.md
```

**Steps**
1. Require `inventory.json`.
2. Choose candidate action per file from category + score:
   - `agent-artifact`, `generated` (tracked by mistake), `tool-state` → `delete` / `untrack`
   - `research-note`, `idea-doc`, `experiment` → `distill` if it holds a conclusion, else `archive`/`delete`
   - `duplicate` → `delete` the unreferenced copy
   - `config-variant` → `edit` (merge) or `needs-human`
   - `dead-code` → `delete` (whole file) or `edit` (unused export/dep)
   - misplaced but live docs → `move`
3. Spawn `keep-advocate` agents (batched, parallel) for every `delete`, `archive`, `distill`, `edit` candidate. Apply verdicts: `refuted` → `keep`; `unsure` → `needs-human`.
4. Spawn `distiller` agent for `distill` items, grouped by topic. It writes drafts to `.cleanup/distill/` (ADRs in MADR format, entries for `docs/decisions/log.md`), each citing the source paths and the `pre-cleanup` tag.
5. Write `plan.yaml`; render `CLEANUP_PLAN.md`:
   - summary table (files/bytes per action and batch);
   - **needs-human** list first;
   - per batch: every item with path, action, reason, score, verifier note;
   - draft decision records (or links to them);
   - instructions: how to edit `plan.yaml` (`decision: approve|reject`), and that edits require re-running `/cleanup-plan --revalidate`.
6. Run `validate_plan.py`. Fix and re-run until it passes.
7. Write `plan.sha256`. End with:
   > Review CLEANUP_PLAN.md. When ready, run: `/cleanup-apply <hash>`

**Option `--revalidate`:** skip steps 2–5; re-validate a human-edited `plan.yaml` and print the new hash.

---

## /cleanup-apply

**Purpose:** apply the approved plan, in batches, verifying each.

```yaml
name: cleanup-apply
description: Apply an approved day-one cleanup plan. Manual only.
disable-model-invocation: true
arguments: plan_hash
hooks: # register the destructive-command guard for the session (see 04-safety.md)
```

**Refuses unless all are true**
- argument equals the current hash of `plan.yaml`, and `validate_plan.py` passes;
- working tree clean;
- `pre-cleanup-<date>` tag exists and points at `plan.base_commit` (or an ancestor);
- current branch is `cleanup/day-one` (create it from base if missing — the only branch op allowed);
- session is not in a bypass-permissions mode (check and refuse if detectable).

**Steps** (for each batch in order from `01` §4)
1. `apply_plan.py --batch <name>` performs the file-level actions (`move`, `distill`, `archive`, `delete`, `untrack`) for eligible items and stages them.
2. For `edit` items in the batch: Claude makes each change, smallest first. No other files touched.
3. Run `verify.sh`. Compare to baseline.
4. Green → commit `chore(cleanup): <batch> — <n> files` with the item IDs in the body; log SHA to `apply.log`.
5. Red → `git restore --staged --worktree` **only the paths in this batch**, mark those items `needs-human` with the failure, continue with next batch. If the failure can be pinned to one item (bisect within batch), revert only that item and retry the rest once.
6. Stop entirely on: unexpected git error, any file changed that isn't in the plan, verify script itself crashing.

After the last batch: print summary and tell the user to run `/cleanup-verify`.

---

## /cleanup-verify

**Purpose:** final proof that nothing broke; write the restore guide; set the anchor.

```yaml
name: cleanup-verify
description: Verify the day-one cleanup against the baseline, check for dangling references, write CLEANUP.md and tag day-one.
```

**Steps**
1. Full `verify.sh` run; diff against baseline:
   - build/test/lint/typecheck/smoke exit codes unchanged (or better);
   - no test ID disappeared, except tests deliberately removed with their dead code (listed in plan);
   - lint/type error counts not higher;
   - build output file list: report differences.
2. Dangling reference check: search remaining files for every removed/moved path and basename. Local link check on markdown (`lychee --offline` if installed).
3. Root check: root contains only `root_allowlist` (report extras).
4. Write `CLEANUP.md` (or `docs/cleanup-<date>.md`): what was removed per batch, what was distilled where, `needs-human` items left, and restore commands:
   ```bash
   git show pre-cleanup-<date>:<path>
   git restore --source=pre-cleanup-<date> -SW -- <path>
   git diff --stat --diff-filter=D pre-cleanup-<date> day-one
   ```
5. Commit `CLEANUP.md`. Create annotated tag `day-one` **locally**. Print push / PR instructions; don't push.
6. Delete `CLEANUP_PLAN.md` from the root if it was committed by mistake; keep `.cleanup/` (gitignored) until the PR is merged.

---

## /day-one (orchestrator)

```yaml
name: day-one
description: Guided day-one cleanup of a cluttered repo. Runs preflight, audit and plan, then stops for human review.
disable-model-invocation: true
```

**Steps:** run `/cleanup-preflight` → `/cleanup-audit` → `/cleanup-plan`, stopping wherever those stop. Never continue into apply. Finish by telling the user exactly what to review and the apply command.

(Since skills marked `disable-model-invocation` can't be invoked by Claude, the orchestrator should **include the steps by reference** — e.g. read the sibling SKILL.md files or call the shared scripts — rather than trying to invoke the other skills. Maintainer decides the cleanest mechanism.)

---

## /janitor (after day one)

```yaml
name: janitor
description: Monthly repo hygiene report — new clutter, dead code, duplicates, size and file-count trends since day-one. Report only.
disallowed-tools: Edit
```

Runs a lighter audit (inventory + detectors + root/junk-pattern check + metrics vs the `day-one` tag) and writes a report (or opens an issue if a GitHub tool is available). Never deletes. Suggests running `/cleanup-plan` if there's enough to clean. See `05-regrowth-prevention.md`.
