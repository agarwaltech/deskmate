<div align="center">

<img src="https://img.shields.io/badge/DeskMate-AI%20Helpdesk-6366f1?style=for-the-badge&logo=robot&logoColor=white" alt="DeskMate"/>

# 🤖 DeskMate
### AI-Powered IT Helpdesk Assistant

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-F55036?style=flat-square&logo=groq&logoColor=white)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**An agentic AI assistant that handles IT helpdesk queries end-to-end —**  
**from entitlement checks to ticket creation — using real LLM-powered reasoning.**

[Features](#-features) · [Architecture](#-architecture) · [Setup](#-setup) · [Demo](#-demo) · [Design Decisions](#-design-decisions)

---

![DeskMate Demo](https://img.shields.io/badge/Status-Working%20POC-brightgreen?style=for-the-badge)

</div>

---

## 🎯 What is DeskMate?

DeskMate is a proof-of-concept AI IT helpdesk assistant.  

An employee types a question in natural language. DeskMate:
1. **Understands** the intent using an LLM
2. **Decides** which internal IT systems to query
3. **Acts** — fetches data, creates tickets, resets passwords
4. **Responds** with something actionable

No rigid intent classifiers. No hardcoded flows. Pure agentic reasoning.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Agentic Loop** | LLM decides what tools to call and when — handles multi-step queries natively |
| 🔧 **6 IT Tools** | Entitlement checks, ticket creation, ticket lookup, password reset, user profiles, ticket listing |
| 💬 **Chat Interface** | Clean, real-time web UI with employee selector |
| 🔍 **Observable Execution** | Every tool call is traced and visible in the UI — full transparency |
| 🚫 **Scope Enforcement** | Gracefully refuses out-of-scope queries (HR, payroll, general knowledge) |
| ⚡ **Fast Responses** | Powered by Groq's LLaMA 3.1 — sub-second inference |
| 🛡️ **Error Handling** | Handles missing data, invalid inputs, tool failures, and rate limits |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Employee (Browser)                    │
│                    Chat Interface                        │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP POST /chat
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│            Session Management · Logging                  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Agentic Loop (llm.py)                       │
│                                                          │
│   1. Build messages (system + history + user turn)       │
│   2. Call Groq API with tool schemas                     │
│   3. If tool_calls → execute → append results → loop    │
│   4. If finish_reason = stop → return final answer       │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│              Tool Dispatcher (tools.py)                   │
│                                                           │
│  get_user_profile          check_software_entitlement     │
│  create_ticket             get_ticket_status              │
│  list_user_tickets         reset_password                 │
└──────────────┬────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│           Mock IT Systems (mock_data.py)                  │
│                                                           │
│   👤 User Directory    📦 Software Catalog               │
│   🎫 Ticket Store      (in-memory, mutable)              │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Setup

### Prerequisites
- Python 3.11+
- Free Groq API key from [console.groq.com](https://console.groq.com)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/deskmate.git
cd deskmate
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API key
Create a `.env` file in the project root:
```bash
echo GROQ_API_KEY=your_groq_key_here > .env
```
Get your free Groq API key from [console.groq.com](https://console.groq.com)
````

### 5. Run
```bash
python main.py
```

Open **http://localhost:8000** in your browser.

---

## 🎬 Demo

### Multi-step conditional request
```
Employee: I need access to Adobe Creative Suite — if I'm not entitled, raise a high-priority ticket

DeskMate: → check_software_entitlement(EMP001, "Adobe Creative Suite")
          → Not entitled. Available licenses: 5
          → create_ticket(EMP001, priority="high", ...)
          
          "You're not currently entitled to Adobe Creative Suite. I've raised 
           ticket TKT-1001 (high priority) on your behalf. Expected response: 2 hours."
```

### Password reset
```
Employee: I can't log into my account, reset my password

DeskMate: → reset_password(EMP001)
          
          "Done! A temporary password has been sent to alice.johnson@blackbox.com.
           You'll be required to change it on first login."
```

### Out-of-scope refusal
```
Employee: Can you help me negotiate my salary raise?

DeskMate: "That's outside what I can help with — salary discussions are handled 
           by your HR Business Partner. Is there anything IT-related I can assist with?"
```

---

## 📁 Project Structure

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
├── .env.example
```

---

## 🛠️ Tools Available

| Tool | Description |
|---|---|
| `get_user_profile` | Fetch employee name, department, role, entitlements |
| `check_software_entitlement` | Check if employee has access to specific software |
| `create_ticket` | Open a new IT support ticket with priority and category |
| `get_ticket_status` | Look up status and resolution of any ticket |
| `list_user_tickets` | List all tickets raised by an employee |
| `reset_password` | Reset employee password and issue temporary credential |

---

## 🔍 Observability

Every request is fully traceable:

- **Terminal** — all tool calls and iterations logged to stdout
- **UI Trace Panel** — click 🔍 Trace to see the agent's reasoning step by step
- **`GET /trace`** — full structured JSON log of all activity

---

## 💡 Design Decisions


**Why a tool-use loop instead of intent classification?**  
Multi-step queries like "check my entitlement and raise a ticket if I don't have it" require the model to make a conditional decision based on live data. A classifier can't do this — an agentic loop does it natively.

**Why Groq (LLaMA 3.1) instead of GPT-4?**  
Free tier, function calling support, and sub-second latency. The architecture is model-agnostic — swapping to GPT-4o or Claude is a 3-line change.

**Why in-memory mock data?**  
Zero setup — clone and run. The data shape maps directly to what real systems (ServiceNow, Okta, AD) would return. Production would use real API integrations.

---

## 🏭 Production Design


**TL;DR:** Azure Container Apps + Azure OpenAI + Azure AD (JWT auth) + Cosmos DB + Redis Cache + Azure Monitor.

---

## 📋 Sample Queries

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

Built with ❤️ for AI

**[FastAPI](https://fastapi.tiangolo.com) · [Groq](https://groq.com) · [LLaMA 3.1](https://llama.meta.com)**

</div>
