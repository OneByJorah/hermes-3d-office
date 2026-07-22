<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=three.js&logoColor=white">
  <img src="https://img.shields.io/badge/WebSocket-4CAF50?style=for-the-badge&logo=socket.io&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</div>

<br>

<div align="center">
  <h1>VirtOffice</h1>
  <p><strong>Animated 3D Virtual Office for AI Agents</strong></p>
  <p>Real-time isometric visualization of Hermes AgentOS subagents working, walking, and meeting.</p>
  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#contributing">Contributing</a>
  </p>
</div>

---

## Screenshot

![VirtOffice 3D Visualization](docs/screenshot.png)
*Animated 3D virtual office showing AI agents working in real-time.*

## Features

- **3D Agent Visualization** — Animated avatars showing agents working, walking, and meeting.
- **Real-Time Updates** — WebSocket, SSE, API polling, and webhook push for live updates.
- **Interactive UI** — Click-to-inspect agents, camera zoom/rotate, chat bubbles.
- **Detailed Environment** — Server room, meeting area, kitchen, and more.
- **Multiple Data Sources** — Bridge script, API polling, static JSON, and webhooks.
- **Python Stdlib Server** — Zero external dependencies, pure stdlib HTTP server.
- **Docker Compose** — One-command deployment.

## Quick Start

```bash
git clone https://github.com/OneByJorah/VirtOffice.git
cd VirtOffice

cp .env.example .env
python3 server.py
```

Open **http://localhost:9502** in your browser.

### Docker Deployment

```bash
docker compose up -d
```

### Using the Hermes Bridge

```bash
python3 scripts/hermes_bridge.py --api http://localhost:8080
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `9502` | Server port |
| `HOST` | `127.0.0.1` | Bind address |
| `HERMES_AGENT_API` | — | Hermes agent snapshot endpoint |
| `AGENTS_JSON_PATH` | `./agents.json` | Agents JSON file path |
| `POLL_INTERVAL_SECONDS` | `5` | API polling interval |
| `ENABLE_SSE` | `true` | Enable Server-Sent Events |
| `ENABLE_WEBSOCKET` | `true` | Enable WebSocket updates |

## Architecture

```
Browser (Three.js) ──WebSocket/SSE──▶ Python Server ──▶ Agent Data Source
                                        │
                                        ├──▶ Hermes Agent API
                                        ├──▶ Static JSON
                                        └──▶ Webhook Push
```

## Tech Stack

- **Backend**: Python 3.10+ (stdlib HTTP server, zero dependencies)
- **Frontend**: Three.js (3D rendering), Vanilla JS
- **Real-time**: WebSocket, SSE, API polling, webhooks
- **Deployment**: Docker Compose, systemd service

## Project Structure

```
VirtOffice/
├── server.py                    # Python stdlib HTTP server
├── scripts/
│   ├── hermes_bridge.py         # Hermes AgentOS integration
│   └── example_agent_emitter.py # Example agent data emitter
├── index.html                   # Main 3D office page
├── office.js                    # Three.js scene setup
├── agents.js                    # Agent rendering logic
├── agents.json                  # Agent data file
├── docker-compose.yml           # Docker deployment
└── .env.example                 # Configuration template
```

## Configuration

### Data Sources

VirtOffice supports multiple data sources for agent data:

1. **Hermes Agent API** — Real-time polling of Hermes AgentOS
2. **Static JSON** — Load agents from `agents.json`
3. **Webhook Push** — POST agent updates to `/webhook/agents`
4. **Example Emitter** — Run `scripts/example_agent_emitter.py` for demo

### Environment Zones

The 3D office includes:
- **Server Room** — Where agents run computations
- **Meeting Area** — Agent collaboration space
- **Kitchen** — Break area for agents
- **Desks** — Individual agent workstations

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

## Security

For security concerns, see [SECURITY.md](SECURITY.md). Please report vulnerabilities to **info@jorahone.com** — do not use public issues.

## License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>3D visualization for Hermes AgentOS.</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
