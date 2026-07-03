#!/usr/bin/env python3
"""
Example Hermes agent status emitter.

This script writes agents.json every few seconds so the dashboard reflects
live state. In a real setup, replace the fake logic with reads from your
Hermes session store, cron jobs, or webhook receiver.

Run:
    python3 scripts/example_agent_emitter.py

It updates the agents.json file configured by AGENTS_JSON_PATH (default ./agents.json).
"""
import json
import os
import random
import time
from pathlib import Path

AGENTS_JSON_PATH = os.environ.get("AGENTS_JSON_PATH", "./agents.json")

STATUSES = ["idle", "walking", "working", "meeting"]
TASKS = {
    "orchestrator": ["Reviewing pipeline", "Coordinating agents", "Approving handoffs", "Standup moderation"],
    "analyst": ["Market research", "Data synthesis", "Trend analysis", "Competitor scrape"],
    "writer": ["Drafting article", "Editing copy", "SEO optimization", "Thread hook"],
    "marketer": ["Campaign planning", "Audience targeting", "Post scheduling", "Launch brief"],
    "coder": ["Feature build", "Code review", "Deploy checks", "API wiring"],
}


def load_agents():
    example = Path(__file__).parent.parent / "agents.json.example"
    path = Path(AGENTS_JSON_PATH)
    if path.exists():
        with path.open() as f:
            return json.load(f).get("agents", [])
    if example.exists():
        with example.open() as f:
            return json.load(f).get("agents", [])
    return []


def tick(agents):
    for a in agents:
        if random.random() < 0.4:
            a["status"] = random.choice(STATUSES)
            a["task"] = random.choice(TASKS.get(a["id"], ["Working"]))
            a["typing"] = a["status"] == "working"
            stats = a.setdefault("stats", {})
            stats["hours"] = round(float(stats.get("hours", 0)) + random.uniform(0, 0.05), 2)
    return agents


def main():
    agents = load_agents()
    print(f"Emitting live agent state to {AGENTS_JSON_PATH}")
    while True:
        agents = tick(agents)
        path = Path(AGENTS_JSON_PATH)
        path.write_text(json.dumps({"agents": agents}, indent=2))
        print(f"Updated {len(agents)} agents at {time.strftime('%H:%M:%S')}")
        time.sleep(5)


if __name__ == "__main__":
    main()
