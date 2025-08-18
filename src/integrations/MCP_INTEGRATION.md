# MCP Integration Guide

## Overview

This project has been integrated with the unified MCP (Model Context Protocol) client to provide seamless interaction with both Atlassian (Confluence/Jira) and GitHub Enterprise services. The integration replaces the previous separate API integrations with a unified agent-based approach.

## Architecture

### Unified MCP Client (`src/integrations/mcp_unified.py`)

The `MCPUnified` class provides:
- **Atlassian MCP Server**: 25+ tools for Confluence and Jira operations
- **GitHub Enterprise MCP Server**: 80+ tools for GitHub operations  
- **Unified Agent**: Single LangChain agent with access to all tools
- **Session Management**: Persistent sessions for the entire workflow

### Key Components

1. **MultiServerMCPClient**: Manages connections to multiple MCP servers
2. **LangChain Adapters**: Convert MCP tools to LangChain tools
3. **GPT-4o Agent**: Uses all available tools to execute complex workflows
4. **Response Formatting**: Human-readable output formatting

## Integration Points

### WorkflowAgent Updates

The `WorkflowAgent` has been updated to use MCP for:

- **Confluence Operations**:
  - `_create_confluence_project_folder()`: Creates parent pages via MCP
  - `_create_confluence_requirements_page()`: Creates requirements pages via MCP
  - `_create_confluence_design_page()`: Creates design specification pages via MCP
  - `_create_confluence_page()`: Generic page creation via MCP

- **GitHub Operations**:
  - `_create_pull_request()`: Creates pull requests via MCP

### Workflow Process

1. **Initialization**: MCP client is initialized at workflow start
2. **Session Management**: Single session maintained throughout workflow
3. **Tool Execution**: Agent uses appropriate tools (Atlassian vs GitHub) automatically
4. **Response Handling**: Formatted responses provided for human readability

## Environment Setup

Required environment variables:

```bash
# Core API Configuration
OPENAI_API_KEY=your_openai_api_key
ENDPOINT_BASE_URL=https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/

# GitHub Enterprise Configuration  
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat
GITHUB_HOST=https://dsgithub.trendmicro.com

# Atlassian MCP Server
ATLASSIAN_MCP_SERVER_URL=https://mcp.atlassian.com/v1/sse
```

## Dependencies

The following dependencies have been added:

```
langchain-mcp-adapters>=0.1.0
```

## Usage

### Basic MCP Testing

```bash
# Test MCP integration
python test_mcp_integration.py
```

### Running the Full Workflow

```bash
# Run with MCP integration
python -m src.main example_transcript.txt
```

## MCP Server Configuration

### Atlassian MCP Server
- **URL**: `https://mcp.atlassian.com/v1/sse`
- **Transport**: SSE (Server-Sent Events) via mcp-remote
- **Tools**: 25+ tools for Confluence and Jira operations
- **Authentication**: Handled automatically by the MCP server

### GitHub Enterprise MCP Server  
- **Binary**: `src/integrations/github-mcp-server`
- **Transport**: stdio
- **Tools**: 80+ tools for GitHub operations
- **Authentication**: Uses `GITHUB_PERSONAL_ACCESS_TOKEN`

## Client Lifecycle

1. **Initialization**: `MCPUnified.initialize()` sets up both servers
2. **Session Creation**: Active sessions established for both servers
3. **Tool Loading**: All tools from both servers loaded into single agent
4. **Workflow Execution**: Agent uses tools as needed throughout workflow
5. **Session Cleanup**: Automatic cleanup when workflow completes

## Error Handling

The integration includes robust error handling:

- **Initialization Failures**: Clear error messages for missing configuration
- **Connection Issues**: Graceful degradation with detailed logging
- **Tool Execution Errors**: Fallback mechanisms and error reporting
- **Response Parsing**: Multiple parsing strategies for different response formats

## Benefits

### Unified Interface
- Single agent handles both Confluence and GitHub operations
- Consistent response formatting across all tools
- Simplified workflow logic

### Enhanced Capabilities
- Natural language queries work across both platforms
- Agent can make intelligent tool selection decisions
- Complex multi-step operations possible in single queries

### Maintainability  
- Reduced integration complexity
- Official MCP servers (maintained by Atlassian/GitHub)
- Automatic tool discovery and loading

## Troubleshooting

### Common Issues

1. **MCP Server Connection Failures**
   - Check environment variables are set correctly
   - Verify network connectivity to MCP servers
   - Check GitHub PAT permissions

2. **Tool Loading Issues**
   - Ensure `github-mcp-server` binary is executable
   - Verify mcp-remote is available (`npx -y mcp-remote`)
   - Check tool loading logs for specific errors

3. **Agent Execution Failures**
   - Review agent query formatting
   - Check LLM model availability and configuration
   - Verify tool permissions (GitHub repo access, Confluence space access)

### Debug Mode

Enable detailed logging by setting:

```bash
export MCP_DEBUG=1
```

### Testing Individual Components

```bash
# Test Atlassian MCP connection
npx -y mcp-remote https://mcp.atlassian.com/v1/sse

# Test GitHub MCP binary
./src/integrations/github-mcp-server stdio

# Test unified client
python test_mcp_integration.py
```

## Future Enhancements

Potential improvements for the MCP integration:

1. **Additional MCP Servers**: Slack, Teams, other services
2. **Tool Caching**: Cache frequently used tool responses
3. **Parallel Execution**: Execute independent tool calls in parallel
4. **Custom Tools**: Add project-specific MCP tools
5. **Monitoring**: Add metrics and monitoring for MCP operations

## References

- [LangChain MCP Adapters Documentation](https://python.langchain.com/docs/integrations/tools/mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Atlassian MCP Server](https://mcp.atlassian.com/)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
