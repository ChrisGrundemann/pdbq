# pdbq

Ask natural-language questions about PeeringDB data — powered by Claude, stored locally in DuckDB.

```
pdbq query "Which networks peer at more than 10 IXes in Europe?"
pdbq query "All facilities in Japan" --output japan-facilities.csv
```

## Overview

pdbq mirrors the PeeringDB dataset into a local DuckDB file and exposes it through a Claude-powered agent. You ask questions in plain English; the agent writes SQL, runs it, and returns a formatted answer. Everything runs locally — no data leaves your machine except the natural-language query sent to the Anthropic API.

**Stack:**
- **DuckDB** — embedded analytical database, stores the full PeeringDB mirror (~hundreds of MB)
- **Claude API (Anthropic)** — translates natural-language questions into SQL and formats results
- **FastAPI** — optional HTTP API for programmatic access or web frontends
- **CLI** — the primary interface; built with Click and Rich

---

## Example Queries

Simple geographic queries:
```
$ uv run pdbq query "how many IXes are in Africa?"
There are 85 active Internet Exchange Points (IXes) in Africa according to PeeringDB.
$
```

Compound queries:
```
$ uv run pdbq query "how many IXes are in Africa with more than 10 members? list them all, including which data center they are in"
Perfect! I found 28 Internet Exchanges in Africa with more than 10 members. Let me format this into a clear report:                                                                                              

African Internet Exchanges with More Than 10 Members                                                                                                                                                             

Total Count: 28 IXes                                                                                                                                                                                             

 IX Name                         City           Country        Members  Data Centers                                                                                                                             
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
 NAPAfrica IX Johannesburg       Johannesburg   South Africa   541      • Teraco Johannesburg Campus, South Africa                                                                                               
 NAPAfrica IX Cape Town          Cape Town      South Africa   278      • Teraco CT1 Cape Town, South Africa• Teraco CT2 Cape Town, South Africa                                                                 
 JINX                            Johannesburg   South Africa   191      • Africa Data Centres, Johannesburg JHB1, South Africa• Africa Data Centres, Johannesburg JHB2, South Africa• Digital Parks - Samrand•   
                                                                        Equinix JN1 - Johannesburg• NTT Data (MEA) - Parklands• NTT Johannesburg 1 Data Center (JOH1)• OADC JNB1 - Johannesburg• Teraco          
                                                                        Johannesburg Campus, South Africa• xneelo JNB1 (Formerly Hetzner SA)                                                                     
 NAPAfrica IX Durban             Durban         South Africa   135      • Teraco DB1 Durban, South Africa                                                                                                        
 KIXP - Nairobi                  Nairobi        Kenya          125      • Africa Data Centres, Nairobi NBO1, Kenya• PAIX Nairobi• iXAfrica NBOX1 (Nairobi X One)• icolo.io Nairobi One (NBO1)                    
 CINX                            Cape Town      South Africa   115      • Africa Data Centres, Cape Town CPT1, South Africa• NTT Data (MEA) - Cape Town• OADC CPT1 - Cape Town• OADC CPT2 - Brackenfell• Teraco  
                                                                        CT1 Cape Town, South Africa• Teraco CT2 Cape Town, South Africa                                                                          
 IXPN Lagos                      Lagos          Nigeria        114      • Africa Data Centres, Lagos LOS1, Nigeria• Cloud Exchange West Africa• Digital Realty Lagos (LOS1-2)• Digital Realty Lekki (LKK1-2)•    
                                                                        Equinix LG1/LG2 – Lagos, Lekki• NCR-Marina• OADC LOS1 - Lagos• Rack Centre Lagos                                                         
 DINX                            Durban         South Africa   99       • NTT DATA, Umhlanga• Teraco DB1 Durban, South Africa                                                                                    
 AMS-IX Lagos                    Lagos          Nigeria        49       • Equinix LG1/LG2 – Lagos, Lekki                                                                                                         
 LINX Mombasa                    Mombasa        Kenya          43       • icolo.io Mombasa One (MBA1)• icolo.io Mombasa Two (MBA2)                                                                               
 LINX Nairobi                    Nairobi        Kenya          40       • Africa Data Centres, Nairobi NBO1, Kenya• PAIX Nairobi• iXAfrica NBOX1 (Nairobi X One)• icolo.io Nairobi One (NBO1)                    
 AF-CIX                          Lagos          Nigeria        38       • Rack Centre Lagos                                                                                                                      
 KIXP - Mombasa icolo            Mombasa        Kenya          33       • icolo.io Mombasa One (MBA1)                                                                                                            
 TIX Tanzania - Dar es Salaam    Dar es Salaam  Tanzania       32       • National Internet Data Center (NIDC)• STELLAR IX SALASALA DataCenter• TIX - Tanzania - Posta House• Wingu Dar es Salaam                
 NAPAfrica MAPS Johannesburg     Johannesburg   South Africa   26       • Teraco Johannesburg Campus, South Africa                                                                                               
 UIXP                            Kampala        Uganda         24       • Communications House• Raxio Kampala UG1                                                                                                
 GIXA                            Accra          Ghana          23       • Digital Realty Accra (ACR12)• Equinix AC1 - Accra• NITA data center• ONIX Data Centre Accra• PAIX Accra                                
 angonix                         Luanda         Angola         23       • AngoNAP Luanda                                                                                                                         
 KINIX                           Kinshasa       DR Congo       22       No facility data available                                                                                                               
 Accra Internet Exchange LBG     Accra          Ghana          21       • PAIX Accra                                                                                                                             
 MIXP                            Ebene          Mauritius      21       • Government Online Centre• Rogers Capital Data Center                                                                                   
 AMS-IX Djibouti                 Djibouti       Djibouti       20       • Djibouti Data Center                                                                                                                   
 PyramIX                         Cairo          Egypt          20       • Digital Realty Frankfurt FRA1-16• GPX Cairo 1• NIKHEF Amsterdam                                                                        
 MOZIX                           Maputo         Mozambique     18       No facility data available                                                                                                               
 IXPN Abuja                      Abuja          Nigeria        17       No facility data available                                                                                                               
 BFIX Ouagadougou                Ouagadougou    Burkina Faso   16       • Datacenter Immeuble du Faso• Datacenter Ministere de l'agriculture• Virtix Data Center                                                 
 TIX Tanzania - Arusha (AIXP)    Arusha         Tanzania       16       No facility data available                                                                                                               
 BGP.Exchange - Johannesburg     Johannesburg   South Africa   15       No facility data available                                                                                                               
 RINEX                           Kigali         Rwanda         15       • Telecom House Kigali                                                                                                                   
 Angola IXP                      Luanda         Angola         14       • Paratus ITA-DC1• Paratus ITA-DC2• Raxio Luanda AO1                                                                                     
 CIVIX                           Abidjan        Côte d'Ivoire  14       No facility data available                                                                                                               
 LUBIX                           Lubumbashi     DR Congo       12       No facility data available                                                                                                               
 Lusaka Internet Exchange Point  Lusaka         Zambia         12       No facility data available                                                                                                               
 NMBINX                          Gqeberha       South Africa   12       • NTT Data (MEA) - Gqeberha (Port Elizabeth)                                                                                             
 GOMIX                           Goma           DR Congo       11       No facility data available                                                                                                               
                                                                                                                                                                                                                 

Key Insights:                                                                                                                                                                                                    

 • South Africa dominates with the most IXes (9 total) and largest membership counts                                                                                                                             
 • NAPAfrica IX Johannesburg is the largest IX in Africa with 541 members                                                                                                                                        
 • Teraco facilities in South Africa host multiple major IXes                                                                                                                                                    
 • Kenya has strong IX presence with KIXP and LINX deployments across multiple facilities                                                                                                                        
 • Nigeria has significant peering infrastructure in Lagos with 4 IXes                                                                                                                                           
 • Several smaller IXes (7 total) have no facility data registered in PeeringDB                                                                                                                                  
$
```
---

## Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management
- An [Anthropic API key](https://console.anthropic.com/)
- A [PeeringDB API key](https://www.peeringdb.com/account/apikey) (optional but recommended — unauthenticated access is rate-limited)

---

## Installation

```bash
git clone https://github.com/ChrisGrundemann/pdbq.git
cd pdbq
uv sync
cp .env.example .env
# Edit .env and fill in your API keys
```

Install the `pdbq` CLI into your path:

```bash
uv pip install -e .
```

Or run without installing:

```bash
uv run pdbq <command>
```

---

## Configuration

Copy `.env.example` to `.env` and set the values below. Variables marked **required** must be set before the app will function.

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | **Yes** | — | Anthropic API key for Claude |
| `PEERINGDB_API_KEY` | Recommended | — | PeeringDB API key; unauthenticated access is heavily rate-limited |
| `PEERINGDB_BASE_URL` | No | `https://www.peeringdb.com/api` | PeeringDB API base URL |
| `DUCKDB_PATH` | No | `data/pdbq.duckdb` | Path to the local DuckDB database file |
| `QUERY_HISTORY_PATH` | No | `data/query_history.jsonl` | Path to the JSONL query history log |
| `QUERY_HISTORY_MAX_ENTRIES` | No | `10000` | Max history entries before rotation; `0` = unlimited |
| `PDBQ_API_KEYS` | API only | `changeme-key-1` | Comma-separated Bearer tokens for the FastAPI `/query` endpoint |
| `ADMIN_API_KEY` | API only | `changeme-admin-key` | Bearer token for `/sync/status` and `/sync/trigger` |
| `GOOGLE_CLIENT_SECRETS_PATH` | Sheets only | `secrets/google_client_secrets.json` | Google OAuth client secrets for Sheets export |
| `GOOGLE_TOKEN_STORE_PATH` | Sheets only | `data/google_tokens/` | Directory where per-user OAuth tokens are stored |
| `ALLOWED_ORIGINS` | Production | — | Comma-separated CORS origins, e.g. `https://yourdomain.com` |
| `ENVIRONMENT` | No | `development` | Set to `production` to enforce API key auth and enable startup credential checks |

**Production note:** When `ENVIRONMENT=production`, the app refuses to start if `ADMIN_API_KEY` or any entry in `PDBQ_API_KEYS` still contains the default `changeme-*` values.

---

## Usage — CLI

### Sync PeeringDB data

Populate the local database before querying. A full sync takes several minutes due to PeeringDB's rate limit (1 request/second per page).

```bash
# Full sync — fetches all tables
pdbq sync run

# Incremental sync — fetches only records updated since last sync
pdbq sync run --incremental

# Sync specific tables only
pdbq sync run --tables ixfac,as_set

# Show sync status (last synced time and record counts per table)
pdbq sync status
```

`sync run` flags:

| Flag | Description |
|---|---|
| `--incremental` | Only fetch records updated since the last successful sync |
| `--tables TABLES` | Comma-separated list of tables to sync, e.g. `--tables ixfac,as_set` |
| `--debug` | Enable verbose logging (API calls, pagination, upsert counts) |

### Query

```bash
pdbq query "Which networks peer at more than 5 IXes in Asia Pacific?"
pdbq query "All IXes in Germany with more than 100 members"
pdbq query "What ASes are present at Equinix NY9?" --show-sql
pdbq query "Top 10 networks by IPv4 prefix count" --output prefixes.md
pdbq query "All facilities in Singapore" --output sg-facs.csv
pdbq query "Carriers at Equinix AM1" --export-sheets
```

`query` flags:

| Flag | Description |
|---|---|
| `--output FILE` | Save the response to a file. `.md` files get the markdown answer; `.csv` files get the raw tabular data from the last query the agent ran. Falls back to markdown if no tabular data is available. Prompts before overwriting an existing file. |
| `--show-sql` | Print the SQL statements the agent executed after displaying the answer |
| `--export-sheets` | Export results to a new Google Sheet (requires Google OAuth setup) |
| `--debug` | Enable verbose logging |

### History

Every query is logged to `data/query_history.jsonl`.

```bash
# Show the last 20 queries (default)
pdbq history

# Show the last 5 queries
pdbq history --last 5

# Re-display the full answer for the most recent query
pdbq history --show 1

# Re-display the full answer for the 3rd most recent query
pdbq history --show 3
```

`history` flags:

| Flag | Default | Description |
|---|---|---|
| `--last N` | `20` | Show only the last N history entries |
| `--show N` | — | Re-display the full answer for the Nth most recent query (1 = most recent) |

### Other commands

```bash
# Open an interactive DuckDB SQL shell against the local database
pdbq db shell

# Start the FastAPI server locally
pdbq serve
pdbq serve --host 0.0.0.0 --port 9000
pdbq serve --reload   # auto-reload on code changes (development)
```

---

## Usage — API

Start the server with `pdbq serve` or `uv run uvicorn pdbq.api.main:app --port 8080`.

All endpoints except `/health` require a `Bearer` token in the `Authorization` header.

### `POST /query`

Run a natural-language query. Requires an API key from `PDBQ_API_KEYS`.

```bash
curl -X POST http://localhost:8080/query \
  -H "Authorization: Bearer <key>" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many networks are in the database?"}'
```

Request body:

| Field | Type | Description |
|---|---|---|
| `query` | string | The natural-language question |
| `stream` | bool | If `true`, streams the final answer as `text/plain` |
| `google_token` | string | OAuth token for Sheets export (optional) |

Response:

| Field | Type | Description |
|---|---|---|
| `answer` | string | Formatted markdown answer |
| `sql_executed` | string[] | SQL statements the agent ran |
| `tool_calls` | object[] | Full tool invocation log |
| `elapsed_ms` | int | Total time in milliseconds |

### `GET /health`

No auth required. Returns `{"status": "ok"}`. Used by load balancers and the Docker health check.

### `GET /sync/status`

Requires the admin API key. Returns last sync time and record count for each table, plus database size on disk.

### `POST /sync/trigger`

Requires the admin API key. Starts a background sync and returns immediately.

```bash
curl -X POST "http://localhost:8080/sync/trigger?incremental=true" \
  -H "Authorization: Bearer <admin-key>"
```

---

## Deployment — Fly.io

The project is configured to deploy on [Fly.io](https://fly.io) with a persistent volume for the DuckDB file.

### First deploy

```bash
# Install the Fly CLI and authenticate
fly auth login

# Create the app (only needed once)
fly apps create pdbq

# Create the persistent volume for the database
fly volumes create pdbq_data --size 10 --region den

# Set secrets (do not put these in fly.toml or .env)
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
fly secrets set PEERINGDB_API_KEY=...
fly secrets set PDBQ_API_KEYS=your-strong-key-1,your-strong-key-2
fly secrets set ADMIN_API_KEY=your-strong-admin-key
fly secrets set ENVIRONMENT=production

# Deploy
fly deploy
```

### Subsequent deploys

```bash
fly deploy
```

### Scheduled sync

The nightly incremental sync runs as a separate Fly machine on a cron schedule:

```bash
fly machine run . \
  --schedule="0 2 * * *" \
  --entrypoint="uv run python sync/run.py --incremental"
```

For an initial full sync on the deployed instance:

```bash
fly ssh console -C "uv run python sync/run.py"
```

### Configuration notes

- The Fly volume is mounted at `/app/data`. The entrypoint script fixes ownership at startup so the non-root app user can write to it.
- `secrets/` (Google OAuth client secrets) must be provisioned separately if Sheets export is needed. Copy the file into the running machine with `fly sftp`.
- `min_machines_running = 0` means the machine stops when idle. The first request after a cold start will be slower while the machine wakes.

---

## Data

pdbq mirrors the following PeeringDB tables:

| Table | PeeringDB endpoint | Description |
|---|---|---|
| `org` | `/org` | Organizations |
| `network` | `/net` | Networks (ASNs) |
| `ix` | `/ix` | Internet Exchange Points |
| `facility` | `/fac` | Physical colocation facilities |
| `ixlan` | `/ixlan` | LANs within an IX |
| `ixpfx` | `/ixpfx` | IP prefixes announced on IX LANs |
| `netixlan` | `/netixlan` | Networks present at IX LANs (peering sessions) |
| `netfac` | `/netfac` | Networks present at facilities |
| `poc` | `/poc` | Points of contact for networks |
| `carrier` | `/carrier` | Carrier/transit providers |
| `ixfac` | `/ixfac` | IXes present at facilities |
| `carrierfac` | `/carrierfac` | Carriers present at facilities |
| `campus` | `/campus` | Campus groupings of facilities |
| `as_set` | `/as_set` | Network IRR AS-SET routing policy objects |

**PeeringDB AUP:** Use of this data is subject to the [PeeringDB Acceptable Use Policy](https://www.peeringdb.com/aup). The data is provided for operational network planning and peering purposes. Do not bulk-redistribute the raw data or use it for commercial purposes without reviewing the AUP.

---

## Status

This is an early-stage tool, feedback and PRs welcome!

---

## License

Apache 2.0. See [LICENSE](LICENSE).
