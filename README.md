# Hermes 3D Office

Animated 3D virtual office floor plan for Hermes AgentOS subagents. Each subagent appears as a living worker inside an isometric office with desks, meeting room, lounge, kitchen, server room, and real-time status.

## Features

- **5 animated subagents**: Orchestrator, Analyst, Writer, Marketer, Coder
- **Live state**: status, current task, task list, recent output, stats
- **Animated behaviors**: walking, working, meeting, idle, coffee runs
- **Click-to-inspect**: click any avatar or top-bar portrait for details
- **Chat bubbles**: agents talk when nearby
- **Office details**: server room (blinking LEDs), meeting area, kitchen, phone booths, lounge, ping pong, bookshelf, water cooler, plants, wall clock, posters
- **Controls**: zoom, auto-rotate, name-label toggle
- **Plug-and-play Hermes integration**: poll a Hermes API, drop an `agents.json`, or receive webhook pushes

## Quick Start

```bash
git clone https://github.com/OneByJorah/hermes-3d-office.git
cd hermes-3d-office
./install.sh
python3 server.py
```

Visit `http://localhost:9502`.

## Hermes Agent Integration

### ⭐ Recommended: Bridge Script (auto plug-and-play)

The included bridge script auto-discovers your Hermes agents — no configuration needed.

```bash
# One-shot: write agents.json once
python3 scripts/hermes_bridge.py

# Continuous: refresh every 10 seconds
python3 scripts/hermes_bridge.py --watch --interval 10

# Or push via webhook
python3 scripts/hermes_bridge.py --webhook http://localhost:9502/webhook/agents
```

The bridge reads from:
- **Hermes Gateway API** (`http://localhost:51763/api/snapshot`) — agent activity, status, sessions
- **Session DB** (`~/.hermes/state.db`) — recent/active sessions per platform
- **Cron jobs** (`~/.hermes/cron/jobs.json`) — scheduled task status
- **Content directories** (`~/.hermes/content/`) — files written per agent
- **Kanban DB** (`~/.hermes/kanban.db`) — open tasks

It auto-maps agents from your `config.yaml` Discord `channel_prompts` and Telegram sessions.

### Other wiring options (set in `.env`):

### 1. Poll a Hermes status API

```bash
HERMES_AGENT_API=http://localhost:8080/api/agents/status
```

The server polls it every `POLL_INTERVAL_SECONDS` and serves `/api/agents` to the dashboard.

### 2. Static JSON file drop

```bash
AGENTS_JSON_PATH=./agents.json
```

Any Hermes cron job or script writes `agents.json`; the dashboard reflects it immediately.

### 3. Webhook push

Configure Hermes to POST to:

```
POST http://your-host:9502/webhook/agents
```

with a JSON body containing an `agents` array. The dashboard updates live via SSE.

See `docs/HERMES_INTEGRATION.md` for the full agent JSON contract.

## Deployment

### Python (recommended)

```bash
cp .env.example .env
# edit .env
python3 server.py
```

### Docker

```bash
docker compose up --build
```

### systemd auto-start

The systemd unit uses `%I` so it works for any username. Replace `youruser`:

```bash
sudo cp hermes-office.service /etc/systemd/system/hermes-office@youruser.service
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-office@youruser
```

Example for user `j1admin`:

```bash
sudo cp hermes-office.service /etc/systemd/system/hermes-office@j1admin.service
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-office@j1admin
```

## Mesh-VPN / Remote Access

If you run the server on a Mesh-VPN node:

```
http://100.66.142.21:9502
```

For a cleaner URL, run on that node:

```bash
sudo mesh-vpn set --operator=$USER
sudo mesh-vpn serve https://localhost:9502
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Dashboard |
| `/api/agents` | Live agent array |
| `/api/config` | Safe config summary |
| `/webhook/agents` | Receive Hermes webhooks |
| `/events` | Server-Sent Events stream |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `9502` | Server port |
| `HOST` | `0.0.0.0` | Bind address |
| `HERMES_AGENT_API` | `""` | Hermes status API URL |
| `AGENTS_JSON_PATH` | `./agents.json` | Static agents JSON |
| `POLL_INTERVAL_SECONDS` | `5` | Poll interval |
| `ENABLE_SSE` | `true` | Live browser SSE |

## Tech

- Three.js r128
- Pure static HTML/CSS/JS
- Python 3 HTTP server (no framework dependencies)

## License

MIT
