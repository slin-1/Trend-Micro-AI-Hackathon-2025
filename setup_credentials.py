#!/usr/bin/env python3
# Credentials Setup Assistant for AI Employee Workflow System

import os
import shutil
from pathlib import Path
from typing import Dict, Any

def setup_credentials():
    """
    Interactive setup assistant to help configure credentials and settings
    for the AI Employee Workflow System
    """
    
    print("🤖 AI Employee Workflow - Credentials Setup Assistant")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📄 Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("✅ .env file created")
    
    print("\n🔍 Please configure the following credentials:")
    print("\n1. 🌐 Trend Micro RDSec AI Endpoint")
    print("   • Get your API key from Trend Micro's internal AI infrastructure")
    print("   • Set OPENAI_API_KEY in .env file")
    print("   • Base URL is already configured: https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/")
    
    print("\n2. 📄 Confluence Integration")
    print("   • Go to your Atlassian account settings")
    print("   • Create an API token: https://id.atlassian.com/manage-profile/security/api-tokens")
    print("   • Set these in .env file:")
    print("     - CONFLUENCE_BASE_URL (your Atlassian instance URL)")
    print("     - CONFLUENCE_API_TOKEN (the API token you created)")
    print("     - CONFLUENCE_USER_EMAIL (your email address)")
    print("     - CONFLUENCE_SPACE_KEY (space where pages will be created)")
    
    print("\n3. 📢 Slack Integration")
    print("   • Create Slack app at https://api.slack.com/apps")
    print("   • Add bot token scopes: chat:write, channels:read")
    print("   • Install app to workspace and get bot token")
    print("   • Set these in .env file:")
    print("     - SLACK_BOT_TOKEN (bot user oauth token)")
    print("     - SLACK_CHANNEL_ID (channel ID like C1234567890)")
    print("     - SLACK_CHANNEL_NAME (human readable channel name)")
    
    print("\n4. 💙 GitHub Integration")
    print("   • Go to GitHub Settings > Developer settings > Personal access tokens")
    print("   • Generate new token with 'repo' scope")
    print("   • Set these in .env file:")
    print("     - GITHUB_TOKEN (the personal access token)")
    print("     - GITHUB_REPO_URL (e.g., https://github.com/owner/repo)")
    
    print("\n5. 📁 Workspace Configuration")
    print("   • These are pre-configured but you can customize:")
    print("     - WORKSPACE_DIR (default: ./workspace)")
    print("     - OUTPUT_DIR (default: ./outputs)")
    print("     - CHROMA_DB_PATH (default: ./data/chroma_db)")
    
    print("\n📜 Next Steps:")
    print("1. Edit the .env file with your actual credentials")
    print("2. Test the setup with: python -m src.main example_transcript.txt")
    print("3. Check the outputs/ directory for generated files")
    
    print("\n⚠️  Security Notes:")
    print("• Never commit the .env file to version control")
    print("• Keep your API tokens secure and don't share them")
    print("• Use only approved AI tools listed on the RDSec Portal")
    
    print("\n🎆 Ready to build your AI Employee workflow!")

if __name__ == "__main__":
    setup_credentials()