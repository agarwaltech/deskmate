"""
Mock data used by DeskMate.
Contains users, software list, and sample tickets.
"""

from datetime import datetime, timedelta

# User data
USERS = {
    "EMP001": {
        "employee_id": "EMP001",
        "name": "Bruce Wayne",
        "email": "bruce.wayne@gmail.com",
        "department": "Engineering",
        "role": "Software Engineer",
        "manager_id": "EMP010",
        "entitlements": ["Microsoft 365", "Slack", "GitHub", "Jira", "Zoom"],
        "active": True,
    },
    "EMP002": {
        "employee_id": "EMP002",
        "name": "Tony Stark",
        "email": "tony.stark@gmail.com",
        "department": "Marketing",
        "role": "Marketing Analyst",
        "manager_id": "EMP011",
        "entitlements": ["Microsoft 365", "Slack", "Zoom", "Adobe Creative Suite"],
        "active": True,
    },
    "EMP003": {
        "employee_id": "EMP003",
        "name": "Peter Parker",
        "email": "peter.parker@gmail.com",
        "department": "Finance",
        "role": "Financial Analyst",
        "manager_id": "EMP012",
        "entitlements": ["Microsoft 365", "Slack", "Zoom", "SAP"],
        "active": True,
    },
    "EMP004": {
        "employee_id": "EMP004",
        "name": "Clark Kent",
        "email": "clark.kent@gmail.com",
        "department": "HR",
        "role": "HR Specialist",
        "manager_id": "EMP013",
        "entitlements": ["Microsoft 365", "Slack", "Zoom", "Workday"],
        "active": True,
    },
    "EMP005": {
        "employee_id": "EMP005",
        "name": "Leonardo DiCaprio",
        "email": "leonardo.dicaprio@gmail.com",
        "department": "Engineering",
        "role": "DevOps Engineer",
        "manager_id": "EMP010",
        "entitlements": ["Microsoft 365", "Slack", "GitHub", "Jira", "Zoom", "AWS Console"],
        "active": True,
    },
}

# Software catalog
SOFTWARE_CATALOG = {
    "Adobe Creative Suite": {
        "name": "Adobe Creative Suite",
        "category": "Design",
        "approval_required": True,
        "approver_role": "Department Manager",
        "available_licenses": 5,
    },
    "Microsoft 365": {
        "name": "Microsoft 365",
        "category": "Productivity",
        "approval_required": False,
        "available_licenses": 100,
    },
    "Slack": {
        "name": "Slack",
        "category": "Communication",
        "approval_required": False,
        "available_licenses": 100,
    },
    "GitHub": {
        "name": "GitHub",
        "category": "Development",
        "approval_required": True,
        "approver_role": "Engineering Manager",
        "available_licenses": 30,
    },
    "Jira": {
        "name": "Jira",
        "category": "Project Management",
        "approval_required": False,
        "available_licenses": 50,
    },
    "Zoom": {
        "name": "Zoom",
        "category": "Communication",
        "approval_required": False,
        "available_licenses": 100,
    },
    "SAP": {
        "name": "SAP",
        "category": "ERP",
        "approval_required": True,
        "approver_role": "Finance Director",
        "available_licenses": 10,
    },
    "AWS Console": {
        "name": "AWS Console",
        "category": "Cloud Infrastructure",
        "approval_required": True,
        "approver_role": "CTO",
        "available_licenses": 20,
    },
    "Workday": {
        "name": "Workday",
        "category": "HR",
        "approval_required": True,
        "approver_role": "HR Director",
        "available_licenses": 15,
    },
    "Figma": {
        "name": "Figma",
        "category": "Design",
        "approval_required": True,
        "approver_role": "Design Lead",
        "available_licenses": 8,
    },
}

# Ticket data
_ticket_counter = [1000]


def _next_ticket_id() -> str:
    _ticket_counter[0] += 1
    return f"TKT-{_ticket_counter[0]}"


TICKETS: dict = {
    "TKT-0990": {
        "ticket_id": "TKT-0990",
        "employee_id": "EMP001",
        "title": "VPN not connecting from home",
        "description": "VPN stopped working after internet change.",
        "priority": "high",
        "status": "resolved",
        "category": "Network",
        "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "assigned_to": "L2-Network",
        "resolution": "Updated VPN settings and issue fixed.",
    },
    "TKT-0995": {
        "ticket_id": "TKT-0995",
        "employee_id": "EMP003",
        "title": "SAP access request — month-end closing",
        "description": "Need SAP FI module access for month-end closing activities.",
        "priority": "medium",
        "status": "in_progress",
        "category": "Software Access",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "updated_at": datetime.now().isoformat(),
        "assigned_to": "L1-Software",
        "resolution": None,
    },
    "TKT-0998": {
        "ticket_id": "TKT-0998",
        "employee_id": "EMP005",
        "title": "Laptop battery draining within 2 hours",
        "description": "MacBook Pro battery life dropped suddenly. Shows 'Service Recommended'.",
        "priority": "medium",
        "status": "open",
        "category": "Hardware",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "assigned_to": "L1-HelpDesk",
        "resolution": None,
    },
}
