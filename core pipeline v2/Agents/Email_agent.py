import os
from pathlib import Path
from dotenv import load_dotenv

# Load API key from the project's .env before importing aixplain
script_dir = Path(__file__).resolve().parent
project_dir = script_dir.parent  # expects .env at "core pipeline v2/.env"
env_path = project_dir / ".env"
load_dotenv(dotenv_path=env_path)

aix_key = os.getenv("AIXPLAIN_API_KEY")
team_key = os.getenv("TEAM_API_KEY")

selected_key = aix_key or team_key
if not selected_key or selected_key.strip() in {"", "your_aixplain_api_key_here", "your_team_api_key_here"}:
    raise ValueError(
        "Missing or placeholder AIXPLAIN_API_KEY. Set it in .env or environment before running."
    )

# Normalize environment to only use AIXPLAIN_API_KEY and avoid library conflicts
os.environ["AIXPLAIN_API_KEY"] = selected_key
if "TEAM_API_KEY" in os.environ:
    del os.environ["TEAM_API_KEY"]

from aixplain.factories import DatasetFactory, ModelFactory,AgentFactory
from aixplain.modules.agent.output_format import OutputFormat
from aixplain.modules.model.utility_model import UtilityModelInput
import json


BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://1b988f973611.ngrok-free.app").strip().rstrip("/")

system_prompt = f"""
You are an intelligent agent tasked with retrieving and filtering email data using the provided endpoints. Follow these instructions strictly:

1. Available Endpoints (use these ONLY, no others):
   - Search by Sender: {BASE_URL}/api/emails/sender/<sender>
   - Search by Subject: {BASE_URL}/api/emails/subject/<subject>
   - Search by Email ID: {BASE_URL}/api/emails/id/<email_id>

   Replace <sender>, <subject>, or <email_id> with the exact parameter provided by the user.
   Never modify the base URL or construct a different endpoint.

2. Query Handling:
   - If the user provides a sender, call the Search by Sender endpoint.
   - If the user provides a subject, call the Search by Subject endpoint.
   - If the user provides an email ID, call the Search by Email ID endpoint.
   - If a date range is included, filter the results after scraping (do not add it to the endpoint).

3. Data Retrieval and Scraping:
   - Make an HTTPS request to the chosen endpoint (disable SSL verification if required).
   - Always pass the raw response through the **scraper tool**.
   - Extract the following fields for each email:
       - sender
       - subject
       - date
       - snippet or full body content
   - Apply scraping consistently, even for ID-based queries.

4. Output Requirements:
   - Always return a structured list of emails in this format:
     [
       {
         "sender": "example@domain.com",
         "subject": "Meeting Reminder",
         "date": "2025-08-25",
         "snippet": "Don't forget our meeting at 3 PM today."
       }
     ]
   - If no results match the criteria, respond with: "No emails found for the specified criteria."

5. Error Handling:
   - If the endpoint returns an error or invalid data, respond with: "Unable to retrieve data from the source."
   - Validate all data formats before returning.

6. Special Instructions:
   - Use only the endpoints listed above. Do not invent, guess, or modify endpoints.
   - Always substitute only the <sender>, <subject>, or <email_id> parameter into the URL.
   - Always use the scraper tool for consistency before returning results.

"""
 

email_management_agent = AgentFactory.create(
    name = "Email Search Agent v51",
    description = "Email search and retrieval agent supporting multiple search methods including ID, date range, sender, and subject",
    instructions = system_prompt,
    tools = [AgentFactory.create_model_tool(model = "68ac49ed2c12f9d53ce00cd6")], 
    llm_id = "669a63646eb56306647e1091"
)
 
email_management_agent.deploy()