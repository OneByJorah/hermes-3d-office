# =============================================================================
# Hermes 3D Office — Virtual agent office dashboard
# JorahOne
#
# Serves the static 3D office dashboard with live agent-state API.
# Uses only Python stdlib — no pip dependencies required.
# =============================================================================
FROM python:3.14-alpine

WORKDIR /app

# Copy application
COPY server.py .
COPY public/ ./public/
COPY .env.example ./.env

# Create agents.json placeholder if it doesn't exist
RUN touch agents.json

EXPOSE 9502

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-9502}/api/config', timeout=5)" || exit 1

CMD ["python3", "server.py"]
