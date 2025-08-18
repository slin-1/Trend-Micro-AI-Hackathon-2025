# Quick Start Guide for Team Members

## 🚀 **Getting Started in 5 Minutes**

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd ai-hackathon-2025-team-9-ai-agent
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
```

### 2. Setup MCP Servers (Essential!)
**📖 [Complete MCP Setup Guide](MCP_SETUP_GUIDE.md)** ← **Required reading!**

Quick setup:
```bash
# Terminal 1: Start Atlassian MCP (keep this running)
npx -y mcp-remote https://mcp.atlassian.com/v1/sse

# Terminal 2: Build GitHub MCP  
git clone https://github.com/github/github-mcp-server.git
cd github-mcp-server && go build -o github-mcp-server ./cmd/github-mcp-server

# IMPORTANT: Copy the executable to the integrations directory
cp github-mcp-server ../ai-hackathon-2025-team-9-ai-agent/src/integrations/

# Alternative: Use the pre-built executable directly from the cloned repo
# If go build fails, you can reference the executable in the github-mcp-server directory
# The system expects to find it at: ai-hackathon-2025-team-9-ai-agent/src/integrations/github-mcp-server
```

### 3. Configure Your API Keys
Edit `.env` file:
```bash
# Required for AI models
OPENAI_API_KEY=your_rdsec_endpoint_key_here
ENDPOINT_BASE_URL=https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/

# Required for GitHub MCP
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat_here

# Required for Confluence
CONFLUENCE_SPACE_KEY=your_confluence_space_key
```

### 4. Test the Complete Setup
```bash
# Test with example transcript (both MCP servers must be running)
python -m src.main example_transcript.txt
```

---

## 👥 **Find Your Task**

### 🤖 **AI Workflow Developer** 
**Your mission**: Make the AI brain work
```bash
# Your main file
src/agents/workflow_agent.py

# Test your changes
python -c "from src.agents.workflow_agent import WorkflowAgent; print('✅ Import works')"
```

### 🔧 **Git Integration Developer**
**Your mission**: Handle repository operations
```bash
# Your main file
src/integrations/git_integration.py

# Create the demo repo separately
# Test git operations locally first
```

### 📚 **Knowledge Base Developer**
**Your mission**: Build the RAG system
```bash
# Your main files
src/knowledge_base/rag_system.py
src/knowledge_base/indexer.py

# Test embeddings
pip install sentence-transformers
```

### 🔗 **Integrations Developer**
**Your mission**: Connect to external services
```bash
# Your main files
src/integrations/confluence_integration.py
src/integrations/teams_integration.py

# Test API connections first
```

### 🧪 **QA & Testing Developer**
**Your mission**: Ensure everything works
```bash
# Your focus areas
tests/
# Add testing logic to workflow_agent.py

# Run tests
pytest tests/
```

### 🎯 **Demo & Presentation Lead**
**Your mission**: Make us look amazing
```bash
# Your deliverables
- Meeting transcripts (realistic scenarios)
- Presentation slides
- Demo environment setup
- Backup plans
```

---

## 🔄 **Daily Workflow**

### Morning (30 min)
1. **Pull latest changes**: `git pull origin main`
2. **Check team updates**: Review other members' progress
3. **Plan your day**: Focus on your specific tasks

### Development (Core work time)
1. **Focus on your component**: Don't try to do everything
2. **Test frequently**: Make sure your part works
3. **Document as you go**: Add comments and update docs

### Evening (15 min)
1. **Commit your changes**: `git add . && git commit -m "Your progress"`
2. **Push to your branch**: `git push origin feature/your-feature`
3. **Update the team**: Share what you accomplished

---

## 🆘 **Quick Help**

### Common Issues
```bash
# Import errors
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Missing packages
pip install -r requirements.txt

# Config issues
cp .env.example .env  # and edit with your keys
```

### Team Communication
- **Blockers**: Ask for help immediately, don't struggle alone
- **Integration**: Coordinate with other members early
- **Testing**: Test with the full workflow, not just your component

### Getting Unstuck
1. **Check DEVELOPMENT.md**: Detailed technical guidance
2. **Ask team members**: Someone might have solved it
3. **Focus on MVP**: Get basic functionality working first
4. **Document workarounds**: Note issues for later fixing

---

## 📊 **Progress Tracking**

### Individual Progress
- [ ] Basic setup completed
- [ ] Main component implemented  
- [ ] Unit tests written
- [ ] Integration tested
- [ ] Documentation updated

### Team Integration
- [ ] All components can talk to each other
- [ ] End-to-end workflow runs
- [ ] Demo environment ready
- [ ] Presentation materials complete
- [ ] Backup plans prepared

### Demo Readiness
- [ ] Live demo rehearsed
- [ ] Technical issues resolved
- [ ] Presentation polished
- [ ] Q&A preparation done
- [ ] Contingency plans ready

---

## 🏆 **Success Tips**

### For Everyone
1. **Start simple**: Get basic functionality working first
2. **Test early and often**: Don't wait until the end
3. **Communicate constantly**: Keep the team informed
4. **Focus on your area**: Don't try to do everything
5. **Prepare for demo day**: Practice and have backups

### Technical Tips
- Use LangChain for flexibility with AI models
- Mock external APIs during development
- Create realistic test data
- Handle errors gracefully
- Log everything for debugging

### Presentation Tips
- Focus on business value, not just technical details
- Show before/after comparisons
- Demonstrate real time savings
- Prepare for technical questions
- Have a backup demo video ready

**Remember: The goal is to impress judges with a working AI system that solves real business problems!**
