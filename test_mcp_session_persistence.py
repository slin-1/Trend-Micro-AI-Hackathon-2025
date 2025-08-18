#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.integrations.mcp_unified import MCPUnified

async def test_session_persistence():
    """Test that MCP sessions are created once and reused"""
    
    print("🧪 Testing MCP Session Persistence")
    print("=" * 50)
    
    # Initialize MCP client
    client = MCPUnified()
    await client.initialize()
    
    print(f"✅ MCP client initialized")
    print(f"🔧 Sessions initialized: {client.sessions_initialized}")
    
    # First call - should establish sessions
    print("\n📍 First call - should establish sessions:")
    result1 = await client.run_with_unified_agent([
        "Get information about the current user from Atlassian"
    ])
    
    print(f"🔧 Sessions initialized after first call: {client.sessions_initialized}")
    
    # Second call - should reuse existing sessions
    print("\n📍 Second call - should reuse existing sessions:")
    result2 = await client.run_with_unified_agent([
        "Get information about my GitHub account"
    ])
    
    print(f"🔧 Sessions initialized after second call: {client.sessions_initialized}")
    
    # Third call - should still reuse existing sessions
    print("\n📍 Third call - should still reuse existing sessions:")
    result3 = await client.run_with_unified_agent([
        "List Confluence spaces I have access to"
    ])
    
    print(f"🔧 Sessions initialized after third call: {client.sessions_initialized}")
    
    # Cleanup
    await client.cleanup()
    print(f"🔧 Sessions initialized after cleanup: {client.sessions_initialized}")
    
    print("\n✅ Session persistence test completed!")
    print("Expected behavior:")
    print("- First call: 'Establishing MCP sessions...'")
    print("- Second call: 'Reusing existing MCP sessions...'")
    print("- Third call: 'Reusing existing MCP sessions...'")

if __name__ == "__main__":
    asyncio.run(test_session_persistence())
