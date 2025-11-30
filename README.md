# DEMO VIDEO

➡️ https://www.youtube.com/watch?v=8zZqAM4LOrI

# 🤖 AI Employee Workflow System

**Trend Micro AI Hackathon 2025 - Team 9**

An autonomous AI Employee that manages complete software development workflows from meeting transcripts to deployed code.

## 🆕 MCP Integration

**NEW**: This project now uses unified MCP servers for enhanced external integrations:

- **🔧 105 Total Tools**: 25 Atlassian tools + 80 GitHub tools in one agent
- **📊 Atlassian MCP**: Official server from https://mcp.atlassian.com/v1/sse
- **⚡ GitHub Enterprise MCP**: Local binary for https://dsgithub.trendmicro.com  
- **🤖 Unified Agent**: Single LangChain agent with access to all tools
- **🔄 Persistent Sessions**: Client lifecycle managed throughout workflow

### MCP Benefits
- **Natural Language Queries**: "Create a Confluence page and GitHub PR for this feature"
- **Intelligent Tool Selection**: Agent automatically chooses appropriate tools
- **Official Servers**: Maintained by Atlassian and GitHub teams
- **Enhanced Capabilities**: More robust than custom API integrations

## 🎯 What the AI Employee Does

The AI Employee autonomously executes a complete 6-step development workflow:

1. **📝 Parse Transcript** - Extracts project requirements, participants, and technical details from meeting recordings
2. **📋 Generate Requirements** - Creates business requirements document in Confluence using MCP
3. **🏗️ Create Design Spec** - Uses internal knowledge base (RAG) to generate technical design for Linux→Windows conversion
4. **🌿 Setup Git Environment** - Clones reference repository, creates feature branch
5. **💻 Implement Code** - AI converts Linux system calls to Windows APIs using knowledge base
6. **📢 Create PR & Notify** - Creates pull request via MCP, notifies team

## 🏆 Hackathon Innovation

- **MCP Integration**: Unified MCP client with 105 tools from official servers
- **Productivity Focus**: Automates entire development lifecycle
- **AI-Driven**: Uses GPT-4o via Trend Micro's RDSec AI Endpoint
- **RAG Knowledge**: ChromaDB with Linux→Windows API conversion expertise
- **Platform Conversion**: Specialized in Linux to Windows system code conversion

## Project Structure

```
├── src/
│   ├── agents/
│   │   └── workflow_agent.py    # Single agent performing complete workflow
│   ├── knowledge_base/          # RAG system for codebase knowledge
│   ├── integrations/            # External service integrations
│   ├── workflow/
│   │   └── orchestrator.py     # Sequential workflow orchestration
│   └── main.py                 # CLI entry point
├── workspace/                  # Working directory for cloned repos (created at runtime)
├── config/                     # Configuration files
├── templates/                  # Document templates
└── tests/                      # Test suite
```

## 🚀 Quick Start

### 1. Setup MCP Servers (Required)
Before running the AI workflow, you must set up the required MCP servers:

**📖 [Complete MCP Setup Guide](MCP_SETUP_GUIDE.md)** ← **Start here!**

Quick summary:
```bash
# Terminal 1: Start Atlassian MCP server (keep running)
npx -y mcp-remote https://mcp.atlassian.com/v1/sse

# Terminal 2: Build GitHub MCP server  
git clone https://github.com/github/github-mcp-server.git
cd github-mcp-server
go build -o github-mcp-server ./cmd/github-mcp-server
```

### 2. Setup Credentials
```bash
pip install -r requirements.txt
python setup_credentials.py
```

### 2. Configure Environment
Edit the generated `.env` file with your credentials:
```bash
# Trend Micro RDSec AI Endpoint
OPENAI_API_KEY=your_rdsec_ai_endpoint_api_key_here
ENDPOINT_BASE_URL=https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/

# GitHub Enterprise (for MCP)
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat
GITHUB_HOST=https://dsgithub.trendmicro.com

# Atlassian MCP Server  
ATLASSIAN_MCP_SERVER_URL=https://mcp.atlassian.com/v1/sse

# Legacy Integrations (still supported)
CONFLUENCE_BASE_URL=https://trendmicro.atlassian.net
CONFLUENCE_API_TOKEN=your_atlassian_api_token
CONFLUENCE_USER_EMAIL=your_email@trendmicro.com
CONFLUENCE_SPACE_KEY=your_space_key
TEAMS_WEBHOOK_URL=your_teams_webhook_url
```

### 3. Test MCP Integration
```bash
# Test unified MCP client
python test_mcp_integration.py

# Demo MCP workflow
python demo_mcp_workflow.py
```

### 4. Test Legacy Setup
```bash
python test_setup.py
```

### 5. Run AI Employee
```bash
python -m src.main example_transcript.txt
```

### 6. View Results
- Check `outputs/` directory for generated files
- View Confluence for requirements and design docs (created via MCP)
- Check GitHub for created pull request (created via MCP)
- See Teams for completion notification

## LangChain Integration

This project uses **LangChain** for maximum flexibility with LLM providers:

- **Model Switching**: Easy to switch between OpenAI, Anthropic, or other providers
- **Unified Interface**: Same code works with different LLMs
- **Advanced Features**: Built-in support for RAG, chains, and agents
- **Configuration**: Model selection happens in `config/agent_config.yaml`

```python
# Example: The workflow agent can use any LangChain-supported model
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Configured via YAML, no hard-coded API calls
model = ChatOpenAI(model="gpt-4")  # or ChatAnthropic(model="claude-3-sonnet")
```

## Demo Scenario

The demo showcases implementing Windows process metrics monitoring based on:
- **Input**: Meeting transcript file (hardcoded path for simplicity - `example_transcript.txt`)
- **Reference**: External repository containing Linux implementation (cloned during workflow)
- **Knowledge Base**: Architecture documentation and coding standards
- **Output**: Complete Windows implementation with tests and documentation in new feature branch

## Team Collaboration

Each team member can work on different components:
- **Workflow Agent**: Implement sequential workflow steps and AI prompts
- **Integrations**: Build connections to external services (Git, Confluence, Teams)
- **Knowledge Base**: Enhance RAG system and indexing for better context
- **Templates**: Improve document templates and output formatting
- **Demo**: Refine demo scenario and presentation materials
- **Testing**: Develop comprehensive test coverage for workflow steps

## Configuration

Key configuration files:
- `config/agent_config.yaml`: Single workflow agent settings and step-specific configurations
- `.env`: API keys and credentials
- `templates/`: Document templates for generated outputs

## Architecture

The system uses a **single-agent sequential workflow**:
- **Workflow Agent**: Performs all development tasks sequentially (requirements → design → implementation → testing → documentation)
- **Sequential Execution**: One-pass workflow from start to finish with no iteration or multi-agent communication
- **Knowledge Base**: RAG system for contextual information
- **Integrations**: External service connections (Git, Confluence, Teams)
