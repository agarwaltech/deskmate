# Design Notes : DeskMate

*The decisions I made and why. Keeping it honest.*


## Why an agentic loop and not intent classification

My first instinct was to classify the intent and route it to a handler. But the example query in the spec killed that idea fast "request Adobe if I'm not entitled" needs the system to check entitlement first, then decide whether to raise a ticket based on the result. You can't hardcode that branching for every possible combination. An agentic loop handles it naturally because the LLM is making the decision, not a switch statement.

The downside is latency: multiple API round trips add up. For a helpdesk POC that's fine. For production I'd look at streaming responses so the user sees something happening immediately.


## Why Groq + LLaMA 3.1 and not GPT-4

Purely practical as Groq's free tier supports function calling and responds in under a second. The architecture doesn't care which model is underneath. Swapping to GPT-4o or Azure OpenAI is literally changing one line in `llm.py`. I chose the model that lets me demo without a credit card, not the one that sounds impressive.


## Why in-memory mock data

The spec said mocks with realistic data shapes. In-memory dicts give me zero setup, clone and run. The data structure mirrors what ServiceNow and Okta would actually return, so the tool contracts are realistic even if the backend isn't. Tickets created during a session persist until restart, which is enough for a demo.


## Why conversation history is capped at 20 messages

Every API call sends the full history. Without a cap you eventually hit the context window limit or run up costs. 20 messages is 10 exchanges which is more than enough for any realistic helpdesk conversation.


## The scope boundary is soft, not hard

The system prompt tells the model to refuse out of scope queries. That's a prompt level guardrail, not a code level one. It works well enough for a POC. In production I'd add a preclassification step that rejects off topic queries before they even reach the LLM saves tokens and is harder to jailbreak.


## Observability

Three levels : terminal logs for development, an in-memory ring buffer exposed at `/trace` for inspection, and a trace panel in the UI that shows every tool call step by step. No external infrastructure needed. Production would replace this with Azure Monitor and OpenTelemetry.


## What I'd do differently in production

| This POC | Production |
| Dropdown for employee ID | Azure AD JWT token — identity from auth, not client |
| In-memory sessions | Redis with TTL |
| Mock IT systems | ServiceNow API + Okta + Microsoft Graph |
| Single process | Azure Container Apps |
| Prompt-only scope guard | Pre-classifier + prompt |
| Stdout logs | Azure Monitor + App Insights |