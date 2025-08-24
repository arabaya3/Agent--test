import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_EMAIL = os.getenv("DEFAULT_USER_ID")
AIXPLAIN_API_KEY = os.getenv("AIXPLAIN_API_KEY")
TEAM_API_KEY = os.getenv("TEAM_API_KEY")
GRAPH_USERNAME = os.getenv("GRAPH_USERNAME")
GRAPH_PASSWORD = os.getenv("GRAPH_PASSWORD")
DELEGATED_SCOPES = os.getenv("DELEGATED_SCOPES", "Files.Read.All")

GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
DEFAULT_TOP_LIMIT = 100
MAX_FILE_SIZE_DISPLAY = 10 * 1024 * 1024
MAX_CONTENT_LENGTH = 5000
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

SUPPORTED_TEXT_EXTENSIONS = ['.txt', '.csv', '.json', '.xml', '.html', '.py', '.js', '.css']
SUPPORTED_DOCUMENT_EXTENSIONS = ['.pdf', '.docx', '.doc']

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

if not all([CLIENT_ID, TENANT_ID, CLIENT_SECRET, USER_EMAIL]):
    missing_vars = []
    if not CLIENT_ID:
        missing_vars.append("CLIENT_ID")
    if not TENANT_ID:
        missing_vars.append("TENANT_ID")
    if not CLIENT_SECRET:
        missing_vars.append("CLIENT_SECRET")
    if not USER_EMAIL:
        missing_vars.append("DEFAULT_USER_ID")
    
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
