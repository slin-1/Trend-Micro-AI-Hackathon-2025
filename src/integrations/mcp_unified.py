from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv
import asyncio
import os
import json
from typing import Dict, Any, List, Optional

# Load environment variables
load_dotenv()

# MCP Tools Provider - Atlassian + GitHub Enterprise
# ==================================================
# This implementation provides MCP tools from both Atlassian and GitHub Enterprise servers
# for use by external AI agents. No AI model is instantiated here.
# 
# Components:
# - Atlassian MCP: 25 tools via mcp-remote bridge
# - GitHub Enterprise MCP: 80 tools via local binary
# - Pure tool provider interface
#
# Prerequisites:
# 1. Atlassian MCP proxy running: npx -y mcp-remote https://mcp.atlassian.com/v1/sse
# 2. GitHub MCP binary in same directory
# 3. Valid environment variables set

class MCPToolsProvider:
    """Pure MCP tools provider - no AI model, just tools for external agents"""
    
    def __init__(self):
        """Initialize MCP tools provider"""
        # MCP Client Configuration 
        self.client = None
        
        # Session storage - NOT async context managers themselves
        self.atlassian_session = None
        self.github_session = None
        self.sessions_initialized = False
        
        # Tool collections
        self.atlassian_tools = []
        self.github_tools = []
        
        # Configuration
        load_dotenv()
        self.confluence_space_key = os.getenv('CONFLUENCE_SPACE_KEY')
        
    def format_agent_response(self, response: Dict[str, Any]) -> str:
        """Format agent response for better human readability"""
        formatted_output = []
        
        # Add header
        formatted_output.append("=" * 60)
        formatted_output.append("🤖 UNIFIED MCP AGENT RESPONSE")
        formatted_output.append("=" * 60)
        
        # Extract the main message content
        if 'messages' in response:
            messages = response['messages']
            if isinstance(messages, list) and len(messages) > 0:
                # Get the last message (usually the final response)
                final_message = messages[-1]
                if hasattr(final_message, 'content'):
                    formatted_output.append("\n📝 RESPONSE:")
                    formatted_output.append("-" * 40)
                    formatted_output.append(final_message.content)
                    
                # Show any tool calls that were made
                tool_calls = []
                for msg in messages:
                    if hasattr(msg, 'additional_kwargs') and 'tool_calls' in msg.additional_kwargs:
                        tool_calls.extend(msg.additional_kwargs['tool_calls'])
                
                if tool_calls:
                    formatted_output.append("\n🔧 TOOLS USED:")
                    formatted_output.append("-" * 40)
                    for i, tool_call in enumerate(tool_calls, 1):
                        if 'function' in tool_call:
                            func_name = tool_call['function'].get('name', 'Unknown')
                            # Add source indicator
                            source = "📊" if func_name.startswith(('mcp_my-atlassian', 'searchJiraIssuesUsingJql', 'searchConfluenceUsingCql')) else "⚡"
                            formatted_output.append(f"{i}. {source} {func_name}")
        
        formatted_output.append("\n" + "=" * 60)
        return "\n".join(formatted_output)
    
    async def initialize(self) -> bool:
        """Initialize the MCP tools provider with both servers"""
        try:
            # Load and validate environment variables
            github_pat = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
            atlassian_mcp_url = os.getenv("ATLASSIAN_MCP_SERVER_URL", "https://mcp.atlassian.com/v1/sse")
            github_host = "https://dsgithub.trendmicro.com"  # GitHub Enterprise Server
            
            # Load Confluence configuration for targeted space usage
            self.confluence_space_key = os.getenv("CONFLUENCE_SPACE_KEY")
            self.confluence_base_url = os.getenv("CONFLUENCE_BASE_URL", "https://trendmicro.atlassian.net")
            
            # Validate required environment variables
            missing_vars = []
            if not github_pat:
                missing_vars.append("GITHUB_PERSONAL_ACCESS_TOKEN")
                
            if missing_vars:
                print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
                return False
            
            print(f"✅ Environment variables validated")
            print(f"✅ GitHub PAT length: {len(github_pat)} characters")
            print(f"✅ GitHub Enterprise Server: {github_host}")
            print(f"✅ Atlassian MCP URL: {atlassian_mcp_url}")
            if self.confluence_space_key:
                print(f"✅ Confluence Space Key: {self.confluence_space_key}")
            else:
                print(f"⚠️ No Confluence space key specified, will use default space")
            
        except Exception as e:
            print(f"❌ Error loading environment variables: {e}")
            return False
        
        # Configure MCP client with servers
        try:
            github_binary_path = os.path.join(os.path.dirname(__file__), "github-mcp-server")
            
            self.client = MultiServerMCPClient({
                "atlassian": {
                    "command": "npx",
                    "args": ["-y", "mcp-remote", atlassian_mcp_url],
                    "transport": "stdio",
                },
                "github": {
                    "command": github_binary_path,
                    "args": ["stdio"],
                    "transport": "stdio",
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": github_pat,
                        "GITHUB_HOST": github_host  # Configure for GitHub Enterprise Server
                    }
                }
            })
            
            print(f"🔗 Configured unified MCP client:")
            print(f"   📊 Atlassian MCP: {atlassian_mcp_url}")
            print(f"   ⚡ GitHub Enterprise: {github_host}")
            print(f"   🛠️  GitHub binary: {github_binary_path}")
            
        except Exception as e:
            print(f"❌ Error configuring MCP client: {e}")
            return False
            
        return True
    
    async def _ensure_sessions_initialized(self):
        """Ensure MCP sessions are initialized, creating them if needed"""
        if not self.sessions_initialized:
            print("⏳ Establishing MCP sessions...")
            
            # Create and enter session contexts
            self.atlassian_session_cm = self.client.session("atlassian")
            self.github_session_cm = self.client.session("github")
            
            # Enter the contexts
            self.atlassian_session = await self.atlassian_session_cm.__aenter__()
            self.github_session = await self.github_session_cm.__aenter__()
            
            print("✅ Both MCP sessions initialized")
            
            # Load tools from both servers
            self.atlassian_tools = await load_mcp_tools(self.atlassian_session)
            self.github_tools = await load_mcp_tools(self.github_session)
            
            print(f"✅ Loaded {len(self.atlassian_tools)} tools from Atlassian MCP server")
            print(f"✅ Loaded {len(self.github_tools)} tools from GitHub MCP server")
            
            # Store all tools for external use (no agent creation here)
            all_tools = self.atlassian_tools + self.github_tools
            total_tools = len(all_tools)
            
            print(f"✅ MCP tools ready for external agent: {total_tools} total tools")
            print(f"   📊 Atlassian: {len(self.atlassian_tools)} tools")
            print(f"   ⚡ GitHub: {len(self.github_tools)} tools")
            
            self.sessions_initialized = True
        else:
            print("🔄 Reusing existing MCP sessions...")

    def get_all_tools(self) -> List[Any]:
        """Get all MCP tools for use by external agents"""
        if not self.sessions_initialized:
            raise RuntimeError("Tools not initialized. Call initialize() and _ensure_sessions_initialized() first.")
        
        return self.atlassian_tools + self.github_tools

    async def execute_mcp_query(self, query: str, tool_name: str = None) -> Optional[Dict[str, Any]]:
        """Execute a query using specific MCP tools (helper method for external agents)"""
        if not self.client:
            print("❌ Client not initialized. Call initialize() first.")
            return None
            
        try:
            # Ensure sessions are initialized
            await self._ensure_sessions_initialized()
            
            # This is a helper method - actual execution should be done by the external agent
            # that has access to the tools via get_all_tools()
            print(f"📝 Query received: {query}")
            print(f"⚠️ Note: This method is for compatibility. External agents should use get_all_tools()")
            
            return {"query": query, "status": "tools_available", "note": "Use get_all_tools() for agent integration"}
                    
        except Exception as e:
            print(f"❌ Error in MCP query execution: {e}")
            return None
    
    def get_tool_summary(self) -> Dict[str, int]:
        """Get summary of available tools by source"""
        return {
            "atlassian_tools": len(self.atlassian_tools),
            "github_tools": len(self.github_tools),
            "total_tools": len(self.atlassian_tools) + len(self.github_tools)
        }

    async def cleanup(self):
        """Clean up MCP sessions and client resources with aggressive task context management"""
        try:
            print("🧹 Cleaning up MCP sessions...")
            
            # Try to cleanup in the same task context
            if self.sessions_initialized and self.client:
                try:
                    # Force cleanup of sessions within current task context
                    print("🔄 Attempting graceful session cleanup...")
                    
                    # Note: No agent cleanup needed - this is a pure tools provider
                    
                    # Try to cleanup the client sessions
                    if hasattr(self.client, 'close') or hasattr(self.client, 'cleanup'):
                        try:
                            if hasattr(self.client, 'close'):
                                await self.client.close()
                            elif hasattr(self.client, 'cleanup'):
                                await self.client.cleanup()
                        except Exception as client_err:
                            print(f"⚠️ Client cleanup error (ignored): {client_err}")
                
                except Exception as session_cleanup_err:
                    print(f"⚠️ Session cleanup error (ignored): {session_cleanup_err}")
            
            # Reset our state regardless of cleanup success
            self.sessions_initialized = False
            print("🔄 Session state reset")
                
            # Clear references but don't try to close them manually
            self.atlassian_session = None
            self.github_session = None
            self.atlassian_tools = []
            self.github_tools = []
            
            # Let the client cleanup naturally when it goes out of scope
            # DO NOT call client cleanup methods that might interfere with async contexts
            self.client = None
                
            print("🧹 MCP client cleaned up successfully")
        except Exception as e:
            print(f"⚠️ Error during MCP cleanup: {e}")

    def format_confluence_query(self, query: str) -> str:
        """Format a Confluence query with the configured space"""
        if self.confluence_space_key:
            # Insert space information into the query
            if "create" in query.lower() and "confluence" in query.lower():
                # For page creation queries, add explicit space specification with more detail
                space_spec = f" IMPORTANT: Create this page specifically in the Confluence space with key '{self.confluence_space_key}'. Do not use any other space or default space."
                return query + space_spec
            else:
                # For other queries, add space context
                return f"In Confluence space '{self.confluence_space_key}': {query}"
        else:
            return query

    # Compatibility methods for existing workflow_agent.py
    async def run_with_unified_agent(self, queries: List[str]) -> List[Optional[Dict[str, Any]]]:
        """
        DEPRECATED: Compatibility method for existing workflow_agent.py
        Use get_all_tools() and integrate with your own agent instead
        """
        print("⚠️ DEPRECATED: run_with_unified_agent() should be replaced with get_all_tools()")
        print("💡 External agents should create their own agent with MCP tools")
        
        results = []
        for query in queries:
            # Simulate response format that workflow_agent expects
            results.append({
                "messages": f"MCP tools available for query: {query}",
                "note": "Please integrate MCP tools with your agent using get_all_tools()"
            })
        return results

    def format_agent_response(self, response: Dict[str, Any]) -> str:
        """
        COMPATIBILITY: Format agent response for display
        """
        if isinstance(response, dict):
            return response.get("messages", str(response))
        return str(response)


# Create an alias for backward compatibility
MCPUnified = MCPToolsProvider


async def demo_mcp_tools():
    """Demonstration of MCP tools provider functionality"""
    print("🚀 MCP Tools Provider Demo")
    print("=" * 50)
    
    # Initialize tools provider
    tools_provider = MCPToolsProvider()
    
    try:
        # Initialize configuration
        if not await tools_provider.initialize():
            print("❌ Failed to initialize MCP tools provider")
            return
        
        # Ensure sessions are ready
        await tools_provider._ensure_sessions_initialized()
        
        # Get available tools
        all_tools = tools_provider.get_all_tools()
        tool_summary = tools_provider.get_tool_summary()
        
        print(f"📊 Available tools: {tool_summary}")
        print(f"🛠️ Total tools loaded: {len(all_tools)}")
        
        # Display some tool names
        if all_tools:
            print("\n� Sample available tools:")
            for i, tool in enumerate(all_tools[:5]):  # Show first 5 tools
                print(f"   {i+1}. {tool.name if hasattr(tool, 'name') else str(tool)}")
        
        print("\n✅ Tools are ready for external agent use!")
        print("💡 External agents can use get_all_tools() to access these MCP tools")
    
    except Exception as e:
        print(f"❌ Error in demo: {e}")
    finally:
        # Clean up
        await tools_provider.cleanup()
        print("✅ Demo complete")


if __name__ == "__main__":
    asyncio.run(demo_mcp_tools())
