FROM python:3.11-slim

WORKDIR /app
COPY server.py ./
COPY public ./public
COPY .env.example ./.env

EXPOSE 9502
CMD ["python3", "server.py"]
