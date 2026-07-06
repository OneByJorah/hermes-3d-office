FROM python:3.11-slim

WORKDIR /app
COPY server.py ./
COPY public ./public
COPY .env.example ./.env

RUN addgroup --system --gid 1001 office && \
    adduser --system --uid 1001 --ingroup office --no-create-home office && \
    chown -R office:office /app

USER office

EXPOSE 9502
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:9502/api/agents', timeout=5)" || exit 1
CMD ["python3", "server.py"]
