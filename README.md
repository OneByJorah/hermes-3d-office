# VirtOffice

Animated 3D virtual office for Hermes AgentOS subagents — real-time isometric visualization of AI agents working, walking, and meeting.

![status](https://img.shields.io/badge/status-active-FFB300?style=flat-square)
![language](https://img.shields.io/badge/python+javascript-0d0d0c?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-FFB300?style=flat-square)

## Overview

VirtOffice is a self-hosted animated 3D virtual office that visualizes Hermes AgentOS subagents in real time. Built with a Python HTTP server (stdlib only) and a Three.js frontend, it renders an isometric office environment where AI agents are shown working, walking, meeting, and performing tasks. Supports WebSocket, API polling, SSE, and webhook push for real-time updates.

## Features

- 3D agent visualization with animated avatars
- Real-time updates via WebSocket, API polling, SSE, or webhook push
- Interactive UI — click-to-inspect, camera zoom/rotate, chat bubbles
- Detailed environment — server room, meeting area, kitchen, and more
- Multiple data sources — bridge script, API polling, static JSON, webhooks
- Python stdlib HTTP server (no Flask dependency)
- Docker Compose deployment

## Architecture / Tech Stack

- **Backend**: Python 3.10+ (stdlib HTTP server)
- **Frontend**: Three.js (3D rendering)
- **Real-time**: WebSocket, SSE, API polling, webhooks
- **Deployment**: Docker Compose, systemd service

## Installation

```bash
git clone https://github.com/OneByJorah/VirtOffice.git
cd VirtOffice

cp .env.example .env
python3 server.py
```

Or with Docker:
```bash
docker compose up -d
```

Open `http://localhost:9502`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `9502` | Server port |
| `HOST` | `127.0.0.1` | Bind address |
| `HERMES_AGENT_API` | — | Hermes agent snapshot endpoint |
| `AGENTS_JSON_PATH` | `./agents.json` | Agents JSON file path |
| `POLL_INTERVAL_SECONDS` | `5` | Polling interval |
| `ENABLE_SSE` | `true` | Enable Server-Sent Events |

## License

MIT — see [LICENSE](LICENSE).

---
Part of the JorahOne / J1 ecosystem — 3D visualization for Hermes AgentOS.
