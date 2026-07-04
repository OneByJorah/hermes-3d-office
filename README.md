# Hermes 3D Office

> Animated 3D virtual office floor plan for Hermes AgentOS subagents.

![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/status-active-%23FFB300?style=for-the-badge)
![Language](https://img.shields.io/badge/language-Python-informational?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-linux-informational?style=for-the-badge)

Hermes 3D Office is an enterprise-grade, ops-precise platform built for VIDE and SMB operations. Run it solo. Deliver results.

- **5 animated subagents**: Orchestrator, Analyst, Writer, Marketer, Coder
- **Live state**: status, current task, task list, recent output, stats
- **Animated behaviors**: walking, working, meeting, idle, coffee runs
- **Click-to-inspect**: click any avatar or top-bar portrait for details
- **Chat bubbles**: agents talk when nearby
- **Office details**: server room (blinking LEDs), meeting area, kitchen, phone booths, lounge, ping pong, bookshelf, water cooler, plants, wall clock, posters
- **Controls**: zoom, auto-rotate, name-label toggle
- **Plug-and-play Hermes integration**: poll a Hermes API, drop an `agents.json`, or receive webhook pushes

| Layer | Stack |
|---|---|
| Runtime | Python |
| Environment | Linux |
| VCS | Git + GitHub |

## Quickstart

```bash
git clone https://github.com/OneByJorah/hermes-3d-office.git
cd hermes-3d-office
docker compose up -d
```
Verify at `http://<host-ip>`.

## Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| (see Environment Variables) | — | — | — |

For full details, see the in-repo [Environment Variables](#environment-variables) section.

## Roadmap

- Feature parity with production requirements
- Observability and alerting expansions
- Community feedback integration

## License

MIT — Copyright JorahOne, LLC. See [LICENSE](LICENSE) for details.

---

[OneByJorah](https://github.com/OneByJorah) · [JorahOne-Services](https://github.com/JorahOne-Services)
