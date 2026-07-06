<!-- j1-brand:v2 -->
<div align="center">

# Hermes 3D Office

An animated 3D virtual office floor plan that visualizes Hermes AgentOS subagents in real time — watch your AI agents work in an isometric browser scene.

[![GitHub](https://img.shields.io/badge/github-OneByJorah%2Fhermes--3d--office-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah/hermes-3d-office)
[![License](https://img.shields.io/badge/license-MIT-FFB300?style=for-the-badge&labelColor=0d0d0c)](LICENSE)
[![Language](https://img.shields.io/badge/HTML-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![Built by](https://img.shields.io/badge/built%20by-JorahOne%20LLC-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah)

</div>

---

## Why This Exists

When your Hermes agents are running, you can't see them. Hermes 3D Office changes that — rendering each subagent (Orchestrator, Analyst, Writer, etc.) as an animated avatar in an isometric office. Agents move between rooms, update their status in real time via WebSockets, and the scene auto-discovers new agents from the Hermes Gateway API. It's a window into your agent swarm.

## Key Features

| Feature | Why It Matters |
|---|---|
| 3D avatar animations | See which agents are active and what they're doing at a glance |
| Real-time WebSocket updates | Agent status changes appear instantly in the office |
| Auto-discovery bridge | Scans Hermes Gateway API, Session DB, and Kanban for new agents |
| Interactive scene | Zoom, rotate, and pan around the office to inspect agents |
| Multiple data sources | API polling, static JSON, or webhooks — whichever fits your setup |

## Quick Start

```bash
git clone https://github.com/OneByJorah/hermes-3d-office.git
cd hermes-3d-office

# Native
python3 server.py

# Docker
docker compose up -d
```

Open `http://localhost:8080` in your browser.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Hermes API   │────▶│  Bridge       │────▶│  Flask Server  │
│  Gateway      │     │  (Auto-disc)  │     │  (Backend)     │
│  Session DB   │     │               │     └──────┬───────┘
│  Kanban       │     │               │            │
└──────────────┘     └──────────────┘     ┌──────▼──────┐
                                          │  Three.js    │
                                          │  3D Office   │
                                          │  (Frontend)  │
                                          └─────────────┘
```

## Documentation

| Doc | Description |
|---|---|
| [Setup Guide](docs/setup.md) | Deployment options and configuration |
| [Bridge Configuration](docs/bridge.md) | Connecting to Hermes Gateway API |

---

## License

MIT © JorahOne, LLC — see [LICENSE](LICENSE)

<sub>Part of the JorahOne infrastructure ecosystem.</sub>
