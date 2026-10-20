# 05 — Keeping It Clean After Day One

Instructions in `CLAUDE.md` are advice; hooks and CI checks are enforcement. Use both.

## 1. CLAUDE.md snippet for the target project

Keep it short and hand-written (research found auto-generated agent instruction files lowered task success and raised cost).

```markdown
## Where files go
- Temporary work (notes, plans, research, experiments, test scripts, summaries) goes ONLY in `.scratch/` (gitignored). Never commit it.
- Never create summary / plan / report `.md` files in the repo root.
- Lasting knowledge goes in `docs/` or as a decision record in `docs/decisions/` (ADR, or a row in `docs/decisions/log.md`).
- Experiments happen on a branch or worktree. When abandoned: tag `archive/<name>`, delete the branch, add a row to `docs/decisions/log.md`.
- Don't create `*_v2`, `*_old`, `*_final`, `*copy*` files — change the original; git keeps history.
- One config per concern; environment differences go in environment variables, documented in `.env.example`.
```

Optional stricter variant: put scratch **outside** the repo (e.g. `../<repo>-scratch/`), since `.gitignore` can be bypassed with `git add -f`.

## 2. Pre-commit hooks (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0            # pin to current
    hooks:
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: check-merge-conflict
      - id: detect-private-key
      - id: check-case-conflict
  - repo: local
    hooks:
      - id: block-junk-files
        name: Block scratch / junk files
        language: fail
        entry: "Junk file — move it to .scratch/ or docs/"
        files: '(\.(tmp|bak|orig|log)$|^(notes|scratch|experiments|tmp)/|(^|/)[^/]*(SUMMARY|PLAN|REPORT|NOTES)[^/]*\.md$|_v[0-9]+\.|_old\.|_final\.|[ _-]copy\.)'
      - id: root-allowlist
        name: Only allowed files in repo root
        language: script
        entry: .claude/skills/cleanup-lib/scripts/check_root.sh   # reads root_allowlist from config
        pass_filenames: false
  # - repo: https://github.com/gitleaks/gitleaks   (or betterleaks)
```

## 3. CI checks

| Check | Tool | Notes |
|---|---|---|
| Dead code / unused deps | knip (JS/TS), vulture + deptry (Python), Go deadcode, cargo-udeps | Clear the backlog at day one first, otherwise the check gets disabled. Suppressions live in reviewed files. |
| Duplicates | jscpd `--baseline` / fail on new clones | |
| File-count budget | `git ls-files \| wc -l` vs `.repo-budget` file | Raising the budget = reviewed change |
| Root allowlist / new top-level folders | script or Danger JS | Warn on new root files |
| Large files / repo size | `check-added-large-files`, `git-sizer` | |
| Secrets | gitleaks / betterleaks | |
| Broken doc links | lychee (`--offline` for local links) | |

Add `CODEOWNERS` for the root, `.github/`, dependency manifests and `.repo-budget` so structural growth needs a maintainer's review.

## 4. Monthly `/janitor`

Run as a scheduled task (monthly) or manually. Report only:
- new files matching `junk_patterns` or outside `root_allowlist`;
- detector findings since `day-one`;
- new duplicates;
- branches with no commits in `stale_days` (suggest `archive/` tags);
- TODOs without an issue link;
- `.scratch/` size reminder (local only).

**Metrics vs `day-one` tag** (keep a small history in `docs/metrics.md` or CI artifacts): tracked file count, lines of code by language (`scc`), dependency count, dead-code findings, duplication %, largest blob (`git-sizer`), lint/type error count.

If findings are big enough, it recommends running `/cleanup-plan` (the same approved-plan flow — never deletes on its own).
