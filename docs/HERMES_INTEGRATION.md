# Hermes 3D Office — Agent State API Contract

This dashboard consumes a simple JSON contract. Any Hermes installation can feed live agent data using one of three integration patterns.

## Agent Object

```json
{
  "id": "analyst",
  "name": "Analyst",
  "role": "Research",
  "emoji": "📊",
  "color": "#3B82F6",
  "home": "left",
  "status": "working",
  "task": "Competitor deep-dive",
  "tasks": ["Market research", "Data synthesis", "Trend analysis"],
  "output": ["Competitor report v1", "Keyword research"],
  "stats": { "tasksDone": 12, "active": 3, "hours": 4.2 },
  "mood": 0.8,
  "typing": true,
  "position": { "x": -10.5, "z": -2.5 }
}
```

Allowed `status` values: `idle`, `walking`, `working`, `meeting`, `away`, `offline`.
Allowed `home` values: `meeting`, `left`, `center`, `right`, `right2`.

## Integration Patterns

### 1. Hermes Agent Status API (Polling)

Configure Hermes to expose `GET /api/agents/status`. Set `HERMES_AGENT_API` to that URL. The dashboard server proxies it and injects the result into the page.

### 2. Hermes Webhook Push

The dashboard server exposes `POST /webhook/agents`. Add it as a Hermes webhook target. Any agent status update POSTed to that URL is broadcast to connected dashboards via SSE.

### 3. Static JSON File Drop

Hermes cron jobs or scripts can write `agents.json` into the repo root. The server serves it as `/api/agents`.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agents` | GET | Live agent array (proxied, file, or generated demo fallback) |
| `/webhook/agents` | POST | Receive agent state updates from Hermes |
| `/api/config` | GET | Current dashboard config (safe, no secrets) |
| `/events` | SSE | Stream live updates to the browser |

## Security

- Never commit API keys, tokens, or connection strings.
- Set secrets via environment variables only.
- Use Tailscale or HTTPS when exposing outside localhost.
- The webhook endpoint (`POST /webhook/agents`) supports optional Bearer token authentication via the `WEBHOOK_SECRET` environment variable. Set it to protect the endpoint from unauthorized access.
