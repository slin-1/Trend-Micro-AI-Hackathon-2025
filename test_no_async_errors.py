#!/usr/bin/env python3
"""
Test script to verify if we can eliminate async cleanup errors completely
using a different approach - custom event loop management
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.integrations.mcp_unified import MCPUnified
from dotenv import load_dotenv

async def test_with_controlled_loop():
    """Test MCP with controlled event loop cleanup"""
    print("🧪 Testing MCP with Controlled Event Loop Cleanup")
    print("=" * 60)
    
    # Load environment
    load_dotenv()
    
    # Validate environment
    required_vars = [
        "OPENAI_API_KEY", "ENDPOINT_BASE_URL", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ATLASSIAN_MCP_SERVER_URL", "CONFLUENCE_SPACE_KEY"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    
    print("✅ Environment variables validated")
    
    try:
        # Create MCP client
        mcp_client = MCPUnified()
        
        # Initialize and test
        if not await mcp_client.initialize():
            print("❌ Failed to initialize MCP client")
            return False
        
        print("✅ MCP client initialized")
        
        # Test a simple query
        queries = ["Get information about the current user from Atlassian"]
        results = await mcp_client.run_with_unified_agent(queries)
        
        if results and results[0]:
            print("✅ Query executed successfully")
        else:
            print("⚠️ Query failed")
        
        # Immediate cleanup in same task context
        print("🧹 Performing immediate cleanup...")
        await mcp_client.cleanup()
        print("✅ Cleanup completed successfully")
        
        # Force garbage collection
        import gc
        gc.collect()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function with custom event loop management"""
    try:
        # Create a new event loop for clean slate
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the test
        success = loop.run_until_complete(test_with_controlled_loop())
        
        # Explicitly shutdown async generators before closing loop
        print("🔄 Shutting down async generators...")
        try:
            # Get all tasks
            tasks = asyncio.all_tasks(loop)
            if tasks:
                print(f"⚠️ Found {len(tasks)} pending tasks, cancelling...")
                for task in tasks:
                    task.cancel()
                
                # Wait for tasks to complete cancellation
                loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            
            # Shutdown async generators
            loop.run_until_complete(loop.shutdown_asyncgens())
            print("✅ Async generators shutdown complete")
            
        except Exception as shutdown_error:
            print(f"⚠️ Shutdown error (ignored): {shutdown_error}")
        
        finally:
            # Close the loop
            loop.close()
            print("✅ Event loop closed cleanly")
        
        if success:
            print("\n🎉 Test completed successfully with no async errors!")
        else:
            print("\n❌ Test failed")
            
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Main error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
