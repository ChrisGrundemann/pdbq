# pdbq

Natural-language query agent over [PeeringDB](https://www.peeringdb.com/) data. Ask questions in plain English about networks, IXes, facilities, ASNs, and peering relationships — the agent translates them into SQL against a local DuckDB database and returns polished markdown reports.

## Architecture

```
CLI / React SPA (later)
        │
        ▼
FastAPI backend  (/query, /export, /sync/status)
        │
        ▼
Agent Core (Claude API, tool-use loop)
  ├── tool: query_db(sql)                  → DuckDB (local sync of PeeringDB)
  ├── tool: get_live_record(resource, id)  → PeeringDB REST API
  ├── tool: export_to_sheets(data, title)  → Google Sheets (OAuth)
  └── tool: render_report(data, fmt)       → formatted markdown
        │
        ▼
DuckDB  (file: data/pdbq.duckdb)
        ▲
Sync job (pdbq/sync/run.py — nightly cron / Fly scheduled machine)
```

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- An [Anthropic API key](https://console.anthropic.com/)
- A [PeeringDB API key](https://www.peeringdb.com/account/api-keys/) (for authenticated access)

## Setup

```bash
# Clone and enter the project
git clone <repo-url>
cd pdbq

# Install dependencies
uv sync

# Copy and fill in the environment file
cp .env.example .env
$EDITOR .env
```

### Required environment variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `PEERINGDB_API_KEY` | PeeringDB API key for authenticated access |
| `DUCKDB_PATH` | Path to the DuckDB file (default: `data/pdbq.duckdb`) |
| `PDBQ_API_KEYS` | Comma-separated API keys for the FastAPI backend |
| `ADMIN_API_KEY` | Admin key for sync trigger endpoint |

See `.env.example` for all available variables.

## Quick Start

### 1. Sync PeeringDB data

```bash
# Full sync (first run — takes a few minutes)
uv run pdbq sync run

# Subsequent incremental syncs
uv run pdbq sync run --incremental

# Check sync status
uv run pdbq sync status
```

### 2. Ask a question

```bash
uv run pdbq query "Which IXes in North America have more than 100 member networks?"

uv run pdbq query "What ASNs are present at Equinix NY?"

uv run pdbq query "Show me all IPv6-enabled peering sessions at DE-CIX Frankfurt"

# Export to Google Sheets (requires Google OAuth setup)
uv run pdbq query "All networks present at more than 5 IXes in Europe" --export-sheets
```

### 3. Start the API server

```bash
uv run pdbq serve

# Or directly with uvicorn
uv run uvicorn pdbq.api.main:app --reload
```

The API will be at `http://localhost:8080`. In development mode, authentication is disabled.

## API

### `POST /query`

```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many networks have IPv6 peering sessions?"}'
```

Response:
```json
{
  "answer": "# IPv6-Enabled Networks\n\n...",
  "sql_executed": ["SELECT COUNT(DISTINCT net_id) FROM netixlan WHERE ipaddr6 IS NOT NULL AND status = 'ok'"],
  "tool_calls": [...],
  "elapsed_ms": 1240
}
```

### `GET /sync/status`

```bash
curl http://localhost:8080/sync/status \
  -H "Authorization: Bearer <admin-key>"
```

### `POST /sync/trigger`

```bash
curl -X POST "http://localhost:8080/sync/trigger?incremental=true" \
  -H "Authorization: Bearer <admin-key>"
```

### `GET /health`

```bash
curl http://localhost:8080/health
# {"status": "ok"}
```

## Google Sheets Export

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google Sheets API and Google Drive API
3. Create OAuth 2.0 credentials (Desktop app type)
4. Download the client secrets JSON to `secrets/google_client_secrets.json`

For CLI usage, the first `--export-sheets` call opens a browser for OAuth consent.

## Development

```bash
# Run tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run the API in dev mode (auto-reload)
uv run pdbq serve --reload
```

## Deployment (Fly.io)

```bash
# Create the app
fly apps create pdbq

# Create a volume for DuckDB data
fly volumes create pdbq_data --size 10 --region den

# Set secrets
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
fly secrets set PEERINGDB_API_KEY=...
fly secrets set PDBQ_API_KEYS=your-key-here
fly secrets set ADMIN_API_KEY=your-admin-key
fly secrets set ENVIRONMENT=production

# Deploy
fly deploy
```

The nightly sync runs as a Fly scheduled machine:
```bash
fly machine run . \
  --schedule="0 2 * * *" \
  --entrypoint="uv run python sync/run.py --incremental" \
  --env ENVIRONMENT=production
```

## Project Structure

```
pdbq/
├── pdbq/
│   ├── config.py           # Settings via pydantic-settings
│   ├── db/
│   │   ├── connection.py   # DuckDB connection management
│   │   └── schema.sql      # All table definitions
│   ├── sync/
│   │   ├── client.py       # PeeringDB API client (with retry)
│   │   ├── models.py       # Pydantic models for PeeringDB objects
│   │   └── run.py          # Sync entrypoint
│   ├── agent/
│   │   ├── core.py         # Tool-use loop
│   │   ├── tools.py        # Tool definitions and implementations
│   │   ├── prompts.py      # System prompt with schema injection
│   │   └── sheets.py       # Google Sheets OAuth + export
│   └── api/
│       ├── main.py         # FastAPI app
│       ├── auth.py         # API key middleware
│       ├── models.py       # Request/response models
│       └── routers/        # Route handlers
├── cli.py                  # Click CLI
├── sync/run.py             # Standalone sync for Fly scheduler
└── tests/                  # Pytest tests
```
