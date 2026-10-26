#!/usr/bin/env python3
"""
cc_sessions.py - Parse Claude Code local transcripts (~/.claude/projects/<project>/<session>.jsonl)
into per-session and per-segment timing stats for estimation calibration.

Robust to unknown/missing fields: every access is defensive; unknown record types are counted
and ignored. Standard library only. Run with `python3 -I cc_sessions.py ...`.

Usage:
  python3 -I cc_sessions.py [--root ~/.claude/projects] [--idle 15] [--split 45]
                            [--out sessions.csv] [--segments segments.csv] [--no-text]

Definitions (all minutes):
  wall_min      last event ts - first event ts (main thread only)
  agent_min     sum over turns of (last agent event in turn - human prompt ts)
                = time Claude was working (incl. tool runs and permission waits inside the turn)
  human_min     sum of gaps (turn end -> next human prompt) that are <= idle threshold
                = human reading / reviewing / thinking / testing time
  idle_min      sum of human gaps > idle threshold (excluded from active time)
  active_min    agent_min + human_min   (WakaTime-style: gaps > timeout count 0)
  segments      session split wherever a human gap > --split minutes (candidate task boundaries)
"""
import argparse, csv, glob, json, os, re, sys
from collections import Counter
from datetime import datetime

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
NON_PROMPT_PREFIXES = ("<command-name>", "<local-command-stdout>", "<local-command-stderr>",
                       "<command-message>", "[Request interrupted", "Caveat: The messages below",
                       "<task-notification", "<system-reminder", "[SYSTEM NOTIFICATION", "<agent-message")


def ts(o):
    t = o.get("timestamp")
    if not isinstance(t, str):
        return None
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00"))
    except ValueError:
        return None


def content_blocks(msg):
    c = (msg or {}).get("content")
    if isinstance(c, str):
        return [{"type": "text", "text": c}]
    return [b for b in c if isinstance(b, dict)] if isinstance(c, list) else []


def is_human_prompt(o):
    """A 'user' record is a real human prompt only if it is not a tool_result, not meta,
    not a sidechain (subagent), and not a slash-command/system echo. Verify locally:
    newer versions also carry origin.kind == 'human' / turnOrigin == 'human'."""
    if o.get("type") != "user" or o.get("isSidechain") or o.get("isMeta") or o.get("isCompactSummary"):
        return False
    origin = o.get("origin")
    if isinstance(origin, dict) and origin.get("kind") not in (None, "human"):
        return False
    blocks = content_blocks(o.get("message"))
    if not blocks or any(b.get("type") == "tool_result" for b in blocks):
        return False
    text = " ".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
    if not text and not any(b.get("type") == "image" for b in blocks):
        return False
    return not text.startswith(NON_PROMPT_PREFIXES)


def is_agent_event(o):
    """Assistant output or a tool result: evidence the agent was working at this timestamp."""
    if o.get("type") == "assistant":
        return True
    return o.get("type") == "user" and any(b.get("type") == "tool_result" for b in content_blocks(o.get("message")))


def last_agent_ts(recs, lo, hi, default):
    """Timestamp of the last agent event in recs[lo:hi], else default."""
    for i in range(hi - 1, lo, -1):
        if is_agent_event(recs[i]):
            return ts(recs[i])
    return default


def prompt_text(o):
    return " ".join(b.get("text", "") for b in content_blocks(o.get("message")) if b.get("type") == "text").strip()


def parse_session(path, idle_min, split_min, keep_text):
    recs, unknown, bad = [], Counter(), 0
    title = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            if not isinstance(o, dict):
                continue
            t = o.get("type")
            if t == "ai-title" and o.get("aiTitle"):
                title = o["aiTitle"]
            elif t == "summary" and o.get("summary") and not title:   # older versions
                title = o["summary"]
            if t not in ("user", "assistant", "system", "attachment"):
                unknown[t] += 1
            if o.get("isSidechain"):          # subagent records inline (older versions)
                continue
            if ts(o) is not None:
                recs.append(o)
    if not recs:
        return None, []
    recs.sort(key=ts)

    sid = next((r.get("sessionId") for r in recs if r.get("sessionId")), os.path.basename(path)[:-6])
    meta = {k: next((r.get(k) for r in recs if r.get(k)), "") for k in ("cwd", "gitBranch", "version", "entrypoint")}

    # token + tool stats (dedupe usage by message.id: one API message is split across records)
    seen_msg, models, tools = set(), Counter(), Counter()
    tok = Counter()
    files_edited, git_commits = set(), 0
    for r in recs:
        if r.get("type") != "assistant":
            continue
        m = r.get("message") or {}
        mid = m.get("id") or r.get("requestId") or r.get("uuid")
        if mid not in seen_msg:
            seen_msg.add(mid)
            if m.get("model"):
                models[m["model"]] += 1
            u = m.get("usage") or {}
            for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
                if isinstance(u.get(k), (int, float)):
                    tok[k] += u[k]
        for b in content_blocks(m):
            if b.get("type") == "tool_use":
                name = b.get("name", "?")
                tools[name] += 1
                inp = b.get("input") or {}
                if name in EDIT_TOOLS and isinstance(inp, dict):
                    fp = inp.get("file_path") or inp.get("notebook_path")
                    if fp:
                        files_edited.add(fp)
                if name in ("Bash", "PowerShell") and isinstance(inp, dict) and re.search(r"\bgit\s+commit\b", str(inp.get("command", ""))):
                    git_commits += 1

    # turns: each human prompt opens a turn; turn ends at last non-human record before next prompt
    prompts = [i for i, r in enumerate(recs) if is_human_prompt(r)]
    agent_s = human_s = idle_s = 0.0
    seg_bounds, cur_start = [], 0
    for n, pi in enumerate(prompts):
        nxt = prompts[n + 1] if n + 1 < len(prompts) else len(recs)
        t0 = ts(recs[pi])
        t_end = last_agent_ts(recs, pi, nxt, t0)
        agent_s += max(0.0, (t_end - t0).total_seconds())
        if nxt < len(recs):
            gap = (ts(recs[nxt]) - t_end).total_seconds()
            if gap <= idle_min * 60:
                human_s += max(0.0, gap)
            else:
                idle_s += gap
            if gap > split_min * 60:
                seg_bounds.append((cur_start, n))
                cur_start = n + 1
    if prompts:
        seg_bounds.append((cur_start, len(prompts) - 1))

    first, last = ts(recs[0]), ts(recs[-1])
    first_prompt = prompt_text(recs[prompts[0]]) if prompts else ""
    session = {
        "session_id": sid, "file": path, "project_dir": os.path.basename(os.path.dirname(path)),
        "title": title or "", **meta,
        "start_utc": first.isoformat(), "end_utc": last.isoformat(),
        "wall_min": round((last - first).total_seconds() / 60, 1),
        "active_min": round((agent_s + human_s) / 60, 1),
        "agent_min": round(agent_s / 60, 1), "human_min": round(human_s / 60, 1),
        "idle_min": round(idle_s / 60, 1),
        "n_prompts": len(prompts), "n_segments": len(seg_bounds),
        "n_api_msgs": len(seen_msg), "models": ";".join(f"{k}:{v}" for k, v in models.most_common()),
        "tool_calls": sum(tools.values()), "top_tools": ";".join(f"{k}:{v}" for k, v in tools.most_common(6)),
        "files_edited": len(files_edited), "git_commit_cmds": git_commits,
        "subagent_files": len(glob.glob(os.path.join(path[:-6], "subagents", "*.jsonl"))),
        **{k: int(v) for k, v in tok.items()},
        "bad_lines": bad, "unknown_types": ";".join(f"{k}:{v}" for k, v in unknown.items()),
        "first_prompt": first_prompt[:500] if keep_text else "",
    }

    segments = []
    for k, (a, b) in enumerate(seg_bounds):
        pa, pb = prompts[a], prompts[b]  # first / last prompt index of the segment
        hi = prompts[b + 1] if b + 1 < len(prompts) else len(recs)
        s_t0 = ts(recs[pa])
        s_t1 = last_agent_ts(recs, pb, hi, ts(recs[pb]))
        segments.append({
            "session_id": sid, "segment": k + 1, "start_utc": s_t0.isoformat(), "end_utc": s_t1.isoformat(),
            "span_min": round((s_t1 - s_t0).total_seconds() / 60, 1), "n_prompts": b - a + 1,
            "first_prompt": prompt_text(recs[pa])[:300] if keep_text else "",
        })
    return session, segments


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude") + "/projects"))
    ap.add_argument("--idle", type=float, default=15, help="human gap (min) above which time counts as idle")
    ap.add_argument("--split", type=float, default=45, help="human gap (min) that starts a new segment")
    ap.add_argument("--out", default="sessions.csv")
    ap.add_argument("--segments", default="segments.csv")
    ap.add_argument("--no-text", action="store_true", help="omit prompt text (privacy)")
    a = ap.parse_args()

    files = [p for p in glob.glob(os.path.join(os.path.expanduser(a.root), "*", "*.jsonl"))]
    sessions, segs = [], []
    for p in sorted(files):
        try:
            s, sg = parse_session(p, a.idle, a.split, not a.no_text)
        except Exception as e:  # never die on one bad file
            print(f"WARN {p}: {e}", file=sys.stderr)
            continue
        if s:
            sessions.append(s)
            segs.extend(sg)
    for path, rows in ((a.out, sessions), (a.segments, segs)):
        if not rows:
            continue
        cols = list(dict.fromkeys(k for r in rows for k in r))
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
    print(f"{len(sessions)} sessions, {len(segs)} segments -> {a.out}, {a.segments}", file=sys.stderr)


if __name__ == "__main__":
    main()
