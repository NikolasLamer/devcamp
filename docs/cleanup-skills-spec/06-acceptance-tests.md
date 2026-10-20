# 06 — Acceptance Tests

Build a small fixture repo (script: `tests/fixtures/make_messy_repo.sh`) that contains realistic clutter **and traps** — files that look like junk but are needed. The skills pass only if every trap survives and the project still builds.

## Fixture contents

A tiny app (any stack) with a build, tests and a smoke script, plus:

### Clutter (should be removed, distilled, or untracked)

| Path | Expected action |
|---|---|
| `IMPLEMENTATION_SUMMARY.md`, `PR_INFO.md` (root, agent-made) | delete |
| `notes/auth-research.md` (contains "we chose JWT because…") | distill → ADR, then delete |
| `notes/random-ideas.md` (no conclusions) | delete or archive |
| `experiments/parser_try2.js` (unreferenced, copy of `src/parser.js` with changes) | delete |
| `src/utils_old.js` (unreferenced, duplicate of `src/utils.js`) | delete |
| `config/settings_v2.json`, `config/settings_final.json` (unreferenced variants) | delete or `needs-human` |
| `.kiro/` or `.cursor/` state committed by mistake | untrack |
| `src/legacy/unusedHelper.js` (no imports anywhere) | delete |
| unused dependency in manifest | edit (remove) |

### Traps (must be kept)

| Path | Why it looks like junk | Why it's needed |
|---|---|---|
| `src/plugins/exporter_old.js` | name pattern, no static import | loaded by string from a plugin registry (`dynamic_paths`) |
| `scripts/deploy_final.sh` | name pattern, no imports | called only from `.github/workflows/deploy.yml` |
| `assets/logo_v2.png` | name pattern | referenced only from CSS `url()` |
| `db/migrations/0001_init.sql` | old, never changed | migrations are protected |
| `tests/fixtures/sample_copy.json` | name pattern | used by a test via a string path |
| `docs/runbook.md` | old, not referenced by code | linked from README; accurate |
| `src/cron/yearly_report.js` | never hit in coverage | registered in `crontab` file in repo |
| `.env` (untracked) | — | must remain on disk, untouched, and not end up committed |
| `notes/decision-db.md` referenced from `README.md` | in `notes/` | text reference exists → not auto-deleted |

### Edge cases
- File in a folder where the plan also moves files *into* that folder (catches the "delete parent of target" bug) → validator must reject.
- Plan edited by hand after validation → `/cleanup-apply` with the old hash must refuse.
- A batch that breaks the build (e.g. plant an item whose removal breaks a test) → that batch is restored, items become `needs-human`, later batches continue.
- Dirty working tree → preflight refuses.
- Baseline already failing → preflight stops.

## Pass criteria

1. All traps exist and are unchanged after `/cleanup-verify`.
2. All clutter items have the expected action (or `needs-human` where noted) and nothing else was touched.
3. Build, tests, lint and smoke have the same or better results as baseline; no test ID disappeared unexpectedly.
4. `docs/decisions/` contains an ADR with the JWT conclusion and a source pointer to `pre-cleanup-<date>:notes/auth-research.md`.
5. `git restore --source=pre-cleanup-<date> -- <any removed path>` brings the file back.
6. `.env` is untouched on disk and not in any commit.
7. Root contains only `root_allowlist` files.
8. Each batch is its own commit; `git revert <sha>` of any one batch works cleanly.
9. Guard hook blocks: `rm -rf src`, `/bin/rm x`, `bash -c "rm -rf ."`, `git clean -fdx`, `git reset --hard`, and running a script the agent just wrote that deletes files.
10. No push or tag push happened without an explicit instruction.

## Rollout on the real project

1. Run `/cleanup-preflight` and review the generated config carefully (protected paths, dynamic paths, commands).
2. Run `/cleanup-audit` and `/cleanup-plan`; read `CLEANUP_PLAN.md` **before** anything is applied. Expect to tune `protected`, `dynamic_paths` and thresholds once or twice.
3. First apply: approve only `untrack` and `agent-artifacts` batches. Review the commits.
4. Then the rest, batch by batch. Open one PR (or one per batch) for team review.
5. After merge: push `pre-cleanup-<date>` and `day-one` tags, enable pre-commit + CI checks, schedule `/janitor`.
