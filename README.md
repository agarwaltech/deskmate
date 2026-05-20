<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=6366f1&height=200&section=header&text=DeskMate&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=AI-Powered%20IT%20Helpdesk%20Assistant&descAlignY=55&descAlign=50" width="100%"/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-F55036?style=flat-square&logoColor=white)](https://groq.com)
[![Status](https://img.shields.io/badge/Status-Working%20POC-brightgreen?style=flat-square)](https://github.com/agarwaltech/deskmate)

**An agentic AI assistant that handles IT helpdesk queries end-to-end —**
**from entitlement checks to ticket creation — using real LLM-powered reasoning.**

</div>

---

## What is DeskMate?

DeskMate is a proof-of-concept AI IT helpdesk assistant .

An employee types a question in natural language. DeskMate:
1. **Understands** the intent using an LLM
2. **Decides** which internal IT systems to query
3. **Acts** — fetches data, creates tickets, resets passwords
4. **Responds** with something actionable

No rigid intent classifiers. No hardcoded flows. Pure agentic reasoning.

---

## Features

| Feature | Description |
|---|---|
| 🧠 **Agentic Loop** | LLM decides what tools to call and when — handles multi-step queries natively |
| 🔧 **6 IT Tools** | Entitlement checks, ticket creation, ticket lookup, password reset, user profiles, ticket listing |
| 💬 **Chat Interface** | Clean, real-time web UI with employee selector |
| 🔍 **Observable Execution** | Every tool call is traced and visible in the UI |
| 🚫 **Scope Enforcement** | Gracefully refuses out-of-scope queries |
| ⚡ **Fast Responses** | Powered by Groq LLaMA 3.1 — sub-second inference |
| 🛡️ **Error Handling** | Handles missing data, invalid inputs, and tool failures |

---

## Architecture

```
Employee (Browser)
       │
       ▼
FastAPI Backend  ──  Session Management + Logging
       │
       ▼
Agentic Loop (llm.py)
  1. Build messages (system + history + user turn)
  2. Call Groq API with tool schemas
  3. If tool_calls → execute → append results → loop
  4. If finish_reason = stop → return final answer
       │
       ▼
Tool Dispatcher (tools.py)
  get_user_profile        check_software_entitlement
  create_ticket           get_ticket_status
  list_user_tickets       reset_password
       │
       ▼
Mock IT Systems (mock_data.py)
  User Directory    Software Catalog    Ticket Store
```

---

## Setup

### Prerequisites
- Python 3.11+
- Free Groq API key from [console.groq.com](https://console.groq.com)

### 1. Clone the repository
```bash
git clone https://github.com/agarwaltech/deskmate.git
cd deskmate
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API key

Create a `.env` file in the project root:
```
GROQ_API_KEY="your_groq_key_here"
```
Get your free key from [console.groq.com](https://console.groq.com)

### 5. Run
```bash
python main.py
```

Open **http://localhost:8000** in your browser.

---

## Demo

### Multi-step conditional request
```
Employee: I need access to Adobe Creative Suite —
          if I'm not entitled, raise a high-priority ticket

DeskMate: → check_software_entitlement(EMP001, "Adobe Creative Suite")
          → Not entitled. Licenses available: 5
          → create_ticket(EMP001, priority="high")

          "You're not currently entitled to Adobe Creative Suite.
           Ticket TKT-1001 raised (high priority). Response in 2 hours."
```

### Password reset
```
Employee: I can't log into my account, reset my password

DeskMate: → reset_password(EMP001)

          "Done! Temporary password sent to alice.johnson@blackbox.com.
           Change it on first login."
```

### Out-of-scope refusal
```
Employee: Can you help me negotiate my salary raise?

DeskMate: "That's outside what I can help with — salary discussions
           are handled by your HR Business Partner."
```

---

## Project Structure

```
deskmate/
├── main.py              # FastAPI app — routes, session management
├── llm.py               # Agentic loop — Groq API + tool-use
├── tools.py             # 6 tool implementations + JSON schemas
├── mock_data.py         # In-memory mock IT systems
├── logger.py            # Structured logging + ring buffer
├── static/
│   └── index.html       # Chat UI — single file, no build step
├── requirements.txt
├── DESIGN_NOTES.md      # Architecture decisions
├── PRODUCTION_NOTE.md   # Azure production design
└── sample_transcript.md # End-to-end demo transcripts
```

---

## Tools Available

| Tool | Description |
|---|---|
| `get_user_profile` | Fetch employee name, department, role, entitlements |
| `check_software_entitlement` | Check if employee has access to specific software |
| `create_ticket` | Open a new IT support ticket with priority and category |
| `get_ticket_status` | Look up status and resolution of any ticket |
| `list_user_tickets` | List all tickets raised by an employee |
| `reset_password` | Reset employee password and issue temporary credential |

---

## Observability

Every request is fully traceable:

- **Terminal** — all tool calls and iterations logged to stdout
- **UI Trace Panel** — click Trace to see the agent's step-by-step reasoning
- **`GET /trace`** — full structured JSON log of all activity

---

## Design Decisions

See [DESIGN_NOTES.md](DESIGN_NOTES.md) for the full breakdown.

**Why a tool-use loop instead of intent classification?**
Multi-step queries require conditional decisions based on live data. A classifier can't do this — an agentic loop does it natively.

**Why Groq LLaMA 3.1?**
Free tier, function calling support, sub-second latency. Model is swappable in one line.

**Why in-memory mock data?**
Zero setup — clone and run. Data shapes map directly to real systems (ServiceNow, Okta, AD).

---

## Production Design

See [PRODUCTION_NOTE.md](PRODUCTION_NOTE.md) for the Azure production architecture.

**TL;DR:** Azure Container Apps + Azure OpenAI + Azure AD + Cosmos DB + Redis + Azure Monitor.

---

## Sample Queries

| Query | What happens |
|---|---|
| `I need Adobe Creative Suite access` | Checks entitlement → raises ticket if not entitled |
| `Reset my password` | Issues temporary credential via email |
| `What's the status of TKT-0990?` | Fetches ticket status and resolution |
| `Show me all my tickets` | Lists all tickets for current employee |
| `Do I have GitHub access?` | Checks entitlement → yes/no with details |
| `Help me with my taxes` | Graceful out-of-scope refusal |

---

<div align="center">


**[FastAPI](https://fastapi.tiangolo.com) · [Groq](https://groq.com) · [LLaMA 3.1](https://llama.meta.com)**

<img src="https://capsule-render.vercel.app/api?type=waving&color=6366f1&height=100&section=footer" width="100%"/>

</div>
