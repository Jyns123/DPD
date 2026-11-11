FROM node:22-bookworm-slim AS web-build
WORKDIR /app
COPY package*.json .npmrc ./
RUN npm ci
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM python:3.12-slim-bookworm AS backend
ENV PYTHONUNBUFFERED=1 NEXT_TELEMETRY_DISABLED=1 NODE_ENV=production TZ=America/Lima
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 tzdata ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=web-build /usr/local/bin/node /usr/local/bin/node
COPY analytics/requirements.txt /tmp/analytics-requirements.txt
COPY urbania/requirements.txt /tmp/urbania-requirements.txt
RUN pip install --no-cache-dir -r /tmp/analytics-requirements.txt -r /tmp/urbania-requirements.txt

COPY --from=web-build --chown=1000:1000 /app /app
RUN mkdir -p storage captures tests/results && chown -R 1000:1000 /app
USER 1000:1000
EXPOSE 5173
CMD ["python", "scripts/container_server.py"]
