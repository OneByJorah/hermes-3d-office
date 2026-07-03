# Hermes 3D Office

Animated 3D virtual office floor plan for Hermes AgentOS subagents. Each subagent appears as a living worker inside an isometric office with desks, meeting room, lounge, kitchen, server room, and real-time status.

## Live Demo

Open in browser (Mesh-VPN):

```
http://100.66.142.21:9502/office.html
```

## Quick Start

```bash
git clone https://github.com/OneByJorah/hermes-3d-office.git
cd hermes-3d-office
python3 -m pip install -r requirements.txt  # no deps for static server
python3 server.py
```

Visit `http://localhost:9502`.

## Hermes Agent Integration

The dashboard reads agent state from a JSON endpoint that Hermes can expose. Edit `HERMES_AGENT_API` in `server.py` to point to your Hermes agent status endpoint.

Example:

```python
HERMES_AGENT_API = "http://localhost:8080/api/agents/status"
```

Deploy as a systemd service:

```bash
sudo cp hermes-office.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-office
```

## Features

- 5 animated subagents: Orchestrator, Analyst, Writer, Marketer, Coder
- Walking, working, meeting, and idle animations
- Click any avatar to see live status, tasks, and recent output
- Chat bubbles when agents meet
- Pulsing mood rings and typing particles
- Server room, meeting area, kitchen, phone booths, lounge, ping pong

## Tech

- Three.js r128
- Pure static HTML/CSS/JS + Python HTTP server

## License

MIT
