# 01 — Config, Working Folder, Plan Schema, Scoring

## 1. Project config: `.claude/cleanup.config.yaml`

Committed to the target project. Makes the skills project-specific without changing their code. `/cleanup-preflight` creates a draft on first run (by inspecting the repo) and **stops** so a human can review it.

```yaml
project: my-project

# Commands that prove the project works. Empty = skipped (and reported as a gap).
commands:
  install:   "npm ci"
  build:     "npm run build"
  test:      "npm test -- --reporter=junit --outputFile=.cleanup/runs/$RUN/junit.xml"
  lint:      "npm run lint"
  typecheck: "npx tsc --noEmit"
  smoke:     "scripts/smoke.sh"     # start app, hit health + main pages, stop
  build_output_dir: "dist"          # file list + sizes compared before/after

# Dead-code / duplicate detectors to run in /cleanup-audit (pick per stack).
detectors:
  - knip            # JS/TS: files, exports, deps
  - jscpd           # duplicates, any language
  # - vulture        # Python  (use --min-confidence)
  # - deptry         # Python unused deps
  # - deadcode-go    # golang.org/x/tools/cmd/deadcode
  # - cargo-udeps    # Rust

# Real entry points (help detectors avoid false positives).
entry_points:
  - src/index.ts
  - scripts/*.ts

# Never deleted, moved or edited by cleanup. Globs.
protected:
  - "**/migrations/**"
  - "**/fixtures/**"
  - "LICENSE*"
  - "**/*.lock"
  - "package-lock.json"
  - ".github/**"
  - "Dockerfile*"
  - "infra/**"

# Paths loaded at runtime by string / plugin systems: treated as live.
dynamic_paths:
  - "src/plugins/**"

# What may live in the repo root after cleanup.
root_allowlist:
  - README.md
  - CONTRIBUTING.md
  - LICENSE
  - CHANGELOG.md
  - CLAUDE.md
  - .gitignore
  - .env.example
  - package.json
  - package-lock.json
  - tsconfig.json

# Name patterns that suggest clutter (raise score, never decide alone).
junk_patterns:
  - "*_v[0-9]*"
  - "*_old*"
  - "*final*"
  - "*copy*"
  - "try[0-9]*"
  - "*SUMMARY*.md"
  - "*PLAN*.md"
  - "*REPORT*.md"
  - "scratch/**"
  - "experiments/**"

archive:
  tag_prefix: "archive/"            # archive/<name> tags for experiment branches
  external_location: ""             # optional: URL/path for large papers/datasets

scratch_dir: ".scratch/"            # gitignored; where agents put temp work from now on
decisions_dir: "docs/decisions/"

thresholds:
  delete_min_score: 0.8             # below this, a delete becomes archive or needs-human
  stale_days: 90

batch:
  max_files_per_commit: 50
```

## 2. Working folder: `.cleanup/` (gitignored)

```
.cleanup/
  config.snapshot.yaml        # copy of config used for this run
  preflight.json              # tag names, backup paths, secret-scan summary
  baseline/                   # results of commands BEFORE cleanup
    build.log  build.exit  build-files.txt
    test.log   test.exit   junit.xml  test-ids.txt
    lint.log   lint.count  typecheck.count
    smoke.log  smoke.exit
  inventory.json              # every tracked file + signals (from /cleanup-audit)
  detectors/                  # raw detector outputs (knip.json, jscpd.json, ...)
  verdicts/                   # keep-advocate output, one JSON per candidate
  distill/                    # draft decision records, reviewed with the plan
  plan.yaml                   # SOURCE OF TRUTH; human may edit
  plan.sha256                 # hash of plan.yaml after validation
  runs/<n>/                   # verify results per batch
  apply.log                   # every operation applied, with commit SHAs
```

Backups that must survive a mistake in the repo go **outside** the repo: `../<repo>-cleanup-backups/<date>/` (bundle + tarballs).

`CLEANUP_PLAN.md` (repo root, gitignored or removed at the end) is a human-readable rendering of `plan.yaml`.

## 3. Inventory record (`inventory.json`, one per tracked file)

```json
{
  "path": "notes/auth-research-v2.md",
  "kind": "docs",
  "size_bytes": 18234,
  "last_commit": "2026-07-02",
  "commit_count": 1,
  "added_in_burst": true,
  "text_refs": [],                     // files that mention path or basename
  "static_reachable": null,            // true/false/null (not code)
  "detector_findings": [],             // e.g. {"tool":"knip","type":"unused-file"}
  "duplicate_of": null,
  "junk_pattern": "*_v[0-9]*",
  "protected": false,
  "dynamic": false,
  "category": "research-note",
  "score": 0.6
}
```

**Categories:** `source`, `test`, `config`, `config-variant`, `docs`, `research-note`, `idea-doc`, `experiment`, `duplicate`, `generated`, `agent-artifact`, `asset`, `dead-code`, `tool-state`.

## 4. Plan schema (`plan.yaml`)

```yaml
version: 1
created: 2026-10-20T12:00:00Z
base_commit: 0c475d4
pre_cleanup_tag: pre-cleanup-2026-10-20
items:
  - id: 17
    path: notes/auth-research-v2.md
    category: research-note
    action: distill                  # see actions below
    target: docs/decisions/0003-auth-approach.md   # for move / distill
    reason: "Research for auth choice; decision already implemented in src/auth"
    evidence:
      text_refs: 0
      last_commit: 2026-07-02
      duplicate_of: null
      detectors: []
    score: 0.85
    verifier: agree                  # agree | refuted | unsure
    verifier_note: "No references in code, CI, docs or scripts"
    batch: research                  # commit group
    decision: pending                # pending | approve | reject  (human may set)
```

**Actions:**

| Action | Meaning | Done by |
|---|---|---|
| `keep` | No change | — |
| `move` | `git mv` to `target` | `apply_plan.py` |
| `distill` | Install reviewed draft record at `target`, then `git rm` source | `apply_plan.py` |
| `archive` | Tag/branch already holds it; `git rm` from main; listed in CLEANUP.md | `apply_plan.py` |
| `delete` | `git rm` | `apply_plan.py` |
| `untrack` | Add pattern to `.gitignore`, `git rm --cached` (file stays on disk) | `apply_plan.py` |
| `edit` | Code/config change (remove unused export/dep, merge config variants) | Claude, one item at a time, verify after each |
| `needs-human` | Human must decide; never applied | — |

**Batch order (one commit each, verify after each):**
1. `untrack` — tool/agent state into `.gitignore`
2. `agent-artifacts` — summary/plan/report markdown
3. `research` — distill + archive + delete of notes/ideas
4. `experiments` — abandoned attempts, duplicates
5. `configs` — config variants (mostly `edit` / `needs-human`)
6. `code` — unused files, exports, deps
7. `layout` — moves into the target layout

Approval rule: items with `decision: pending` are applied **only** if `verifier: agree` and `score >= delete_min_score` (for delete/archive/distill). Everything else must be explicitly set to `approve` by the human.

## 5. Scoring rubric (starting point, tune per project)

Score from 0 to 1. Start at 0.

| Signal | Effect |
|---|---|
| Detector says unreachable/unused, high-confidence (knip unused file, vulture 100%, Go deadcode) | +0.40 |
| Detector finding, low-confidence (vulture 60%) | +0.15 |
| Zero text references anywhere (code, CI, Docker, Make, scripts, HTML/CSS, docs, IaC) | +0.30 |
| **Any** text reference found | score capped at 0.30 |
| Not changed in `stale_days`, or added in one burst commit and never touched | +0.10 |
| Matches a `junk_patterns` entry | +0.10 |
| Exact or near duplicate of a file that **is** referenced | +0.20 |
| No runtime/coverage hits (only if runtime data is available) | +0.10 |
| Under `protected`, `dynamic_paths`, public API of a published package, `.env*` | **veto** → `keep` or `needs-human`, score 0 |

Rules:
- Age alone never justifies deletion (old files are often stable and critical).
- Non-code files (notes, docs) get no static-reachability signal; they rely on references, patterns, age and the verifier.
- Keep-advocate verdict `refuted` → `keep`. Verdict `unsure` → `needs-human`.
