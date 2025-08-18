# AI Employee Workflow Setup Instructions

## Overview

This system creates an AI Employee that manages a complete development workflow from meeting transcripts to deployed code. Built for the Trend Micro AI Hackathon, it demonstrates an autonomous AI agent that can:

1. **Parse meeting transcripts** to understand project requirements
2. **Generate requirements documents** in Confluence
3. **Create design specifications** using internal knowledge base
4. **Clone repositories** and set up development environment
5. **Implement code** converting Linux to Windows APIs
6. **Create pull requests** and notify teams

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

```bash
python setup_credentials.py
```

This will guide you through setting up:
- Trend Micro RDSec AI Endpoint credentials
- Confluence API access
- MS Teams webhook
- GitHub personal access token

### 3. Edit Environment Variables

Edit the `.env` file created by the setup script:

```bash
# Required: Get from Trend Micro's internal AI infrastructure
OPENAI_API_KEY=your_rdsec_ai_endpoint_api_key_here

# Required: Confluence settings
CONFLUENCE_BASE_URL=https://yourcompany.atlassian.net
CONFLUENCE_API_TOKEN=your_atlassian_api_token_here
CONFLUENCE_USER_EMAIL=your_email@trendmicro.com
CONFLUENCE_SPACE_KEY=your_confluence_space_key

# Required: Teams webhook for notifications
TEAMS_WEBHOOK_URL=https://yourcompany.webhook.office.com/webhookb2/your_webhook_url

# Required: GitHub for PR creation
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO_URL=https://github.com/your-username/your-repo
```

### 4. Run the AI Employee

```bash
python -m src.main example_transcript.txt
```

## Detailed Configuration

### Trend Micro RDSec AI Endpoint

- **What it does**: Provides access to gpt-4o and text-embedding-3-large models
- **How to get**: Contact your AI infrastructure team for API key
- **Security**: Uses company-approved endpoint with security compliance

### Confluence Integration

1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create a new API token
3. Find your Confluence space key in the space settings
4. The AI will create project folders and documentation pages

### Slack Integration

**Change of Plans**: We needed to contact IT for permissions to use MS Teams, which would have taken more time for this hackathon. So, for this demo, we are using Slack.

1. Create a Slack app at https://api.slack.com/apps
2. Add bot token scopes: `chat:write`, `channels:read`
3. Install app to your workspace
4. Get bot token and channel ID
5. AI will send rich workflow completion notifications

### GitHub Integration

1. Go to [GitHub Personal Access Tokens](https://github.com/settings/tokens)
2. Generate new token with "repo" scope
3. AI will create branches and pull requests

## MCP Server Setup

This system uses Model Context Protocol (MCP) servers to integrate with external services like Atlassian (Confluence) and GitHub. You need to set up these MCP servers before running the AI workflow.

### Atlassian MCP Server Setup

The Atlassian MCP server provides access to tools for Confluence and Jira.
- [Getting Started with the Atlassian Remote MCP Server](https://support.atlassian.com/rovo/docs/getting-started-with-the-atlassian-remote-mcp-server/)
- [Setting Up IDEs](https://support.atlassian.com/rovo/docs/setting-up-ides/)

#### Prerequisites
- Node.js v18 or later
- npx for installation
- An Atlassian Cloud site with Confluence access
- A modern browser for OAuth authentication

#### Setup Instructions

1. **Start the Atlassian MCP Server**
   
   Open a separate terminal and run:
   ```bash
   npx -y mcp-remote https://mcp.atlassian.com/v1/sse
   ```

   Note: If you encounter version-related issues, try specifying an older version:
   ```bash
   npx -y mcp-remote@0.1.13 https://mcp.atlassian.com/v1/sse
   ```

2. **Authentication**
   
   - The first time you run this command, it will open a browser for OAuth authentication
   - Log in with your Atlassian account credentials
   - Grant the necessary permissions for Confluence access
   - The authentication token will be cached for future use

3. **Keep the Terminal Open**
   
   - **Important**: Keep this terminal session running while using the AI workflow
   - If your token expires, simply re-run the `mcp-remote` command
   - The server runs on the default port and will be automatically detected by the workflow

#### Troubleshooting Atlassian MCP
- **Authentication Issues**: Re-run the `npx -y mcp-remote` command to refresh tokens
- **Connection Problems**: Ensure you have internet access and Atlassian Cloud is accessible
- **Permission Errors**: Verify your Atlassian account has Confluence write permissions in the target space

### GitHub MCP Server Setup

The GitHub MCP server provides repository management, issue tracking, and pull request creation capabilities.
- [Build From the Source](https://github.com/github/github-mcp-server?tab=readme-ov-file#build-from-source:~:text=and%20setup%20process.-,Build%20from%20source,-If%20you%20don%27t)

#### Prerequisites
- Git installed on your system
- Go programming language (1.21 or later) for building from source
- Docker (optional, for containerized setup)
- GitHub Personal Access Token

#### Setup Instructions

1. **Clone the Official GitHub MCP Repository**
   
   ```bash
   git clone https://github.com/github/github-mcp-server.git
   cd github-mcp-server
   ```

2. **Build from Source**
   
   Build the MCP server binary:
   ```bash
   go build -o github-mcp-server ./cmd/github-mcp-server
   ```
   
   Or specify a custom output location:
   ```bash
   go build -o /path/to/your/bin/github-mcp-server ./cmd/github-mcp-server
   ```

3. **Create GitHub Personal Access Token**
   
   - Go to [GitHub Personal Access Tokens](https://github.com/settings/personal-access-tokens/new)
   - Generate a new token with the following scopes:
     - `repo` (Full control of private repositories)
     - `read:org` (Read organization membership)
     - `write:discussion` (Write repository discussions)
     - `read:user` (Read user profile data)
   - Copy the token securely

4. **Configure Environment Variables**
   
   Add your GitHub token to your `.env` file:
   ```bash
   GITHUB_PERSONAL_ACCESS_TOKEN=your_github_personal_access_token_here
   ```

5. **Test the Setup**
   
   Test the GitHub MCP server:
   ```bash
   GITHUB_PERSONAL_ACCESS_TOKEN=your_token ./github-mcp-server stdio
   ```

#### GitHub Enterprise Setup

For GitHub Enterprise Server or Enterprise Cloud with data residency:

1. **Set the GitHub Host**
   ```bash
   export GITHUB_HOST=https://your-github-enterprise-domain.com
   ```

2. **Run with Custom Host**
   ```bash
   GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
   GITHUB_HOST=https://your-enterprise-domain.com \
   ./github-mcp-server stdio
   ```

#### Troubleshooting GitHub MCP
- **Build Issues**: Ensure Go 1.21+ is installed and `$GOPATH` is configured
- **Token Problems**: Verify your PAT has the required scopes and hasn't expired
- **Enterprise Connectivity**: Ensure the `GITHUB_HOST` environment variable is set correctly
- **Docker Issues**: Run `docker logout ghcr.io` if you encounter authentication problems

### Integration Verification

After setting up both MCP servers, verify the integration:

1. **Check Atlassian MCP**
   - Ensure the `npx -y mcp-remote` command is running in a separate terminal
   - Look for successful connection messages in the terminal output

2. **Check GitHub MCP**
   - Verify the `github-mcp-server` binary is built and accessible
   - Test with a simple command to ensure authentication works

3. **Run the AI Workflow**
   ```bash
   python -m src.main example_transcript.txt
   ```
   
   Look for these success messages:
   - `✅ Both MCP sessions initialized`
   - `✅ Loaded X tools from Atlassian MCP server`
   - `✅ Loaded Y tools from GitHub MCP server`

### MCP Server Ports and Configuration

The AI workflow automatically detects and connects to:
- **Atlassian MCP**: Uses the SSE endpoint at `https://mcp.atlassian.com/v1/sse`
- **GitHub MCP**: Uses the local binary via stdio interface
- **Port Management**: Automatically handles port allocation and session management

## Architecture

### Core Components

- **WorkflowOrchestrator**: Manages the sequential execution of all steps
- **WorkflowAgent**: Single AI agent that performs all workflow steps
- **AIClient**: Configured for Trend Micro's RDSec AI endpoint
- **LinuxWindowsRAGSystem**: ChromaDB-based knowledge for API conversions
- **MCP Servers**: Integration with Confluence and GitHub via MCP protocol

### Workflow Steps

1. **Transcript Parsing**: AI extracts project details, requirements, participants
2. **Requirements Generation**: Creates business requirements document
3. **Design Specification**: Uses RAG to create technical design with conversion patterns
4. **Git Setup**: Clones reference repo, creates feature branch
5. **Implementation**: AI converts Linux code to Windows using knowledge base
6. **PR Creation**: Commits code, creates pull request, notifies team

### Knowledge Base

The system includes a pre-populated ChromaDB with Linux-to-Windows API conversion knowledge:

- File operations: `open()` → `CreateFile()`, `read()` → `ReadFile()`
- Process management: `fork()` → `CreateProcess()`
- Memory management: `mmap()` → `MapViewOfFile()`
- Networking: `socket()` → `WSASocket()`
- Threading: `pthread_create()` → `CreateThread()`

## Testing

### Test with Example Transcript

The included `example_transcript.txt` contains a sample meeting about implementing Windows process monitoring. Run:

```bash
python -m src.main example_transcript.txt --output-dir ./test_output
```

### Expected Outputs

- `requirements.md`: AI-generated requirements document
- `design_spec.md`: Technical design with Windows conversion strategy
- `src/windows_*.c`: Converted Windows implementation files
- `workflow_summary.md`: Complete workflow execution summary

### Confluence Artifacts

- Project folder with timestamp
- Requirements page
- Design specification page

### Teams Notification

Receive completion notification with links to:
- GitHub pull request
- Confluence documentation
- Workflow summary

## Troubleshooting

### Common Issues

1. **AI Endpoint Connection Issues**
   - Verify your API key is correct
   - Check network access to Trend Micro's AI endpoint
   - Ensure you're using approved tools from RDSec Portal

2. **Confluence API Errors**
   - Verify API token has proper permissions
   - Check space key exists and you have write access
   - Ensure base URL format is correct

3. **Teams Webhook Issues**
   - Verify webhook URL is active
   - Check Teams channel permissions
   - Test webhook manually if needed

4. **GitHub API Issues**
   - Verify personal access token has repo scope
   - Check repository URL format
   - Ensure you have push access to the repo

### Debug Mode

Set environment variable for verbose logging:

```bash
LOG_LEVEL=DEBUG python -m src.main example_transcript.txt
```

### Knowledge Base Issues

If ChromaDB fails to initialize:

```bash
# Reset the knowledge base
rm -rf ./data/chroma_db
python -c "from src.knowledge_base.rag_system import rag_system; print('Knowledge base reset')"
```

## Security Best Practices

- Never commit `.env` file to version control
- Use only approved AI tools from RDSec Portal
- Follow company guidelines for Generative AI services
- Keep API tokens secure and rotate regularly
- Ensure proper endpoint configuration per company policy

## Support

For hackathon support, contact the AI Hackathon Taskforce via the Teams channel.

For production deployment questions, consult your security and AI infrastructure teams.

---

🤖 **Ready to deploy your AI Employee!** 🚀
