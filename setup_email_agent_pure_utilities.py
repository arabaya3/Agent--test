#!/usr/bin/env python3
"""
Setup Email Agent with pure aiXplain Utility Models (no ngrok)
- Creates 4 Utility Models whose code runs on aiXplain and calls Microsoft Graph directly
- Each utility receives Microsoft app credentials and user_id as inputs
- Creates and deploys the Email Agent with these utilities attached

Inputs to utilities (pass at runtime or via agent tool calls):
- tenant_id, client_id, client_secret
- user_id (email or GUID)  # uses /users/{USER_ID}/..., never /me
- plus function-specific fields (start_date, end_date, sender, subject, email_ids)

Prereqs:
- AIXPLAIN_API_KEY set in environment
"""

import json
from datetime import datetime
from typing import List
from dotenv import load_dotenv

load_dotenv()

from aixplain.factories import ModelFactory, AgentFactory
from aixplain.enums import DataType
from aixplain.modules.model.utility_model import UtilityModelInput, utility_tool

GPT_4_ID = "669a63646eb56306647e1091"

# ---------------- Utility code (executed on aiXplain) ----------------

def _get_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    import requests
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    resp = requests.post(url, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def _graph_get(url: str, token: str, headers_extra=None):
    import requests
    headers = {"Authorization": f"Bearer {token}"}
    if headers_extra:
        headers.update(headers_extra)
    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


@utility_tool(
    name="email_date_range",
    description="Return emails between start_date and end_date (YYYY-MM-DD)",
    inputs=[
        UtilityModelInput(name="tenant_id", description="Azure AD tenant ID", type=DataType.TEXT),
        UtilityModelInput(name="client_id", description="Microsoft app (client) ID", type=DataType.TEXT),
        UtilityModelInput(name="client_secret", description="Microsoft app client secret", type=DataType.TEXT),
        UtilityModelInput(name="user_id", description="Graph user identifier (/users/{USER_ID})", type=DataType.TEXT),
        UtilityModelInput(name="start_date", description="Start date YYYY-MM-DD", type=DataType.TEXT),
        UtilityModelInput(name="end_date", description="End date YYYY-MM-DD", type=DataType.TEXT),
    ],
)
def email_by_date_range_main(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    user_id: str,
    start_date: str,
    end_date: str,
):
    """Return emails for a date range. Dates in YYYY-MM-DD."""
    token = _get_token(tenant_id, client_id, client_secret)
    start_dt = f"{start_date}T00:00:00Z"
    end_dt = f"{end_date}T23:59:59Z"
    url = (
        "https://graph.microsoft.com/v1.0/users/"
        f"{user_id}/messages?$top=50&$orderby=receivedDateTime desc&"
        f"$filter=receivedDateTime ge {start_dt} and receivedDateTime le {end_dt}"
    )
    data = _graph_get(url, token)
    items = data.get("value", [])
    return {
        "count": len(items),
        "summary": f"Found {len(items)} emails between {start_date} and {end_date}",
        "items": items,
        "analysis": "",
    }


@utility_tool(
    name="email_sender_date",
    description="Return emails from sender on date (YYYY-MM-DD)",
    inputs=[
        UtilityModelInput(name="tenant_id", description="Azure AD tenant ID", type=DataType.TEXT),
        UtilityModelInput(name="client_id", description="Microsoft app (client) ID", type=DataType.TEXT),
        UtilityModelInput(name="client_secret", description="Microsoft app client secret", type=DataType.TEXT),
        UtilityModelInput(name="user_id", description="Graph user identifier (/users/{USER_ID})", type=DataType.TEXT),
        UtilityModelInput(name="sender", description="Sender email address", type=DataType.TEXT),
        UtilityModelInput(name="date", description="Date YYYY-MM-DD", type=DataType.TEXT),
    ],
)
def email_by_sender_date_main(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    user_id: str,
    sender: str,
    date: str,
):
    """Return emails from a sender on a date (YYYY-MM-DD)."""
    token = _get_token(tenant_id, client_id, client_secret)
    start_dt = f"{date}T00:00:00Z"
    end_dt = f"{date}T23:59:59Z"
    # Filter on from address and date range
    # Using headers for advanced query if needed
    filter_q = (
        f"from/emailAddress/address eq '{sender}' and "
        f"receivedDateTime ge {start_dt} and receivedDateTime le {end_dt}"
    )
    url = (
        "https://graph.microsoft.com/v1.0/users/"
        f"{user_id}/messages?$top=50&$orderby=receivedDateTime desc&$filter={filter_q}"
    )
    data = _graph_get(url, token)
    items = data.get("value", [])
    return {
        "count": len(items),
        "summary": f"Found {len(items)} emails from {sender} on {date}",
        "items": items,
        "analysis": "",
    }


@utility_tool(
    name="email_subject_range",
    description="Search emails by subject within a date range",
    inputs=[
        UtilityModelInput(name="tenant_id", description="Azure AD tenant ID", type=DataType.TEXT),
        UtilityModelInput(name="client_id", description="Microsoft app (client) ID", type=DataType.TEXT),
        UtilityModelInput(name="client_secret", description="Microsoft app client secret", type=DataType.TEXT),
        UtilityModelInput(name="user_id", description="Graph user identifier (/users/{USER_ID})", type=DataType.TEXT),
        UtilityModelInput(name="subject", description="Subject keyword", type=DataType.TEXT),
        UtilityModelInput(name="start_date", description="Start date YYYY-MM-DD", type=DataType.TEXT),
        UtilityModelInput(name="end_date", description="End date YYYY-MM-DD", type=DataType.TEXT),
    ],
)
def email_by_subject_date_range_main(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    user_id: str,
    subject: str,
    start_date: str,
    end_date: str,
):
    """Search by subject text within a date range."""
    token = _get_token(tenant_id, client_id, client_secret)
    # Use $search for subject, then client-side filter by date
    url = (
        "https://graph.microsoft.com/v1.0/users/"
        f"{user_id}/messages?$top=50&$search=\"subject:{subject}\"&$orderby=receivedDateTime desc"
    )
    data = _graph_get(url, token, headers_extra={"ConsistencyLevel": "eventual"})
    items = data.get("value", [])

    # Client-side date filter
    from datetime import datetime as _dt
    filtered: List[dict] = []
    start_dt = _dt.fromisoformat(f"{start_date}T00:00:00+00:00")
    end_dt = _dt.fromisoformat(f"{end_date}T23:59:59+00:00")
    for it in items:
        ts = it.get("receivedDateTime") or it.get("createdDateTime")
        if not ts:
            continue
        try:
            t = _dt.fromisoformat(ts.replace("Z", "+00:00"))
            if start_dt <= t <= end_dt:
                filtered.append(it)
        except Exception:
            pass

    return {
        "count": len(filtered),
        "summary": f"Found {len(filtered)} emails with subject '{subject}' between {start_date} and {end_date}",
        "items": filtered,
        "analysis": "",
    }


@utility_tool(
    name="email_ids",
    description="Retrieve emails by IDs provided as a JSON array string",
    inputs=[
        UtilityModelInput(name="tenant_id", description="Azure AD tenant ID", type=DataType.TEXT),
        UtilityModelInput(name="client_id", description="Microsoft app (client) ID", type=DataType.TEXT),
        UtilityModelInput(name="client_secret", description="Microsoft app client secret", type=DataType.TEXT),
        UtilityModelInput(name="user_id", description="Graph user identifier (/users/{USER_ID})", type=DataType.TEXT),
        UtilityModelInput(name="email_ids_json", description="JSON array string of email IDs", type=DataType.TEXT),
    ],
)
def email_by_ids_main(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    user_id: str,
    email_ids_json: str,
):
    """Retrieve emails by IDs. email_ids_json is a JSON array string."""
    import json as _json
    token = _get_token(tenant_id, client_id, client_secret)
    try:
        email_ids = _json.loads(email_ids_json)
    except Exception:
        email_ids = []
    items: List[dict] = []
    for eid in email_ids:
        url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{eid}"
        try:
            data = _graph_get(url, token)
            items.append(data)
        except Exception as e:
            items.append({"id": eid, "error": str(e)})

    return {
        "count": len([i for i in items if 'error' not in i]),
        "summary": f"Retrieved {len(items)} emails by ID",
        "items": items,
        "analysis": "",
    }


# ---------------- Orchestration ----------------

def create_and_deploy_utility(name: str, func, inputs, description: str = ""):
    util = ModelFactory.create_utility_model(
        name=name,
        code=func,
        inputs=inputs,
        description=description,
    )
    util.deploy()
    print(f"✓ Utility created & deployed: {name} → {util.id}")
    return util


def build_email_agent_with_pure_utilities():
    llm = ModelFactory.get(GPT_4_ID)
    try:
        llm.model_params.temperature = 0.1
        llm.model_params.max_tokens = 2000
        llm.model_params.top_p = 0.9
    except Exception:
        pass

    print("Creating Utility Models (direct Graph API)...")
    common_creds = [
        UtilityModelInput(name="tenant_id", type=DataType.TEXT, description="Azure AD tenant ID"),
        UtilityModelInput(name="client_id", type=DataType.TEXT, description="Microsoft app (client) ID"),
        UtilityModelInput(name="client_secret", type=DataType.TEXT, description="Microsoft app client secret"),
        UtilityModelInput(name="user_id", type=DataType.TEXT, description="Graph user identifier (/users/{USER_ID})"),
    ]

    u_date_range = create_and_deploy_utility(
        "email_date_range",
        email_by_date_range_main,
        inputs=common_creds + [
            UtilityModelInput(name="start_date", type=DataType.TEXT, description="Start date YYYY-MM-DD"),
            UtilityModelInput(name="end_date", type=DataType.TEXT, description="End date YYYY-MM-DD"),
        ],
        description="Return emails between start_date and end_date (YYYY-MM-DD)",
    )

    u_sender_date = create_and_deploy_utility(
        "email_sender_date",
        email_by_sender_date_main,
        inputs=common_creds + [
            UtilityModelInput(name="sender", type=DataType.TEXT, description="Sender email address"),
            UtilityModelInput(name="date", type=DataType.TEXT, description="Date YYYY-MM-DD"),
        ],
        description="Return emails from 'sender' on 'date' (YYYY-MM-DD)",
    )

    u_subject_range = create_and_deploy_utility(
        "email_subject_range",
        email_by_subject_date_range_main,
        inputs=common_creds + [
            UtilityModelInput(name="subject", type=DataType.TEXT, description="Subject keyword"),
            UtilityModelInput(name="start_date", type=DataType.TEXT, description="Start date YYYY-MM-DD"),
            UtilityModelInput(name="end_date", type=DataType.TEXT, description="End date YYYY-MM-DD"),
        ],
        description="Search emails by subject text within a date range",
    )

    u_by_ids = create_and_deploy_utility(
        "email_ids",
        email_by_ids_main,
        inputs=common_creds + [
            UtilityModelInput(name="email_ids_json", type=DataType.TEXT, description="JSON array string of email IDs e.g. [\"id1\",\"id2\"]"),
        ],
        description="Retrieve emails by IDs; email_ids_json is a JSON array string",
    )

    instructions = (
        "You are the Email Agent using Microsoft Graph API (application permissions).\n"
        "Always use /users/{USER_ID}/..., never /me.\n"
        "Call tools to fetch real data and return JSON: count, summary, items, analysis."
    )

    print("Creating and deploying Email Agent...")
    agent = AgentFactory.create(
        name="Core Assistant Email Agent",
        description="Email management via Microsoft Graph (no webhooks)",
        instructions=instructions,
        llm=llm,
        tools=[
            AgentFactory.create_model_tool(model=u_date_range.id),
            AgentFactory.create_model_tool(model=u_sender_date.id),
            AgentFactory.create_model_tool(model=u_subject_range.id),
            AgentFactory.create_model_tool(model=u_by_ids.id),
        ],
    )
    agent.deploy()

    info = {
        "agent_id": agent.id,
        "utilities": {
            "email_date_range": u_date_range.id,
            "email_sender_date": u_sender_date.id,
            "email_subject_range": u_subject_range.id,
            "email_ids": u_by_ids.id,
        },
        "api_url": f"https://platform-api.aixplain.com/sdk/agents/{agent.id}/run",
        "dashboard_url": f"https://platform.aixplain.com/discover/agent/{agent.id}",
        "created_at": datetime.now().isoformat(),
    }
    with open("email_agent_info.json", "w") as f:
        json.dump(info, f, indent=2)

    print("\n✓ Email Agent created and deployed")
    print(f"Agent ID: {agent.id}")
    print(f"Dashboard: {info['dashboard_url']}")
    return agent


if __name__ == "__main__":
    build_email_agent_with_pure_utilities()
