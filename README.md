# 🤖 DeskMate — AI-Powered IT Helpdesk Assistant

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-F55036?style=flat-square&logo=groq&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

An **agentic AI IT-helpdesk assistant**. An employee types a request in natural language; DeskMate uses an LLM tool-calling loop to decide which internal IT systems to query, performs the actions (entitlement checks, ticket creation, password resets), and replies with something actionable — no hardcoded intent classifiers.

---

## ✨ Features

- **Agentic tool-calling loop** — the LLM decides which tools to call and when, natively handling multi-step conditional requests (e.g. *"request Adobe if I'm not entitled"*).
- **6 IT tools** — user profile, software-entitlement check, ticket create / status / list, and password reset.
- **Web chat UI** — single-file frontend with an employee selector and a live agent-trace panel.
- **Full observability** — every tool call is traced to an in-memory ring buffer and exposed at `GET /trace`.
- **Scope & privacy guardrails** — a 10-rule system prompt refuses out-of-scope (HR/payroll/general) queries and blocks access to other employees' data.
- **Resilient** — automatic rate-limit retry with exponential backoff, per-tool error handling, and capped session memory.

---

## 🏗️ Architecture

```
Browser (chat UI)  →  FastAPI  →  Agentic Loop (llm.py)  →  Tool Dispatcher (tools.py)  →  Mock IT Systems (mock_data.py)
                                      │
                                 Groq API (LLaMA 3.1)
```

**Agentic loop:** builds messages (system prompt + history + user turn) → calls Groq with the tool schemas → if the model returns `tool_calls`, executes them, appends results, and loops (up to 10 iterations) → returns the final answer when the model stops.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI + Uvicorn |
| **LLM** | Groq API — `llama-3.1-8b-instant` (called via `httpx`, OpenAI-compatible endpoint) |
| **Validation** | Pydantic |
| **Frontend** | Single-file HTML / CSS / JS chat UI |
| **State & logs** | In-memory sessions + a `deque` ring-buffer logger |

---

## 🔧 Tools Available

| Tool | Description |
|---|---|
| `get_user_profile` | Fetch employee name, department, role, email, and current entitlements |
| `check_software_entitlement` | Check access to a specific app + approval requirement and license count |
| `create_ticket` | Open an IT ticket with title, priority, description, and category |
| `get_ticket_status` | Look up status, assignment, and resolution of a ticket |
| `list_user_tickets` | List all tickets raised by an employee |
| `reset_password` | Reset a password and issue a temporary credential |

---

## 🌐 API Endpoints

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Serve the chat UI |
| `POST` | `/chat` | Send a message; returns the agent's response + execution trace |
| `GET` | `/trace` | Full structured log of recent activity |
| `GET` | `/employees` | List demo employees (populates the UI selector) |
| `DELETE` | `/session/{session_id}` | Clear a session's conversation history |
| `GET` | `/health` | Health check |

---

## 🚀 Setup

**Prerequisites:** Python 3.11+ and a free Groq API key from [console.groq.com](https://console.groq.com).

```bash
# 1. Create & activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key to a .env file in the project root
echo GROQ_API_KEY=your_key_here > .env

# 4. Run
python main.py
```

Open **http://localhost:8000** in your browser.

> **Dependencies:** `fastapi`, `uvicorn[standard]`, `httpx`, `python-dotenv`, `pydantic`.

---

## 📁 Project Structure

```
deskmate/
├── main.py            # FastAPI app — routes, session management
├── llm.py             # Agentic loop — Groq API call + tool execution
├── tools.py           # 6 tool implementations + JSON schemas + dispatcher
├── mock_data.py       # In-memory users, software catalog, seed tickets
├── logger.py          # In-memory ring-buffer logger (exposed at /trace)
├── static/
│   └── index.html     # Single-file chat UI
├── requirements.txt
└── .env               # GROQ_API_KEY (not committed)
```

---

## 💡 Design Notes

- **Why a tool-calling loop, not intent classification?** Conditional multi-step queries (*"check entitlement, then raise a ticket if I'm not entitled"*) require a decision based on live data — an agentic loop does this natively; a classifier can't.
- **Why Groq + LLaMA 3.1?** Free tier, function-calling support, and sub-second latency. The design is model-agnostic — swapping to another provider is a small change in `llm.py`.
- **Why in-memory mock data?** Zero setup — clone and run. The data shapes mirror what real systems (ServiceNow, Okta, AD) would return.

---

## 📄 License

MIT
