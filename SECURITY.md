# Security Policy

JorahOne projects are self-hosted infrastructure tools. Security matters.

## Supported versions

We patch security issues in the latest release of the default branch. Older releases are best-effort.

## Reporting a vulnerability

Please **do not** open a public issue for security vulnerabilities.

Instead, email `security@jorahone.com` with:

- Affected repository and version/branch.
- Steps to reproduce or proof-of-concept.
- Possible impact.
- Suggested fix (optional).

We will respond within 72 hours and coordinate disclosure.

## Security practices for self-hosters

- Run services behind a reverse proxy (Caddy/Nginx) with TLS.
- Keep Tailscale/WireGuard as the preferred exposure model.
- Rotate secrets and API keys regularly.
- Bind services to localhost unless a reverse proxy handles TLS.