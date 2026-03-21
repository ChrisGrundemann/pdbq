FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY pdbq/ ./pdbq/
COPY cli.py ./
COPY sync/ ./sync/

# Create data directory (will be overridden by Fly volume mount)
RUN mkdir -p /app/data /app/secrets

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "pdbq.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
