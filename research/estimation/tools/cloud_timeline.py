#!/usr/bin/env python3
"""Turn saved list_events dumps into a compact, deduped session timeline + time stats.

Usage:
  python3 timeline.py add  <session_id> <dump_file> [<dump_file> ...]   # merge pages into store
  python3 timeline.py show <session_id> [--max-chars N]                 # print condensed timeline
  python3 timeline.py stats <session_id> [--idle-min 15]                # print time stats JSON

Store: pilot/store/<session_id>.jsonl (one condensed event per line, deduped by uuid).
Dump files are the text files the list_events tool saved (wrapped in <other-session> tags)
or plain JSON with {"ccr":{"data":[...]}} / {"data":[...]}.
"""
import json, os, sys, re
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "store")
os.makedirs(STORE, exist_ok=True)


def load_dump(path):
    t = open(path, encoding="utf-8").read()
    i = t.find("{")
    j = t.rfind("</other-session")
    body = t[i:j] if j > i else t[i:]
    body = body.strip()
    d = json.loads(body, strict=False)
    if "ccr" in d:
        d = d["ccr"]
    return d.get("data", [])


def ts_of(e, inner):
    return inner.get("timestamp") or e.get("created_at")


def text_of(content):
    """Return (typed_text, tool_results_count, tool_uses list)."""
    typed, n_res, uses = [], 0, []
    if isinstance(content, str):
        return content, 0, []
    for c in content or []:
        if not isinstance(c, dict):
            continue
        ty = c.get("type")
        if ty == "text":
            typed.append(c.get("text", ""))
        elif ty == "tool_result":
            n_res += 1
        elif ty == "tool_use":
            inp = c.get("input") or {}
            hint = ""
            for k in ("description", "command", "file_path", "pattern", "prompt", "url", "query"):
                if k in inp and isinstance(inp[k], str):
                    hint = inp[k]
                    break
            uses.append({"name": c.get("name"), "hint": hint[:160]})
    return "\n".join(typed), n_res, uses


def condense(e):
    for kind in ("user", "assistant", "result", "system"):
        if kind in e:
            inner = e[kind].get("internal_anthropic_catchall", e[kind]) or {}
            uuid = e[kind].get("uuid") or inner.get("uuid") or e.get("uuid")
            rec = {"uuid": uuid, "kind": kind, "ts": ts_of(e, inner)}
            if kind in ("user", "assistant"):
                msg = inner.get("message") or {}
                typed, n_res, uses = text_of(msg.get("content"))
                rec["text"] = typed[:4000]
                if n_res:
                    rec["tool_results"] = n_res
                if uses:
                    rec["tool_uses"] = uses
                if kind == "assistant":
                    rec["model"] = msg.get("model")
                    u = msg.get("usage") or {}
                    rec["out_tok"] = u.get("output_tokens")
                if inner.get("parent_tool_use_id"):
                    rec["sub"] = True  # subagent traffic
                if kind == "user" and inner.get("isSynthetic"):
                    rec["synthetic"] = True
            elif kind == "result":
                rec.update({k: inner.get(k) for k in ("num_turns", "duration_ms", "subtype", "is_error", "terminal_reason")})
            else:
                rec["subtype"] = inner.get("subtype")
            return rec
    return None


def store_path(sid):
    return os.path.join(STORE, sid + ".jsonl")


def load_store(sid):
    p = store_path(sid)
    out = {}
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            out[r["uuid"]] = r
    return out


def cmd_add(sid, files):
    recs = load_store(sid)
    before = len(recs)
    for f in files:
        for e in load_dump(f):
            r = condense(e)
            if r and r.get("uuid"):
                recs[r["uuid"]] = r
    rows = sorted(recs.values(), key=lambda r: r.get("ts") or "")
    with open(store_path(sid), "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{sid}: {before} -> {len(rows)} events; span {rows[0]['ts'] if rows else '-'} .. {rows[-1]['ts'] if rows else '-'}")


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


NON_HUMAN_PREFIXES = ("<task-notification", "<system-reminder", "<command-", "<local-command",
                      "[SYSTEM NOTIFICATION", "[Request interrupted", "<agent-message", "<webhook")


def is_human(r):
    if r["kind"] != "user" or not r.get("text") or r.get("tool_results") or r.get("sub") or r.get("synthetic"):
        return False
    return not r["text"].lstrip().startswith(NON_HUMAN_PREFIXES)


def cmd_show(sid, max_chars=600):
    for r in sorted(load_store(sid).values(), key=lambda r: r.get("ts") or ""):
        if r.get("sub"):
            continue
        ts = (r.get("ts") or "")[5:19]
        if is_human(r):
            print(f"\n[{ts}] HUMAN: {r['text'][:max_chars]}")
        elif r["kind"] == "assistant":
            if r.get("text"):
                print(f"[{ts}] CLAUDE: {r['text'][:max_chars]}")
            for u in r.get("tool_uses", []):
                print(f"[{ts}]   tool {u['name']}: {u['hint'][:120]}")
        elif r["kind"] == "result":
            print(f"[{ts}] --- turn end ({r.get('num_turns')} steps, {r.get('subtype')})")


def cmd_stats(sid, idle_min=15):
    rows = [r for r in sorted(load_store(sid).values(), key=lambda r: r.get("ts") or "") if r.get("ts")]
    if not rows:
        print(json.dumps({"session": sid, "error": "no events"}))
        return
    t = [parse_ts(r["ts"]) for r in rows]
    gaps = [(t[i + 1] - t[i]).total_seconds() for i in range(len(t) - 1)]
    idle = idle_min * 60
    active = sum(g for g in gaps if g <= idle)
    # human vs agent: time from a turn end (result / last assistant) to next human msg = human time
    human_secs, agent_secs, n_human = 0.0, 0.0, 0
    last_kind, last_t = None, t[0]
    for r, tt in zip(rows, t):
        g = (tt - last_t).total_seconds()
        if g <= idle:
            if is_human(r):
                human_secs += g
            else:
                agent_secs += g
        if is_human(r):
            n_human += 1
        last_t = tt
    out = {
        "session": sid,
        "first": rows[0]["ts"], "last": rows[-1]["ts"],
        "wall_min": round((t[-1] - t[0]).total_seconds() / 60, 1),
        f"active_min_idle{idle_min}": round(active / 60, 1),
        "agent_min": round(agent_secs / 60, 1),
        "human_min": round(human_secs / 60, 1),
        "human_msgs": n_human,
        "turns": sum(1 for r in rows if r["kind"] == "result"),
        "idle_breaks": sum(1 for g in gaps if g > idle),
        "events": len(rows),
    }
    print(json.dumps(out))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    if a[0] == "add":
        cmd_add(a[1], a[2:])
    elif a[0] == "addraw":
        # lines of {"uuid","kind","ts","text"} written by hand for small inline pages
        recs = load_store(a[1])
        for line in open(a[2], encoding="utf-8"):
            line = line.strip()
            if line:
                r = json.loads(line); recs[r["uuid"]] = r
        rows = sorted(recs.values(), key=lambda r: r.get("ts") or "")
        with open(store_path(a[1]), "w", encoding="utf-8") as fh:
            for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{a[1]}: now {len(rows)} events")
    elif a[0] == "show":
        mc = int(a[a.index("--max-chars") + 1]) if "--max-chars" in a else 600
        cmd_show(a[1], mc)
    elif a[0] == "stats":
        im = int(a[a.index("--idle-min") + 1]) if "--idle-min" in a else 15
        cmd_stats(a[1], im)
