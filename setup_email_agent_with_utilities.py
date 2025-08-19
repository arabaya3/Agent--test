#!/usr/bin/env python3
"""
Setup Email Agent using aiXplain Utility Models
- Creates 4 Utility Models that proxy to your FastAPI endpoints
- Creates the Email Agent and attaches these utilities as tools
- Deploys the agent and saves info to email_agent_info.json

Prerequisites:
- Public API base URL in env: AIXPLAIN_PUBLIC_API_BASE (e.g., https://<ngrok-id>.ngrok-free.app)
- AIXPLAIN_API_KEY in env
- FastAPI server running locally and exposed via ngrok
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

from aixplain.factories import ModelFactory, AgentFactory

GPT_4_ID = "669a63646eb56306647e1091"


def require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"Environment variable '{var_name}' is required but not set.")
    return value


# -------- Utility model functions (code executed on aiXplain) --------
# Each function reads AIXPLAIN_PUBLIC_API_BASE at runtime in aiXplain cloud

def email_by_date_range_main(inputs: Dict[str, Any]):
    import os, requests
    base = os.getenv("AIXPLAIN_PUBLIC_API_BASE")
    if not base:
        raise ValueError("AIXPLAIN_PUBLIC_API_BASE not set")
    url = f"{base}/email/by-date-range"
    payload = {
        "start_date": inputs.get("start_date"),
        "end_date": inputs.get("end_date"),
        "user_id": inputs.get("user_id"),
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def email_by_sender_date_main(inputs: Dict[str, Any]):
    import os, requests
    base = os.getenv("AIXPLAIN_PUBLIC_API_BASE")
    if not base:
        raise ValueError("AIXPLAIN_PUBLIC_API_BASE not set")
    url = f"{base}/email/by-sender-date"
    payload = {
        "sender": inputs.get("sender"),
        "date": inputs.get("date"),
        "user_id": inputs.get("user_id"),
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def email_by_subject_date_range_main(inputs: Dict[str, Any]):
    import os, requests
    base = os.getenv("AIXPLAIN_PUBLIC_API_BASE")
    if not base:
        raise ValueError("AIXPLAIN_PUBLIC_API_BASE not set")
    url = f"{base}/email/by-subject-date-range"
    payload = {
        "subject": inputs.get("subject"),
        "start_date": inputs.get("start_date"),
        "end_date": inputs.get("end_date"),
        "user_id": inputs.get("user_id"),
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def email_by_ids_main(inputs: Dict[str, Any]):
    import os, requests
    base = os.getenv("AIXPLAIN_PUBLIC_API_BASE")
    if not base:
        raise ValueError("AIXPLAIN_PUBLIC_API_BASE not set")
    url = f"{base}/email/by-ids"
    payload = {
        "email_ids": inputs.get("email_ids"),
        "user_id": inputs.get("user_id"),
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


# -------- Orchestration helpers --------

def create_and_deploy_utility(name: str, func):
    util = ModelFactory.create_utility_model(name=name, code=func)
    util.deploy()
    print(f"✓ Utility created & deployed: {name} → {util.id}")
    return util


def build_email_agent_with_utilities():
    # Ensure required env exists before we create anything
    require_env("AIXPLAIN_API_KEY")
    public_base = require_env("AIXPLAIN_PUBLIC_API_BASE")
    if not public_base.startswith("https://"):
        raise ValueError("AIXPLAIN_PUBLIC_API_BASE must be a public HTTPS URL (e.g., ngrok https URL)")

    print("Creating Utility Models (proxy to your FastAPI endpoints)...")
    u_date_range = create_and_deploy_utility("email_by_date_range", email_by_date_range_main)
    u_sender_date = create_and_deploy_utility("email_by_sender_date", email_by_sender_date_main)
    u_subject_range = create_and_deploy_utility("email_by_subject_date_range", email_by_subject_date_range_main)
    u_by_ids = create_and_deploy_utility("email_by_ids", email_by_ids_main)

    print("Configuring LLM (GPT-4) for the agent...")
    llm = ModelFactory.get(GPT_4_ID)
    try:
        llm.model_params.temperature = 0.1
        llm.model_params.max_tokens = 2000
        llm.model_params.top_p = 0.9
    except Exception:
        pass

    instructions = (
        "You are the Email Agent, specialized in email management and analysis using Microsoft Graph API with "
        "application permissions.\n\n"
        "CORE RULES:\n"
        "- ALWAYS use /users/{USER_ID}/... endpoints, NEVER use /me endpoints\n"
        "- Parse relative dates (today, yesterday, last week) to YYYY-MM-DD format\n"
        "- Always call tools to get data; never fabricate email information\n"
        "- Return structured responses with count, summary, and items\n"
        "- Handle natural language queries intelligently\n\n"
        "RESPONSE FORMAT:\n"
        "Return JSON with keys: count, summary, items, analysis."
    )

    print("Creating Email Agent with utility tools attached...")
    agent = AgentFactory.create(
        name="Core Assistant Email Agent",
        description="Email management via Microsoft Graph (app permissions)",
        instructions=instructions,
        llm=llm,
        tools=[
            AgentFactory.create_model_tool(model=u_date_range.id),
            AgentFactory.create_model_tool(model=u_sender_date.id),
            AgentFactory.create_model_tool(model=u_subject_range.id),
            AgentFactory.create_model_tool(model=u_by_ids.id),
        ],
    )

    print("Deploying agent...")
    agent.deploy()

    # Save info locally
    info = {
        "agent_id": agent.id,
        "api_url": f"https://platform-api.aixplain.com/sdk/agents/{agent.id}/run",
        "dashboard_url": f"https://platform.aixplain.com/discover/agent/{agent.id}",
        "utilities": {
            "email_by_date_range": u_date_range.id,
            "email_by_sender_date": u_sender_date.id,
            "email_by_subject_date_range": u_subject_range.id,
            "email_by_ids": u_by_ids.id,
        },
        "created_at": datetime.now().isoformat(),
    }
    with open("email_agent_info.json", "w") as f:
        json.dump(info, f, indent=2)

    print("\n✓ Email Agent created and deployed successfully!")
    print(f"Agent ID: {agent.id}")
    print(f"API: {info['api_url']}")
    print(f"Dashboard: {info['dashboard_url']}")
    return agent


def main():
    build_email_agent_with_utilities()


if __name__ == "__main__":
    main()
