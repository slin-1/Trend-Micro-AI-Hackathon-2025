#!/usr/bin/env python3
# Test script to validate AI Employee Workflow setup

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_setup():
    """
    Test the AI Employee Workflow setup without making actual API calls
    """
    
    print("🤖 AI Employee Workflow - Setup Validation")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("❌ .env file not found. Run: python setup_credentials.py")
        return False
    
    # Check required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL", 
        "CONFLUENCE_BASE_URL",
        "CONFLUENCE_API_TOKEN",
        "CONFLUENCE_USER_EMAIL",
        "CONFLUENCE_SPACE_KEY",
        "SLACK_BOT_TOKEN",
        "SLACK_CHANNEL_ID",
        "GITHUB_TOKEN",
        "GITHUB_REPO_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value and not value.startswith("your_"):
            print(f"✅ {var} configured")
        else:
            print(f"❌ {var} not configured or using placeholder value")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Please configure these variables in .env file:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    # Test imports
    print("\n📆 Testing imports...")
    try:
        from src.utils.ai_client import ai_client
        print("✅ AI client import successful")
        
        from src.knowledge_base.rag_system import rag_system
        print("✅ RAG system import successful")
        
        from src.workflow.orchestrator import WorkflowOrchestrator
        print("✅ Workflow orchestrator import successful")
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("   Please install dependencies: pip install -r requirements.txt")
        return False
    
    # Test AI client configuration
    print("\n🤖 Testing AI client configuration...")
    try:
        config = ai_client.get_config()
        print(f"✅ AI client configured:")
        print(f"   - Base URL: {config['base_url']}")
        print(f"   - Chat Model: {config['chat_model']}")
        print(f"   - Embedding Model: {config['embedding_model']}")
        print(f"   - API Key: {'Configured' if config['api_key_configured'] else 'Missing'}")
    except Exception as e:
        print(f"❌ AI client configuration error: {str(e)}")
        return False
    
    # Test knowledge base
    print("\n📚 Testing knowledge base...")
    try:
        stats = rag_system.get_collection_stats()
        if 'error' in stats:
            print(f"❌ Knowledge base error: {stats['error']}")
            return False
        else:
            print(f"✅ Knowledge base loaded:")
            print(f"   - Documents: {stats['total_documents']}")
            print(f"   - Categories: {list(stats['categories'].keys())}")
    except Exception as e:
        print(f"❌ Knowledge base error: {str(e)}")
        return False
    
    # Check example transcript
    transcript_file = Path("example_transcript.txt")
    if transcript_file.exists():
        print(f"✅ Example transcript found: {transcript_file}")
    else:
        print(f"❌ Example transcript not found: {transcript_file}")
        return False
    
    # Test workspace directories
    print("\n📁 Testing workspace setup...")
    workspace_dir = Path(os.getenv("WORKSPACE_DIR", "./workspace"))
    output_dir = Path(os.getenv("OUTPUT_DIR", "./outputs"))
    
    try:
        workspace_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Workspace directories created:")
        print(f"   - Workspace: {workspace_dir}")
        print(f"   - Output: {output_dir}")
    except Exception as e:
        print(f"❌ Workspace setup error: {str(e)}")
        return False
    
    print("\n🎆 Setup validation complete!")
    print("\n🚀 Ready to run AI Employee Workflow:")
    print("   python -m src.main example_transcript.txt")
    
    return True

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)