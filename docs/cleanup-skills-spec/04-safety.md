# 04 — Safety Layer

Build this **before** any skill that changes files. Several independent layers, because each one alone can be bypassed.

Why: real incidents with coding agents include `rm -rf` on a parent folder during a "move files" reorganization (~1,500 files lost, claude-code #49129), `rm -rf "$HOME"` hidden in a compound command (#93099), and deletes hidden inside a script the agent wrote, so the permission check only saw `bash script.sh` (#88462). Claude Code's `/rewind` checkpoints do **not** cover files changed by shell commands — git is the only reliable undo.

## Layer 1 — Git as the undo button
- Only tracked files are changed. Untracked/ignored files (where `.env`, local DBs, secrets live) are never touched.
- Preflight backups: tag + archive branch + bundle + tarballs outside the repo.
- Work happens on `cleanup/day-one` branch; `main` is never modified directly.

## Layer 2 — Permission deny rules (`.claude/settings.json` in the target project)

```json
{
  "permissions": {
    "deny": [
      "Bash(rm *)",
      "Bash(rmdir *)",
      "Bash(find * -delete*)",
      "Bash(git clean *)",
      "Bash(git reset --hard*)",
      "Bash(git checkout -- *)",
      "Bash(git restore .)",
      "Bash(git push --force*)",
      "Bash(git push -f*)",
      "Bash(git filter-repo*)",
      "Bash(git branch -D *)",
      "Bash(git tag -d *)"
    ]
  }
}
```
Deny rules are not a hard boundary (`/bin/rm`, `bash -c '...'`, or a script can get around them), hence the next layers. Maintainer: check rule syntax against current docs (code.claude.com/docs/en/permissions).

## Layer 3 — PreToolUse guard hook
A hook on `Bash` that parses the command (including `bash -c`, `sh -c`, `xargs`, `env`, subshells, `&&`/`;` chains) and blocks:
- any of the deny-list commands above, by any path (`/bin/rm`, `command rm`);
- `git mv`/`git rm` on paths **not** in the approved plan while `/cleanup-apply` is running;
- running scripts the agent created in this session (anything not in the skill's `scripts/` folder) during apply.

Options: an existing parser-based guard such as `kenryu42/claude-code-safety-net` (note: it fails open on bad config — test it), or a small custom hook. Register it project-wide, or via the `hooks:` field of `/cleanup-apply`.

## Layer 4 — Sandbox
Enable Claude Code's sandbox (`sandbox.enabled: true`) so file writes are confined to the repo, including from subprocesses and scripts.

## Layer 5 — Process rules
- `/cleanup-apply` is manual only and needs the plan hash typed by the human.
- Don't run apply in bypass-permissions or fully automatic modes.
- No improvised deletion: only `apply_plan.py` changes files at file level.
- Never delete through a variable that could be empty or wrong; keep destructive operations as single, explicit commands.
- Any unexpected error → stop and report. Don't retry with a different command.
- Never push, force-push or rewrite history without a direct human instruction.

## History rewrite (separate, opt-in only)

Only for: a secret that was committed (after rotating it), or a repo bloated by large binaries. Steps for the human/maintainer, not automated:
1. Rotate/revoke secrets first — often enough on its own.
2. Freeze pushes; merge or close open PRs.
3. In a fresh `git clone --no-local` copy: `git filter-repo --sensitive-data-removal --invert-paths --path <file>` (or `--strip-blobs-bigger-than 10M`).
4. `git push --force --mirror`; everyone re-clones; contact GitHub Support for cached views / PR refs.
5. Tag `day-one` on the rewritten history.

"Fresh start" alternatives (orphan branch with one initial commit, or a brand-new repo) give a history that literally begins at day one, but lose blame/bisect, break open branches and PRs, and force everyone to re-clone. Not recommended for clutter alone.

## Failure handling summary

| Situation | Behavior |
|---|---|
| Dirty tree at start | Stop |
| Baseline build/tests already failing | Stop; human fixes or explicitly accepts |
| Batch fails verify | Restore only that batch's paths; mark `needs-human`; continue |
| File changed that isn't in the plan | Stop entirely |
| Plan hash mismatch | Refuse apply |
| Secret found | Report; recommend rotation; never rewrite automatically |
| Detector missing for stack | Continue with reference + git signals; report gap; more items become `needs-human` |
