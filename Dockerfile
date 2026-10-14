# Vantage engine — portable image for GCP Cloud Run, Azure Container Apps, AWS Fargate.
# Runs as a service (default CMD `serve`) or a batch job (override CMD with `run --client ...`).
FROM python:3.14-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VANTAGE_HARNESS_DIR=/app/harness \
    VANTAGE_OUTPUT_DIR=/data/runs \
    PORT=8080

# uv for fast, reproducible installs
RUN pip install --no-cache-dir uv

WORKDIR /app

# Install dependencies first (better layer caching)
COPY pyproject.toml README.md ./
COPY src ./src
COPY harness ./harness
COPY config ./config

# Core engine (workflow + api backends work out of the box). Add framework/cloud extras with:
#   docker build --build-arg EXTRAS="langgraph,cloud-gcp" .
ARG EXTRAS=""
RUN uv pip install --system . \
 && if [ -n "$EXTRAS" ]; then uv pip install --system ".[$EXTRAS]"; fi

RUN mkdir -p /data/runs
VOLUME ["/data"]
EXPOSE 8080

# Service by default; Cloud Run Jobs / ACA Jobs / Fargate tasks override the args, e.g.:
#   ["run","--client","ACME","--slug","acme-2026-08","--backend","api"]
ENTRYPOINT ["vantage"]
CMD ["serve"]
