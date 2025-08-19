#!/usr/bin/env python3
"""
Fix Dependencies Script
Resolves dependency conflicts for AIXPLAIN Email Agent setup
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def main():
    """Main function to fix dependencies"""
    print("🔧 AIXPLAIN Email Agent - Dependency Fix")
    print("=" * 50)
    
    # Step 1: Upgrade pip
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️ Failed to upgrade pip, continuing...")
    
    # Step 2: Uninstall conflicting packages
    print("\n🧹 Cleaning up conflicting packages...")
    packages_to_remove = ["pydantic", "aixplain"]
    
    for package in packages_to_remove:
        run_command(f"pip uninstall {package} -y", f"Removing {package}")
    
    # Step 3: Install compatible versions
    print("\n📦 Installing compatible packages...")
    
    # Install pydantic first (compatible version)
    if not run_command("pip install pydantic>=2.10.6", "Installing Pydantic >=2.10.6"):
        print("❌ Failed to install Pydantic")
        return False
    
    # Install AIXPLAIN
    if not run_command("pip install aixplain==0.2.33", "Installing AIXPLAIN"):
        print("❌ Failed to install AIXPLAIN")
        return False
    
    # Install other dependencies
    other_deps = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-dotenv==1.0.0",
        "requests==2.31.0"
    ]
    
    for dep in other_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, continuing...")
    
    # Step 4: Verify installation
    print("\n🔍 Verifying installation...")
    
    try:
        import aixplain
        import pydantic
        import fastapi
        import uvicorn
        
        print("✅ All packages imported successfully!")
        print(f"📦 AIXPLAIN version: {aixplain.__version__}")
        print(f"📦 Pydantic version: {pydantic.__version__}")
        print(f"📦 FastAPI version: {fastapi.__version__}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    print("\n🎉 Dependency fix completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set up your .env file with AIXPLAIN credentials")
    print("2. Run: python run_aixplain_email_agent.py")
    print("3. Or start manually: python api_server.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Dependency fix failed. Please check the errors above.")
        sys.exit(1)
