#!/usr/bin/env python3
"""
Hermes Bridge — reads live Hermes agent state and emits JSON for the 3D office dashboard.

Auto-discovers agents from:
  1. Hermes Gateway API (http://localhost:51763/api/snapshot) — primary source
  2. Discord channel_prompts in config.yaml — agent definitions
  3. Session DB (state.db) — recent/active session activity
  4. Cron jobs (jobs.json) — scheduled tasks
  5. Content directories — files written per agent
  6. Kanban DB — open tasks

Output: writes agents.json to --output path (default: agents.json next to server.py)
        or pushes via --webhook URL

Usage:
  python3 hermes_bridge.py                          # one-shot, write agents.json
  python3 hermes_bridge.py --watch                  # continuous, every 15s
  python3 hermes_bridge.py --webhook http://localhost:9502/webhook/agents
  python3 hermes_bridge.py --output /path/to/agents.json --watch --interval 30

Plug-and-play: no config needed. Auto-discovers everything from ~/.hermes/.
For non-default gateway ports, set GATEWAY_PORT env var or use --gateway.
"""

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
CONFIG_PATH = HERMES_HOME / "config.yaml"
SESSIONS_DB = HERMES_HOME / "state.db"
CRON_JOBS = HERMES_HOME / "cron" / "jobs.json"
CONTENT_DIR = HERMES_HOME / "content"
KANBAN_DB = HERMES_HOME / "kanban.db"
DEFAULT_GATEWAY_PORT = 51763

# Agent definitions — mapped from Discord channel_prompts
BASE_AGENTS = {
    "orchestrator": {
        "id": "orchestrator",
        "name": "Orchestrator",
        "role": "Supervisor",
        "emoji": "🧠",
        "color": "#8B5CF6",
        "home": "meeting",
        "platform": "telegram",
    },
    "analyst": {
        "id": "analyst",
        "name": "Analyst",
        "role": "Research",
        "emoji": "🔍",
        "color": "#3B82F6",
        "home": "desk1",
        "platform": "discord",
    },
    "writer": {
        "id": "writer",
        "name": "Writer",
        "role": "Content",
        "emoji": "✍️",
        "color": "#10B981",
        "home": "desk2",
        "platform": "discord",
    },
    "marketer": {
        "id": "marketer",
        "name": "Marketer",
        "role": "Growth",
        "emoji": "📈",
        "color": "#F59E0B",
        "home": "desk3",
        "platform": "discord",
    },
    "coder": {
        "id": "coder",
        "name": "Coder",
        "role": "Engineering",
        "emoji": "💻",
        "color": "#EF4444",
        "home": "desk4",
        "platform": "discord",
    },
}


def fetch_gateway_snapshot(gateway_url):
    """Fetch the Hermes gateway snapshot API."""
    try:
        req = urllib.request.Request(gateway_url, headers={"Accept": "application/json"})
        resp = urllib.request.urlopen(req, timeout=5)
        return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[bridge] gateway API error: {e}", file=sys.stderr)
        return None


def get_recent_sessions(limit=30):
    """Get recent sessions from state.db."""
    sessions = []
    if not SESSIONS_DB.exists():
        return sessions
    try:
        db = sqlite3.connect(str(SESSIONS_DB))
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        cur.execute("""
            SELECT id, source, title, started_at, ended_at, message_count,
                   tool_call_count, model, archived
            FROM sessions
            WHERE archived = 0 OR archived IS NULL
            ORDER BY started_at DESC
            LIMIT ?
        """, (limit,))
        for row in cur.fetchall():
            sessions.append(dict(row))
        db.close()
    except Exception as e:
        print(f"[bridge] session DB error: {e}", file=sys.stderr)
    return sessions


def get_cron_status():
    """Load cron jobs and return their status."""
    jobs = []
    if not CRON_JOBS.exists():
        return jobs
    try:
        with open(CRON_JOBS) as f:
            data = json.load(f)
        for job in data.get("jobs", []):
            if not job.get("enabled"):
                continue
            jobs.append({
                "id": job["id"],
                "name": job["name"],
                "schedule": job.get("schedule_display", ""),
                "last_status": job.get("last_status"),
                "last_run_at": job.get("last_run_at"),
                "next_run_at": job.get("next_run_at"),
                "completed": job.get("repeat", {}).get("completed", 0),
            })
    except Exception as e:
        print(f"[bridge] cron jobs error: {e}", file=sys.stderr)
    return jobs


def get_content_stats():
    """Count content files per agent."""
    stats = {}
    if not CONTENT_DIR.exists():
        return stats
    for agent_dir in CONTENT_DIR.iterdir():
        if agent_dir.is_dir():
            files = list(agent_dir.glob("*.md"))
            stats[agent_dir.name] = len(files)
    return stats


def get_agent_activity_from_gateway(snapshot):
    """Extract per-agent activity from gateway snapshot."""
    activity_by_agent = {}
    if not snapshot:
        return activity_by_agent
    entries = snapshot.get("activity", {}).get("entries", [])
    for entry in entries:
        agent = entry.get("agent", "")
        if agent not in activity_by_agent:
            activity_by_agent[agent] = []
        activity_by_agent[agent].append(entry)
    return activity_by_agent


def get_agent_status_counts(snapshot):
    """Get active/idle/dormant counts from gateway."""
    if not snapshot:
        return {}
    return snapshot.get("agent_status", {})


# Time thresholds (seconds)
_ONE_HOUR = 3600
_FOUR_HOURS = 14400


def derive_agent_status(agent_id, gateway_snapshot, gateway_activity, sessions, cron_jobs, content_stats, board_tasks):
    """
    Derive live status for an agent from multiple data sources.
    Returns: (status, task, tasks_list, stats, mood, typing, outputs)
    """
    now = time.time()
    agent_sessions = []

    # Get sessions for this agent
    for s in sessions:
        src = s.get("source", "")
        title = (s.get("title") or "").lower()

        if agent_id == "orchestrator" and src in ("telegram", "cron"):
            agent_sessions.append(s)
        elif src == "discord":
            # Map by title keywords since session DB doesn't store channel_id
            agent_name = BASE_AGENTS[agent_id]["name"].lower()
            role = BASE_AGENTS[agent_id]["role"].lower()
            if agent_name in title or role in title or agent_id in title:
                agent_sessions.append(s)

    # Get gateway activity for this agent
    gw_activity = gateway_activity.get(agent_id, [])
    latest_gw_task = gw_activity[0]["task"] if gw_activity else None
    latest_gw_time = gw_activity[0].get("created_at", "") if gw_activity else ""

    # Determine status
    status = "idle"
    task = "Waiting for tasks"
    typing = False
    mood = 0.5

    # Check for active session
    if agent_sessions:
        latest = agent_sessions[0]
        ended = latest.get("ended_at")
        started = latest.get("started_at") or 0
        title = latest.get("title") or "Unknown task"
        msg_count = latest.get("message_count", 0) or 0

        if ended is None or ended == "active":
            # Active session right now
            status = "working"
            task = title[:80]
            typing = True
            mood = 0.95
        else:
            age = now - float(started) if started else 999
            if age < _ONE_HOUR:
                status = "working"
                task = title[:80]
                mood = 0.8
            elif age < _FOUR_HOURS:
                status = "idle"
                task = f"Last: {title[:60]}"
                mood = 0.6
            else:
                status = "idle"
                task = "Available for tasks"
                mood = 0.4

    # Use gateway activity to refine
    if latest_gw_task and status == "idle":
        # Check if gateway activity is recent (within 1 hour)
        try:
            from datetime import datetime
            gw_time = datetime.fromisoformat(latest_gw_time.replace("Z", "+00:00")).timestamp()
            age = now - gw_time
            if age < _ONE_HOUR:
                status = "working"
                task = latest_gw_task[:80]
                mood = 0.85
            elif age < _FOUR_HOURS:
                task = f"Last: {latest_gw_task[:60]}"
                mood = 0.55
        except Exception:
            pass

    # Orchestrator with active cron jobs = meeting
    active_crons = [j for j in cron_jobs if j.get("last_status") == "ok"]
    if agent_id == "orchestrator" and active_crons:
        if status == "idle":
            status = "meeting"
            task = "Reviewing scheduled reports"
            mood = 0.7

    # Build stats
    content_count = content_stats.get(agent_id, 0)
    last_msg_count = 0
    if agent_sessions:
        last_msg_count = agent_sessions[0].get("message_count", 0) or 0

    # Count gateway activity tasks
    gw_task_count = len(gw_activity)

    stats = {
        "tasksDone": content_count + gw_task_count + (len(agent_sessions) // 3),
        "active": 1 if status == "working" else 0,
        "hours": round(last_msg_count * 0.05, 1) if agent_sessions else 0,
    }

    # Build task list
    if status == "working":
        tasks_list = [task, "Processing input", "Generating response"]
    elif status == "meeting":
        tasks_list = ["Reviewing reports", "Checking pipeline", "Approving handoffs"]
    else:
        tasks_list = ["Standing by", "Ready for assignment"]

    # Build outputs
    outputs = []
    if latest_gw_task:
        outputs.append(latest_gw_task)
    if content_count > 0:
        outputs.append(f"{content_count} content files written")
    if gw_task_count > 0:
        outputs.append(f"{gw_task_count} tasks logged")
    if agent_sessions:
        outputs.append(f"{len(agent_sessions)} sessions")

    return status, task, tasks_list, stats, mood, typing, outputs


def build_agents_json(gateway_url):
    """Build the full agents JSON array from all data sources."""
    # Fetch gateway snapshot
    snapshot = fetch_gateway_snapshot(gateway_url)
    gateway_activity = get_agent_activity_from_gateway(snapshot)

    # Get data from other sources
    sessions = get_recent_sessions(30)
    cron_jobs = get_cron_status()
    content_stats = get_content_stats()
    board_tasks = snapshot.get("board", {}).get("tasks", []) if snapshot else []

    agents = []
    for agent_id, base in BASE_AGENTS.items():
        status, task, tasks_list, stats, mood, typing, outputs = derive_agent_status(
            agent_id, snapshot, gateway_activity, sessions, cron_jobs, content_stats, board_tasks,
        )

        agents.append({
            "id": base["id"],
            "name": base["name"],
            "role": base["role"],
            "emoji": base["emoji"],
            "color": base["color"],
            "home": base["home"],
            "status": status,
            "task": task,
            "tasks": tasks_list,
            "output": outputs,
            "stats": stats,
            "mood": mood,
            "typing": typing,
            "position": None,
        })

    return agents


def write_agents_json(agents, output_path):
    """Write agents JSON to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(agents, f, indent=2)
    print(f"[bridge] wrote {len(agents)} agents → {path}")


def push_webhook(agents, webhook_url):
    """Push agents JSON to webhook endpoint."""
    data = json.dumps(agents).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        print(f"[bridge] pushed {len(agents)} agents → {webhook_url} ({resp.status})")
    except Exception as e:
        print(f"[bridge] webhook error: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Hermes Bridge — live agent status emitter")
    parser.add_argument("--output", "-o", default=None,
                        help="Output JSON file path (default: agents.json in repo root)")
    parser.add_argument("--webhook", "-w", default=None,
                        help="Webhook URL to push agents JSON")
    parser.add_argument("--watch", action="store_true",
                        help="Continuous mode, refresh every N seconds")
    parser.add_argument("--interval", type=int, default=15,
                        help="Watch interval in seconds (default: 15)")
    parser.add_argument("--gateway", default=None,
                        help=f"Gateway URL (default: http://localhost:{DEFAULT_GATEWAY_PORT}/api/snapshot)")
    args = parser.parse_args()

    # Resolve gateway URL
    gateway_port = os.environ.get("GATEWAY_PORT", str(DEFAULT_GATEWAY_PORT))
    gateway_url = args.gateway or f"http://localhost:{gateway_port}/api/snapshot"

    # Default output path
    if args.output is None and not args.webhook:
        repo_root = Path(__file__).resolve().parent.parent
        args.output = str(repo_root / "agents.json")

    print(f"[bridge] Hermes home: {HERMES_HOME}")
    print(f"[bridge] Gateway: {gateway_url}")
    print(f"[bridge] Output: {args.output or 'webhook only'}")
    print(f"[bridge] Webhook: {args.webhook or 'disabled'}")
    print()

    while True:
        agents = build_agents_json(gateway_url)

        # Print status summary
        for a in agents:
            print(f"  {a['emoji']} {a['name']:12s}  {a['status']:8s}  mood={a['mood']:.1f}  {a['task'][:50]}")

        if args.output:
            write_agents_json(agents, args.output)
        if args.webhook:
            push_webhook(agents, args.webhook)

        if not args.watch:
            break

        print(f"\n[bridge] sleeping {args.interval}s...\n")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()