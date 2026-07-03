#!/usr/bin/env python3
"""
Hermes 3D Office Dashboard Server

Serves the static 3D office dashboard and provides a live agent-state API.
Three wiring modes are supported out of the box:

1. Demo mode            - Auto-generated sample agents (default).
2. Hermes status API    - Poll HERMES_AGENT_API for live agents.
3. Static JSON drop     - Serve AGENTS_JSON_PATH if it exists.
4. Webhook push         - Receive updates on POST /webhook/agents.

Environment variables (see .env.example):
    PORT                  Server port (default 9502)
    HOST                  Bind address (default 0.0.0.0)
    HERMES_AGENT_API      URL to Hermes GET /api/agents/status endpoint
    AGENTS_JSON_PATH      Path to agents.json file drop
    POLL_INTERVAL_SECONDS Polling interval for HERMES_AGENT_API
    ENABLE_SSE            Enable Server-Sent Events for live browser updates
"""
import http.server
import socketserver
import os
import json
import time
import threading
import urllib.request
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus

PORT = int(os.environ.get("PORT", "9502"))
HOST = os.environ.get("HOST", "0.0.0.0")
HERMES_AGENT_API = os.environ.get("HERMES_AGENT_API", "").strip()
AGENTS_JSON_PATH = os.environ.get("AGENTS_JSON_PATH", "").strip() or str(Path(__file__).parent / "agents.json")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL_SECONDS", "5"))
ENABLE_SSE = os.environ.get("ENABLE_SSE", "true").lower() in ("1", "true", "yes")
DEMO_MODE = not (HERMES_AGENT_API or AGENTS_JSON_PATH)

DIRECTORY = Path(__file__).parent / "public"
ROOT = Path(__file__).parent

# Demo agents used when no Hermes source is configured
DEMO_AGENTS = [
    {
        "id": "orchestrator",
        "name": "Orchestrator",
        "role": "Supervisor",
        "emoji": "🧠",
        "color": "#8B5CF6",
        "home": "meeting",
        "status": "meeting",
        "task": "Coordinating daily standup",
        "tasks": ["Reviewing pipeline", "Coordinating agents", "Approving handoffs"],
        "output": ["Daily brief issued", "Pipeline updated"],
        "stats": {"tasksDone": 34, "active": 5, "hours": 6.2},
        "mood": 0.9,
        "typing": False,
    },
    {
        "id": "analyst",
        "name": "Analyst",
        "role": "Research",
        "emoji": "📊",
        "color": "#3B82F6",
        "home": "left",
        "status": "working",
        "task": "Market research in progress",
        "tasks": ["Market research", "Data synthesis", "Trend analysis"],
        "output": ["Competitor report v1", "Keyword research"],
        "stats": {"tasksDone": 18, "active": 3, "hours": 4.5},
        "mood": 0.75,
        "typing": True,
    },
    {
        "id": "writer",
        "name": "Writer",
        "role": "Content",
        "emoji": "✍️",
        "color": "#EC4899",
        "home": "center",
        "status": "working",
        "task": "Drafting launch blog post",
        "tasks": ["Drafting article", "Editing copy", "SEO optimization"],
        "output": ["Blog post v2", "Thread draft"],
        "stats": {"tasksDone": 21, "active": 2, "hours": 5.1},
        "mood": 0.8,
        "typing": True,
    },
    {
        "id": "marketer",
        "name": "Marketer",
        "role": "Growth",
        "emoji": "📢",
        "color": "#F59E0B",
        "home": "right",
        "status": "walking",
        "task": "Walking to meeting room",
        "tasks": ["Campaign planning", "Audience targeting", "Post scheduling"],
        "output": ["Launch plan", "Campaign brief"],
        "stats": {"tasksDone": 15, "active": 2, "hours": 3.8},
        "mood": 0.85,
        "typing": False,
    },
    {
        "id": "coder",
        "name": "Coder",
        "role": "Dev",
        "emoji": "💻",
        "color": "#10B981",
        "home": "right2",
        "status": "working",
        "task": "Building API endpoint",
        "tasks": ["Feature build", "Code review", "Deploy checks"],
        "output": ["API endpoint merged", "Bug fix deployed"],
        "stats": {"tasksDone": 29, "active": 4, "hours": 6.7},
        "mood": 0.7,
        "typing": True,
    },
]

# Thread-safe shared state
state_lock = threading.Lock()
latest_agents = list(DEMO_AGENTS)
sse_clients = []
sse_lock = threading.Lock()
last_poll = 0


def _read_agents_json():
    try:
        path = Path(AGENTS_JSON_PATH)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
                if isinstance(data, dict) and "agents" in data:
                    return data["agents"]
    except Exception as e:
        print(f"[agents.json] read failed: {e}")
    return None


def _fetch_hermes_agents():
    if not HERMES_AGENT_API:
        return None
    try:
        req = urllib.request.Request(
            HERMES_AGENT_API,
            headers={"Accept": "application/json", "User-Agent": "hermes-3d-office/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data.get("agents", data.get("results", []))
    except Exception as e:
        print(f"[Hermes API] poll failed: {e}")
    return None


def _normalize_agent(agent):
    """Ensure every agent has the keys the dashboard needs."""
    defaults = {
        "id": str(agent.get("id", "agent")),
        "name": agent.get("name", "Agent"),
        "role": agent.get("role", "Worker"),
        "emoji": agent.get("emoji", "🤖"),
        "color": agent.get("color", "#8B5CF6"),
        "home": agent.get("home", "center"),
        "status": agent.get("status", "idle"),
        "task": agent.get("task", agent.get("status", "idle")),
        "tasks": agent.get("tasks", []),
        "output": agent.get("output", []),
        "stats": agent.get("stats", {"tasksDone": 0, "active": 0, "hours": 0}),
        "mood": agent.get("mood", 0.8),
        "typing": agent.get("typing", False),
        "position": agent.get("position", None),
    }
    return defaults


def refresh_agents():
    """Refresh latest_agents from API, file, or demo fallback."""
    global latest_agents, last_poll

    data = None
    if HERMES_AGENT_API:
        data = _fetch_hermes_agents()
    if data is None:
        data = _read_agents_json()
    if data is None:
        data = list(DEMO_AGENTS)

    normalized = [_normalize_agent(a) for a in data]

    with state_lock:
        latest_agents = normalized
        last_poll = time.time()

    _broadcast_sse(json.dumps({"agents": normalized}))


def _broadcast_sse(payload):
    if not ENABLE_SSE:
        return
    dead = []
    with sse_lock:
        for q in sse_clients:
            try:
                q.append(payload)
            except Exception:
                dead.append(q)
        for q in dead:
            if q in sse_clients:
                sse_clients.remove(q)


def _polling_loop():
    while True:
        refresh_agents()
        time.sleep(POLL_INTERVAL)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def log_message(self, format, *args):
        # Quiet logs; remove if you want access logging
        pass

    def _send_json(self, data, status=HTTPStatus.OK):
        body = json.dumps(data).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/agents":
            with state_lock:
                agents = list(latest_agents)
            self._send_json(agents)
            return

        if path == "/api/config":
            self._send_json({
                "mode": "hermes_api" if HERMES_AGENT_API else ("json_file" if Path(AGENTS_JSON_PATH).exists() else "demo"),
                "poll_interval_seconds": POLL_INTERVAL,
                "enable_sse": ENABLE_SSE,
                "hermes_agent_api": "[REDACTED]" if HERMES_AGENT_API else None,
            })
            return

        if path == "/events":
            self._handle_sse()
            return

        if path in ("", "/"):
            self.path = "/index.html"
            return super().do_GET()

        try:
            return super().do_GET()
        except (BrokenPipeError, ConnectionResetError):
            return

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/webhook/agents":
            try:
                body = self._read_json_body()
                agents = body.get("agents", body if isinstance(body, list) else [])
                normalized = [_normalize_agent(a) for a in agents]
                with state_lock:
                    latest_agents = normalized
                _broadcast_sse(json.dumps({"agents": normalized}))
                self._send_json({"ok": True, "count": len(normalized)})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, HTTPStatus.BAD_REQUEST)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _handle_sse(self):
        import queue
        q = queue.Queue()
        with sse_lock:
            sse_clients.append(q)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        try:
            # Send current state immediately
            with state_lock:
                snapshot = json.dumps({"agents": list(latest_agents)})
            self.wfile.write(f"data: {snapshot}\n\n".encode("utf-8"))
            self.wfile.flush()
            while True:
                try:
                    payload = q.get(timeout=30)
                    self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": keep-alive\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with sse_lock:
                if q in sse_clients:
                    sse_clients.remove(q)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main():
    refresh_agents()
    threading.Thread(target=_polling_loop, daemon=True).start()

    os.chdir(DIRECTORY)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        mode = "DEMO" if DEMO_MODE else ("Hermes API" if HERMES_AGENT_API else "agents.json file")
        print(f"🖥  Hermes 3D Office running at http://{HOST}:{PORT}")
        print(f"🔗 Tailscale URL: http://100.66.142.21:{PORT}")
        print(f"📡 Mode: {mode}")
        print(f"📊 Agent API: http://{HOST}:{PORT}/api/agents")
        print(f"🔔 Webhook: POST http://{HOST}:{PORT}/webhook/agents")
        print(f"⚙️  Config: http://{HOST}:{PORT}/api/config")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
