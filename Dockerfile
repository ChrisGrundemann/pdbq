FROM python:3.11-slim

# Install gosu (privilege drop) and curl (healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gosu \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install pinned uv version
COPY --from=ghcr.io/astral-sh/uv:0.10.12 /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first (layer cache — local package excluded until source is present)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY pdbq/ ./pdbq/
COPY cli.py ./
COPY sync/ ./sync/

# Install the local pdbq package and its entry points into the venv
RUN uv pip install -e . --no-deps

# Confirm the entry point is baked in (fails the build if missing)
RUN test -f /app/.venv/bin/pdbq

# Create data and secrets directories (data will be overridden by Fly volume mount)
RUN mkdir -p /app/data /app/secrets

# Non-root user — chown happens at runtime via entrypoint for volume-mounted dirs
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Entrypoint fixes volume ownership then drops to appuser
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["/app/.venv/bin/uvicorn", "pdbq.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
