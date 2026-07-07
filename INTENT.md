# INTENT.md — J1-PIPELINE Phase -1 (ORACLE)

**Repository:** `OneByJorah/VirtOffice`
**Analysis Date:** 2026-07-05
**Analyst:** J1-PIPELINE ORACLE (read-only)
**Status:** Intent Reconstructed

---

## What This System Does

**VirtOffice** is a real-time 3D virtual office visualization dashboard for AI agents running under the Hermes AgentOS platform. It renders an animated isometric office environment where agent avatars (Orchestrator, Analyst, Writer, Marketer, Coder) are shown working, walking, meeting, or idle — with live status updates, chat bubbles, and click-to-inspect detail panels.

### Technical Role

| Component | Technology | Role |
|-----------|-----------|------|
| Backend Server | Python 3 stdlib (`http.server`) | Serves static frontend, exposes REST API + SSE + webhook endpoints, polls Hermes Gateway for live agent state |
| Frontend | Three.js (r128, CDN) | 3D isometric office rendering with animated jointed agents, lighting, shadows, furniture, and UI overlay |
| Bridge Script | Python 3 (`scripts/hermes_bridge.py`) | Auto-discovers agents from Hermes Gateway API, Session DB, cron jobs, content directories, and Kanban; writes `agents.json` or pushes via webhook |
| Deployment | Docker + systemd | Containerized via Dockerfile/docker-compose, or installed as a systemd user service |

### Operational Role

The dashboard is a **visual observability layer** for Hermes AgentOS. It answers the question "what are my AI agents doing right now?" by providing:

- **Live agent status** — working, idle, meeting, walking, away, offline
- **Task visibility** — current task, task queue, recent outputs
- **Agent stats** — tasks completed, active hours, mood indicator
- **Real-time updates** — via Server-Sent Events (SSE), API polling, or webhook push
- **Interactive exploration** — click any agent to see details, zoom/rotate the office

It runs as a companion service alongside a Hermes AgentOS gateway, consuming its snapshot API. It can also run standalone in demo mode with pre-generated sample agents.

---

## Why This Was Built

### Real Problem

Hermes AgentOS orchestrates multiple AI subagents (Orchestrator, Analyst, Writer, Marketer, Coder) that work asynchronously across Telegram, Discord, and cron schedules. These agents produce output, run sessions, and change state — but there was **no visual interface** to see what they were doing. Operators had to check logs, session databases, and cron job status separately to understand agent activity. The system was functionally powerful but **observability-poor**: you couldn't glance at a screen and know which agents were busy, idle, or meeting.

### Why Existing Tools Were Insufficient

- **Hermes CLI / terminal logs** — Text-only, no spatial or simultaneous multi-agent view. Requires scrolling through session history.
- **Session DB queries** — Raw SQLite, no visualization. Requires manual queries to understand agent state.
- **Generic monitoring (Grafana/Prometheus)** — Overkill for agent state visualization. These tools track metrics (CPU, memory, requests), not semantic agent states like "working on market research" or "walking to meeting room."
- **Existing 3D office dashboards** — None were designed for AI agent observability. They lacked the agent-specific data model (status, task, mood, emoji, home position) and the Hermes integration patterns (gateway API, session DB, webhook).
- **Simple status boards** — Could show a list of agents and their status, but not the spatial, animated, "living office" experience that makes agent activity intuitively understandable at a glance.

### What Triggered Development

Development of the **Hermes AgentOS multi-agent system** created an immediate need for a visual observability layer. As the number of subagents grew (Orchestrator, Analyst, Writer, Marketer, Coder), the lack of a unified, glanceable status display became a bottleneck for operators. The initial commit (`5746e6b`, July 3, 2026) was titled *"feat: initial 3d office dashboard with hermes integration"* — the system was built from the start as a companion to Hermes, not as a standalone product.

### Ecosystem Fit

```
JorahOne / OneByJorah Ecosystem
│
├── Hermes AgentOS (core orchestration platform)
│   ├── Hermes Gateway API (agent lifecycle, snapshot, activity)
│   ├── Hermes Session DB (state.db — session history)
│   ├── Hermes Cron (jobs.json — scheduled tasks)
│   ├── Hermes Kanban (kanban.db — task board)
│   └── Hermes Content (content/ — agent output files)
│
├── VirtOffice ← YOU ARE HERE
│   └── Visual observability layer consuming all of the above
│
├── Other JorahOne repos (hermes-agent, etc.)
```

The 3D Office is a **consumer** of Hermes data sources. It does not produce agent state — it visualizes it. The bridge script (`scripts/hermes_bridge.py`) is the integration glue that reads from multiple Hermes data stores and emits the unified agent state JSON.

---

## Operational Classification

**Classification: BETA → PRODUCTION**

Evidence:
- **Docker support** — `Dockerfile` + `docker-compose.yml` with restart policy, volume mounts, env file
- **systemd service** — `hermes-office.service` with auto-restart, journal logging
- **CI/CD** — GitHub Actions CodeQL analysis (Python + JavaScript/TypeScript)
- **Dependabot** — Weekly updates for pip, npm, Docker, GitHub Actions
- **Security policy** — `SECURITY.md` with 90-day disclosure timeline, dedicated email
- **Community readiness** — `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, issue/PR templates
- **License** — MIT, copyright Jhonattan L. Jimenez
- **Health endpoints** — `/api/agents`, `/api/config`, `/events` (SSE), `/webhook/agents`
- **Graceful degradation** — Falls back to demo mode if no Hermes source configured
- **No tests** — No test files found. This is the primary gap for PRODUCTION classification.
- **Repo age** — 3 days old (18 commits). Very young but well-structured.

**Verdict:** BETA — production-ready in architecture and deployment tooling, but lacks test coverage and has minimal operational history.

---

## Key Architectural Decisions

1. **Zero external Python dependencies** — The server uses only Python stdlib (`http.server`, `json`, `threading`, `urllib.request`). This eliminates dependency management, reduces the attack surface, and makes the server trivially deployable. The `requirements.txt` is explicitly a placeholder.

2. **In-memory state with polling** — Agent state is held in a thread-safe global variable, refreshed by a background polling loop. No database, no persistence. This is appropriate for a visualization dashboard that doesn't need to survive restarts — it re-fetches from Hermes on startup.

3. **Three.js CDN (no build step)** — The frontend loads Three.js from CDN with no bundler, no npm, no build step. The entire frontend is a single `index.html` file (~2000 lines). This keeps deployment trivial but limits code organization.

4. **Multiple data source modes** — The server supports four modes (demo, Hermes API polling, static JSON file, webhook push) with automatic fallback. This makes it useful in development (demo), staging (file drop), and production (API + webhook) without config changes.

5. **Bridge script as integration layer** — Rather than embedding Hermes-specific logic in the server, the bridge script (`scripts/hermes_bridge.py`) is a separate process that reads from multiple Hermes data stores (Gateway API, Session DB, cron jobs, content directories, Kanban) and writes the unified `agents.json`. This separation of concerns keeps the server generic and the integration logic isolated.

6. **SSE for live updates** — Server-Sent Events over WebSocket-like polling. Simpler than WebSocket (no bidirectional protocol), supported natively by browsers, and sufficient for one-way agent state updates.

7. **Jointed agent avatars** — Agents have articulated bodies (upper/lower arms with elbow bend, separate head/torso/legs) rather than simple geometric shapes. This enables walking animations and makes the visualization more engaging, at the cost of rendering complexity.

8. **systemd user service** — The service file uses `%I` (instance template) pattern, making it deployable per-user without root. This aligns with Hermes's user-level deployment model.

---

## Repository Structure

```
VirtOffice/
├── README.md                    # Primary intent document — features, quick start, architecture
├── INTENT.md                    # ← THIS FILE (Phase -1 ORACLE output)
├── LICENSE                      # MIT, © Jhonattan L. Jimenez
├── .gitignore                   # Python/Docker/node common ignores
│
├── server.py                    # Backend HTTP server (Python stdlib, 369 lines)
├── requirements.txt             # Placeholder — no external deps
├── Dockerfile                   # python:3.11-slim container
├── docker-compose.yml           # Single-service compose with env + volume
├── hermes-office.service        # systemd user service template
├── install.sh                   # One-shot setup script (cp .env, pip install)
│
├── .env.example                 # Environment config template
├── agents.json                  # Live agent state (written by bridge or emitter)
├── agents.json.example          # Example agent state with sample data
│
├── public/
│   └── index.html               # Single-page Three.js frontend (~2073 lines)
│
├── scripts/
│   ├── hermes_bridge.py         # Auto-discovery bridge (427 lines)
│   └── example_agent_emitter.py # Demo emitter for testing (67 lines)
│
├── docs/
│   └── HERMES_INTEGRATION.md    # API contract and integration patterns
│
├── .github/
│   ├── workflows/codeql.yml     # CodeQL analysis (Python + JS/TS)
│   ├── dependabot.yml           # Weekly updates for 4 ecosystems
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       ├── feature_request.md
│       └── PULL_REQUEST_TEMPLATE.md
│
├── CODE_OF_CONDUCT.md           # Contributor Covenant v2.1
├── CONTRIBUTING.md              # Standard JorahOne contributing guide
└── SECURITY.md                  # Security policy with disclosure timeline
```

---

## Notes

- **Repo name vs README brand** — Updated. Repo is now `VirtOffice`, README brand is "VirtOffice". Naming aligned.
- **Empty directories** — None found.
- **Submodules** — None.
- **Security audit history** — Two security-related commits: `f80b28d` ("security: redact exposed tailscale IPs and demo emails") and `0004b82` ("security: redact hardcoded Tailscale IP"). The repo had hardcoded Tailscale IPs and emails that were later sanitized. This is a positive signal — the author actively audits and redacts sensitive data.
- **No test files** — No `tests/` directory, no test files, no test framework configured. This is the most significant gap for a production classification.
- **No monitoring/alerting** — No health check endpoint for Docker, no metrics export, no structured logging. The server suppresses access logs (`log_message` is a no-op).
- **No rate limiting** — The webhook endpoint (`POST /webhook/agents`) has no authentication or rate limiting. In production, this should be behind a reverse proxy or Tailscale.
- **Bridge script hardcodes agent definitions** — The five agents (Orchestrator, Analyst, Writer, Marketer, Coder) are hardcoded in `BASE_AGENTS` dict. Adding new agents requires code changes.
- **Repo is 3 days old** — 18 commits, all within July 3-5, 2026. Very early in its lifecycle.
- **Dependabot ecosystem mismatch** — Dependabot is configured for `npm` ecosystem, but no `package.json` exists (the frontend loads Three.js from CDN with no build step). This is a template vestige — the npm entry should be removed from `dependabot.yml`.
- **Author** — Jhonattan L. Jimenez (j1admin@onebyjorah.com), the same individual behind the broader JorahOne ecosystem.
