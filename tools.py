"""
Helper tools used by DeskMate.
Contains ticket handling, entitlement checks,
password reset logic, and tool dispatcher functions.
"""

import json
import random
import string
from datetime import datetime
from mock_data import USERS, SOFTWARE_CATALOG, TICKETS, _next_ticket_id


# Helper functions

def _match_software(name: str) -> str | None:
    """Case-insensitive partial match against catalog keys."""
    name_lower = name.lower()
    for key in SOFTWARE_CATALOG:
        if name_lower in key.lower() or key.lower() in name_lower:
            return key
    return None


# Ticket operations

def get_user_profile(employee_id: str) -> dict:
    """Return employee profile (name, dept, role, entitlements)."""
    user = USERS.get(employee_id.upper())
    if not user:
        return {"error": f"No employee found with ID '{employee_id}'. Check the ID and try again."}
    if not user["active"]:
        return {"error": f"Employee {employee_id} account is inactive. Contact HR."}
    return {
        "employee_id": user["employee_id"],
        "name": user["name"],
        "email": user["email"],
        "department": user["department"],
        "role": user["role"],
        "active": user["active"],
        "current_entitlements": user["entitlements"],
    }


def check_software_entitlement(employee_id: str, software_name: str) -> dict:
    """Check if an employee has a software entitlement; return catalog info too."""
    user = USERS.get(employee_id.upper())
    if not user:
        return {"error": f"Employee '{employee_id}' not found."}

    matched = _match_software(software_name)
    if not matched:
        return {
            "error": f"Software '{software_name}' not found in the catalog.",
            "available_software": list(SOFTWARE_CATALOG.keys()),
        }

    sw = SOFTWARE_CATALOG[matched]
    entitled = matched in user["entitlements"]

    return {
        "employee_id": employee_id,
        "employee_name": user["name"],
        "software": matched,
        "entitled": entitled,
        "approval_required": sw["approval_required"],
        "approver_role": sw.get("approver_role", "IT Admin"),
        "available_licenses": sw["available_licenses"],
        "cost_per_seat_usd": sw["cost_per_seat_usd"],
    }


def create_ticket(
    employee_id: str,
    title: str,
    priority: str,
    description: str,
    category: str = "General",
) -> dict:
    """Create a helpdesk ticket."""
    user = USERS.get(employee_id.upper())
    if not user:
        return {"error": f"Employee '{employee_id}' not found. Cannot create ticket."}

    priority = priority.lower()
    if priority not in ("low", "medium", "high", "critical"):
        priority = "medium"

    ticket_id = _next_ticket_id()
    now = datetime.now().isoformat()
    sla = {"low": "5 business days", "medium": "24 hours", "high": "2 hours", "critical": "30 minutes"}

    ticket = {
        "ticket_id": ticket_id,
        "employee_id": employee_id.upper(),
        "title": title,
        "description": description,
        "priority": priority,
        "status": "open",
        "category": category,
        "created_at": now,
        "updated_at": now,
        "assigned_to": "L1-HelpDesk",
        "resolution": None,
    }
    TICKETS[ticket_id] = ticket

    return {
        "ticket_id": ticket_id,
        "status": "open",
        "priority": priority,
        "category": category,
        "assigned_to": "L1-HelpDesk",
        "estimated_response_time": sla[priority],
        "message": f"Ticket {ticket_id} created successfully for {user['name']}.",
    }


def get_ticket_status(ticket_id: str) -> dict:
    """Fetch status and details of an existing support ticket."""
    ticket = TICKETS.get(ticket_id.upper())
    if not ticket:
        return {"error": f"Ticket '{ticket_id}' not found. Check the ticket ID."}
    return {
        "ticket_id": ticket["ticket_id"],
        "title": ticket["title"],
        "status": ticket["status"],
        "priority": ticket["priority"],
        "category": ticket["category"],
        "assigned_to": ticket["assigned_to"],
        "created_at": ticket["created_at"],
        "updated_at": ticket["updated_at"],
        "resolution": ticket["resolution"],
    }


def list_user_tickets(employee_id: str) -> dict:
    """List all support tickets raised by an employee."""
    user = USERS.get(employee_id.upper())
    if not user:
        return {"error": f"Employee '{employee_id}' not found."}

    user_tickets = [
        {
            "ticket_id": t["ticket_id"],
            "title": t["title"],
            "status": t["status"],
            "priority": t["priority"],
            "category": t["category"],
            "created_at": t["created_at"],
        }
        for t in TICKETS.values()
        if t["employee_id"] == employee_id.upper()
    ]

    return {
        "employee_id": employee_id,
        "employee_name": user["name"],
        "total_tickets": len(user_tickets),
        "tickets": user_tickets,
    }


def reset_password(employee_id: str) -> dict:
    """Reset employee password."""
    user = USERS.get(employee_id.upper())
    if not user:
        return {"error": f"Employee '{employee_id}' not found."}

    chars = string.ascii_letters + string.digits + "!@#$"
    temp_pw = "".join(random.choices(chars, k=14))

    return {
        "employee_id": employee_id,
        "name": user["name"],
        "status": "success",
        "temporary_password": temp_pw,
        "note": (
            f"Temporary password issued. An email with login instructions has been "
            f"sent to {user['email']}. Password must be changed on first login."
        ),
    }


# Tool schemas for LLM

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": (
                "Retrieve an employee's profile from the HR/IT directory: "
                "name, department, role, email, and list of currently entitled software. "
                "Call this first when you need to know who the employee is or what they already have."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Employee ID, e.g. EMP001",
                    }
                },
                "required": ["employee_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_software_entitlement",
            "description": (
                "Check whether an employee is currently entitled to a specific software application. "
                "Also returns whether approval is required and how many licenses are available."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID"},
                    "software_name": {
                        "type": "string",
                        "description": "Name of the software, e.g. 'Adobe Creative Suite', 'GitHub'",
                    },
                },
                "required": ["employee_id", "software_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": (
                "Open a new IT helpdesk support ticket for an employee. "
                "Use this for software access requests, hardware issues, network problems, "
                "password resets needing L2 attention, or any issue that needs tracking."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string"},
                    "title": {
                        "type": "string",
                        "description": "Short descriptive title for the ticket",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Ticket priority. Use 'high' for access blockers or business-critical issues.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue or request",
                    },
                    "category": {
                        "type": "string",
                        "description": "Category: 'Software Access', 'Hardware', 'Network', 'Password Reset', 'General'",
                    },
                },
                "required": ["employee_id", "title", "priority", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_ticket_status",
            "description": "Get the current status, assignment, and resolution details of an IT support ticket by ticket ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID, e.g. TKT-1001",
                    }
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_user_tickets",
            "description": "List all IT support tickets raised by a specific employee.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID"}
                },
                "required": ["employee_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reset_password",
            "description": (
                "Reset an employee's network/system password and generate a temporary credential. "
                "The employee will receive login instructions by email."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID"}
                },
                "required": ["employee_id"],
            },
        },
    },
]

# Tool dispatcher

_TOOL_FUNCTIONS = {
    "get_user_profile": get_user_profile,
    "check_software_entitlement": check_software_entitlement,
    "create_ticket": create_ticket,
    "get_ticket_status": get_ticket_status,
    "list_user_tickets": list_user_tickets,
    "reset_password": reset_password,
}


def dispatch_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool by name and return JSON string result."""
    func = _TOOL_FUNCTIONS.get(tool_name)
    if not func:
        return json.dumps({"error": f"Unknown tool: '{tool_name}'"})
    try:
        result = func(**arguments)
        return json.dumps(result, default=str)
    except TypeError as e:
        return json.dumps({"error": f"Invalid arguments for {tool_name}: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Tool '{tool_name}' failed: {e}"})
