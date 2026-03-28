# pdbq frontend

Browser-based interface for [pdbq](https://github.com/ChrisGrundemann/pdbq) — a natural-language query agent over PeeringDB data. Live at [peeringdb.ai](https://peeringdb.ai).

---

## Stack

| Tool | Choice | Why |
|------|--------|-----|
| **Bundler** | Vite | Fast dev server, simple config, no SSR overhead needed |
| **Framework** | React 18 | Component model fits the query/result UI well; no routing needed |
| **Styling** | Tailwind CSS | Utility-first keeps iteration fast; no design system fighting us |
| **Markdown** | react-markdown + remark-gfm + rehype-highlight | Answers from the LLM include tables, code blocks, and lists — raw text isn't enough |
| **Fonts** | Syne (UI/headings) + Outfit (body) + JetBrains Mono (code/wordmark) | Loaded via Google Fonts; chosen to feel technical without being generic |

---

## Design system

All colors are CSS custom properties defined in `src/index.css`. **Never hardcode colors** — always use the variables so dark/light theme switching works automatically.

Key tokens:
```css
--bg-primary      /* #090c10 — page background */
--bg-secondary    /* #0d1117 — cards, panels */
--bg-tertiary     /* #161b22 — inputs, code blocks */
--accent          /* #22d3ee — cyan, primary interactive color */
--violet          /* #a78bfa — SQL syntax highlight */
--amber           /* #f59e0b — warnings, sync status */
--text-primary    /* #e6edf3 */
--text-secondary  /* #8b949e */
--text-muted      /* #484f58 */
```

Dark theme is the default. Light theme is applied via `[data-theme="light"]` on `<html>`.

---

## Project structure
```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── Logo.jsx          # SVG peering topology mark + pdbq wordmark
│   │   ├── Header.jsx        # Top bar — logo, sync status, theme toggle, settings
│   │   ├── QueryInput.jsx    # Textarea, suggestion pills, submit button
│   │   ├── StatusIndicator.jsx # Live status events during tool-use loop
│   │   ├── AnswerPanel.jsx   # Streaming markdown answer display
│   │   ├── DetailPanel.jsx   # SQL / Tool Calls / Meta tabbed panel
│   │   ├── HistoryPanel.jsx  # Session query history sidebar
│   │   ├── SettingsModal.jsx # Key entry (pdbq key and/or Anthropic key)
│   │   ├── SyncStatus.jsx    # Polls /sync/status, shows last sync time
│   │   ├── ThemeToggle.jsx   # Dark/light toggle
│   │   └── Footer.jsx        # Disclaimer + ToS/Privacy links
│   ├── hooks/
│   │   ├── useQuery.js       # Streaming query state machine
│   │   └── useSettings.js    # Key and theme persistence (localStorage)
│   ├── lib/
│   │   ├── api.js            # fetch wrappers — streaming query, health, sync
│   │   └── errors.js         # Error normalization and friendly messages
│   ├── constants/
│   │   └── index.js          # API base URL, suggested queries, storage keys
│   ├── App.jsx               # Top-level layout and state wiring
│   ├── main.jsx              # Vite entry point
│   └── index.css             # Design tokens, base styles, markdown styles
├── .env.example              # Copy to .env for local dev overrides
├── index.html                # Google Fonts loaded here
├── package.json
├── tailwind.config.js
├── vite.config.js
└── postcss.config.js
```

---

## Auth model

The frontend supports two modes — at least one key is required:

- **pdbq access key** — request from the maintainer. Uses the server-side Anthropic key; no Anthropic account needed.
- **Anthropic API key (BYOC)** — bring your own key, fund your own queries. Goes directly to Anthropic via the `X-Anthropic-Key` header; never stored on the pdbq backend.

Both keys are stored in `localStorage` under the `pdbq:` namespace. They are never logged.

---

## Streaming

Queries use NDJSON streaming (`POST /query` with `{"stream": true}`). Each line is a JSON object:
```json
{"type": "status", "text": "Running SQL query..."}
{"type": "token", "text": "There are 1,305 "}
{"type": "metadata", "sql_executed": [...], "tool_calls": [...], "elapsed_ms": 3388}
```

The `useQuery` hook handles stream parsing. `status` chunks feed the `StatusIndicator`; `token` chunks accumulate into the `AnswerPanel`; the `metadata` chunk triggers the `DetailPanel`.

---

## Local development
```bash
# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Production build
npm run build
```

To run against a local backend instead of `api.peeringdb.ai`, copy `.env.example` to `.env` and set:
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Contributing

- Match the existing design token system — no hardcoded colors or fonts
- New components go in `src/components/`
- New API calls go in `src/lib/api.js`
- Keep the `useQuery` state machine clean — side effects belong in the hook, not in components
- The target audience is network engineers — clarity and information density matter more than decoration