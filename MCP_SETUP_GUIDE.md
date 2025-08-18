# MCP Server Setup Guide

This guide provides step-by-step instructions for setting up the Model Context Protocol (MCP) servers required by the AI Employee Workflow system.

## Overview

The AI workflow uses two MCP servers:
- **Atlassian MCP Server**: For Confluence integration (documentation creation)
- **GitHub MCP Server**: For repository management and pull request creation

Both servers must be running before starting the AI workflow.

## Quick Setup Checklist

- [ ] Node.js v18+ installed
- [ ] Go 1.21+ installed (for GitHub MCP)
- [ ] Atlassian account with Confluence access
- [ ] GitHub Personal Access Token created
- [ ] Atlassian MCP server running in separate terminal
- [ ] GitHub MCP server binary built and configured

## Atlassian MCP Server

### Step 1: Start the Server

Open a **separate terminal** and run:

```bash
npx -y mcp-remote https://mcp.atlassian.com/v1/sse
```

**Important**: Keep this terminal open during the entire workflow execution.

### Step 2: Authenticate

- Browser will open automatically for OAuth authentication
- Log in with your Atlassian credentials
- Grant Confluence permissions when prompted
- Token is cached for future use

### Step 3: Verify Connection

Look for these messages in the terminal:
```
Connected to remote server using SSEClientTransport
Local STDIO server running
Proxy established successfully
```

## GitHub MCP Server

### Step 1: Clone and Build

```bash
# Clone the official repository
git clone https://github.com/github/github-mcp-server.git
cd github-mcp-server

# Build the binary
go build -o github-mcp-server ./cmd/github-mcp-server

# IMPORTANT: Copy the executable to the integrations directory
# The system expects to find it here:
cp github-mcp-server ../ai-hackathon-2025-team-9-ai-agent/src/integrations/

# Alternative: If go build fails or you encounter issues
# You can reference the executable directly from the cloned repo directory
# Just ensure the path is: ai-hackathon-2025-team-9-ai-agent/src/integrations/github-mcp-server
```

### Step 2: Create GitHub Token

1. Go to [GitHub Personal Access Tokens](https://github.com/settings/personal-access-tokens/new)
2. Create token with these scopes:
   - `repo` (Full control of repositories)
   - `read:org` (Read organization membership)  
   - `write:discussion` (Write discussions)
   - `read:user` (Read user profile)

### Step 3: Configure Environment

Add to your `.env` file:
```bash
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

### Step 4: Test the Server

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=your_token ./github-mcp-server stdio
```

Press `Ctrl+C` to exit the test.

## For GitHub Enterprise Users

If using GitHub Enterprise Server or Enterprise Cloud:

```bash
# Set your enterprise hostname
export GITHUB_HOST=https://github.your-company.com

# Run with enterprise configuration
GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
GITHUB_HOST=https://github.your-company.com \
./github-mcp-server stdio
```

## Troubleshooting

### Atlassian MCP Issues

**Problem**: Connection fails with 404 error
```
Solution: The server will automatically fallback to SSE-only mode. This is normal.
```

**Problem**: Authentication expires
```bash
Solution: Re-run the npx command to refresh tokens:
npx -y mcp-remote https://mcp.atlassian.com/v1/sse
```

**Problem**: Version compatibility issues
```bash
Solution: Use a specific version:
npx -y mcp-remote@0.1.13 https://mcp.atlassian.com/v1/sse
```

### GitHub MCP Issues

**Problem**: Build fails
```bash
Solution: Ensure Go 1.21+ is installed:
go version
# Should show go1.21 or later
```

**Problem**: Token authentication fails
```
Solution: Verify token scopes and regenerate if needed
```

**Problem**: Enterprise connection issues
```bash
Solution: Verify GITHUB_HOST environment variable:
echo $GITHUB_HOST
# Should show your enterprise URL
```

## Verification

### Check Both Servers

Run the AI workflow to verify both servers:

```bash
cd /path/to/ai-hackathon-2025-team-9-ai-agent
python -m src.main example_transcript.txt
```

### Expected Success Messages

```
✅ Both MCP sessions initialized
✅ Loaded 25 tools from Atlassian MCP server
✅ Loaded 80 tools from GitHub MCP server
✅ Unified agent created with 105 total tools
```

## Running the Complete Workflow

Once both MCP servers are set up:

1. **Terminal 1**: Keep Atlassian MCP running
   ```bash
   npx -y mcp-remote https://mcp.atlassian.com/v1/sse
   ```

2. **Terminal 2**: Run the AI workflow
   ```bash
   cd ai-hackathon-2025-team-9-ai-agent
   python -m src.main example_transcript.txt
   ```

The workflow will automatically:
- Connect to both MCP servers
- Create Confluence documentation
- Generate code implementations
- Create GitHub pull requests
- Send Slack notifications

## Security Notes

- Never commit MCP tokens or API keys to version control
- Keep the Atlassian MCP terminal session secure
- Rotate GitHub tokens regularly
- Use environment variables for sensitive configuration

## Support

- **Atlassian MCP**: [Official Documentation](https://support.atlassian.com/rovo/docs/setting-up-ides/)
- **GitHub MCP**: [Official Repository](https://github.com/github/github-mcp-server)
- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)

---

🔧 **MCP servers ready!** Your AI workflow can now integrate with Confluence and GitHub seamlessly.
