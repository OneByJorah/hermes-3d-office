# VirtOffice

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![Three.js](https://img.shields.io/badge/Three.js-000000?logo=threedotjs&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

Animated 3D virtual office for Hermes AgentOS subagents. Real-time isometric visualization of AI agents working, walking, meeting, and more.

## Features

- 3D agent visualization with animated avatars
- Real-time updates via WebSocket, API polling, or webhook push
- Interactive UI with click-to-inspect, camera zoom/rotate, and chat bubbles
- Detailed environment: server room, meeting area, kitchen, and more
- Multiple data sources: bridge script, API polling, static JSON, webhooks

## Tech Stack

- Python 3.10+
- Flask-style HTTP server (stdlib only)
- Three.js frontend
- Docker / Docker Compose

## Installation

```bash
git clone https://github.com/OneByJorah/VirtOffice.git
cd VirtOffice
cp .env.example .env
# Edit .env as needed
python3 server.py
```

Or with Docker:

```bash
docker compose up -d
```

Open **http://localhost:9502** in your browser.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `9502` | Server port |
| `HOST` | `127.0.0.1` | Bind address |
| `HERMES_AGENT_API` | — | URL to Hermes agent snapshot endpoint |
| `AGENTS_JSON_PATH` | `./agents.json` | Path to agents JSON file |
| `POLL_INTERVAL_SECONDS` | `5` | Polling interval |
| `ENABLE_SSE` | `true` | Enable Server-Sent Events |

## Data Sources

| Source | Method | Description |
|--------|--------|-------------|
| Bridge script | Auto | Auto-discovers agents from Hermes Gateway API |
| API polling | Configurable | Polls Hermes status API periodically |
| Static JSON | File | Direct consumption of `agents.json` |
| Webhook | POST | Real-time updates via webhook endpoint |

## Project Structure

```
VirtOffice/
├── server.py              # Python backend server
├── public/                # 3D frontend (Three.js)
├── scripts/               # Bridge and utility scripts
├── docs/                  # Documentation
├── agents.json.example    # Example agent configuration
├── Dockerfile             # Container image
├── docker-compose.yml     # Deployment
└── requirements.txt       # Python dependencies (placeholder)
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

Report vulnerabilities privately to **info@jorahone.com**. See [SECURITY.md](SECURITY.md).

## License

MIT © Jhonattan L. Jimenez
