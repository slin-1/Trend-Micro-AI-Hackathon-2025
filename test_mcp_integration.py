#!/usr/bin/env python3
"""
Test script for MCP integration in the AI workflow system.
This script tests the unified MCP client functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.integrations.mcp_unified import MCPUnified

async def test_mcp_integration():
    """Test the unified MCP client integration"""
    print("🧪 Testing MCP Integration")
    print("=" * 50)
    
    try:
        # Initialize MCP client
        print("📡 Initializing MCP client...")
        mcp_client = MCPUnified()
        
        if not await mcp_client.initialize():
            print("❌ Failed to initialize MCP client")
            return False
            
        print("✅ MCP client initialized successfully")
        
        # Test basic tool listing
        tool_summary = mcp_client.get_tool_summary()
        print(f"🔧 Tool Summary: {tool_summary}")
        
        # Test simple queries
        test_queries = [
            "List the available Confluence spaces.",
            "Get information about the current GitHub user.",
        ]
        
        print("\n🚀 Testing MCP queries...")
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test Query {i}: {query}")
            try:
                results = await mcp_client.run_with_unified_agent([query])
                if results and results[0]:
                    formatted_response = mcp_client.format_agent_response(results[0])
                    print(f"✅ Success:\n{formatted_response}")
                else:
                    print("⚠️ No result returned")
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        print("\n✅ MCP integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_integration():
    """Test workflow integration with MCP"""
    print("\n🔄 Testing Workflow Integration")
    print("=" * 50)
    
    try:
        # Test importing the updated workflow agent
        from src.agents.workflow_agent import WorkflowAgent
        
        print("✅ Successfully imported updated WorkflowAgent")
        
        # Test basic initialization
        config = {
            "ai_model": "gpt-4o",
            "git": {
                "repo_url": "https://example.com/repo.git",
                "branch_name": "feature/ai-test"
            }
        }
        
        workflow_agent = WorkflowAgent(config=config, output_dir="test_output")
        print("✅ Successfully initialized WorkflowAgent with MCP support")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🔬 MCP Integration Test Suite")
    print("=" * 60)
    
    # Check environment variables
    required_env_vars = [
        "OPENAI_API_KEY",
        "ENDPOINT_BASE_URL", 
        "GITHUB_PERSONAL_ACCESS_TOKEN"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file before running tests.")
        return False
    
    print("✅ All required environment variables are set")
    
    # Run tests
    tests = [
        ("MCP Integration", test_mcp_integration),
        ("Workflow Integration", test_workflow_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"{'✅' if result else '❌'} {test_name} test {'passed' if result else 'failed'}")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
