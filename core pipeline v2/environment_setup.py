#!/usr/bin/env python3
import os
import shutil
from pathlib import Path


def create_env_file():
    template_path = Path("environment_template.txt")
    env_path = Path(".env")
    
    if not template_path.exists():
        print("Environment template file not found. Creating basic .env file...")
        create_basic_env_file()
        return
    
    if env_path.exists():
        print(".env file already exists. Skipping creation.")
        return
    
    try:
        shutil.copy(template_path, env_path)
        print("Environment file created successfully from template.")
        print("Please edit .env file with your actual credentials.")
    except Exception as e:
        print(f"Error creating .env file: {str(e)}")
        create_basic_env_file()


def create_basic_env_file():
    env_content = """# Microsoft Graph API Configuration
CLIENT_ID=your_client_id_here
TENANT_ID=your_tenant_id_here
CLIENT_SECRET=your_client_secret_here

# Default User ID for Application Permissions
DEFAULT_USER_ID=your_email@domain.com

# AIXplain Configuration
AIXPLAIN_API_KEY=your_aixplain_api_key_here

# Graph API Username/Password for delegated permissions
GRAPH_USERNAME=your_email@domain.com
GRAPH_PASSWORD=your_password_here
DELEGATED_SCOPES=Files.Read.All

# Optional Configuration
DEBUG=false
API_TIMEOUT=30
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("Basic .env file created. Please edit with your actual credentials.")
    except Exception as e:
        print(f"Error creating basic .env file: {str(e)}")


def validate_env_file():
    env_path = Path(".env")
    if not env_path.exists():
        print("No .env file found. Creating one...")
        create_env_file()
        return False
    
    required_vars = [
        "CLIENT_ID",
        "TENANT_ID", 
        "CLIENT_SECRET",
        "DEFAULT_USER_ID"
    ]
    
    missing_vars = []
    with open(env_path, "r") as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=your_" in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"Missing or placeholder values for: {', '.join(missing_vars)}")
        print("Please edit .env file with your actual credentials.")
        return False
    
    print("Environment file validation passed.")
    return True


def main():
    print("OneDrive Agent Environment Setup")
    print("=" * 40)
    
    create_env_file()
    validate_env_file()
    
    print("\nSetup complete!")
    print("Next steps:")
    print("1. Edit .env file with your actual credentials")
    print("2. Run: python usage_examples.py")


if __name__ == "__main__":
    main()
