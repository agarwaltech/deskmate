"""
Handles LLM calls and tool execution for DeskMate.
"""

import json
import os
import time
import httpx
from tools import TOOL_SCHEMAS, dispatch_tool
import logger

MODEL = "llama-3.1-8b-instant"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """\
You are DeskMate, an AI-powered IT helpdesk assistant for Black Box Network Services.

You help employees with:
- Software access requests and entitlement checks
- Password resets
- VPN and network troubleshooting guidance
- IT support ticket creation and status lookups
- Hardware issues
- General IT queries

RULES — follow these strictly:
1. SCOPE: Only handle IT helpdesk topics. For anything else (HR policies, payroll, \
personal advice, general knowledge), politely decline and redirect to the appropriate team.
2. TOOL-FIRST: Only call tools when the user is explicitly requesting an action or \
information. Short replies like "thanks", "ok", "what?", "really?", "and?" are \
acknowledgements — respond conversationally, do NOT call any tools or repeat previous actions.
3. TICKET INFO: Before creating any ticket, you MUST have a clear description of the \
issue from the user. If the user says "create a ticket" without explaining the problem, \
ask "Sure, could you briefly describe the issue so I can log it accurately?" \
Never create a ticket with a vague or missing description.
4. MULTI-STEP: For requests like "request access if I don't have it", check entitlement \
first, then decide whether to raise a ticket based on the result.
5. TRANSPARENCY: When you create a ticket, always tell the employee the ticket ID and \
expected response time.
6. ERRORS: If a tool returns an error, tell the employee clearly what went wrong.
7. TONE: Concise, professional, friendly. No jargon.
8. PRIVACY: Never list or summarize tickets, entitlements, or profile data belonging \
to other employees. If asked about other employees data, decline and say this \
information is confidential.
9. FAREWELLS AND ACKNOWLEDGEMENTS: For "thanks", "thank you", "ok", "great", "bye", \
"exit", "goodbye" — respond with a short friendly message only. \
Never call tools or repeat previous actions for these messages.
10. VALIDATION: If the user message appears to be random characters, keyboard spam, \
or gibberish, do not call any tools. Politely ask them to clarify their IT issue.\
"""


def _call_groq(messages: list, api_key: str) -> dict:
    """Call Groq API with automatic retry on rate limit."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOL_SCHEMAS,
        "tool_choice": "auto",
        "temperature": 0.2,
    }
    for attempt in range(4):
        with httpx.Client(timeout=60) as client:
            resp = client.post(GROQ_API_URL, headers=headers, json=payload)
            if resp.status_code == 429:
                wait = 20 * (attempt + 1)
                logger.log(f"[Agent] Rate limited, waiting {wait}s before retry {attempt+1}/4...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
    raise RuntimeError("Rate limit exceeded after retries. Please wait a minute and try again.")


def run_agent(
    user_message: str,
    conversation_history: list,
    employee_id: str = "EMP001",
) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is not set.")

    augmented_message = f"[Employee ID: {employee_id}]\n{user_message}"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": augmented_message})

    trace = []
    MAX_ITERATIONS = 10

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.log(f"[Agent] Iteration {iteration} — calling Groq API")

        data = _call_groq(messages, api_key)

        choice = data["choices"][0]
        finish_reason = choice["finish_reason"]
        assistant_msg = choice["message"]
        tool_calls = assistant_msg.get("tool_calls") or []

        step = {"iteration": iteration, "finish_reason": finish_reason, "tool_calls": []}

        msg_dict = {"role": "assistant", "content": assistant_msg.get("content") or ""}
        if tool_calls:
            msg_dict["tool_calls"] = tool_calls
        messages.append(msg_dict)

        if not tool_calls or finish_reason == "stop":
            trace.append(step)
            logger.log(f"[Agent] Done after {iteration} iteration(s)")
            return {
                "response": assistant_msg.get("content") or "(No response generated)",
                "trace": trace,
            }

        for tc in tool_calls:
            tool_name = tc["function"]["name"]
            try:
                arguments = json.loads(tc["function"]["arguments"])
            except (json.JSONDecodeError, KeyError):
                arguments = {}

            logger.log(f"[Tool →] {tool_name}({json.dumps(arguments)})")
            result_str = dispatch_tool(tool_name, arguments)
            result_obj = json.loads(result_str)
            logger.log(f"[Tool ←] {tool_name} → {result_str[:200]}")

            step["tool_calls"].append({
                "tool": tool_name,
                "arguments": arguments,
                "result": result_obj,
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "name": tool_name,
                "content": result_str,
            })

        trace.append(step)

    logger.log("[Agent] Max iterations reached", level="warning")
    return {
        "response": (
            "I've run into an issue processing your request. "
            "Please try rephrasing, or contact helpdesk@blackbox.com directly."
        ),
        "trace": trace,
    }