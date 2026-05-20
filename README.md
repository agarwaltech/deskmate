# DeskMate — AI-Powered IT Helpdesk Assistant

**Black Box Network Services | AI Center of Excellence — Take-Home Exercise**

DeskMate is a proof-of-concept agentic IT helpdesk assistant. An employee asks a question in natural language. DeskMate decides what tools to call (entitlement checks, ticket creation, password resets, etc.), fetches or writes to mock internal systems, and replies through an LLM with something actionable.

---

## Architecture Overview

```
Browser (Chat UI)
       │  HTTP POST /chat
       ▼
  FastAPI (main.py)
       │
       ▼
  Agent Loop (llm.py)
       │  Mistral API — mistral-small-latest
       │  with function calling (tools)
       ▼
  Tool Dispatcher (tools.py)
       │
       ├── get_user_profile
       ├── check_software_entitlement
       ├── create_ticket
       ├── get_ticket_status
       ├── list_user_tickets
       └── reset_password
                │
                ▼
        Mock IT Systems (mock_data.py)
        · User Directory
        · Software Catalog
        · Ticket Store (in-memory, mutable)
```

The agent loop is a standard **ReAct-style** loop:
1. Build `messages` list (system prompt + history + user turn)
2. Call Mistral with tool schemas
3. If the model returns `tool_calls` → execute each, append results, go to step 2
4. If `finish_reason == stop` → return final text response

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- A free Mistral API key from [console.mistral.ai](https://console.mistral.ai)

### 1 — Clone / open the project

```bash
cd deskmate
```

### 2 — Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Set your API key

```bash
# Windows (PowerShell)
Copy-Item .env.example .env
# Then open .env and replace your_mistral_api_key_here with your real key

# macOS / Linux
cp .env.example .env
nano .env   # or open in VS Code
```

### 5 — Run the server

```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6 — Open the UI

Go to **http://localhost:8000** in your browser.

---

## Demo Employee IDs

| ID | Name | Department | Notable Entitlements |
|---|---|---|---|
| EMP001 | Alice Johnson | Engineering | M365, Slack, GitHub, Jira |
| EMP002 | Bob Martinez | Marketing | M365, Slack, **Adobe Creative Suite** |
| EMP003 | Carol White | Finance | M365, Slack, **SAP** |
| EMP004 | David Lee | HR | M365, Slack, **Workday** |
| EMP005 | Eva Chen | Engineering | M365, GitHub, **AWS Console** |

**Pre-existing tickets:**
- `TKT-0990` — EMP001, VPN issue (resolved)
- `TKT-0995` — EMP003, SAP access (in progress)
- `TKT-0998` — EMP005, hardware (open)

---

## Sample Queries to Try

| Query (as EMP001) | What DeskMate does |
|---|---|
| `I need Adobe Creative Suite access — if I'm not entitled, please raise a high-priority ticket` | Checks entitlement → not entitled → creates ticket |
| `Reset my password` | Calls `reset_password(EMP001)` → returns temp credential |
| `What's the status of TKT-0990?` | Calls `get_ticket_status` → returns resolution details |
| `Show me all my tickets` | Calls `list_user_tickets` → lists history |
| `Do I have access to GitHub?` | Checks entitlement → EMP001 does have GitHub |
| `Help me with my tax return` | Out-of-scope → graceful refusal |

---

## Observability

- **Terminal**: All tool calls and agent iterations are logged to stdout.
- **Browser**: Click the **🔍 Trace** button in the top-right corner to see the agent's step-by-step execution (which tools were called, with what args, and what they returned).
- **API**: `GET /trace` returns the full structured log as JSON.

---

## Project Structure

```
deskmate/
├── main.py          # FastAPI app — routes, session management
├── llm.py           # Agentic loop — Mistral + tool-use
├── tools.py         # Tool implementations + Mistral schemas
├── mock_data.py     # In-memory mock IT systems
├── logger.py        # Structured logging + in-memory ring buffer
├── static/
│   └── index.html   # Chat UI (single-file, no build step)
├── requirements.txt
├── .env.example
├── DESIGN_NOTES.md  # Architecture decisions I'd defend in an interview
└── PRODUCTION_NOTE.md  # How I'd take this to production on Azure
```
